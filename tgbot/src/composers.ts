import {Composer} from 'telegraf';

import {MENU_SCENE} from './constants';
import {type TGContext} from './context';

export const StudentComposerImpl = () => {
    const composer = new Composer<TGContext>();

    composer.start((ctx) => ctx.scene.enter(MENU_SCENE));

    return composer;
};
