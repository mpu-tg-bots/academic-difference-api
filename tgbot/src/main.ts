import {Writable} from 'node:stream';

import express from 'express';
import type {Request, Response} from 'express';
import {Scenes, Telegraf, session} from 'telegraf';

import {StudentComposerImpl} from './composers/student';
import {getConfig} from './config';
import {createClient, createConfig} from './generated/django-client/client';
import {StudentRegisterSceneImpl} from './scenes/student_register';
import {type TGContext} from './types/context';

const main = async () => {
    const config = getConfig();

    const djangoClient = createClient(
        createConfig({
            baseUrl: 'http://academic-api:8000',
            headers: {
                Authorization: `Token ${config.DJANGO_TELEGRAM_BOT_API_TOKEN}`,
                Accept: 'application/json',
            },
        }),
    );

    const bot = new Telegraf<TGContext>(config.TELEGRAM_BOT_TOKEN);

    const studentRegister = StudentRegisterSceneImpl(djangoClient);

    const stage = new Scenes.Stage<TGContext>([studentRegister]);

    bot.use(session());
    bot.use(stage.middleware());
    bot.use(StudentComposerImpl(djangoClient));

    bot.launch();

    const server = express();

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
