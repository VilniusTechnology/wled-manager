<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useBackupService } from '../../services/context/ApiServiceProvider'
import { parseBackupDate, formatDateTime } from '../../utils/dateUtils'
import NotificationModal from '../shared/NotificationModal.vue'
import RestoreDialog from '../shared/RestoreDialog.vue'

interface DeviceDetails {
  device_id: string
  mac: string
  name?: string
  has_backups: boolean
}

interface Props {
  device: DeviceDetails
  deviceStatus?: string
}

interface Backup {
  id: string
  mac: string
  timestamp: string
  presets_path: string
  cfg_path: string
  formatted_date?: string
}

const props = defineProps<Props>()

// Use API services
const backupService = useBackupService()

const isBackupOperationsDisabled = computed(() => {
  return props.deviceStatus === 'dead' || props.deviceStatus === 'Dead'
})

const backups = ref<Backup[]>([])
const isLoadingBackups = ref(true)
const isBackingUp = ref(false)
const isRestoring = ref(false)
const selectedBackup = ref<Backup | null>(null)
const showRestoreDialog = ref(false)

// Notification state
const showNotificationModal = ref(false)
const notificationTitle = ref('')
const notificationMessage = ref('')
const notificationType = ref<'success' | 'error' | 'warning' | 'info'>('info')

const showNotification = (title: string, message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
  notificationTitle.value = title
  notificationMessage.value = message
  notificationType.value = type
  showNotificationModal.value = true
}

const fetchBackups = async () => {
  try {
    isLoadingBackups.value = true
    
    const response = await backupService.getBackups()
    const allBackupsData = response.data
    
    // Filter backups for this specific device
    const deviceBackups = allBackupsData[props.device.mac] || []
    backups.value = deviceBackups
      .map((backup: Backup) => ({
        ...backup,
        formatted_date: formatBackupDate(backup.timestamp)
      }))
      .sort((a: Backup, b: Backup) => parseBackupDate(b.timestamp).getTime() - parseBackupDate(a.timestamp).getTime())
    
  } catch (error) {
    console.error('Failed to fetch backups:', error)
  } finally {
    isLoadingBackups.value = false
  }
}

const createBackup = async () => {
  try {
    isBackingUp.value = true
    
    const result = await backupService.backupDevice(props.device.device_id)
    console.log('Backup created:', result.data)
    
    // Refresh backups list
    await fetchBackups()
    
  } catch (error) {
    console.error('Failed to create backup:', error)
    showNotification('Backup Failed', `Failed to create backup: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
  } finally {
    isBackingUp.value = false
  }
}

const restoreFromBackup = async (backup: Backup, restoreConfig: boolean = true, restorePresets: boolean = true) => {
  try {
    isRestoring.value = true
    
    const result = await backupService.restoreDevice(props.device.device_id, {
      backup_id: backup.id,
      restore_config: restoreConfig,
      restore_presets: restorePresets
    })
    console.log('Restore completed:', result.data)
    
    // Wait 10 seconds for device to reboot and apply configuration
    console.log('Waiting 10 seconds for device to reboot...')
    await new Promise(resolve => setTimeout(resolve, 10000))
    
    showNotification('Success', 'Device restored successfully!', 'success')
    showRestoreDialog.value = false
    
  } catch (error) {
    console.error('Failed to restore backup:', error)
    showNotification('Restore Failed', `Failed to restore backup: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
  } finally {
    isRestoring.value = false
  }
}

const handleRestoreConfirmed = async (_device: any, backup: Backup, options: { restore_config: boolean; restore_presets: boolean }) => {
  await restoreFromBackup(backup, options.restore_config, options.restore_presets)
}

const formatBackupDate = (timestamp: string) => {
  try {
    return formatDateTime(timestamp, 'EU_NRML')
  } catch {
    return 'Invalid date'
  }
}

const getBackupAge = (timestamp: string) => {
  try {
    const backupDate = parseBackupDate(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - backupDate.getTime()
    
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
    
    if (diffDays > 0) {
      return `${diffDays}d ago`
    } else if (diffHours > 0) {
      return `${diffHours}h ago`
    } else if (diffMinutes > 0) {
      return `${diffMinutes}m ago`
    } else {
      return 'Just now'
    }
  } catch {
    return 'Unknown'
  }
}

const openRestoreDialog = (backup: Backup) => {
  selectedBackup.value = backup
  showRestoreDialog.value = true
}

onMounted(() => {
  fetchBackups()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Backup Actions -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">Device Backups</h3>
        <button
          @click="createBackup"
          :disabled="isBackingUp || isBackupOperationsDisabled"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-medium rounded-md transition-colors flex items-center space-x-2"
        >
          <svg v-if="isBackingUp" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <span>{{ isBackingUp ? 'Creating Backup...' : 'Create Backup' }}</span>
          <span v-if="isBackupOperationsDisabled && !isBackingUp" class="text-xs opacity-75">(Device Offline)</span>
        </button>
      </div>
      
      <div class="text-sm text-gray-600 dark:text-gray-400">
        <p>Create and manage backups of your WLED device configuration and presets.</p>
        <p class="mt-1">Backups include device settings, LED configurations, effects, and custom presets.</p>
      </div>
    </div>

    <!-- Backups List -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Available Backups</h3>
      
      <!-- Loading State -->
      <div v-if="isLoadingBackups" class="text-center py-8">
        <svg class="animate-spin mx-auto h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Loading backups...</p>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="backups.length === 0" class="text-center py-8">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 48 48">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v6a2 2 0 002 2h6a2 2 0 002-2v-6m0 0V9a2 2 0 00-2-2h-6a2 2 0 00-2 2v4z"></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No backups yet</h3>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Create your first backup to get started.
        </p>
      </div>
      
      <!-- Backups Grid -->
      <div v-else class="grid gap-4">
        <div
          v-for="backup in backups"
          :key="backup.id"
          class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3">
                <div class="flex-shrink-0">
                  <svg class="h-8 w-8 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm0 2h12v8H4V6z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 class="text-sm font-medium text-gray-900 dark:text-white">
                    Backup {{ backup.formatted_date }}
                  </h4>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    Created {{ getBackupAge(backup.timestamp) }} • ID: {{ backup.id.substring(0, 8) }}...
                  </p>
                </div>
              </div>
              
              <!-- Backup Details -->
              <div class="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div class="flex items-center space-x-2">
                  <svg class="h-4 w-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-gray-600 dark:text-gray-300">Configuration</span>
                  <span class="text-green-600 dark:text-green-400">✓</span>
                </div>
                <div class="flex items-center space-x-2">
                  <svg class="h-4 w-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-gray-600 dark:text-gray-300">Presets</span>
                  <span class="text-green-600 dark:text-green-400">✓</span>
                </div>
              </div>
            </div>
            
            <!-- Actions -->
            <div class="flex items-center space-x-2">
              <button
                @click="openRestoreDialog(backup)"
                :disabled="isBackupOperationsDisabled"
                class="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white text-xs font-medium rounded transition-colors"
              >
                Restore
                <span v-if="isBackupOperationsDisabled" class="text-xs opacity-75">(Offline)</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Restore Dialog -->
    <RestoreDialog
      :is-open="showRestoreDialog"
      :device="device"
      :backup="selectedBackup"
      @close="showRestoreDialog = false"
      @restore="handleRestoreConfirmed"
    />

    <!-- Notification Modal -->
    <NotificationModal
      :is-open="showNotificationModal"
      :title="notificationTitle"
      :message="notificationMessage"
      :type="notificationType"
      @close="showNotificationModal = false"
    />
  </div>
</template>
```