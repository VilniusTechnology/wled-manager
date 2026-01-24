<template>
  <div class="space-y-6">
    <!-- Selected Configurations -->
    <div v-if="selectedBackups.length > 0" class="space-y-4">
      <h3 class="text-sm font-medium text-gray-900 dark:text-white">Selected Backups ({{ selectedBackups.length }})</h3>
      <div class="space-y-2">
        <div 
          v-for="(backup, index) in selectedBackups" 
          :key="`${backup.backupId}-${index}`"
          class="flex items-center justify-between p-3 border rounded-lg"
          :class="[
            editingIndex === index 
              ? 'bg-blue-100 border-blue-400 dark:bg-blue-900/40 dark:border-blue-500' 
              : 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
          ]"
        >
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <div 
                class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
                :class="[
                   editingIndex === index 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-blue-500 text-white'
                ]"
              >
                {{ index + 1 }}
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900 dark:text-white">{{ backup.deviceName }}</p>
              <p class="text-xs text-gray-600 dark:text-gray-400">
                {{ formatDate(backup.timestamp) }} • {{ backup.mac }}
              </p>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <button
              @click="editBackup(index)"
              class="text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
              title="Edit Backup"
              :disabled="isEditing && editingIndex !== index"
              :class="{ 'opacity-50 cursor-not-allowed': isEditing && editingIndex !== index }"
            >
             <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </button>
            <button
              @click="removeBackup(index)"
              class="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
              title="Remove Backup"
              :disabled="isEditing"
               :class="{ 'opacity-50 cursor-not-allowed': isEditing }"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Device Selection -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Device Selector -->
      <div class="space-y-4" ref="dropdownRef">
        <h3 class="text-sm font-medium text-gray-900 dark:text-white">1. Select Device</h3>
        <div class="relative">
          <input
            type="text"
            v-model="searchQuery"
            @focus="isDropdownOpen = true"
            @input="isDropdownOpen = true"
            placeholder="Search device by name or MAC..."
            class="block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          <div v-if="selectedDeviceId" class="absolute inset-y-0 right-0 flex items-center pr-3">
             <button @click="() => { selectedDeviceId = ''; searchQuery = ''; isDropdownOpen = true; handleDeviceChange() }" class="text-gray-400 hover:text-gray-500">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
             </button>
          </div>
          <div v-else class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>

          <!-- Dropdown Options -->
          <ul
            v-if="isDropdownOpen"
            class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white dark:bg-gray-700 py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
          >
            <li
              v-if="filteredDevices.length === 0"
              class="relative cursor-default select-none py-2 pl-3 pr-9 text-gray-700 dark:text-gray-300"
            >
              No devices found.
            </li>
            <li
              v-for="device in filteredDevices"
              :key="device.device_id"
              @click="selectDevice(device)"
              class="relative cursor-default select-none py-2 pl-3 pr-9 text-gray-900 dark:text-white hover:bg-blue-600 hover:text-white"
            >
              <div class="flex items-center">
                <span class="block truncate" :class="{ 'font-semibold': selectedDeviceId === device.device_id }">
                  {{ device.name || device.hostname || 'Unknown Device' }}
                </span>
                <span class="ml-2 truncate text-gray-500 dark:text-gray-400">
                  ({{ device.mac }})
                </span>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- Version Selector -->
      <div class="space-y-4">
        <h3 class="text-sm font-medium text-gray-900 dark:text-white">2. Select Backup Version</h3>
        <select
          v-model="selectedBackupId"
          :disabled="!selectedDeviceId || availableBackups.length === 0"
          class="block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50"
        >
          <option value="">
             {{ availableBackups.length === 0 && selectedDeviceId ? 'No backups available' : 'Choose a backup version...' }}
          </option>
          <option 
            v-for="backup in availableBackups" 
            :key="backup.id"
            :value="backup.id"
          >
            {{ formatDate(backup.timestamp) }}
          </option>
        </select>
      </div>
    </div>

    <!-- Add/Update Configuration Button -->
    <div class="flex justify-center pt-4 space-x-3">
      <button
        v-if="isEditing"
        @click="cancelEdit"
        class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
      >
        Cancel
      </button>
      <button
        @click="saveBackup"
        :disabled="!selectedBackupId || isLoading"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg v-if="isLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ isLoading ? 'Loading...' : (isEditing ? 'Update Backup' : 'Add Backup') }}
      </button>
    </div>

    <!-- Action Buttons -->
    <div v-if="selectedBackups.length >= 2" class="flex justify-center space-x-4 pt-6 border-t border-gray-200 dark:border-gray-700">
      <button
        @click="compareBackups"
        class="inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
      >
        Compare Backups
      </button>
      <button
        @click="clearAll"
        class="inline-flex items-center px-6 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
      >
        Clear All
      </button>
    </div>

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
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useBackups } from '../../composables/useBackups'
import { buildApiUrl } from '../../utils/apiConfig'
import { formatDateTime } from '../../utils/dateUtils'
import NotificationModal from '../shared/NotificationModal.vue'
import type { SelectedBackup } from '../../types/backupCompare'

// Use a local interface matching what the composable returns or expects
interface Device {
  device_id: string
  mac: string
  name?: string
  hostname?: string
  has_backups: boolean
}

const emit = defineEmits<{
  'backups-selected': [backups: SelectedBackup[]]
}>()

defineProps<{
  isLoading?: boolean
}>()

const { backups, devices, fetchBackups } = useBackups()
const selectedDeviceId = ref('')
const selectedBackupId = ref('')
const selectedBackups = ref<SelectedBackup[]>([])
const isLoading = ref(false)
const editingIndex = ref<number | null>(null)

// Search/Dropdown state
const searchQuery = ref('')
const isDropdownOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

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
const devicesWithBackups = computed(() => {
  return devices.value.filter(device => device.has_backups)
})

const filteredDevices = computed(() => {
  if (!searchQuery.value) return devicesWithBackups.value
  const query = searchQuery.value.toLowerCase()
  return devicesWithBackups.value.filter(device => 
    (device.name && device.name.toLowerCase().includes(query)) || 
    (device.hostname && device.hostname.toLowerCase().includes(query)) ||
    device.mac.toLowerCase().includes(query)
  )
})

const selectedDevice = computed(() => {
  return devices.value.find(device => device.device_id === selectedDeviceId.value)
})

const availableBackups = computed(() => {
  const device = selectedDevice.value
  if (!device || !device.mac) return []
  return backups.value[device.mac] || []
})

const selectedBackup = computed(() => {
  return availableBackups.value.find(backup => backup.id === selectedBackupId.value)
})

const isEditing = computed(() => editingIndex.value !== null)

// Watchers
watch(selectedDeviceId, (newId: string) => {
  // If set programmatically (e.g. edit or selection), ensure name is shown
  if (!newId) {
    searchQuery.value = ''
    selectedBackupId.value = ''
  } else {
    selectedBackupId.value = '' // Reset backup selection on device change
    const device = devices.value.find(d => d.device_id === newId)
    if (device) {
       searchQuery.value = device.name || device.hostname || 'Unknown Device'
    }
  }
})

// Click outside handler
onMounted(() => {
  fetchBackups()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isDropdownOpen.value = false
    // Maintain search query if a device is selected
    if (selectedDevice.value && searchQuery.value !== (selectedDevice.value.name || selectedDevice.value.hostname)) {
       searchQuery.value = selectedDevice.value.name || selectedDevice.value.hostname || 'Unknown Device'
    } else if (!selectedDevice.value && searchQuery.value) {
      searchQuery.value = ''
    }
  }
}

// Methods
const handleDeviceChange = () => {
  selectedBackupId.value = ''
}

const selectDevice = (device: Device) => {
  selectedDeviceId.value = device.device_id
  searchQuery.value = device.name || device.hostname || 'Unknown Device'
  isDropdownOpen.value = false
  handleDeviceChange()
}

const editBackup = (index: number) => {
  const backup = selectedBackups.value[index]
  editingIndex.value = index
  
  // Find device by MAC
  const device = devices.value.find(d => d.mac === backup.mac)
  if (device) {
    selectedDeviceId.value = device.device_id
    // Wait for watchers to update available backups if necessary (should be sync since using computed)
    selectedBackupId.value = backup.backupId
  }
}

const cancelEdit = () => {
  editingIndex.value = null
  selectedDeviceId.value = ''
  selectedBackupId.value = ''
  searchQuery.value = ''
}

const saveBackup = async () => {
  if (!selectedBackup.value || !selectedDevice.value) return

  // Check for duplicates
  const existingIndex = selectedBackups.value.findIndex(
    backup => backup.backupId === selectedBackup.value!.id
  )
  
  if (existingIndex !== -1 && existingIndex !== editingIndex.value) {
    showNotification('Duplicate Selection', 'This backup is already selected.', 'warning')
    return
  }

  try {
    isLoading.value = true
    
    // Fetch the config content
    const response = await fetch(buildApiUrl(`/backups/${selectedBackup.value.id}/config-content`))
    if (!response.ok) {
      throw new Error(`Failed to fetch config: ${response.statusText}`)
    }
    
    const config = await response.json()
    
    const newBackup: SelectedBackup = {
      backupId: selectedBackup.value.id,
      deviceId: selectedDevice.value.device_id,
      deviceName: selectedDevice.value.name || selectedDevice.value.hostname || 'Unknown Device',
      mac: selectedDevice.value.mac,
      timestamp: selectedBackup.value.timestamp,
      config: config
    }
    
    if (isEditing.value && editingIndex.value !== null) {
      selectedBackups.value[editingIndex.value] = newBackup
    } else {
      selectedBackups.value.push(newBackup)
    }
    
    // Clear selection
    cancelEdit()
    
  } catch (error) {
    console.error('Failed to fetch config:', error)
    showNotification('Load Error', 'Failed to load backup configuration. Please try again.', 'error')
  } finally {
    isLoading.value = false
  }
}

const removeBackup = (index: number) => {
  selectedBackups.value.splice(index, 1)
  emit('backups-selected', selectedBackups.value)
}

const compareBackups = () => {
  emit('backups-selected', selectedBackups.value)
}

const clearAll = () => {
  selectedBackups.value = []
  emit('backups-selected', selectedBackups.value)
}

const formatDate = (timestamp: string) => {
  try {
    return formatDateTime(timestamp, 'EU_NRML')
  } catch (error) {
    console.warn('Failed to format backup date:', timestamp, error)
    return timestamp
  }
}
</script>