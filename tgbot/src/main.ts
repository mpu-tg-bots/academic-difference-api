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

    const studentRegister = StudentRegisterSceneImpl(djangoClient, bot.telegram);

    const stage = new Scenes.Stage<TGContext>([studentRegister]);

    bot.use(session());
    bot.use(stage.middleware());
    bot.use(StudentComposerImpl(djangoClient));

    bot.launch();
};

main().catch(console.error);
