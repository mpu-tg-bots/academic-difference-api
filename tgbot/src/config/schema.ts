import z from 'zod';

export const ConfigSchema = z.object({
    TELEGRAM_BOT_TOKEN: z.string().min(1),
    ADMIN_API_TOKEN: z.string().min(1),
    ADMIN_API_BASE_URL: z.string().optional(),
    VACANT_API_TOKEN: z.string().min(1),
    VACANT_API_BASE_URL: z.string().optional(),
    LINK_TELEGRAM_ACCOUNT_URL: z.string().min(1),
});

export type Config = z.infer<typeof ConfigSchema>;
