<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'
import SearchIcon from '../components/shared/SearchIcon.vue'
import DeviceNetworkRow from '../components/DeviceNetworkRow.vue'
import { useDeviceStore } from '../stores/deviceStore'
import { useAppSettingsStore } from '../stores/appSettingsStore'
import { buildApiUrl } from '../utils/apiConfig'
import { useDeviceService } from '../services/context/ApiServiceProvider'
import { formatDateTime } from '../utils/dateUtils'

const deviceStore = useDeviceStore()
const deviceService = useDeviceService()
const settingsStore = useAppSettingsStore()
const { scanInProgress, networkScanDevices } = storeToRefs(deviceStore)
const { settings, isLoading: loadingSettings } = storeToRefs(settingsStore)

const lastSchedulerScan = ref<any>(null)
const loadingSchedulerResults = ref(false)
const isEditingRange = ref(false)
const editNetworkRange = ref('')

// Initialize local edit value when settings are loaded or edit starts
const startEditing = () => {
  editNetworkRange.value = (settings.value?.network_range as string) || ''
  isEditingRange.value = true
}

const cancelEditing = () => {
  isEditingRange.value = false
  editNetworkRange.value = ''
}

const saveNetworkRange = async () => {
  if (!settings.value) return
  
  try {
    await settingsStore.updateSettings({
      ...settings.value,
      network_range: editNetworkRange.value || undefined
    })
    isEditingRange.value = false
  } catch (error) {
    console.error('Failed to update network range:', error)
  }
}

const scanNetwork = async () => {
  try {
    console.log('Starting network scan...')
    await deviceStore.scanNetwork()
    // After manual scan, refresh scheduler results
    await loadLastSchedulerScan()
  } catch (error) {
    console.error('Scan failed:', error)
  }
}

const loadLastSchedulerScan = async () => {
  try {
    loadingSchedulerResults.value = true
    const response = await fetch(buildApiUrl('/schedulers/network_scan/results'))
    if (response.ok) {
      const data = await response.json()
      if (data.success && data.results) {
        lastSchedulerScan.value = data.results
        console.log('Loaded last scheduler scan:', data.results)
      }
    }
  } catch (error) {
    console.error('Failed to load scheduler scan results:', error)
  } finally {
    loadingSchedulerResults.value = false
  }
}

const schedulerScanTime = computed(() => {
  if (!lastSchedulerScan.value?.timestamp) return null
  return formatDateTime(lastSchedulerScan.value.timestamp)
})

onMounted(async () => {
  console.log('NetworkScanPage mounted')
  await Promise.all([
    loadLastSchedulerScan(),
    settingsStore.fetchSettings()
  ])
})

const handleAdoptDevice = async (deviceId: string, localName: string) => {
  try {
    console.log('Adopting device:', deviceId, 'with name:', localName)
    
    // Call the adopt service
    await deviceService.adoptDevices([{
      device_id: deviceId,
      local_device_name: localName
    }])
    
    // After successful adoption, clear scan results
    deviceStore.clearScanResults()
    
    // Refresh device list to show the new device
    await deviceStore.fetchDevices(true)
    
    // Optional: Show success notification (if we had one here)
    // Or just let the list refresh show it
  } catch (error) {
    console.error('Failed to adopt device:', error)
  }
}
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-2xl font-bold">Network Scan</h1>
      <p class="text-gray-600 dark:text-gray-400">Discover and add new WLED devices on your network</p>
    </div>

    <!-- Scan Configuration -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mb-6">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div class="flex-1">
          <h2 class="text-lg font-semibold mb-2">Scan Configuration</h2>
          <div v-if="loadingSettings" class="flex items-center gap-2 text-sm text-gray-500">
             <LoadingSpinner class="w-4 h-4" /> Loading configuration...
          </div>
          <div v-else>
            <div v-if="!isEditingRange" class="flex flex-col gap-1">
               <div class="flex items-center gap-2">
                 <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Network Range:</span>
                 <code class="bg-gray-100 dark:bg-gray-900 px-2 py-0.5 rounded text-sm font-mono text-gray-800 dark:text-gray-200">
                   {{ settings?.network_range || 'Default (Local Network)' }}
                 </code>
               </div>
               <p class="text-gray-600 dark:text-gray-400 text-sm">
                 Defines which IP addresses are scanned. Example: <code>192.168.1.0/24</code>
               </p>
            </div>
            
            <div v-else class="flex flex-col gap-2 max-w-md">
              <label for="network-range" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Network Range (CIDR)</label>
              <input
                id="network-range"
                v-model="editNetworkRange"
                type="text"
                class="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-primary focus:ring-primary sm:text-sm px-3 py-2"
                placeholder="e.g. 192.168.1.0/24"
                @keyup.enter="saveNetworkRange"
                @keyup.esc="cancelEditing"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400">
                Specify a CIDR range (e.g., 192.168.1.0/24) to limit the scan. Leave empty or use default to scan the local subnet automatically.
              </p>
            </div>
          </div>
        </div>
        
        <div class="flex gap-3">
          <template v-if="!isEditingRange">
             <button
              @click="startEditing"
              :disabled="loadingSettings"
              class="text-primary hover:text-primary-dark font-medium text-sm px-3 py-2 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
            >
              Edit Configuration
            </button>
          </template>
          <template v-else>
            <button
              @click="cancelEditing"
              class="text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 font-medium text-sm px-3 py-2 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="saveNetworkRange"
              :disabled="loadingSettings"
              class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 text-sm font-medium"
            >
              Save Changes
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- Scan Controls -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mb-6">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 class="text-lg font-semibold mb-2">Network Discovery</h2>
          <p class="text-gray-600 dark:text-gray-400 text-sm">
            Scan your local network to find WLED devices that haven't been added yet.
          </p>
          <p v-if="lastSchedulerScan" class="text-gray-500 dark:text-gray-400 text-xs mt-2">
            Last scheduled scan: {{ schedulerScanTime }} 
            ({{ lastSchedulerScan.total_discovered }} devices found, {{ lastSchedulerScan.new_devices }} new)
          </p>
        </div>
        <div class="flex gap-3">
          <button
            @click="scanNetwork"
            :disabled="scanInProgress"
            class="bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <LoadingSpinner v-if="scanInProgress" class="w-5 h-5" />
            <SearchIcon v-else class="w-5 h-5" />
            <span>{{ scanInProgress ? 'Scanning...' : 'Start Network Scan' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Scan Results -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
      <div class="p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-semibold">Scan Results</h2>
        <p class="text-gray-600 dark:text-gray-400 text-sm mt-1">
          Devices found during the last network scan
        </p>
      </div>

      <div class="p-4 sm:p-6">
        <div v-if="scanInProgress" class="text-center py-12">
          <div class="inline-flex items-center gap-3">
            <LoadingSpinner class="w-8 h-8 text-primary" />
            <div>
              <p class="text-lg font-medium">Scanning network...</p>
              <p class="text-gray-600 dark:text-gray-400 text-sm">This may take a few moments</p>
            </div>
          </div>
        </div>
        <div v-else-if="networkScanDevices.length === 0" class="text-center py-12">
          <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">No devices found</h3>
          <p class="text-gray-600 dark:text-gray-400 mb-4">
            No WLED devices were found on your network. Make sure your devices are powered on and connected.
          </p>
          <button
            @click="scanNetwork"
            class="bg-primary text-white px-4 py-2 rounded hover:bg-primary-dark transition-colors"
          >
            Try Again
          </button>
        </div>
        <div v-else class="space-y-4">
          <DeviceNetworkRow v-for="device in networkScanDevices" :key="device.device.device_id" :device="device.device" @adopt-device="handleAdoptDevice" />
        </div>
      </div>
    </div>

    <!-- Scan Tips -->
    <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 sm:p-6 mt-6">
      <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">Scan Tips</h3>
      <ul class="text-blue-800 dark:text-blue-200 text-sm space-y-1">
        <li>• Make sure your WLED devices are powered on and connected to the same network</li>
        <li>• Ensure your firewall allows UDP broadcasts on port 21324</li>
        <li>• Check that your devices have unique IP addresses</li>
      </ul>
    </div>
  </div>
</template>
