import {type MiddlewareFn} from 'telegraf';

import {type TGContext} from './context';
import {
    type HttpException,
    getUserByMessengerApiV1MessengersUserMessengerTypeMessengerUserIdGet,
} from './generated/admin-api';
import {type Client as AdminApiClient} from './generated/admin-api/client';

const MESSENGER_NOT_FOUND = 'messenger not found';

export const auth =
    (adminClient: AdminApiClient, linkUrl: string): MiddlewareFn<TGContext> =>
    async (ctx, next) => {
        const telegramId = ctx.from?.id;
        if (!telegramId) return next();

        const {data: user, error} =
            await getUserByMessengerApiV1MessengersUserMessengerTypeMessengerUserIdGet({
                client: adminClient,
                path: {
                    messenger_type: 'telegram',
                    messenger_user_id: String(telegramId),
                },
            });

        if (error) {
            const httpError = error as HttpException;
            if (httpError.errors === MESSENGER_NOT_FOUND) {
                await ctx.reply(
                    `Для использования бота необходимо привязать Telegram-аккаунт.\n\nПерейдите по ссылке для привязки: ${linkUrl}`,
                );
                return;
            }

            console.error(error);
            await ctx.reply('Возникла непредвиденная ошибка! Попробуйте, ещё раз');
            return;
        }

        ctx.state.user = user;
        return next();
    };
