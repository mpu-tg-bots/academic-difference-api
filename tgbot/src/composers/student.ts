import {Composer} from 'telegraf';

import {StartCommandStudentImpl} from '../commands/start_student';
import {type TGContext} from '../types/context';

export const StudentComposerImpl = () => {
    const composer = new Composer<TGContext>();

    composer.start(StartCommandStudentImpl());

    return composer;
};
