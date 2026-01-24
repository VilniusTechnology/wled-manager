<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useDeviceDetails } from '../composables/useDeviceDetails'
import { useDeviceStore } from '../stores/deviceStore'
import { useDeviceService } from '../services/context/ApiServiceProvider'
import type { DeviceDetails } from '../types/device'
import DeviceDetailsHeader from '../components/deviceDetails/DeviceDetailsHeader.vue'
import DeviceOverview from '../components/deviceDetails/DeviceOverview.vue'
import Modal from '../components/shared/Modal.vue'
import DeviceState from '../components/deviceDetails/DeviceState.vue'
import DeviceConfiguration from '../components/deviceDetails/DeviceConfiguration.vue'
import DeviceHardware from '../components/deviceDetails/DeviceHardware.vue'
import DeviceNetwork from '../components/deviceDetails/DeviceNetwork.vue'
import DeviceBackups from '../components/deviceDetails/DeviceBackups.vue'
import DeviceOTA from '../components/deviceDetails/DeviceOTA.vue'

const route = useRoute()
const router = useRouter()
const deviceService = useDeviceService()

const deviceId = computed(() => route.params.deviceId as string)

const device = ref<DeviceDetails | null>(null)

const activeTab = ref('overview')
const isRefreshing = ref(false)

const showAdoptDeviceModal = ref(false)
const newDeviceLocalName = ref('')

const openAdoptDeviceModal = () => {
  if (device.value) {


    newDeviceLocalName.value = device.value.local_name || ''
    showAdoptDeviceModal.value = true
  }
}

const closeAdoptDeviceModal = () => {
  showAdoptDeviceModal.value = false
  newDeviceLocalName.value = ''
}

const adoptDevice = async () => {
  if (newDeviceLocalName.value.trim() && device.value) {
    try {
      await deviceService.adoptDevices([{
        device_id: device.value.device_id, // Use device_id for adoption
        local_device_name: newDeviceLocalName.value.trim()
      }])
      closeAdoptDeviceModal()
      // Refresh to update adopted status
      fetchDeviceDetails()
      // Also update main list
      deviceStore.fetchDevices(true)
    } catch (e) {
      console.error('Failed to adopt device:', e)
    }
  }
}

const tabs = [
  { id: 'overview', name: 'Overview', icon: '📊' },
  { id: 'state', name: 'State', icon: '🔘' },
  { id: 'config', name: 'Configuration', icon: '⚙️' },
  { id: 'hardware', name: 'Hardware', icon: '🔧' },
  { id: 'network', name: 'Network', icon: '🌐' },
  { id: 'backups', name: 'Backups', icon: '💾' },
  { id: 'ota', name: 'OTA Update', icon: '⬆️' }
]

const { fetchDeviceDetails: fetchDetails, refreshDeviceDetails, isLoading: detailsLoading, error } = useDeviceDetails()

const deviceStore = useDeviceStore()
const { deviceList, isLoading: deviceStoreLoading } = storeToRefs(deviceStore)

const allDevices = computed(() => deviceList.value.map(entry => entry.device))

const canGoBack = ref(false)

const updateCanGoBack = () => {
  if (typeof window === 'undefined') {
    canGoBack.value = false
    return
  }

  const historyState = window.history.state as { back?: string } | null
  const hasBack = Boolean(historyState?.back)
  const hasLength = window.history.length > 1
  canGoBack.value = hasBack || hasLength
}

const fetchDeviceDetails = async () => {
  isRefreshing.value = true
  try {
    // 1. Load from DB (Cache)
    const result = await fetchDetails(deviceId.value)
    device.value = result
    
    // 2. Refresh from Device
    if (result) {
      await refreshDevice()
    }
  } finally {
    isRefreshing.value = false
  }
}

const goBack = () => {
  if (!canGoBack.value) return
  router.back()
}

const refreshDevice = async () => {
  const result = await refreshDeviceDetails(deviceId.value)
  if (result) {
    device.value = result
  } else {
    // If refresh fails (returns null), do NOT clear the device.
    // Instead, rely on the 'error' state from useDeviceDetails to show an error message
    // while keeping the stale data visible.
    console.warn('Device refresh returned null, keeping existing data.')
  }
}

const handleTogglePower = async () => {
  if (!device.value) return
  
  // Local optimistic update
  const originalState = device.value.state_on
  device.value.state_on = !originalState

  const result = await deviceStore.togglePower(device.value.device_id || device.value.mac)
  
  if (result.success && typeof result.state === 'boolean') {
    // Sync with authoritative state
    device.value.state_on = result.state
  } else if (!result.success) {
    // Revert on failure
    device.value.state_on = originalState
  }
}

// Computed properties for device status
const deviceStatus = computed(() => {
  if (!device.value) return 'Unknown'
  return device.value.status || 'Unknown'
})

// Watch for route changes
watch(() => route.params.deviceId, (newDeviceId) => {
  if (newDeviceId) {
    fetchDeviceDetails()
  }
  updateCanGoBack()
}, { immediate: true })

watch(() => route.fullPath, () => {
  updateCanGoBack()
})

const openDeviceInNewTab = (targetDeviceId: string) => {
  if (!targetDeviceId) return
  const routeLocation = router.resolve({ name: 'Device Details', params: { deviceId: targetDeviceId } })
  window.open(routeLocation.href, '_blank', 'noopener')
}

const setActiveTab = (tabId: string) => {
  // Update immediately for responsiveness
  activeTab.value = tabId
  
  router.replace({
    query: { ...route.query, tab: tabId }
  })
}

// Watch for route query changes to update active tab
watch(
  () => route.query.tab,
  (newTab) => {
    const rawTab = Array.isArray(newTab) ? newTab[0] : newTab
    const tabId = (rawTab as string) || 'overview'
    
    // Legacy/Deep-link mapping for Config sub-tabs
    const configSubTabs = ['leds', 'interfaces', 'audio', 'usermods', 'raw', 'general']
    if (configSubTabs.includes(tabId)) {
      activeTab.value = 'config'
      router.replace({
        query: { ...route.query, tab: 'config', subTab: tabId }
      })
      return
    }

    // Ensure tab exists
    if (tabs.some(t => t.id === tabId)) {
      activeTab.value = tabId
    } else {
      activeTab.value = 'overview'
    }
  },
  { immediate: true }
)

onMounted(async () => {
  updateCanGoBack()
  if (deviceStore.devices.size === 0) {
    await deviceStore.fetchDevices()
  }
})
</script>

<template>
  <div>
    <!-- Header -->
    <DeviceDetailsHeader 
      :device="device"
      :device-status="deviceStatus" 
      :is-loading="detailsLoading || isRefreshing"
      :available-devices="allDevices"
      :is-device-list-loading="deviceStoreLoading"
      :can-go-back="canGoBack"
      @go-back="goBack"
      @refresh-device="refreshDevice"
      @toggle-power="handleTogglePower"
      @jump-to-device="openDeviceInNewTab"
      @adopt="openAdoptDeviceModal"
    />

    <!-- Content -->
    <div>
      <!-- Loading State -->
      <div v-if="detailsLoading && !device" class="flex items-center justify-center py-12">
        <div class="text-center">
          <svg class="animate-spin mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="mt-4 text-gray-500 dark:text-gray-400">Loading device details...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
        <div class="flex items-center">
          <svg class="h-6 w-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800 dark:text-red-200">Error loading device</h3>
            <p class="mt-1 text-sm text-red-700 dark:text-red-300">{{ error }}</p>
          </div>
        </div>
        
        <div class="mt-4">
          <button
            @click="fetchDeviceDetails"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>

      <!-- Main Content -->
      <div v-else-if="device">
        <!-- Tabs Navigation -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
          <div class="border-b border-gray-200 dark:border-gray-700">
            <nav class="flex space-x-4 sm:space-x-8 px-4 sm:px-6 overflow-x-auto" aria-label="Tabs">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="setActiveTab(tab.id)"
                :class="{
                  'border-blue-500 text-blue-600 dark:text-blue-400': activeTab === tab.id,
                  'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300': activeTab !== tab.id
                }"
                class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors"
              >
                <span class="mr-2">{{ tab.icon }}</span>
                {{ tab.name }}
              </button>
            </nav>
          </div>

          <!-- Tab Content -->
          <div class="p-4 sm:p-6">
            <DeviceOverview v-if="activeTab === 'overview'" :device="device" @device-updated="refreshDevice" />
            <DeviceState v-else-if="activeTab === 'state'" :device="device" />
            <DeviceConfiguration v-else-if="activeTab === 'config'" :device="device" :device-status="deviceStatus" @config-updated="refreshDevice" />
            <DeviceHardware v-else-if="activeTab === 'hardware'" :device="device" />
            <DeviceNetwork v-else-if="activeTab === 'network'" :device="device" :device-status="deviceStatus" />
            <DeviceBackups v-else-if="activeTab === 'backups'" :device="device" :device-status="deviceStatus" />
            <DeviceOTA v-else-if="activeTab === 'ota'" :device="device" :device-status="deviceStatus" />
          </div>
        </div>
      </div>
    </div>
  </div>


  <!-- Adopt Device Modal -->
  <Modal 
    v-if="device"
    :is-open="showAdoptDeviceModal" 
    :title="`Adopt Device: ${device.name || device.local_name || device.device_id}`" 
    @close="closeAdoptDeviceModal">
    <div class="space-y-4">
      <div>
        <label for="localName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Local Name
        </label>
        <input
          id="localName"
          v-model="newDeviceLocalName"
          type="text"
          placeholder="Enter device local name (e.g., wled-livingroom)"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          @keyup.enter="adoptDevice"
        />
      </div>
    </div>

    <template #footer>
      <button
        @click="closeAdoptDeviceModal"
        class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600"
      >
        Cancel
      </button>
      <button
        @click="adoptDevice"
        :disabled="!newDeviceLocalName.trim()"
        class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Add Device
      </button>
    </template>
  </Modal>
</template>