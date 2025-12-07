import {type Telegraf} from 'telegraf';

import {
    FILE_DELETE_SCENE,
    FILE_LIST_SCENE,
    FILE_UPLOAD_SCENE,
    FILE_VIEW_SCENE,
    GO_TO_MENU_ACTION,
    LIST_FILE_ACTION,
    MENU_SCENE,
    UPLOAD_FILE_ACTION,
} from './constants';
import {type TGContext} from './context';
import {type FileDeleteWizardState, type FileViewWizardState} from './scenes';

export const actions = (tg: Telegraf<TGContext>) => {
    tg.action(GO_TO_MENU_ACTION, (ctx) => ctx.scene.enter(MENU_SCENE));

    tg.action(LIST_FILE_ACTION, (ctx) => ctx.scene.enter(FILE_LIST_SCENE));

    tg.action(UPLOAD_FILE_ACTION, (ctx) => ctx.scene.enter(FILE_UPLOAD_SCENE));

    tg.action(/^files_paginate:(.+)$/, async (ctx) => {
        const page = ctx.match[1];
        return ctx.scene.enter(FILE_LIST_SCENE, {page});
    });

    tg.action(/^send_file:(.+)$/, async (ctx) => {
        const fileId = ctx.match[1];
        return ctx.scene.enter(FILE_VIEW_SCENE, {
            fileId: Number(fileId),
        } satisfies FileViewWizardState);
    });

    tg.action(/^delete_file:(.+)$/, async (ctx) => {
        const fileId = ctx.match[1];
        return ctx.scene.enter(FILE_DELETE_SCENE, {
            fileId: Number(fileId),
        } satisfies FileDeleteWizardState);
    });
};
