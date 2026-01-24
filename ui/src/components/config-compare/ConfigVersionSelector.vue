<template>
  <div class="space-y-6">
    <!-- Selected Configurations -->
    <div v-if="selectedVersions.length > 0" class="space-y-4">
      <h3 class="text-sm font-medium text-gray-900 dark:text-white">Selected Configurations ({{ selectedVersions.length }})</h3>
      <div class="space-y-2">
        <div 
          v-for="(version, index) in selectedVersions" 
          :key="`${version.version_id}-${index}`"
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
              <p class="text-sm font-medium text-gray-900 dark:text-white">{{ version.device_name }}</p>
              <p class="text-xs text-gray-600 dark:text-gray-400">
                {{ formatTimestamp(version.timestamp) }} • {{ version.device_mac }}
              </p>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <button
              @click="editVersion(index)"
              class="text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
              title="Edit Version"
              :disabled="isEditing && editingIndex !== index"
              :class="{ 'opacity-50 cursor-not-allowed': isEditing && editingIndex !== index }"
            >
             <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </button>
            <button
              @click="removeVersion(index)"
              class="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
              title="Remove Version"
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
                  {{ device.name || 'Unknown Device' }}
                </span>
                <span class="ml-2 truncate text-gray-500 dark:text-gray-400" :class="{ 'text-blue-100': false /* hover overrides? no handled by hover:text-white */ }">
                  ({{ device.mac }})
                </span>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- Version Selector -->
      <div class="space-y-4">
        <h3 class="text-sm font-medium text-gray-900 dark:text-white">2. Select Config Version</h3>
        <select
          v-model="selectedVersionId"
          :disabled="!selectedDeviceId || (loadingDevices.has(selectedDeviceId))"
          class="block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50"
        >
          <option value="">
            {{ loadingDevices.has(selectedDeviceId) ? 'Loading versions...' : 'Choose a config version...' }}
          </option>
          <option 
            v-for="version in availableVersions" 
            :key="version.version_id"
            :value="version.version_id"
          >
            {{ formatTimestamp(version.timestamp) }}
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
        @click="saveVersion"
        :disabled="!selectedVersionId || isLoading"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg v-if="isLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ isLoading ? 'Loading...' : (isEditing ? 'Update Config Version' : 'Add Config Version') }}
      </button>
    </div>

    <!-- Action Buttons -->
    <div v-if="selectedVersions.length >= 2" class="flex justify-center space-x-4 pt-6 border-t border-gray-200 dark:border-gray-700">
      <button
        @click="compareConfigs"
        class="inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
      >
        Compare Configs
      </button>
      <button
        @click="clearAll"
        class="inline-flex items-center px-6 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
      >
        Clear All
      </button>
    </div>

    <!-- Notification Modal -->
    <div v-if="showNotificationModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
       <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-sm w-full mx-4">
          <div class="flex items-center justify-center mb-4">
              <div v-if="notificationType === 'warning'" class="p-2 bg-orange-100 rounded-full">
                  <svg class="w-6 h-6 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
              </div>
              <div v-else-if="notificationType === 'error'" class="p-2 bg-red-100 rounded-full">
                  <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              </div>
               <div v-else class="p-2 bg-blue-100 rounded-full">
                  <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              </div>
          </div>
          <h3 class="text-lg font-medium text-center text-gray-900 dark:text-white mb-2">{{ notificationTitle }}</h3>
          <p class="text-sm text-center text-gray-500 dark:text-gray-400 mb-6">{{ notificationMessage }}</p>
          <div class="flex justify-center">
              <button @click="showNotificationModal = false" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
                  Close
              </button>
          </div>
       </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import type { ConfigVersion, SelectedConfigVersion } from '../../types/configCompare'
import { formatDateTime } from '../../utils/dateUtils'

interface DeviceInfo {
  mac: string
  device_id: string
  name: string
}

const emit = defineEmits<{
  'versions-selected': [versions: SelectedConfigVersion[]]
}>()

defineProps<{
  isLoading?: boolean
}>()

const selectedVersions = ref<SelectedConfigVersion[]>([])
const selectedDeviceId = ref('')
const selectedVersionId = ref('')
const availableDevices = ref<DeviceInfo[]>([])
const deviceVersionsMap = ref<Map<string, ConfigVersion[]>>(new Map())
const loadingDevices = ref<Set<string>>(new Set())
const isLoading = ref(false)
const editingIndex = ref<number | null>(null)

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

// Fetch available devices on mount
onMounted(async () => {
  await loadAvailableDevices()
})

// Computed Properties
const selectedDevice = computed(() => {
  return availableDevices.value.find(device => device.device_id === selectedDeviceId.value)
})

const availableVersions = computed(() => {
    if (!selectedDeviceId.value) return []
    return deviceVersionsMap.value.get(selectedDeviceId.value) || []
})

const selectedVersion = computed(() => {
    return availableVersions.value.find(v => v.version_id === selectedVersionId.value)
})

const isEditing = computed(() => editingIndex.value !== null)

const searchQuery = ref('')
const isDropdownOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const filteredDevices = computed(() => {
  if (!searchQuery.value) return availableDevices.value
  const query = searchQuery.value.toLowerCase()
  return availableDevices.value.filter(device => 
    device.name.toLowerCase().includes(query) || 
    device.mac.toLowerCase().includes(query)
  )
})

// Methods
const editVersion = async (index: number) => {
  const version = selectedVersions.value[index]
  editingIndex.value = index
  
  // Find device by MAC since we store device_mac
  const device = availableDevices.value.find(d => d.mac === version.device_mac)
  if (device) {
    selectedDeviceId.value = device.device_id
    searchQuery.value = device.name
    await handleDeviceChange() // Load versions
    selectedVersionId.value = version.version_id
  }
}

const cancelEdit = () => {
  editingIndex.value = null
  selectedDeviceId.value = ''
  selectedVersionId.value = ''
  searchQuery.value = ''
}

const saveVersion = async () => {
    if (!selectedVersion.value || !selectedDevice.value) return

    // Check for duplicates (excluding current item if editing)
    const existingIndex = selectedVersions.value.findIndex(
        v => v.version_id === selectedVersion.value!.version_id
    )

    if (existingIndex !== -1 && existingIndex !== editingIndex.value) {
        showNotification('Duplicate Selection', 'This specific configuration version is already selected.', 'warning')
        return
    }

    try {
        isLoading.value = true

        const newVersion: SelectedConfigVersion = {
            version_id: selectedVersion.value.version_id,
            device_mac: selectedDevice.value.mac,
            device_name: selectedDevice.value.name,
            device_id: selectedDevice.value.device_id, // Added device_id
            timestamp: selectedVersion.value.timestamp,
            config: null // Table will load it
        }

        if (isEditing.value && editingIndex.value !== null) {
            selectedVersions.value[editingIndex.value] = newVersion
        } else {
            selectedVersions.value.push(newVersion)
        }

        // Clear selection
        cancelEdit()
    } catch (error) {
        console.error("Error saving version", error)
    } finally {
        isLoading.value = false
    }
}
// Renaming addVersion to saveVersion to reflect dual purpose, 
// need to update template call. Keeping addVersion for compatibility if needed? 
// Better to replace it. I'll replace the old addVersion.

// Click outside handler
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})
import { onUnmounted } from 'vue' // Import onUnmounted
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isDropdownOpen.value = false
    // If we have a selected device but search query doesn't match, reset search query to selected device name
    if (selectedDevice.value && searchQuery.value !== selectedDevice.value.name) {
      searchQuery.value = selectedDevice.value.name
    } else if (!selectedDevice.value && searchQuery.value) {
        // If no device selected but query exists, clear it
        searchQuery.value = ''
    }
  }
}

// Methods
const selectDevice = async (device: DeviceInfo) => {
  selectedDeviceId.value = device.device_id
  searchQuery.value = device.name
  isDropdownOpen.value = false
  await handleDeviceChange()
}

// Watch for external changes to selectedDeviceId (e.g. clearing after add)
watch(selectedDeviceId, (newId: string) => {
  if (!newId) {
    searchQuery.value = ''
  } else {
    // If set programmatically, ensure name is shown
    const device = availableDevices.value.find(d => d.device_id === newId)
    if (device) searchQuery.value = device.name
  }
})

const handleDeviceChange = async () => {
  selectedVersionId.value = ''
  if (selectedDeviceId.value && !deviceVersionsMap.value.has(selectedDeviceId.value)) {
    await loadDeviceVersions(selectedDeviceId.value)
  }
}

const loadAvailableDevices = async () => {
  try {
    isLoading.value = true
    const response = await fetch('/api/config-versions')
    if (!response.ok) throw new Error('Failed to fetch devices')
    
    const data = await response.json()
    
    availableDevices.value = Object.entries(data).map(([mac, versions]: [string, any]) => ({
      mac,
      device_id: versions[0]?.device_id || mac,
      name: versions[0]?.device_name || mac
    }))
  } catch (error) {
    console.error('Error loading devices:', error)
  } finally {
    isLoading.value = false
  }
}

const loadDeviceVersions = async (deviceId: string) => {
  try {
    loadingDevices.value.add(deviceId)
    const response = await fetch(`/api/devices/${deviceId}/config-versions`)
    if (!response.ok) throw new Error('Failed to fetch device versions')
    
    const versions = await response.json()
    deviceVersionsMap.value.set(deviceId, versions)
  } catch (error) {
    console.error('Error loading device versions:', error)
    deviceVersionsMap.value.set(deviceId, [])
  } finally {
    loadingDevices.value.delete(deviceId)
  }
}



const removeVersion = (index: number) => {
  selectedVersions.value.splice(index, 1)
  emit('versions-selected', selectedVersions.value)
}

const compareConfigs = () => {
  emit('versions-selected', selectedVersions.value)
}

const clearAll = () => {
  selectedVersions.value = []
  emit('versions-selected', selectedVersions.value)
}


const formatTimestamp = (timestamp: string): string => {
  return formatDateTime(timestamp)
}
</script>