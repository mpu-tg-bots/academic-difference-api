import {type Context} from 'telegraf';
import {
    type SceneContextScene,
    type WizardContextWizard,
    type WizardSession,
    type WizardSessionData,
} from 'telegraf/typings/scenes';

export interface Session extends WizardSession {
    user?: {
        firstName: string;
        lastName: string;
        middleName: string;
        group: string;
        fileId: string;
    };
}

export interface TGContext extends Context {
    session: Session;
    scene: SceneContextScene<TGContext, WizardSessionData>;
    wizard: WizardContextWizard<TGContext>;
}
