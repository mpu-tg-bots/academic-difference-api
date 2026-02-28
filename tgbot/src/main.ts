import {Writable} from 'node:stream';

import express from 'express';
import type {Request, Response} from 'express';
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

const main = async () => {
    const config = getConfig();

    const djangoClient = createClient(
        createConfig({
            baseUrl: 'http://127.0.0.1:8000',
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

    server.get('/health', (_req: Request, res: Response) => {
        res.status(200).end();
    });

    server.get(`/files/:id`, async (req: Request, res: Response) => {
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

    const port = 3000;

    server.listen(port, '0.0.0.0');
};

main().catch(console.error);
