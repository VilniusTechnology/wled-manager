<template>
  <div>
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Backups</h1>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        View and manage device configuration backups
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && Object.keys(backups).length === 0" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <span class="ml-3 text-gray-600 dark:text-gray-400">Loading backups...</span>
    </div>

    <!-- Filters -->
    <BackupFilters
      v-if="Object.keys(backups).length > 0"
      v-model="filters"
      @update:modelValue="handleFiltersUpdate"
    />

    <!-- Backup List -->
    <BackupList
      :backups="backups"
      :devices="devices"
      :filters="filters"
      :is-loading="isLoading"
      :get-device-name="getDeviceName"
      @download-config="handleDownloadConfig"
      @download-presets="handleDownloadPresets"
      @restore="handleRestore"
      @create-backup="handleCreateBackup"
      @clear-filters="clearFilters"
    />

    <!-- Refresh Button -->
    <div class="mt-8 flex justify-center space-x-4">
      <button
        @click="fetchBackups"
        :disabled="isLoading"
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        {{ isLoading ? 'Refreshing...' : 'Refresh Backups' }}
      </button>

      <!-- Mass Backup Button -->
      <button
        @click="openMassBackupDialog"
        :disabled="isLoading || massBackupInProgress"
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        {{ massBackupInProgress ? 'Backing up...' : 'Backup All Devices' }}
      </button>
    </div>

    <!-- Download Dialog -->
    <DownloadDialog
      :is-open="showDownloadDialog"
      :backup="downloadBackup"
      :file-type="downloadFileType"
      :device-name="downloadDeviceName"
      @close="closeDownloadDialog"
      @download="performDownload"
    />

    <!-- Mass Backup Dialog -->
    <MassBackupDialog
      :is-open="showMassBackupDialog"
      :device-count="deviceCount"
      @close="closeMassBackupDialog"
      @mass-backup="handleMassBackup"
    />

    <!-- Restore Dialog -->
    <RestoreDialog
      :is-open="showRestoreDialog"
      :device="selectedRestoreDevice"
      :backup="selectedRestoreBackup"
      @close="closeRestoreDialog"
      @restore="performRestore"
    />

    <!-- Device Backup Dialog -->
    <BackupDialog
      :is-open="showBackupDialog"
      :device="selectedBackupDevice"
      @close="closeBackupDialog"
      @backup="performBackup"
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

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useBackups } from '../composables/useBackups'
import type { Backup } from '../types/backup'
import BackupDialog from '../components/shared/BackupDialog.vue'
import BackupFilters from '../components/BackupFilters.vue'
import BackupList from '../components/BackupList.vue'
import DownloadDialog from '../components/shared/DownloadDialog.vue'
import MassBackupDialog from '../components/shared/MassBackupDialog.vue'
import RestoreDialog from '../components/shared/RestoreDialog.vue'
import NotificationModal from '../components/shared/NotificationModal.vue'
import { buildApiUrl } from '../utils/apiConfig'
import type { Device } from '../types/device'

const { backups, devices, isLoading, fetchBackups, getDeviceName } = useBackups()

// Filter state
const filters = ref({
  searchQuery: '',
  dateRange: 'all',
  sortBy: 'newest'
})

// Download dialog state
const showDownloadDialog = ref(false)
const downloadBackup = ref<Backup | null>(null)
const downloadFileType = ref<'config' | 'presets'>('config')
const downloadDeviceName = ref<string | undefined>(undefined)

// Mass backup dialog state
const showMassBackupDialog = ref(false)
const massBackupInProgress = ref(false)

// Restore dialog state
const showRestoreDialog = ref(false)
const selectedRestoreBackup = ref<Backup | null>(null)
const selectedRestoreDevice = ref<Device | null>(null)

// Backup dialog state
const showBackupDialog = ref(false)
const selectedBackupDevice = ref<Device | null>(null)

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

// Computed properties
const deviceCount = computed(() => devices.value.length)

// Handle filter updates
const handleFiltersUpdate = (newFilters: typeof filters.value) => {
  filters.value = newFilters
}

// Clear all filters
const clearFilters = () => {
  filters.value = {
    searchQuery: '',
    dateRange: 'all',
    sortBy: 'newest'
  }
}

// Download handlers
const handleDownloadConfig = (backup: Backup) => {
  downloadBackup.value = backup
  downloadFileType.value = 'config'
  downloadDeviceName.value = getDeviceName(backup.mac)
  showDownloadDialog.value = true
}

const handleDownloadPresets = (backup: Backup) => {
  downloadBackup.value = backup
  downloadFileType.value = 'presets'
  downloadDeviceName.value = getDeviceName(backup.mac)
  showDownloadDialog.value = true
}

const closeDownloadDialog = () => {
  showDownloadDialog.value = false
  downloadBackup.value = null
}

const performDownload = async (backup: Backup, fileType: 'config' | 'presets') => {
  try {
    const endpoint = fileType === 'config' ? 'config' : 'presets'
    const response = await fetch(buildApiUrl(`/backups/download/${backup.id}/${endpoint}`))
    
    if (!response.ok) {
      throw new Error(`Failed to download ${fileType} file`)
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${fileType}_${backup.id}.json`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (error) {
    console.error('Download failed:', error)
    showNotification('Download Failed', `Failed to download ${fileType} file. Please try again.`, 'error')
  }
}

// Mass backup handlers
const openMassBackupDialog = () => {
  showMassBackupDialog.value = true
}

const closeMassBackupDialog = () => {
  showMassBackupDialog.value = false
}

const handleMassBackup = async (options: { config: boolean; presets: boolean }) => {
  massBackupInProgress.value = true
  try {
    const response = await fetch(buildApiUrl('/devices/backup-all'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        backup_config: options.config,
        backup_presets: options.presets
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    const result = await response.json()
    console.log('Mass backup successful:', result)
    
    // Refresh backups after mass backup
    await fetchBackups()
    
    showNotification('Success', `Mass backup completed successfully! Backed up ${result.devices_backed_up} out of ${result.total_devices} devices. ${result.failed_backups} failed.`, 'success')
  } catch (error) {
    console.error('Mass backup failed:', error)
    showNotification('Mass Backup Failed', `Mass backup failed: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
  } finally {
    massBackupInProgress.value = false
  }
}

// Restore handlers
const handleRestore = (backup: Backup) => {
  const device = devices.value.find(d => d.mac === backup.mac)
  
  if (!device) {
    showNotification('Device Not Found', `Could not find an active device with MAC ${backup.mac} to restore to. The device must be discovered and online.`, 'warning')
    return
  }
  
  selectedRestoreDevice.value = device
  selectedRestoreBackup.value = backup
  showRestoreDialog.value = true
}

const closeRestoreDialog = () => {
  showRestoreDialog.value = false
  selectedRestoreDevice.value = null
  selectedRestoreBackup.value = null
}

const performRestore = async (device: Device, backup: Backup, options: { restore_config: boolean; restore_presets: boolean }) => {
  try {
    const response = await fetch(buildApiUrl(`/devices/${device.id}/restore`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        backup_id: backup.id,
        restore_config: options.restore_config,
        restore_presets: options.restore_presets
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    const result = await response.json()
    console.log('Restore successful:', result)
    
    showNotification('Restore Successful', `Successfully restored configuration to ${device.name || device.mac}. The device may reboot.`, 'success')
  } catch (error) {
    console.error('Restore failed:', error)
    showNotification('Restore Failed', `Failed to restore device: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
  }
}

// Device Backup handlers
const handleCreateBackup = (mac: string) => {
  const device = devices.value.find(d => d.mac === mac)
  
  if (!device) {
    showNotification('Device Not Found', `Could not find an active device with MAC ${mac} to backup. The device must be discovered and online.`, 'warning')
    return
  }
  
  selectedBackupDevice.value = device
  showBackupDialog.value = true
}

const closeBackupDialog = () => {
  showBackupDialog.value = false
  selectedBackupDevice.value = null
}

const performBackup = async (device: Device, _options: { config: boolean; presets: boolean }) => {
  // Currently backend API only supports full backup (both config and presets), 
  // or via specific separate endpoints if implemented.
  // The existing single device backup endpoint POST /devices/{id}/backup does a full backup.
  
  try {
    // If backend supports selective backup, we would use options.config and options.presets
    const response = await fetch(buildApiUrl(`/devices/${device.id}/backup`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    const result = await response.json()
    console.log('Backup successful:', result)
    
    // Refresh backups list
    await fetchBackups()
    
    showNotification('Backup Successful', `Successfully created backup for ${device.name || device.mac}.`, 'success')
  } catch (error) {
    console.error('Backup failed:', error)
    showNotification('Backup Failed', `Failed to backup device: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
  }
}

// Load backups on component mount
onMounted(() => {
  fetchBackups()
})
</script>
