import {STUDENT_REGISTER_SCENE} from '../scenes/student_register';
import {type TGContext} from '../types/context';

export const StartCommandStudentImpl = () => {
    return async (ctx: TGContext) => {
        if (!ctx.session.user) {
            ctx.reply(`Здравствуйте, пройдите, пожалуйста, регистрацию`);
            return ctx.scene.enter(STUDENT_REGISTER_SCENE);
        }

        await ctx.reply(
            [
                `Здравствуйте, ${ctx.session.user.lastName} ${ctx.session.user.firstName} ${ctx.session.user.middleName}, группа ${ctx.session.user.group}`,
                `Вот ваш файл с РУПами`,
            ].join('\n'),
        );

        await ctx.replyWithDocument(ctx.session.user.fileId);

        return;
    };
};
