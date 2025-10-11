import {academicDifferenceFileList, studentsList} from '../generated/django-client';
import {type Client} from '../generated/django-client/client';
import {STUDENT_REGISTER_SCENE} from '../scenes/student_register';
import {type TGContext} from '../types/context';

export const StartCommandStudentImpl = (client: Client) => {
    return async (ctx: TGContext) => {
        if (!ctx.from) {
            return;
        }

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
            ctx.reply(`Здравствуйте, пройдите, пожалуйста, регистрацию`);
            return ctx.scene.enter(STUDENT_REGISTER_SCENE);
        }

        const [
            {
                user: {first_name: firstName, last_name: lastName, middle_name: middleName},
                group,
            },
        ] = users;

        await ctx.reply(
            `Здравствуйте, ${lastName} ${firstName} ${middleName}, группа ${group.number}`,
        );

        const {data: fileListData, error: fileListError} = await academicDifferenceFileList({
            client,
            query: {student__telegram_id: ctx.from.id},
        });

        if (!fileListData) {
            console.error(fileListError);
            await ctx.reply('Возникла непредвиденная ошибка! Попробуйте, ещё раз');
            return;
        }

        const {results: files} = fileListData;

        if (!files.length) {
            ctx.reply(`Здравствуйте, пройдите, пожалуйста, регистрацию`);
            return ctx.scene.enter(STUDENT_REGISTER_SCENE);
        }

        const [{file_id: fileId}] = files;

        await ctx.replyWithDocument(fileId, {caption: `Вот ваш файл с РУПами`});

        return;
    };
};
