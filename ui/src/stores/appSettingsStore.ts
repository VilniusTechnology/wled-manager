import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { settingsService, type AppSettings } from '../services/settingsService'

export const useAppSettingsStore = defineStore('appSettingsStore', () => {
    const settings = ref<AppSettings | null>(null)
    const isLoading = ref(false)
    const error = ref<string | null>(null)

    // Helper to get browser timezone
    const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone

    const timezone = computed(() => {
        return settings.value?.timezone || browserTimezone
    })

    const dateFormat = computed(() => {
        return settings.value?.date_format || 'EU_NRML'
    })

    async function fetchSettings() {
        isLoading.value = true
        error.value = null
        try {
            settings.value = await settingsService.getSettings()
        } catch (e: any) {
            console.error('Failed to fetch settings:', e)
            error.value = e.message || 'Failed to fetch settings'
        } finally {
            isLoading.value = false
        }
    }

    async function updateSettings(newSettings: AppSettings) {
        isLoading.value = true
        error.value = null
        try {
            await settingsService.updateSettings(newSettings)
            // Ideally we should refetch to get the canonical state, 
            // but setting locally is fine for optimisic UI or if we trust the input
            settings.value = { ...settings.value, ...newSettings }
        } catch (e: any) {
            console.error('Failed to update settings:', e)
            error.value = e.message || 'Failed to update settings'
            throw e
        } finally {
            isLoading.value = false
        }
    }

    return {
        settings,
        timezone,
        dateFormat,
        isLoading,
        error,
        fetchSettings,
        updateSettings
    }
})
