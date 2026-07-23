<template>
  <div>
    <h1 class="text-3xl font-bold mb-6 text-gray-900 dark:text-white">App Configuration</h1>

    <div v-if="isLoading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <div v-else class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 space-y-8">
      
      <!-- Network Scan Settings -->
      <section>
        <h2 class="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200 border-b pb-2">Network Scan Settings</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          <!-- Scan Timeout -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Scan Timeout (seconds)</label>
            <input 
              v-model.number="settings.scan_timeout" 
              type="number"
              step="0.1" 
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Timeout for checking if a device is online</p>
          </div>

          <!-- Info Timeout -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Info Retrieval Timeout (seconds)</label>
            <input 
              v-model.number="settings.info_timeout" 
              type="number" 
              step="0.1"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Timeout for fetching detailed device info</p>
          </div>

          <!-- Backup Download Timeout -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Backup Download Timeout (seconds)</label>
            <input 
              v-model.number="settings.backup_download_timeout" 
              type="number" 
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <!-- Max Workers -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Max Concurrent Workers</label>
            <input 
              v-model.number="settings.max_workers" 
              type="number" 
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Number of parallel threads for scanning</p>
          </div>

          <!-- Connection Pool Size -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Connection Pool Size</label>
            <input 
              v-model.number="settings.connection_pool_size" 
              type="number" 
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <!-- Max Retries -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Max Retries</label>
            <input 
              v-model.number="settings.max_retries" 
              type="number" 
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <!-- Scan Scheduler Start Delay -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Scheduler Initial Delay (seconds)</label>
            <input 
              v-model.number="settings.scheduler_initial_delay" 
              type="number" 
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Delay before starting the first scheduled scan after boot</p>
          </div>
        </div>
      </section>

      <!-- Time Settings -->
      <section>
        <h2 class="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200 border-b pb-2">Time Settings</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          <!-- Timezone -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Timezone</label>
            <select 
              v-model="settings.timezone" 
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option :value="undefined" disabled>Select a timezone...</option>
              <option v-for="tz in availableTimezones" :key="tz" :value="tz">
                {{ tz }}
              </option>
            </select>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Affects all date and time displays. Current selection time: {{ currentTimePreview }}
            </p>
          </div>

          <!-- Date Format -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date Format</label>
            <select 
              v-model="settings.date_format" 
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="EU_NRML">YYYY-MM-DD HH:mm:ss (European)</option>
              <option value="US_STANDARD">MM/DD/YY, HH:mm:ss AM/PM (US)</option>
              <option value="ISO">ISO 8601 (YYYY-MM-DDTHH:mm:ss.sssZ)</option>
              <option value="SHORT">Short Date (locale default)</option>
            </select>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Format for displaying dates throughout the application. Preview: {{ dateFormatPreview }}
            </p>
          </div>
        </div>
      </section>

      <!-- Email Configuration Section -->
      <section>
        <h2 class="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200 border-b pb-2">Email Backup Settings</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          <!-- SMTP Host -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">SMTP Host</label>
            <input 
              v-model="settings.smtp_host" 
              type="text" 
              placeholder="smtp.example.com"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <!-- SMTP Port -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">SMTP Port</label>
            <input 
              v-model.number="settings.smtp_port" 
              type="number" 
              placeholder="587"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <!-- SMTP User -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">SMTP User</label>
            <input 
              v-model="settings.smtp_user" 
              type="text" 
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <!-- SMTP Password -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">SMTP Password</label>
            <input 
              v-model="settings.smtp_password" 
              type="password" 
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <!-- Sender Email -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Sender Email</label>
            <input 
              v-model="settings.smtp_sender" 
              type="email" 
              placeholder="noreply@example.com"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <!-- Receiver Email -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Receiver Email</label>
            <input 
              v-model="settings.smtp_receiver" 
              type="email" 
              placeholder="your-email@example.com"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
        </div>
      </section>

      <!-- Actions -->
      <div class="flex flex-col sm:flex-row gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <button 
          @click="saveSettings" 
          :disabled="isSaving"
          class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {{ isSaving ? 'Saving...' : 'Save Settings' }}
        </button>

        <button 
          @click="testEmail" 
          :disabled="isTesting"
          class="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50"
        >
          {{ isTesting ? 'Sending...' : 'Send Test Email' }}
        </button>
      </div>

      <!-- Notifications -->
      <div v-if="message" :class="`p-4 rounded-md ${messageType === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`">
        {{ message }}
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { settingsService, type AppSettings } from '../services/settingsService';
import { useAppSettingsStore } from '../stores/appSettingsStore';

const store = useAppSettingsStore();
const settings = ref<AppSettings>({} as AppSettings);
const isLoading = ref(true);
const isSaving = ref(false);
const isTesting = ref(false);
const message = ref('');
const messageType = ref<'success' | 'error'>('success');
const availableTimezones = ref<string[]>([]);
const currentTimePreview = ref('');

// Get available timezones
try {
  // @ts-ignore
  availableTimezones.value = Intl.supportedValuesOf('timeZone');
} catch (e) {
  console.warn('Browser does not support Intl.supportedValuesOf', e);
  // Fallback to UTC if not supported
  availableTimezones.value = ['UTC'];
}

// Update time preview
const updateTimePreview = () => {
  if (!settings.value.timezone) return;
  try {
    const date = new Date();
    currentTimePreview.value = new Intl.DateTimeFormat('en-US', {
      timeZone: settings.value.timezone,
      dateStyle: 'medium',
      timeStyle: 'medium'
    }).format(date);
  } catch (e) {
    currentTimePreview.value = 'Invalid Timezone';
  }
};

watch(() => settings.value.timezone, () => {
  updateTimePreview();
});

const dateFormatPreview = ref('');

const updateDateFormatPreview = () => {
  const date = new Date();
  const tz = settings.value.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone;
  const fmt = settings.value.date_format || 'EU_NRML';
  
  try {
    switch (fmt) {
      case 'EU_NRML':
        dateFormatPreview.value = new Intl.DateTimeFormat('sv-SE', {
          timeZone: tz,
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        }).format(date);
        break;
      case 'US_STANDARD':
        dateFormatPreview.value = new Intl.DateTimeFormat('en-US', {
          timeZone: tz,
          dateStyle: 'short',
          timeStyle: 'medium'
        }).format(date);
        break;
      case 'ISO':
        dateFormatPreview.value = date.toISOString();
        break;
      case 'SHORT':
        dateFormatPreview.value = new Intl.DateTimeFormat(undefined, {
          timeZone: tz,
          dateStyle: 'short'
        }).format(date);
        break;
      default:
        dateFormatPreview.value = new Intl.DateTimeFormat(undefined, {
          timeZone: tz,
          dateStyle: 'medium',
          timeStyle: 'medium'
        }).format(date);
    }
  } catch (e) {
    dateFormatPreview.value = 'Invalid format';
  }
};

watch(() => settings.value.date_format, () => {
  updateDateFormatPreview();
});

const loadSettings = async () => {
  try {
    isLoading.value = true;
    await store.fetchSettings();
    
    // Copy store settings to local ref for editing
    if (store.settings) {
      settings.value = { ...store.settings };
      // Default to browser timezone if not set
      if (!settings.value.timezone) {
        settings.value.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        // Also update the store/draft to reflect this default if we want consistency,
        // but let's just keep it in local settings for now.
        // Actually, if we don't save it, next time it will default again.
      }
      updateTimePreview();
      updateDateFormatPreview();
    }
  } catch (error) {
    console.error('Failed to load settings:', error);
    showMessage('Failed to load settings', 'error');
  } finally {
    isLoading.value = false;
  }
};

const saveSettings = async () => {
  try {
    isSaving.value = true;
    await store.updateSettings(settings.value);
    showMessage('Settings saved successfully', 'success');
  } catch (error) {
    console.error('Failed to save settings:', error);
    showMessage('Failed to save settings', 'error');
  } finally {
    isSaving.value = false;
  }
};

const testEmail = async () => {
  try {
    isTesting.value = true;
    await settingsService.sendTestEmail();
    showMessage('Test email sent successfully', 'success');
  } catch (error) {
    console.error('Failed to send test email:', error);
    showMessage('Failed to send test email', 'error');
  } finally {
    isTesting.value = false;
  }
};

const showMessage = (msg: string, type: 'success' | 'error') => {
  message.value = msg;
  messageType.value = type;
  setTimeout(() => {
    message.value = '';
  }, 5000);
};

onMounted(() => {
  loadSettings();
});
</script>
