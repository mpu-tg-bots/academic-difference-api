import {Composer, Scenes, type Telegram} from 'telegraf';
import {message} from 'telegraf/filters';

import {studentsRegisterCreate} from '../generated/django-client';
import {type Client} from '../generated/django-client/client';
import {type TGContext} from '../types/context';

export const STUDENT_REGISTER_SCENE = 'student_register';

type WizardState = {
    firstName: string | undefined;
    lastName: string | undefined;
    middleName: string | undefined;
    group: string | undefined;
};

const getWizardState = (ctx: TGContext) => {
    return ctx.wizard.state as WizardState;
};

export const StudentRegisterSceneImpl = (client: Client, tgapi: Telegram) => {
    const fileHandler = new Composer<TGContext>();

    const allowedMimeTypes = new Set([
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'image/png',
        'image/jpeg',
    ]);

    const handleRegister = async (ctx: TGContext, fileId: string) => {
        const fileUrl = await tgapi.getFileLink(fileId);

        const {error} = await studentsRegisterCreate({
            client,
            body: {
                first_name: getWizardState(ctx).firstName!,
                last_name: getWizardState(ctx).lastName!,
                middle_name: getWizardState(ctx).middleName!,
                group_number: getWizardState(ctx).group!,
                file_id: fileId,
                file_url: fileUrl.toString(),
                telegram_id: ctx.from!.id,
            },
        });

        if (error) {
            console.error(error);
            await ctx.reply(`Возникла непредвиденная ошибка, попробуйте ещё раз`);
            await ctx.scene.reenter();
            return;
        }

        await ctx.scene.leave();

        await ctx.reply(`Введите /start ещё раз`);
    };

    fileHandler.on(message('photo'), async (ctx) => {
        if (!ctx.message.photo.length) {
            await ctx.reply('Вы не загрузили фото, попробуйте ещё раз!');
            return;
        }

        const {file_id: fileId} = ctx.message.photo.pop()!;

        await handleRegister(ctx, fileId);
    });

    fileHandler.on(message('document'), async (ctx) => {
        if (!ctx.message.document) {
            await ctx.reply('Вы не загрузили документ, попробуйте ещё раз!');
            return;
        }

        const {mime_type: mimeType, file_id: fileId} = ctx.message.document;

        if (!mimeType || !allowedMimeTypes.has(mimeType)) {
            await ctx.reply('Неподдерживаемый формат документа');
            return;
        }

        await handleRegister(ctx, fileId);
    });

    return new Scenes.WizardScene<TGContext>(
        STUDENT_REGISTER_SCENE,
        async (ctx) => {
            await ctx.reply(
                'Введите, пожалуйста, ваше ФИО через пробел. Отчество можно пропустить',
            );

            getWizardState(ctx).firstName = undefined;
            getWizardState(ctx).lastName = undefined;
            getWizardState(ctx).middleName = undefined;
            getWizardState(ctx).group = undefined;

            return ctx.wizard.next();
        },
        async (ctx) => {
            if (!getWizardState(ctx).firstName || !getWizardState(ctx).lastName) {
                const msg = ctx.text;
                if (!msg) {
                    await ctx.reply('Неверный формат, попробуйте ещё раз!');
                    return;
                }

                const parts = msg.split(' ');
                if (parts.length < 2) {
                    await ctx.reply('Неверный формат, попробуйте ещё раз!');
                    return;
                }

                getWizardState(ctx).firstName = parts[1];
                getWizardState(ctx).lastName = parts[0];
                getWizardState(ctx).middleName = parts[2] || '';
            }

            await ctx.reply(`Введите, пожалуйста, вашу учебную группу. Например 241-3210`);

            return ctx.wizard.next();
        },
        async (ctx) => {
            if (!getWizardState(ctx).group) {
                const msg = ctx.text;
                if (!msg) {
                    await ctx.reply('Неверный формат, попробуйте ещё раз!');
                    return;
                }

                const parts = msg.split('-');
                if (parts.length !== 2) {
                    await ctx.reply('Неверный формат, попробуйте ещё раз!');
                    return;
                }

                try {
                    const [left, right] = [parseInt(parts[0]), parseInt(parts[1])];
                    getWizardState(ctx).group = `${left}-${right}`;
                } catch (_) {
                    await ctx.reply('Неверный формат, попробуйте ещё раз!');
                    return;
                }
            }

            await ctx.reply(
                `Загрузите, пожалуйста, файл с Расхождениями Учебных Планов. Возможные форматы: .xls, .xlsx, .png, .jpeg, .jpg`,
            );

            return ctx.wizard.next();
        },
        fileHandler,
    );
};
