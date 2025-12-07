import {type MiddlewareFn} from 'telegraf';

import {STUDENT_REGISTER_SCENE} from './constants';
import {type TGContext} from './context';
import {studentsList} from './generated/django-client';
import {type Client} from './generated/django-client/client';

export const auth =
    (client: Client): MiddlewareFn<TGContext> =>
    async (ctx, next) => {
        const telegramId = ctx.from?.id;
        if (!telegramId) return next();

        const {data: studentListData, error: studentListError} = await studentsList({
            client,
            query: {telegram_id: ctx.from.id},
        });

        if (!studentListData) {
            console.error(studentListError);
            await ctx.reply('Возникла непредвиденная ошибка! Попробуйте, ещё раз');
            return;
        }

        const {results: users} = studentListData;

        if (!users.length) {
            return ctx.scene.enter(STUDENT_REGISTER_SCENE);
        }

        const [student] = users;

        ctx.state.student = student as TGContext['state']['student'];

        return next();
    };
