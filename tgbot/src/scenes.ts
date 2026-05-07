import {Scenes} from 'telegraf';

import {MENU_SCENE} from './constants';
import {type TGContext, getUser} from './context';
import {getUserRupsApiV1PrivateUsersUserIdRupsGet} from './generated/vacant-api';
import {type Client as VacantApiClient} from './generated/vacant-api/client';

export const MenuSceneImpl = (vacantClient: VacantApiClient) => {
    return new Scenes.WizardScene<TGContext>(MENU_SCENE, async (ctx) => {
        const user = getUser(ctx);

        const {data, error} = await getUserRupsApiV1PrivateUsersUserIdRupsGet({
            client: vacantClient,
            path: {user_id: user.id},
        });

        if (error) {
            console.error(error);
            await ctx.reply('Возникла непредвиденная ошибка! Попробуйте, ещё раз');
            return ctx.scene.leave();
        }

        const greeting = `Привет, ${user.surname} ${user.name} ${user.patronymic}! 👋`;

        if (!data.must_study.length) {
            await ctx.reply(`${greeting}\n\nУ тебя нет дисциплин для изучения. 🎉`);
            return ctx.scene.leave();
        }

        let message = `${greeting}\n\nДисциплины для изучения (РУП):\n\n`;

        for (const discipline of data.must_study) {
            message += `📚 ${discipline.title}\n   Форма контроля: ${discipline.control}\n\n`;
        }

        await ctx.reply(message);
        return ctx.scene.leave();
    });
};
