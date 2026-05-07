import express from 'express';
import {Scenes, Telegraf, session} from 'telegraf';

import {actions} from './actions';
import {StudentComposerImpl} from './composers';
import {getConfig} from './config';
import {type TGContext} from './context';
import * as admin from './generated/admin-api/client';
import * as vacant from './generated/vacant-api/client';
import {auth} from './middleware';
import {MenuSceneImpl} from './scenes';

const getBaseUrl = (envValue: string | undefined, defaultValue: string): string => {
    if (!envValue) return defaultValue;
    try {
        return new URL(envValue).toString();
    } catch {
        return defaultValue;
    }
};

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const main = async () => {
    const config = getConfig();

    const adminApiClient = admin.createClient(
        admin.createConfig({
            baseUrl: getBaseUrl(config.ADMIN_API_BASE_URL, 'https://admin.kd.mospolytech.ru'),
            headers: {
                Authorization: `Bearer ${config.ADMIN_API_TOKEN}`,
                Accept: 'application/json',
            },
        }),
    );

    const vacantApiClient = vacant.createClient(
        vacant.createConfig({
            baseUrl: getBaseUrl(config.VACANT_API_BASE_URL, 'https://vm.mospolytech.ru'),
            headers: {
                Authorization: `Bearer ${config.VACANT_API_TOKEN}`,
                Accept: 'application/json',
            },
        }),
    );

    const bot = new Telegraf<TGContext>(config.TELEGRAM_BOT_TOKEN);

    const menu = MenuSceneImpl(vacantApiClient);
    const stage = new Scenes.Stage<TGContext>([menu]);

    bot.use(session());
    bot.use(auth(adminApiClient, config.LINK_TELEGRAM_ACCOUNT_URL));
    bot.use(stage.middleware());
    bot.use(StudentComposerImpl());
    actions(bot);

    bot.launch();

    const server = express();

    server.use(express.json());

    server.get('/health', (_req, res) => {
        res.status(200).end();
    });

    server.post('/notify:batchCreate', async (req, res) => {
        const {tg_ids: tgIds, message} = req.body;

        if (!tgIds || !Array.isArray(tgIds) || !message) {
            res.status(400).json({error: 'Неверный формат данных'});
            return;
        }

        res.status(200).json({status: 'queued', count: tgIds.length});

        console.info(`Начинаем рассылку для ${tgIds.length} студентов...`);

        let successCount = 0;
        let failCount = 0;

        for (const tgId of tgIds) {
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

        console.info(`Рассылка завершена. Успешно: ${successCount}, Ошибок: ${failCount}`);
    });

    const port = 3000;

    server.listen(port, '0.0.0.0');
};

main().catch(console.error);
