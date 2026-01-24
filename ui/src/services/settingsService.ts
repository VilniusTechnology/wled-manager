import { SettingsService } from './domain/SettingsService';
import type { AppSettings } from './domain/SettingsService';

// Create a singleton instance
const service = new SettingsService();

// Export an adapter object to maintain backward compatibility
export const settingsService = {
    async getSettings(): Promise<AppSettings> {
        const response = await service.getAllSettings();
        // API returns { settings: {...} }, extract the inner settings object
        return response.data.settings || response.data;
    },

    async updateSettings(settings: AppSettings): Promise<void> {
        await service.setAllSettings(settings);
    },

    async sendTestEmail(): Promise<void> {
        await service.sendTestEmail();
    },

    async triggerBackupEmail(): Promise<void> {
        await service.triggerBackupEmail();
    }
};

export type { AppSettings };
