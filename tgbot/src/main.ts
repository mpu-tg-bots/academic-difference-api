import {Telegraf} from 'telegraf';

import {getConfig} from './config';

const main = async () => {
    const config = getConfig();

    const telegraf = new Telegraf(config.TELEGRAM_BOT_TOKEN);

    telegraf.command('start', async (ctx) => {
        ctx.reply(`Hello, ${ctx.from.id} @${ctx.from.username}`);
    });

    telegraf.launch();
};

main().catch(console.error);
