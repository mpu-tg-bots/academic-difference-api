import {type Telegraf} from 'telegraf';

import {GO_TO_MENU_ACTION, MENU_SCENE} from './constants';
import {type TGContext} from './context';

export const actions = (tg: Telegraf<TGContext>) => {
    tg.action(GO_TO_MENU_ACTION, (ctx) => ctx.scene.enter(MENU_SCENE));
};
