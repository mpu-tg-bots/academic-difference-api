import {Composer} from 'telegraf';

import {FILE_LIST_SCENE, FILE_UPLOAD_SCENE, MENU_SCENE} from './constants';
import {type TGContext} from './context';

export const StudentComposerImpl = () => {
    const composer = new Composer<TGContext>();

    composer.start((ctx) => ctx.scene.enter(MENU_SCENE));
    composer.command('list', (ctx) => ctx.scene.enter(FILE_LIST_SCENE));
    composer.command('upload', (ctx) => ctx.scene.enter(FILE_UPLOAD_SCENE));

    return composer;
};
