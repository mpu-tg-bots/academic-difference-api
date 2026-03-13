import {Writable} from 'node:stream';

import express from 'express';
import {Scenes, Telegraf, session} from 'telegraf';

import {actions} from './actions';
import {StudentComposerImpl} from './composers';
import {getConfig} from './config';
import {type TGContext} from './context';
import {createClient, createConfig} from './generated/django-client/client';
import {auth} from './middleware';
import {
    FileDeleteSceneImpl,
    FileListSceneImpl,
    FileUploadSceneImpl,
    FileViewSceneImpl,
    MenuSceneImpl,
    StudentRegisterSceneImpl,
} from './scenes';

const getDjangoHost = () => {
    try {
        return new URL(process.env.DJANGO_BASE_URL || '').toString();
    } catch {
        return 'http://academic-api:8000';
    }
};

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const main = async () => {
    const config = getConfig();

    const djangoClient = createClient(
        createConfig({
            baseUrl: getDjangoHost(),
            headers: {
                Authorization: `Token ${config.DJANGO_TELEGRAM_BOT_API_TOKEN}`,
                Accept: 'application/json',
            },
        }),
    );

    const bot = new Telegraf<TGContext>(config.TELEGRAM_BOT_TOKEN);

    const studentRegister = StudentRegisterSceneImpl(djangoClient);

    const unauthorizedStage = new Scenes.Stage<TGContext>([studentRegister]);

    bot.use(session());
    bot.use(unauthorizedStage.middleware());

    const fileUplaod = FileUploadSceneImpl(djangoClient);
    const fileList = FileListSceneImpl(djangoClient);
    const fileView = FileViewSceneImpl(djangoClient);
    const fileDelete = FileDeleteSceneImpl(djangoClient);
    const menu = MenuSceneImpl(djangoClient);

    const stage = new Scenes.Stage<TGContext>([fileUplaod, fileList, fileView, fileDelete, menu]);

    bot.use(auth(djangoClient));
    bot.use(stage.middleware());
    bot.use(StudentComposerImpl());
    actions(bot);

    bot.launch();

    const server = express();

    server.use(express.json());

    server.get('/health', (_req, res) => {
        res.status(200).end();
    });

    server.get(`/files/:id`, async (req, res) => {
        const {id} = req.params;
        try {
            const fileLink = await bot.telegram.getFileLink(id);
            const file = await fetch(fileLink.toString());

            if (!file.ok || !file.body) {
                res.status(404).send('File not found');
                return;
            }

            const rawName = fileLink.pathname.split('/').pop() || 'file';
            const fileName = decodeURIComponent(rawName);

            res.setHeader(
                'Content-type',
                file.headers.get('content-type') || 'application/octet-stream',
            );
            res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);

            await file.body.pipeTo(Writable.toWeb(res));
        } catch (err) {
            console.error('File download error: ', err);
            res.status(500).send('Interval server Error');
        }
    });

    server.post('/notify:batchCreate', async (req, res) => {
        const {tg_ids, message} = req.body;

        if (!tg_ids || !Array.isArray(tg_ids) || !message) {
            res.status(400).json({error: 'Неверный формат данных'});
            return;
        }

        res.status(200).json({status: 'queued', count: tg_ids.length});

        console.log(`Начинаем рассылку для ${tg_ids.length} студентов...`);

        let successCount = 0;
        let failCount = 0;

        for (const tgId of tg_ids) {
            try {
                await bot.telegram.sendMessage(tgId, message);
                successCount++;
            } catch (error) {
                if (error instanceof Error) {
                    console.error(`Ошибка отправки студенту ${tgId}:`, error.message);
                }
                failCount++;
            }

            await sleep(50);
        }

        console.log(`Рассылка завершена. Успешно: ${successCount}, Ошибок: ${failCount}`);
    });

    const port = 3000;

    server.listen(port, '0.0.0.0');
};

main().catch(console.error);
