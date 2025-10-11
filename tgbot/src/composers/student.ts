import {Composer} from 'telegraf';

import {StartCommandStudentImpl} from '../commands/start_student';
import {type Client} from '../generated/django-client/client';
import {type TGContext} from '../types/context';

export const StudentComposerImpl = (client: Client) => {
    const composer = new Composer<TGContext>();

    composer.start(StartCommandStudentImpl(client));

    return composer;
};
