<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { Device, DeviceProps } from '../types/device'
import type { DeviceFilters } from '../types/deviceFilters'
import DevicesPageHeader from '../components/devices/DevicesPageHeader.vue'
import DevicesActionBar from '../components/devices/DevicesActionBar.vue'
import DevicesCount from '../components/devices/DevicesCount.vue'
import DeviceFiltersComponent from '../components/devices/DeviceFilters.vue'
import DevicesGridView from '../components/devices/DevicesGridView.vue'
import DevicesListView from '../components/devices/DevicesListView.vue'
import BackupDialog from '../components/shared/BackupDialog.vue'
import Modal from '../components/shared/Modal.vue'
import NotificationModal from '../components/shared/NotificationModal.vue'
import ReleaseConfirmationModal from '../components/modals/ReleaseConfirmationModal.vue'
import ConfirmationModal from '../components/shared/ConfirmationModal.vue'
import AddDeviceModal from '../components/modals/AddDeviceModal.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'
import { useDeviceFilters } from '../composables/useDeviceFilters'
import { useDevices } from '../composables/useDevices'
import { useBackups } from '../composables/useBackups'
import { useDeviceService } from '../services/context/ApiServiceProvider'

interface Props extends DeviceProps {
  devices: Device[]
  isLoading: boolean
  scanInProgress: boolean
}

const props = withDefaults(defineProps<Props>(), {
  devices: () => [],
  isLoading: false,
  scanInProgress: false
})

const emit = defineEmits<{
  'refresh-devices': []
  'scan-network': []
  'backup-device': [deviceId: string]
  'restore-device': [deviceId: string]
  'visit-device': [deviceId: string]
  'delete-device': [deviceId: string]
  'adopt-device': [deviceId: string, localName: string]
  'release-device': [deviceId: string]
  'add-device': [localName: string]
  'set-view-mode': [mode: string]
}>()

// Use API services
const deviceService = useDeviceService()

const viewMode = ref('list')
const currentFilters = ref<DeviceFilters>({
  status: '',
  search: '',
  hasBackups: null,
  stateOn: null,
  adopted: null,
  hasStaticIp: null,
  wifiSleep: null,
  turnOnAfterPowerUp: null,
  mqttEnabled: null,
  architecture: '',
  softwareVersion: ''
})

// Device selection state
const selectedDevices = ref<Set<string>>(new Set())
const selectAll = ref(false)

// Mass OTA update state
const showMassOTADialog = ref(false)
const massOTAFile = ref<File | null>(null)
const isMassOTAInProgress = ref(false)
const massOTAResults = ref<any>(null)

// Mass Health Check state
const isMassHealthCheckInProgress = ref(false)

// Backup dialog state
const showBackupDialog = ref(false)
const backupDeviceData = ref<any>(null)

// Restore dialog state
const restoreDeviceData = ref<any>(null)
const deviceBackups = ref<any[]>([])
const isRestoring = ref(false)

// Adopt dialog state
const showAdoptDialog = ref(false)
const adoptDeviceData = ref<any>(null)
const newDeviceLocalName = ref('')

// Notification modal state
const showNotificationModal = ref(false)
const notificationTitle = ref('')
const notificationMessage = ref('')
const notificationType = ref<'success' | 'error' | 'warning' | 'info'>('info')

// Router for navigation
const router = useRouter()

// Release modal state
const showReleaseModal = ref(false)
const deviceToRelease = ref<{ id: string; name: string; mac: string }>({ id: '', name: '', mac: '' })
const isReleasing = ref(false)
const isAdopting = ref(false)

// Delete modal state
const showDeleteConfirmModal = ref(false)
const deviceToDelete = ref<{ id: string; name: string } | null>(null)

// Add Device modal state
const showAddDeviceModal = ref(false)

const handleAddDeviceConfirmed = async (ip: string, localName: string) => {
  try {
    await useDevices().addDevice(ip, localName)
    
    // Show success notification
    notificationTitle.value = 'Success'
    notificationMessage.value = `Device ${localName || ip} added successfully!`
    notificationType.value = 'success'
    showNotificationModal.value = true
    
    // Refresh devices
    emit('refresh-devices')
  } catch (error) {
    console.error('Add device failed:', error)
    // Show error notification
    notificationTitle.value = 'Error'
    notificationMessage.value = `Failed to add device: ${error instanceof Error ? error.message : 'Unknown error'}`
    notificationType.value = 'error'
    showNotificationModal.value = true
  }
}

// Create a computed ref for devices to make it reactive
const devicesRef = computed(() => {
  return props.devices || []
})

// Use the device filtering composable
const { filteredDevices } = useDeviceFilters(devicesRef, currentFilters)

// Use filtered devices directly (no fallback needed with improved logic)
const displayDevices = computed(() => filteredDevices.value)

// Update device count to show filtered results
const showingDevices = computed(() => displayDevices.value.length)
const totalDevices = computed(() => props.devices.length)

const setViewMode = (mode: string) => {
  viewMode.value = mode
  emit('set-view-mode', mode)
}

const refreshDevices = () => {
  emit('refresh-devices')
}

const scanNetwork = () => {
  emit('scan-network')
}

const backupDevice = (deviceId: string) => {
  // Find the device by ID
  const device = props.devices.find(d => d.device_id === deviceId || d.id === deviceId)
  if (device) {
    backupDeviceData.value = device
    showBackupDialog.value = true
  } else {
    console.error('Device not found:', deviceId)
  }
}

const restoreDevice = async (deviceId: string) => {
  console.log('restoreDevice called with deviceId:', deviceId)
  console.log('All devices:', props.devices)
  // Find the device by ID
  const device = props.devices.find(d => d.device_id === deviceId || d.id === deviceId)
  console.log('Found device:', device)
  if (device) {
    restoreDeviceData.value = device
    // Set loading state
    isRestoring.value = true
    
    // Fetch latest backup data before showing restore dialog
    console.log('Fetching latest backup data...')
    try {
      await fetchBackups()
      console.log('Latest backups fetched successfully')
    } catch (error) {
      console.error('Failed to fetch latest backups:', error)
      notificationTitle.value = 'Error'
      notificationMessage.value = 'Failed to load backup data. Please try again.'
      notificationType.value = 'error'
      showNotificationModal.value = true
      isRestoring.value = false
      return
    }
    
    // Reset loading state
    isRestoring.value = false
    
    // Get backups for this device
    const mac = device.mac
    console.log('Device MAC:', mac)
    console.log('Available backups object:', backups.value)
    console.log('Backups for this MAC:', backups.value[mac])
    console.log('All backup keys:', Object.keys(backups.value))
    
    deviceBackups.value = backups.value[mac] || []
    console.log('Device backups set to:', deviceBackups.value)
    router.push(`/devices/${deviceId}?tab=backups`)
  } else {
    console.error('Device not found:', deviceId)
  }
}

const visitDevice = (deviceId: string) => {
  emit('visit-device', deviceId)
}

const viewDetails = (deviceId: string) => {
  router.push(`/devices/${deviceId}`)
}

const deleteDevice = (deviceId: string) => {
  const device = props.devices.find(d => d.id === deviceId || d.device_id === deviceId)
  if (device) {
    deviceToDelete.value = {
      id: deviceId,
      name: device.name || device.hostname || 'Unknown Device'
    }
    showDeleteConfirmModal.value = true
  }
}

const confirmDeleteDevice = () => {
  if (deviceToDelete.value) {
    emit('delete-device', deviceToDelete.value.id)
    showDeleteConfirmModal.value = false
    deviceToDelete.value = null
    
    // Show success notification
    notificationTitle.value = 'Success'
    notificationMessage.value = 'Device deletion request sent.'
    notificationType.value = 'success'
    showNotificationModal.value = true
  }
}

const adoptDevice = (deviceId: string) => {
  console.log('DevicesPage: adoptDevice called', { deviceId })
  // Find the device by ID
  const device = props.devices.find(d => d.device_id === deviceId || d.id === deviceId)
  console.log('DevicesPage: Found device', device)
  
  if (device) {
    adoptDeviceData.value = device
    showAdoptDialog.value = true
  } else {
    console.error('Device not found:', deviceId)
    // Try to find by partial match or fallback if needed - but for now just logging
    console.log('Available devices:', props.devices.map(d => ({ id: d.id, device_id: d.device_id, name: d.name })))
  }
}

const releaseDevice = async (deviceId: string) => {
  if (!deviceId) {
    console.error('Cannot release device: deviceId is undefined')
    return
  }
  
  // Find device details for the modal
  const device = props.devices.find(d => d.id === deviceId || d.device_id === deviceId)
  
  if (device) {
    // Show the release confirmation modal
    showReleaseModal.value = true
    deviceToRelease.value = {
      id: deviceId,
      name: device.name || device.hostname || 'Unknown Device',
      mac: device.mac || ''
    }
  } else {
    console.error('Device not found for release:', deviceId)
  }
}

const confirmReleaseDevice = async (deviceId: string) => {
  try {
    isReleasing.value = true
    const result = await releaseDevices([deviceId]) // Use composable logic for optimistic update
    console.log('Release successful:', result)
    
    // Close the modal
    showReleaseModal.value = false
    
    // Show success notification
    notificationTitle.value = 'Success'
    notificationMessage.value = 'Device released successfully!'
    notificationType.value = 'success'
    showNotificationModal.value = true
  } catch (error) {
    console.error('Release failed:', error)
    // Show error notification
    notificationTitle.value = 'Error'
    notificationMessage.value = `Release failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    notificationType.value = 'error'
    showNotificationModal.value = true
  } finally {
    isReleasing.value = false
  }
}


const handleFiltersChanged = (filters: DeviceFilters) => {
  currentFilters.value = filters
}

// Get the functions from composables
const { backupDevice: performBackup, scanInProgress, adoptDevices, releaseDevices } = useDevices()
const { backups, fetchBackups } = useBackups()

const closeBackupDialog = () => {
  showBackupDialog.value = false
  backupDeviceData.value = null
}

const closeAdoptDialog = () => {
  showAdoptDialog.value = false
  adoptDeviceData.value = null
  newDeviceLocalName.value = ''
}

const handleBackupConfirmed = async (device: any, _options: { config: boolean; presets: boolean }) => {
  try {
    await performBackup(device.device_id || device.id)
    // Refresh devices after backup
    emit('refresh-devices')
  } catch (error) {
    console.error('Backup failed:', error)
    notificationTitle.value = 'Backup Failed'
    notificationMessage.value = `Backup failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    notificationType.value = 'error'
    showNotificationModal.value = true
  }
}


const handleAdoptConfirmed = async () => {
  if (!adoptDeviceData.value || !newDeviceLocalName.value.trim()) return

  const deviceName = adoptDeviceData.value.name || 'Unknown'

  try {
    isAdopting.value = true
    const result = await adoptDevices([{
      device_id: adoptDeviceData.value.device_id,
      local_device_name: newDeviceLocalName.value.trim()
    }])
    console.log('Adopt successful:', result.data)
    
    // Close the dialog
    closeAdoptDialog()
    
    // Refresh devices after adopt (handled by composable, but keep emit if needed for parent, though mainly used for list refresh which composable does)
    emit('refresh-devices')
    
    // Show success notification
    notificationTitle.value = 'Success'
    notificationMessage.value = `Device ${deviceName} adopted successfully!`
    notificationType.value = 'success'
    showNotificationModal.value = true
  } catch (error) {
    console.error('Adopt failed:', error)
    
    // Show error notification
    notificationTitle.value = 'Error'
    notificationMessage.value = `Adopt failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    notificationType.value = 'error'
    showNotificationModal.value = true
  } finally {
    isAdopting.value = false
  }
}

// Mass OTA functions

// Fetch backups when component mounts and handle query params
onMounted(async () => {
  console.log('DevicesPage onMounted - calling fetchBackups')
  await fetchBackups()
  console.log('DevicesPage - Backups after fetch:', backups.value)
  
  // Check valid query params for actions
  const route = router.currentRoute.value
  
  // Default to grid view on mobile if not explicitly set
  if (typeof window !== 'undefined' && window.innerWidth < 768) {
    viewMode.value = 'grid'
  }

  if (route.query.action === 'restore' && route.query.deviceId) {
    const deviceId = route.query.deviceId as string
    console.log('Found restore action in query, triggering restore for:', deviceId)
    
    // We need to wait for devices to be loaded if they aren't already
    if (props.devices.length === 0 && props.isLoading) {
      const stopWatch = watch(() => props.isLoading, (loading) => {
        if (!loading) {
          stopWatch()
          restoreDevice(deviceId)
          // Clear query params to prevent re-triggering on refresh
          router.replace({ query: {} })
        }
      })
    } else {
      restoreDevice(deviceId)
      // Clear query params
      router.replace({ query: {} })
    }
  }

  // Check for status filter in query params
  if (route.query.status && deviceFiltersRef.value) {
    const status = route.query.status as string
    console.log('Applying status filter from query:', status)
    deviceFiltersRef.value.filters.status = status.toLowerCase()
    // No need to clear query immediately so user sees the filter, 
    // but typically we might want to keep it or clear it. 
    // Keeping it allows bookmarking.
  }
})

// Reference to the filters component
const deviceFiltersRef = ref<InstanceType<typeof DeviceFiltersComponent> | null>(null)

// Device selection functions

// Mass OTA functions
const openMassOTADialog = () => {
  if (selectedDevices.value.size === 0) {
    return
  }
  showMassOTADialog.value = true
}

const closeMassOTADialog = () => {
  showMassOTADialog.value = false
  massOTAFile.value = null
  massOTAResults.value = null
}

const handleMassOTAFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    massOTAFile.value = file
  }
}

const performMassOTAUpdate = async () => {
  if (!massOTAFile.value || selectedDevices.value.size === 0) return

  isMassOTAInProgress.value = true
  massOTAResults.value = null

  try {
    const result = await deviceService.performMassOTAUpdateWithFile(
      massOTAFile.value,
      Array.from(selectedDevices.value)
    )
    massOTAResults.value = result.data

    // Refresh devices after mass update
    emit('refresh-devices')
    
    // Clear selection
    clearSelection()

  } catch (error) {
    console.error('Mass OTA update failed:', error)
    massOTAResults.value = {
      success: false,
      message: `Mass OTA update failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      total_devices: selectedDevices.value.size,
      successful_updates: 0,
      failed_updates: selectedDevices.value.size,
      results: []
    }
  } finally {
    isMassOTAInProgress.value = false
  }
}

const performMassHealthCheck = async () => {
  if (selectedDevices.value.size === 0) return
  
  isMassHealthCheckInProgress.value = true
  
  try {
    const selectedIps = Array.from(selectedDevices.value)
      .map(id => props.devices.find(d => d.device_id === id || d.id === id)?.last_ip)
      .filter((ip): ip is string => Boolean(ip))
      
    if (selectedIps.length > 0) {
      await deviceService.performMassHealthCheck(selectedIps)
      emit('refresh-devices')
      notificationTitle.value = 'Success'
      notificationMessage.value = `Health check completed for ${selectedIps.length} devices.`
      notificationType.value = 'success'
      showNotificationModal.value = true
      clearSelection()
    }
  } catch (error) {
    console.error('Mass health check failed:', error)
    notificationTitle.value = 'Error'
    notificationMessage.value = `Health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    notificationType.value = 'error'
    showNotificationModal.value = true
  } finally {
    isMassHealthCheckInProgress.value = false
  }
}

// Device selection functions
const toggleDeviceSelection = (deviceId: string) => {
  if (selectedDevices.value.has(deviceId)) {
    selectedDevices.value.delete(deviceId)
  } else {
    selectedDevices.value.add(deviceId)
  }
  updateSelectAllState()
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedDevices.value.clear()
    selectAll.value = false
  } else {
    displayDevices.value.forEach(device => {
      selectedDevices.value.add(device.device_id)
    })
    selectAll.value = true
  }
}

const updateSelectAllState = () => {
  const visibleDeviceIds = new Set(displayDevices.value.map(d => d.device_id))
  const selectedVisibleDevices = Array.from(selectedDevices.value).filter(id => visibleDeviceIds.has(id))
  selectAll.value = selectedVisibleDevices.length === displayDevices.value.length && displayDevices.value.length > 0
}

const clearSelection = () => {
  selectedDevices.value.clear()
  selectAll.value = false
}

// Watch for device changes to update select all state
watch(displayDevices, updateSelectAllState, { immediate: true })
</script>

<template>
  <div>
    <DevicesPageHeader />

    <DevicesActionBar
      :view-mode="viewMode"
      :is-loading="props.isLoading"
      :scan-in-progress="scanInProgress"
      @set-view-mode="setViewMode"
      @refresh-devices="refreshDevices"
      @scan-network="scanNetwork"
      @add-device="showAddDeviceModal = true"
    />

    <AddDeviceModal
      :is-open="showAddDeviceModal"
      @close="showAddDeviceModal = false"
      @add="handleAddDeviceConfirmed"
    />

    <DeviceFiltersComponent 
      ref="deviceFiltersRef"
      :devices="devicesRef"
      @filters-changed="handleFiltersChanged" 
    />

    <DevicesCount
      :device-count="showingDevices"
      :is-loading="props.isLoading"
      :total-count="totalDevices"
    />

    <DevicesGridView
      v-if="viewMode === 'grid'"
      :devices="displayDevices"
      :is-loading="props.isLoading"
      :is-restoring="isRestoring"
      @viewDetails="viewDetails"
      @backupDevice="backupDevice"
      @restoreDevice="restoreDevice"
      @visitDevice="visitDevice"
      @deleteDevice="deleteDevice"
      @adoptDevice="adoptDevice"
      @releaseDevice="releaseDevice"
    />

    <DevicesListView
      v-if="viewMode === 'list'"
      :devices="displayDevices"
      :is-loading="props.isLoading"
      :is-restoring="isRestoring"
      :selected-devices="selectedDevices"
      :select-all="selectAll"
      @viewDetails="viewDetails"
      @backupDevice="backupDevice"
      @restoreDevice="restoreDevice"
      @visitDevice="visitDevice"
      @deleteDevice="deleteDevice"
      @adoptDevice="adoptDevice"
      @releaseDevice="releaseDevice"
      @toggle-device-selection="toggleDeviceSelection"
      @toggle-select-all="toggleSelectAll"
      @mass-ota-update="openMassOTADialog"
      @mass-health-check="performMassHealthCheck"
      @clear-selection="clearSelection"
    />

    <!-- Backup Dialog -->
    <BackupDialog
      :is-open="showBackupDialog"
      :device="backupDeviceData"
      @close="closeBackupDialog"
      @backup="handleBackupConfirmed"
    />


    <!-- Adopt Device Modal -->
    <Modal :is-open="showAdoptDialog" :title="`Adopt Device: ${adoptDeviceData?.name || 'Unknown Device'}`" @close="closeAdoptDialog">
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
            @keyup.enter="handleAdoptConfirmed"
          />
        </div>
      </div>

      <template #footer>
        <button
          @click="closeAdoptDialog"
          :disabled="isAdopting"
          class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Cancel
        </button>
        <button
          @click="handleAdoptConfirmed"
          :disabled="!newDeviceLocalName.trim() || isAdopting"
          class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <LoadingSpinner v-if="isAdopting" />
          <span>{{ isAdopting ? 'Adopting...' : 'Adopt Device' }}</span>
        </button>
      </template>
    </Modal>

    <!-- Mass OTA Update Modal -->
    <Modal :is-open="showMassOTADialog" :title="`Mass OTA Update (${selectedDevices.size} devices)`" @close="closeMassOTADialog">
      <div class="space-y-4">
        <div>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Update {{ selectedDevices.size }} selected device(s) with new firmware. This process may take several minutes.
          </p>
          
          <label for="otaFile" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Firmware File
          </label>
          <input
            id="otaFile"
            type="file"
            accept=".bin"
            @change="handleMassOTAFileSelect"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white file:mr-4 file:py-2 file:px-4 file:rounded-l-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Select a .bin firmware file compatible with your WLED devices
          </p>
        </div>

        <div v-if="massOTAResults" class="mt-4">
          <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Update Results</h4>
          <div class="bg-gray-50 dark:bg-gray-800 rounded-md p-3">
            <div class="flex justify-between text-sm mb-2">
              <span>Total devices:</span>
              <span>{{ massOTAResults.total_devices }}</span>
            </div>
            <div class="flex justify-between text-sm mb-2">
              <span class="text-green-600">Successful:</span>
              <span class="text-green-600">{{ massOTAResults.successful_updates }}</span>
            </div>
            <div class="flex justify-between text-sm mb-2">
              <span class="text-red-600">Failed:</span>
              <span class="text-red-600">{{ massOTAResults.failed_updates }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span>Duration:</span>
              <span>{{ massOTAResults.total_duration?.toFixed(2) }}s</span>
            </div>
          </div>
          
          <div v-if="massOTAResults.results && massOTAResults.results.length > 0" class="mt-3">
            <h5 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Device Details</h5>
            <div class="max-h-40 overflow-y-auto space-y-2">
              <div v-for="result in massOTAResults.results" :key="result.device_id" 
                   class="text-xs p-2 rounded" 
                   :class="result.success ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200' : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'">
                <div class="font-medium">{{ result.device_name }}</div>
                <div>{{ result.success ? '✅ Success' : '❌ Failed' }} 
                  <span v-if="result.duration">({{ result.duration.toFixed(2) }}s)</span>
                </div>
                <div v-if="result.error" class="text-xs opacity-75">{{ result.error }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <button
          @click="closeMassOTADialog"
          class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600"
        >
          Cancel
        </button>
        <button
          @click="performMassOTAUpdate"
          :disabled="!massOTAFile || isMassOTAInProgress"
          class="px-4 py-2 text-sm font-medium text-white bg-orange-600 border border-transparent rounded-md hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <LoadingSpinner v-if="isMassOTAInProgress" class="w-4 h-4" />
          <span>{{ isMassOTAInProgress ? 'Updating...' : 'Start Mass Update' }}</span>
        </button>
      </template>
    </Modal>

    <!-- Notification Modal -->
    <NotificationModal
      :is-open="showNotificationModal"
      :title="notificationTitle"
      :message="notificationMessage"
      :type="notificationType"
      @close="showNotificationModal = false"
    />

    <!-- Release Confirmation Modal -->
    <ReleaseConfirmationModal
      :is-open="showReleaseModal"
      :device-id="deviceToRelease.id"
      :device-name="deviceToRelease.name"
      :device-mac="deviceToRelease.mac"
      :is-loading="isReleasing"
      @close="showReleaseModal = false"
      @confirm="confirmReleaseDevice"
    />

    <!-- Delete Confirmation Modal -->
    <ConfirmationModal
      :is-open="showDeleteConfirmModal"
      title="Delete Device"
      :message="`Are you sure you want to delete ${deviceToDelete?.name}? This action cannot be undone.`"
      confirm-text="Delete"
      type="danger"
      @close="showDeleteConfirmModal = false"
      @confirm="confirmDeleteDevice"
    />
  </div>
</template>
