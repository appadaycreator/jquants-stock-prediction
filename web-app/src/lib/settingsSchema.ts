import { z } from "zod";

export const settingsSchema = z.object({
  theme: z.enum(["light", "dark"]),
  language: z.enum(["ja", "en"]),
  notifications: z.object({
    email: z.boolean(),
    push: z.boolean(),
    sms: z.boolean(),
  }),
  privacy: z.object({
    dataSharing: z.boolean(),
    analytics: z.boolean(),
    cookies: z.boolean(),
  }),
  display: z.object({
    fontSize: z.enum(["small", "medium", "large"]).default("medium"),
    colorScheme: z.enum(["default", "high-contrast"]).default("default"),
    animations: z.boolean(),
  }),
  performance: z.object({
    cacheEnabled: z.boolean(),
    compressionEnabled: z.boolean(),
    lazyLoading: z.boolean(),
  }),
  security: z.object({
    twoFactorAuth: z.boolean(),
    sessionTimeout: z.number().int().positive(),
    passwordRequirements: z.object({
      minLength: z.number().int().positive(),
      requireSpecialChars: z.boolean(),
      requireNumbers: z.boolean(),
    }),
  }),
  api: z.object({
    baseUrl: z.string().url(),
    timeout: z.number().int().positive(),
    retries: z.number().int().min(0),
  }),
  features: z.object({
    darkMode: z.boolean(),
    notifications: z.boolean(),
    analytics: z.boolean(),
    debugging: z.boolean(),
  }),
});

export type AppSettings = z.infer<typeof settingsSchema>;


