import { z } from "zod";
import { settingsSchema } from "../settingsSchema";
describe("settingsSchema", () => {
  describe("validates correct settings", () => {
    it("validates complete settings object", () => {
      const validSettings = {
        theme: "light",
        language: "ja",
        notifications: {
          email: true,
          push: false,
          sms: false,
        },
        privacy: {
          dataSharing: false,
          analytics: true,
          cookies: true,
        },
        display: {
          fontSize: "medium",
          colorScheme: "default",
          animations: true,
        },
        performance: {
          cacheEnabled: true,
          compressionEnabled: true,
          lazyLoading: true,
        },
        security: {
          twoFactorAuth: false,
          sessionTimeout: 30,
          passwordRequirements: {
            minLength: 8,
            requireSpecialChars: true,
            requireNumbers: true,
          },
        },
        api: {
          baseUrl: "https://api.example.com",
          timeout: 5000,
          retries: 3,
        },
        features: {
          darkMode: true,
          notifications: true,
          analytics: false,
          debugging: false,
        },
      };
      expect(() => settingsSchema.parse(validSettings)).not.toThrow();
    });
    it("validates minimal settings object", () => {
      const minimalSettings = {
        theme: "light",
        language: "ja",
        notifications: {
          email: false,
          push: false,
          sms: false,
        },
        privacy: {
          dataSharing: false,
          analytics: false,
          cookies: false,
        },
        display: {
          fontSize: "medium",
          colorScheme: "default",
          animations: false,
        },
        performance: {
          cacheEnabled: false,
          compressionEnabled: false,
          lazyLoading: false,
        },
        security: {
          twoFactorAuth: false,
          sessionTimeout: 15,
          passwordRequirements: {
            minLength: 6,
            requireSpecialChars: false,
            requireNumbers: false,
          },
        },
        api: {
          baseUrl: "https://api.example.com",
          timeout: 3000,
          retries: 1,
        },
        features: {
          darkMode: false,
          notifications: false,
          analytics: false,
          debugging: false,
        },
      };
      expect(() => settingsSchema.parse(minimalSettings)).not.toThrow();
    });
  });
  describe("rejects invalid settings", () => {
    it("rejects invalid theme", () => {
      const invalidSettings = {
        theme: "invalid",
        language: "ja",
        notifications: {
          email: false,
          push: false,
          sms: false,
        },
        privacy: {
          dataSharing: false,
          analytics: false,
          cookies: false,
        },
        display: {
          fontSize: "medium",
          colorScheme: "default",
          animations: false,
        },
        performance: {
          cacheEnabled: false,
          compressionEnabled: false,
          lazyLoading: false,
        },
        security: {
          twoFactorAuth: false,
          sessionTimeout: 15,
          passwordRequirements: {
            minLength: 6,
            requireSpecialChars: false,
            requireNumbers: false,
          },
        },
        api: {
          baseUrl: "https://api.example.com",
          timeout: 3000,
          retries: 1,
        },
        features: {
          darkMode: false,
          notifications: false,
          analytics: false,
          debugging: false,
        },
      };
      expect(() => settingsSchema.parse(invalidSettings)).toThrow();
    });
    it("rejects invalid language", () => {
      const invalidSettings = {
        theme: "light",
        language: "invalid",
        notifications: {
          email: false,
          push: false,
          sms: false,
        },
        privacy: {
          dataSharing: false,
          analytics: false,
          cookies: false,
        },
        display: {
          fontSize: "medium",
          colorScheme: "default",
          animations: false,
        },
        performance: {
          cacheEnabled: false,
          compressionEnabled: false,
          lazyLoading: false,
        },
        security: {
          twoFactorAuth: false,
          sessionTimeout: 15,
          passwordRequirements: {
            minLength: 6,
            requireSpecialChars: false,
            requireNumbers: false,
          },
        },
        api: {
          baseUrl: "https://api.example.com",
          timeout: 3000,
          retries: 1,
        },
        features: {
          darkMode: false,
          notifications: false,
          analytics: false,
          debugging: false,
        },
      };
      expect(() => settingsSchema.parse(invalidSettings)).toThrow();
    });
    it("rejects invalid session timeout", () => {
      const invalidSettings = {
        theme: "light",
        language: "ja",
        notifications: {
          email: false,
          push: false,
          sms: false,
        },
        privacy: {
          dataSharing: false,
          analytics: false,
          cookies: false,
        },
        display: {
          fontSize: "medium",
          colorScheme: "default",
          animations: false,
        },
        performance: {
          cacheEnabled: false,
          compressionEnabled: false,
          lazyLoading: false,
        },
        security: {
          twoFactorAuth: false,
          sessionTimeout: -1,
          passwordRequirements: {
            minLength: 6,
            requireSpecialChars: false,
            requireNumbers: false,
          },
        },
        api: {
          baseUrl: "https://api.example.com",
          timeout: 3000,
          retries: 1,
        },
        features: {
          darkMode: false,
          notifications: false,
          analytics: false,
          debugging: false,
        },
      };
      expect(() => settingsSchema.parse(invalidSettings)).toThrow();
    });
    it("rejects invalid API timeout", () => {
      const invalidSettings = {
        theme: "light",
        language: "ja",
        notifications: {
          email: false,
          push: false,
          sms: false,
        },
        privacy: {
          dataSharing: false,
          analytics: false,
          cookies: false,
        },
        display: {
          fontSize: "medium",
          colorScheme: "default",
          animations: false,
        },
        performance: {
          cacheEnabled: false,
          compressionEnabled: false,
          lazyLoading: false,
        },
        security: {
          twoFactorAuth: false,
          sessionTimeout: 15,
          passwordRequirements: {
            minLength: 6,
            requireSpecialChars: false,
            requireNumbers: false,
          },
        },
        api: {
          baseUrl: "https://api.example.com",
          timeout: -1000,
          retries: 1,
        },
        features: {
          darkMode: false,
          notifications: false,
          analytics: false,
          debugging: false,
        },
      };
      expect(() => settingsSchema.parse(invalidSettings)).toThrow();
    });
  });
});
