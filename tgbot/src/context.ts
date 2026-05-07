import assert from 'node:assert';

import {type Context} from 'telegraf';
import {
    type SceneContextScene,
    type WizardContextWizard,
    type WizardSession,
    type WizardSessionData,
} from 'telegraf/typings/scenes';

import {type UserResponse} from './generated/admin-api';

export interface TGContext extends Context {
    session: WizardSession;
    scene: SceneContextScene<TGContext, WizardSessionData>;
    wizard: WizardContextWizard<TGContext>;
    state: {user?: UserResponse};
}

export const getUser = (ctx: TGContext) => {
    const user = ctx.state.user;
    assert(user);
    return user;
};
