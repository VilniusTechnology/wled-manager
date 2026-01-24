<template>
  <div>
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Scheduler Management</h1>
      <p class="text-gray-600 dark:text-gray-400">Monitor and control periodic processes</p>
    </div>

    <!-- Global Actions -->
    <div class="mb-6 flex gap-3">
      <button
        @click="startAllSchedulers"
        :disabled="loading"
        class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors"
      >
        <i class="fas fa-play mr-2"></i>
        Start All
      </button>
      <button
        @click="stopAllSchedulers"
        :disabled="loading"
        class="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors"
      >
        <i class="fas fa-stop mr-2"></i>
        Stop All
      </button>
      <button
        @click="refreshStatuses"
        :disabled="loading"
        class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors"
      >
        <i class="fas fa-sync-alt mr-2" :class="{ 'fa-spin': loading }"></i>
        Refresh
      </button>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <i class="fas fa-exclamation-circle text-red-400"></i>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800 dark:text-red-200">Error</h3>
          <div class="mt-2 text-sm text-red-700 dark:text-red-300">
            {{ error }}
          </div>
        </div>
        <div class="ml-auto pl-3">
          <button
            @click="error = null"
            class="inline-flex bg-red-50 dark:bg-red-900/20 rounded-md p-1.5 text-red-500 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/40"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Success Alert -->
    <div v-if="successMessage" class="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <i class="fas fa-check-circle text-green-400"></i>
        </div>
        <div class="ml-3">
          <div class="text-sm text-green-700 dark:text-green-300">
            {{ successMessage }}
          </div>
        </div>
        <div class="ml-auto pl-3">
          <button
            @click="successMessage = null"
            class="inline-flex bg-green-50 dark:bg-green-900/20 rounded-md p-1.5 text-green-500 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/40"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Schedulers Grid -->
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="scheduler in schedulers"
        :key="scheduler.scheduler_id"
        class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700"
      >
        <!-- Header -->
        <div class="p-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ scheduler.friendly_name || scheduler.name }}
            </h3>
            <StatusBadge :status="scheduler.state" />
          </div>
          <div class="mt-2 flex items-center justify-between border-t border-gray-100 dark:border-gray-700 pt-2">
            <span class="text-sm text-gray-600 dark:text-gray-400">Auto-Run Enabled</span>
            <button 
              @click="toggleScheduler(scheduler.scheduler_id)"
              class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              :class="isSchedulerEnabled(scheduler.scheduler_id) ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'"
            >
              <span
                class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                :class="isSchedulerEnabled(scheduler.scheduler_id) ? 'translate-x-6' : 'translate-x-1'"
              />
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="p-4 space-y-4">
          <!-- Status Info -->
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">Interval:</span>
              <span class="font-medium text-gray-900 dark:text-white">{{ formatInterval(scheduler.interval_days) }}</span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">Last Run:</span>
              <span class="font-medium text-gray-900 dark:text-white">
                {{ scheduler.last_run ? formatDate(scheduler.last_run) : 'Never' }}
              </span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">Last Success:</span>
              <span class="font-medium text-gray-900 dark:text-white">
                {{ scheduler.last_success ? formatDate(scheduler.last_success) : 'Never' }}
              </span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">Next Run:</span>
              <span class="font-medium text-gray-900 dark:text-white">
                {{ scheduler.next_run ? formatDate(scheduler.next_run) : 'Not scheduled' }}
              </span>
            </div>

            <div class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">Success Rate:</span>
              <span class="font-medium text-gray-900 dark:text-white">
                <!-- Show device metrics if available, otherwise show scheduler execution metrics -->
                <template v-if="scheduler.device_success_count !== undefined && scheduler.device_total_count !== undefined">
                  {{ Math.round(scheduler.device_success_rate || 0) }}%
                  ({{ scheduler.device_success_count }}/{{ scheduler.device_total_count }})
                </template>
                <template v-else>
                  {{ Math.round(scheduler.success_rate || 0) }}%
                  ({{ scheduler.success_count }}/{{ scheduler.run_count }})
                </template>
              </span>
            </div>
          </div>

          <!-- Backup Settings Injection -->
          <div v-if="isBackupScheduler(scheduler)" class="pt-4 border-t border-gray-100 dark:border-gray-700 space-y-4">
            <h4 class="text-sm font-medium text-gray-900 dark:text-white">Backup Configuration</h4>
            
            <div>
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Interval (Hours)</label>
              <input 
                v-model.number="settings.backup_interval_hours" 
                type="number" 
                min="1"
                class="w-full text-sm rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Retention (Count)</label>
              <input 
                v-model.number="settings.backup_retention_count" 
                type="number" 
                min="1"
                class="w-full text-sm rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
            
            <div class="flex items-center">
              <input 
                id="backup_email" 
                v-model="settings.backup_email_enabled" 
                @change="saveBackupSettings"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="backup_email" class="ml-2 block text-sm text-gray-900 dark:text-gray-300">
                Send email notification on completion
              </label>
            </div>

            <button 
              @click="saveBackupSettings" 
              :disabled="loading"
              class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-3 py-2 rounded text-sm transition-colors"
            >
              Save Configuration
            </button>

          </div>

          <!-- Network Scan Settings Injection -->
          <div v-if="isNetworkScanScheduler(scheduler)" class="pt-4 border-t border-gray-100 dark:border-gray-700 space-y-4">
            <h4 class="text-sm font-medium text-gray-900 dark:text-white">Scan Configuration</h4>
            
            <div>
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Interval (Hours)</label>
              <input 
                v-model.number="settings.network_scan_interval_hours" 
                type="number" 
                min="1"
                class="w-full text-sm rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
              <p class="text-xs text-gray-400 mt-1">Recommended: 168 hours (7 days)</p>
            </div>

            <button 
              @click="saveNetworkScanSettings" 
              :disabled="loading"
              class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-3 py-2 rounded text-sm transition-colors"
            >
              Save Configuration
            </button>
          </div>

          <!-- Device Refresh Settings Injection -->
          <div v-if="isDeviceRefreshScheduler(scheduler)" class="pt-4 border-t border-gray-100 dark:border-gray-700 space-y-4">
            <h4 class="text-sm font-medium text-gray-900 dark:text-white">Refresh Configuration</h4>
            
            <div>
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Interval (Hours)</label>
              <input 
                v-model.number="settings.device_refresh_interval_hours" 
                type="number" 
                min="1"
                class="w-full text-sm rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <button 
              @click="saveDeviceRefreshSettings" 
              :disabled="loading"
              class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-3 py-2 rounded text-sm transition-colors"
            >
              Save Configuration
            </button>
          </div>

          <!-- Health Check Settings Injection -->
          <div v-if="isHealthCheckScheduler(scheduler)" class="pt-4 border-t border-gray-100 dark:border-gray-700 space-y-4">
            <h4 class="text-sm font-medium text-gray-900 dark:text-white">Health Check Configuration</h4>
            
            <div>
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Interval (Seconds)</label>
              <input 
                v-model.number="settings.health_check_interval_seconds" 
                type="number" 
                min="10"
                class="w-full text-sm rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
              <p class="text-xs text-gray-400 mt-1">Recommended: 30-120 seconds</p>
            </div>

            <button 
              @click="saveHealthCheckSettings" 
              :disabled="loading"
              class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-3 py-2 rounded text-sm transition-colors"
            >
              Save Configuration
            </button>
          </div>

          <!-- Error/Warning Display -->
          <div v-if="scheduler.last_error" :class="scheduler.state === 'warning' ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800' : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'" class="border rounded p-3">
            <div class="flex items-start">
              <i class="fas mt-0.5 mr-2 flex-shrink-0" :class="scheduler.state === 'warning' ? 'fa-exclamation-circle text-yellow-500 dark:text-yellow-400' : 'fa-exclamation-triangle text-red-500 dark:text-red-400'"></i>
              <div class="text-sm">
                <div class="font-medium" :class="scheduler.state === 'warning' ? 'text-yellow-800 dark:text-yellow-200' : 'text-red-800 dark:text-red-200'">
                  {{ scheduler.state === 'warning' ? 'Last Warning:' : 'Last Error:' }}
                </div>
                <div class="mt-1" :class="scheduler.state === 'warning' ? 'text-yellow-700 dark:text-yellow-300' : 'text-red-700 dark:text-red-300'">
                  {{ scheduler.last_error }}
                </div>
                <div v-if="scheduler.last_error_time" class="text-xs mt-1" :class="scheduler.state === 'warning' ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400'">
                  {{ formatDate(scheduler.last_error_time) }}
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 pt-2">
            <button
              v-if="scheduler.state === 'stopped'"
              @click="startScheduler(scheduler.scheduler_id)"
              :disabled="loading"
              class="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-3 py-2 rounded text-sm transition-colors"
            >
              <i class="fas fa-play mr-1"></i>
              Start
            </button>
            
            <button
              v-if="scheduler.state === 'running'"
              @click="stopScheduler(scheduler.scheduler_id)"
              :disabled="loading"
              class="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-3 py-2 rounded text-sm transition-colors"
            >
              <i class="fas fa-stop mr-1"></i>
              Stop
            </button>
            
            <button
              @click="runSchedulerNow(scheduler.scheduler_id)"
              :disabled="loading"
              class="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-3 py-2 rounded text-sm transition-colors"
            >
              <i class="fas fa-play-circle mr-1"></i>
              Run Now
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 flex items-center space-x-3">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        <span class="text-gray-700 dark:text-gray-300">Processing...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { formatDate } from '../utils/dateUtils'
import { schedulerService } from '../services/schedulerService'
import { settingsService, type AppSettings } from '../services/settingsService'
import StatusBadge from '../components/StatusBadge.vue'

interface Scheduler {
  scheduler_id: string
  name: string
  friendly_name?: string
  state: 'running' | 'stopped' | 'error' | 'warning'
  interval_days: number
  last_run: string | null
  last_success: string | null
  next_run: string | null
  last_error: string | null
  last_error_time: string | null
  run_count: number
  success_count: number
  error_count: number
  success_rate: number
  device_success_count?: number
  device_total_count?: number
  device_success_rate?: number
}

const schedulers = ref<Scheduler[]>([])
const settings = ref<AppSettings>({})
const loading = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const loadSchedulers = async () => {
  try {
    loading.value = true
    error.value = null
    const [schedulersResponse, settingsResponse] = await Promise.all([
      schedulerService.getAllSchedulers(),
      settingsService.getSettings()
    ])
    schedulers.value = schedulersResponse.schedulers || []
    settings.value = settingsResponse
  } catch (err: any) {
    error.value = err.message || 'Failed to load data'
  } finally {
    loading.value = false
  }
}

const getSettingKey = (schedulerId: string): string => {
  return `disable_${schedulerId}`
}

const isSchedulerEnabled = (schedulerId: string): boolean => {
  const key = getSettingKey(schedulerId)
  // If setting is true (disabled), then enabled is false
  return !settings.value[key]
}

const toggleScheduler = async (schedulerId: string) => {
  try {
    loading.value = true
    const currentEnabled = isSchedulerEnabled(schedulerId)
    const newEnabled = !currentEnabled
    
    // Update setting first
    const key = getSettingKey(schedulerId)
    const newSettings = { ...settings.value, [key]: !newEnabled } // disable = !enabled
    
    await settingsService.updateSettings(newSettings)
    settings.value = newSettings
    
    // Then start/stop scheduler
    if (newEnabled) {
      await schedulerService.startScheduler(schedulerId)
    } else {
      await schedulerService.stopScheduler(schedulerId)
    }
    
    // Refresh list
    const response = await schedulerService.getAllSchedulers()
    schedulers.value = response.schedulers || []
    
    successMessage.value = `Scheduler ${newEnabled ? 'enabled' : 'disabled'} successfully`
  } catch (err: any) {
    error.value = err.message || 'Failed to toggle scheduler'
    // Reload settings to ensure UI is in sync
    const settingsResponse = await settingsService.getSettings()
    settings.value = settingsResponse
  } finally {
    loading.value = false
  }
}

const startScheduler = async (schedulerId: string) => {
  try {
    loading.value = true
    error.value = null
    const response = await schedulerService.startScheduler(schedulerId)
    if (response.success) {
      successMessage.value = response.message || null
      await loadSchedulers()
    } else {
      error.value = response.message || 'Failed to start scheduler'
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to start scheduler'
  } finally {
    loading.value = false
  }
}

const stopScheduler = async (schedulerId: string) => {
  try {
    loading.value = true
    error.value = null
    const response = await schedulerService.stopScheduler(schedulerId)
    if (response.success) {
      successMessage.value = response.message || null
      await loadSchedulers()
    } else {
      error.value = response.message || 'Failed to stop scheduler'
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to stop scheduler'
  } finally {
    loading.value = false
  }
}

const runSchedulerNow = async (schedulerId: string) => {
  try {
    loading.value = true
    error.value = null
    const response = await schedulerService.runSchedulerNow(schedulerId)
    if (response.success) {
      successMessage.value = response.message || null
      await loadSchedulers()
    } else {
      error.value = response.message || 'Failed to run scheduler'
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to run scheduler'
  } finally {
    loading.value = false
  }
}

const startAllSchedulers = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await schedulerService.startAllSchedulers()
    if (response.success) {
      successMessage.value = response.message || null
    } else {
      error.value = response.message || 'Some schedulers failed to start'
    }
    await loadSchedulers()
  } catch (err: any) {
    error.value = err.message || 'Failed to start all schedulers'
  } finally {
    loading.value = false
  }
}

const stopAllSchedulers = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await schedulerService.stopAllSchedulers()
    if (response.success) {
      successMessage.value = response.message || null
    } else {
      error.value = response.message || 'Some schedulers failed to stop'
    }
    await loadSchedulers()
  } catch (err: any) {
    error.value = err.message || 'Failed to stop all schedulers'
  } finally {
    loading.value = false
  }
}

const refreshStatuses = () => {
  loadSchedulers()
}



const isBackupScheduler = (scheduler: Scheduler) => {
  return scheduler.name === 'device_backup' || scheduler.friendly_name === 'Device Backup'
}

const isHealthCheckScheduler = (scheduler: Scheduler) => {
  return scheduler.name === 'health_check' || scheduler.friendly_name === 'Device Health Check'
}

const isNetworkScanScheduler = (scheduler: Scheduler) => {
  return scheduler.name === 'network_scan' || scheduler.friendly_name === 'Network Scan'
}

const isDeviceRefreshScheduler = (scheduler: Scheduler) => {
  return scheduler.name === 'device_refresh' || scheduler.friendly_name === 'Device Refresh'
}

const saveBackupSettings = async () => {
  try {
    loading.value = true
    await settingsService.updateSettings(settings.value)
    successMessage.value = 'Backup settings saved successfully'
  } catch (err: any) {
    error.value = err.message || 'Failed to save backup settings'
  } finally {
    loading.value = false
  }
}

const saveNetworkScanSettings = async () => {
  try {
    loading.value = true
    await settingsService.updateSettings(settings.value)
    successMessage.value = 'Network scan settings saved successfully. New interval will apply on next page reload or scheduler restart.'
  } catch (err: any) {
    error.value = err.message || 'Failed to save network scan settings'
  } finally {
    loading.value = false
  }
}

const saveDeviceRefreshSettings = async () => {
  try {
    loading.value = true
    await settingsService.updateSettings(settings.value)
    successMessage.value = 'Device refresh settings saved successfully. New interval will apply on next page reload or scheduler restart.'
  } catch (err: any) {
    error.value = err.message || 'Failed to save device refresh settings'
  } finally {
    loading.value = false
  }
}

const saveHealthCheckSettings = async () => {
  try {
    loading.value = true
    await settingsService.updateSettings(settings.value)
    successMessage.value = 'Health check settings saved successfully. New interval will apply on next page reload.'
  } catch (err: any) {
    error.value = err.message || 'Failed to save health check settings'
  } finally {
    loading.value = false
  }
}

const formatInterval = (intervalDays: number): string => {
  if (intervalDays < 1 / 24) {
    // Less than 1 hour - show in minutes
    const minutes = Math.round(intervalDays * 24 * 60)
    return `${minutes} minute(s)`
  } else if (intervalDays < 1) {
    // Less than 1 day - show in hours
    const hours = Math.round(intervalDays * 24)
    return `${hours} hour(s)`
  } else if (intervalDays === 1) {
    return '1 day'
  } else {
    return `${intervalDays} day(s)`
  }
}

// Auto-refresh every 30 seconds
let autoRefreshInterval: number
onMounted(() => {
  loadSchedulers()
  autoRefreshInterval = setInterval(loadSchedulers, 30000)
})

onUnmounted(() => {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval)
  }
})

// Clear messages after 5 seconds
watch(successMessage, (newVal) => {
  if (newVal) {
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  }
})
</script>