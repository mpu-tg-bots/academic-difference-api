import z from 'zod';

export const ConfigSchema = z.object({
    TELEGRAM_BOT_TOKEN: z.string().min(1),
});

export type Config = z.infer<typeof ConfigSchema>;
