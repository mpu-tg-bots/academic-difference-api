import {SQLite} from '@telegraf/session/sqlite';
import {Scenes, Telegraf, session} from 'telegraf';

import {StudentComposerImpl} from './composers/student';
import {getConfig} from './config';
import {StudentRegisterSceneImpl} from './scenes/student_register';
import {type TGContext} from './types/context';

const main = async () => {
    const config = getConfig();

    const bot = new Telegraf<TGContext>(config.TELEGRAM_BOT_TOKEN);

    const store = SQLite<Scenes.WizardSession>({
        filename: 'storage.sqlite',
    });

    const studentRegister = StudentRegisterSceneImpl(bot.telegram);

    const stage = new Scenes.Stage<TGContext>([studentRegister]);

    bot.use(session({store}));
    bot.use(stage.middleware());
    bot.use(StudentComposerImpl());

    bot.launch();
};

main().catch(console.error);
