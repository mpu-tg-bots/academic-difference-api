import assert from 'node:assert';

import {type Context} from 'telegraf';
import {
    type SceneContextScene,
    type WizardContextWizard,
    type WizardSession,
    type WizardSessionData,
} from 'telegraf/typings/scenes';

import {type Student} from './generated/django-client';

type RequiredDeep<T> = {
    [P in keyof T]-?: T[P] extends object
        ? T[P] extends (...args: any[]) => any
            ? T[P]
            : RequiredDeep<T[P]>
        : T[P];
};

export interface TGContext extends Context {
    session: WizardSession;
    scene: SceneContextScene<TGContext, WizardSessionData>;
    wizard: WizardContextWizard<TGContext>;
    state: {student?: RequiredDeep<Student>};
}

export const getStudent = (ctx: TGContext) => {
    const student = ctx.state.student;
    assert(student);
    return student;
};
