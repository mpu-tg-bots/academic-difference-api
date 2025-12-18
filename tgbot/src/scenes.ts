import {Composer, Markup, Scenes} from 'telegraf';
import {message} from 'telegraf/filters';

import {
    FILE_DELETE_SCENE,
    FILE_LIST_SCENE,
    FILE_UPLOAD_SCENE,
    FILE_VIEW_SCENE,
    GO_TO_MENU_ACTION,
    MENU_SCENE,
    STUDENT_REGISTER_SCENE,
} from './constants';
import {type TGContext, getStudent} from './context';
import {
    type StateEnum,
    academicDifferenceFileCreate,
    academicDifferenceFileDestroy,
    academicDifferenceFileList,
    academicDifferenceFileRetrieve,
    studentsRegisterCreate,
} from './generated/django-client';
import {type Client} from './generated/django-client/client';

export type PaginatedResponse<T> = {
    count: number;
    next?: string | null;
    previous?: string | null;
    results: Array<T>;
};

export type Extractor<T> = (data: T) => ReturnType<typeof Markup.button.callback>[];

const getParam = (input: string, key: string) => {
    const url = new URL(input);
    return url.searchParams.get(key);
};

export function buildPaginationMarkupButtons<T>(
    data: PaginatedResponse<T>,
    extractor: Extractor<T>,
    prefix: string,
) {
    const fileButtons = data.results.map(extractor);

    const navRow: ReturnType<typeof Markup.button.callback>[] = [];

    if (data.previous)
        navRow.push(
            Markup.button.callback('Назад', `${prefix}:${getParam(data.previous!, 'page')}`),
        );

    if (data.next)
        navRow.push(Markup.button.callback('Дальше', `${prefix}:${getParam(data.next!, 'page')}`));

    if (navRow.length) fileButtons.push(navRow);

    return fileButtons;
}

export const MenuSceneImpl = (client: Client) => {
    return new Scenes.WizardScene<TGContext>(MENU_SCENE, async (ctx) => {
        const {id, user, group} = getStudent(ctx);

        const {data: fileListData, error: fileListError} = await academicDifferenceFileList({
            client,
            query: {student__id: id, page: getPage(ctx.wizard.state)},
        });

        if (!fileListData) {
            console.error(fileListError);
            await ctx.reply('Возникла непредвиденная ошибка! Попробуйте, ещё раз');
            return ctx.scene.leave();
        }

        if (!fileListData) {
            console.error(fileListError);
            await ctx.reply('Возникла непредвиденная ошибка! Попробуйте, ещё раз');
            return ctx.scene.leave();
        }

        const {results: files} = fileListData;

        await ctx.reply(
            `Привет, ${user.last_name} ${user.first_name} ${user.middle_name} ${group.number}! 👋

Твои основные возможности:
${files.length > 0 ? '\n- 📤 Просматривать текущую информацию по РУПам (/list)' : ''}
- 📋 Загружать файлы РУПов (/upload)
`,
        );
        return ctx.scene.leave();
    });
};

type StudentRegisterWizardState = {
    firstName: string | undefined;
    lastName: string | undefined;
    middleName: string | undefined;
    group: string | undefined;
};

const getStudentRegisterWizardState = (ctx: TGContext) => {
    return ctx.wizard.state as StudentRegisterWizardState;
};

const getHelloMessage = () => {
    return `Привет! 👋
Добро пожаловать в систему управления РУПами. Этот бот создан в рамках проектной деятельности и предназначен для удобной загрузки и управления информацией по твоим РУПам.

📝 Это тестовая версия бота. Мы активно работаем над его функциональностью, и некоторые возможности могут добавляться или изменяться. Ваш фидбек очень важен для нас!

📌 Для начала работы необходимо пройти авторизацию. После этого ты сможешь:
- Загружать файлы РУПов (/upload)
- Просматривать текущую информацию по РУПам (/list)

Если у тебя возникнут вопросы по работе бота, ты можешь обратиться к зам. декана факультета ИТ — Даньшиной Марине Владимировне: @mdanshina.  
`;
};

const getFormatErrorMessage = () => {
    return `Пожалуйста, укажи номер группы в правильном формате (например, 211-321).`;
};

export const StudentRegisterSceneImpl = (client: Client) => {
    return new Scenes.WizardScene<TGContext>(
        STUDENT_REGISTER_SCENE,
        async (ctx) => {
            await ctx.reply(getHelloMessage());

            await ctx.reply(`Давай познакомимся. Как тебя зовут? (Укажи фио полностью)`);

            getStudentRegisterWizardState(ctx).firstName = undefined;
            getStudentRegisterWizardState(ctx).lastName = undefined;
            getStudentRegisterWizardState(ctx).middleName = undefined;
            getStudentRegisterWizardState(ctx).group = undefined;

            return ctx.wizard.next();
        },
        async (ctx) => {
            if (
                !getStudentRegisterWizardState(ctx).firstName ||
                !getStudentRegisterWizardState(ctx).lastName
            ) {
                const msg = ctx.text;
                if (!msg) {
                    await ctx.reply(getFormatErrorMessage());
                    return;
                }

                const parts = msg.split(' ');
                if (parts.length < 2) {
                    await ctx.reply(getFormatErrorMessage());
                    return;
                }

                getStudentRegisterWizardState(ctx).firstName = parts[1];
                getStudentRegisterWizardState(ctx).lastName = parts[0];
                getStudentRegisterWizardState(ctx).middleName = parts[2] || '';
            }

            await ctx.reply(`Какой у тебя номер группы? (Например: 211-321)`);

            return ctx.wizard.next();
        },
        async (ctx) => {
            if (!getStudentRegisterWizardState(ctx).group) {
                const msg = ctx.text;
                if (!msg) {
                    await ctx.reply(getFormatErrorMessage());
                    return;
                }

                const parts = msg.split('-');
                if (parts.length !== 2) {
                    await ctx.reply(getFormatErrorMessage());
                    return;
                }

                try {
                    const [left, right] = [parseInt(parts[0]), parseInt(parts[1])];
                    getStudentRegisterWizardState(ctx).group = `${left}-${right}`;
                } catch (_) {
                    await ctx.reply(getFormatErrorMessage());
                    return;
                }
            }

            const {error} = await studentsRegisterCreate({
                client,
                body: {
                    first_name: getStudentRegisterWizardState(ctx).firstName!,
                    last_name: getStudentRegisterWizardState(ctx).lastName!,
                    middle_name: getStudentRegisterWizardState(ctx).middleName!,
                    group_number: getStudentRegisterWizardState(ctx).group!,
                    telegram_id: ctx.from!.id,
                },
            });

            if (error) {
                console.error(error);
                await ctx.reply(`Возникла непредвиденная ошибка, попробуйте ещё раз`);
                await ctx.scene.reenter();
                return;
            }

            await ctx.reply(`🎉 Регистрация успешно завершена! Спасибо, что заполнил(а) анкету.
Теперь ты полноценный пользователь системы. Твои основные возможности:
- 📤 Загрузить РУП – первый шаг к закрытию расхождений. (/upload)
- 📋 Мои РУПы – просмотр загруженных файлов. (/list)
`);

            await ctx.scene.leave();
        },
    );
};

export const FileUploadSceneImpl = (client: Client) => {
    const fileHandler = new Composer<TGContext>();

    const allowedMimeTypes = new Set([
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'image/png',
        'image/jpeg',
    ]);

    const handleRegister = async (ctx: TGContext, fileId: string) => {
        const {id} = getStudent(ctx);

        const {error} = await academicDifferenceFileCreate({
            client,
            body: {
                student_id: id,
                state: 'REVIEW',
                file_id: fileId,
            },
        });

        if (error) {
            console.error(error);
            await ctx.reply(`Возникла непредвиденная ошибка, попробуй ещё раз`);
            await ctx.scene.reenter();
            return;
        }

        await ctx.scene.enter(FILE_LIST_SCENE);
    };

    fileHandler.on(message('photo'), async (ctx) => {
        if (!ctx.message.photo.length) {
            await ctx.reply('Вы не загрузили фото, попробуй ещё раз!');
            return;
        }

        const {file_id: fileId} = ctx.message.photo.pop()!;

        await handleRegister(ctx, fileId);
    });

    fileHandler.on(message('document'), async (ctx) => {
        if (!ctx.message.document) {
            await ctx.reply('Вы не загрузили документ, попробуй ещё раз!');
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
        FILE_UPLOAD_SCENE,
        async (ctx) => {
            await ctx.reply(
                `Загрузите, пожалуйста, файл с Расхождениями Учебных Планов. Возможные форматы: .xls, .xlsx, .png, .jpeg, .jpg`,
            );

            return ctx.wizard.next();
        },
        fileHandler,
    );
};

const getPage = (input: object) => {
    if ('page' in input) {
        try {
            return Number(input.page);
        } catch (_error) {
            return undefined;
        }
    }
    return undefined;
};

const STATUS_TO_TEXT: Record<StateEnum, string> = {
    APPROVED: 'Подтверждён ✅',
    NOT_ACCEPTED: 'Не принят ❌',
    REVIEW: 'На рассмотрении ⏳',
};

export const FileListSceneImpl = (client: Client) => {
    return new Scenes.WizardScene<TGContext>(FILE_LIST_SCENE, async (ctx) => {
        const {id} = getStudent(ctx);

        const {data: fileListData, error: fileListError} = await academicDifferenceFileList({
            client,
            query: {student__id: id, page: getPage(ctx.wizard.state)},
        });

        if (ctx.updateType === 'callback_query') {
            await ctx.answerCbQuery();
        }

        if (!fileListData) {
            console.error(fileListError);
            await ctx.reply('Возникла непредвиденная ошибка! Попробуйте, ещё раз');
            return ctx.scene.leave();
        }

        const {results: files} = fileListData;

        if (!files.length) {
            await ctx.reply(`У вас нет загруженных файлов с Расхождениями Учебных Планов (РУП)`);
            return ctx.scene.enter(MENU_SCENE);
        }

        await ctx.reply(
            'Список файлов',
            Markup.inlineKeyboard([
                ...buildPaginationMarkupButtons(
                    fileListData,
                    (file) => [
                        Markup.button.callback(
                            `Файл ${file.id}, ${STATUS_TO_TEXT[file.state!]}`,
                            `send_file:${file.id}`,
                        ),
                        Markup.button.callback(`Удалить`, `delete_file:${file.id}`),
                    ],
                    'files_paginate',
                ),
                [Markup.button.callback('Меню', GO_TO_MENU_ACTION)],
            ]),
        );

        return ctx.scene.leave();
    });
};

export type FileViewWizardState = {
    fileId: number;
};

const getFileViewWizardState = (ctx: TGContext) => ctx.wizard.state as FileViewWizardState;

export const FileViewSceneImpl = (client: Client) => {
    return new Scenes.WizardScene<TGContext>(FILE_VIEW_SCENE, async (ctx) => {
        const {data, error} = await academicDifferenceFileRetrieve({
            client,
            path: {id: getFileViewWizardState(ctx).fileId},
        });

        if (error) {
            console.error(error);
            await ctx.reply('Возникла непредвиденная ошибка! Попробуйте, ещё раз');
            return ctx.scene.leave();
        }

        if (ctx.updateType === 'callback_query') {
            await ctx.answerCbQuery();
        }

        if (!data) {
            await ctx.reply('Файл не найден!');
            return ctx.scene.leave();
        }

        await ctx.replyWithDocument(data.file_id);
        return ctx.scene.leave();
    });
};

export type FileDeleteWizardState = {
    fileId: number;
};

const getFileDeleteWizardState = (ctx: TGContext) => ctx.wizard.state as FileViewWizardState;

export const FileDeleteSceneImpl = (client: Client) => {
    return new Scenes.WizardScene<TGContext>(FILE_DELETE_SCENE, async (ctx) => {
        const {data, error: retrieveError} = await academicDifferenceFileRetrieve({
            client,
            path: {id: getFileViewWizardState(ctx).fileId},
        });

        if (retrieveError) {
            await ctx.reply('Возникла непредвиденная ошибка! Попробуйте, ещё раз');
            return ctx.scene.enter(FILE_LIST_SCENE);
        }

        if (ctx.updateType === 'callback_query') {
            await ctx.answerCbQuery();
        }

        if (!data) {
            await ctx.reply('Файл не найден!');
            return ctx.scene.enter(FILE_LIST_SCENE);
        }

        if (data.state === 'APPROVED') {
            await ctx.reply('Файл нельзя удалить, его уже утвердили!');
            return ctx.scene.enter(FILE_LIST_SCENE);
        }

        const {error: deleteError} = await academicDifferenceFileDestroy({
            client,
            path: {id: getFileDeleteWizardState(ctx).fileId},
        });

        if (deleteError) {
            console.error(deleteError);
            await ctx.reply('Возникла непредвиденная ошибка! Попробуйте, ещё раз');
            return ctx.scene.enter(FILE_LIST_SCENE);
        }

        await ctx.reply('Файл успешно удалён');

        return ctx.scene.enter(FILE_LIST_SCENE);
    });
};
