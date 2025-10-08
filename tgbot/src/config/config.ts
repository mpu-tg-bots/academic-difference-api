import {ConfigSchema} from './schema';

export class InvalidConfigError extends Error {
    cause: Error;

    constructor(msg: string, cause: Error) {
        super(msg);
        this.cause = cause;
    }
}

export const getConfig = () => {
    try {
        const validatedConfig = ConfigSchema.parse(process.env);
        return validatedConfig;
    } catch (cause) {
        if (!(cause instanceof Error)) {
            throw cause;
        }
        throw new InvalidConfigError('invalid config', cause);
    }
};
