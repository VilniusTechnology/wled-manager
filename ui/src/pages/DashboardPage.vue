<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Device } from '../types/device'
import DashboardHeader from '../components/DashboardHeader.vue'
import StatCards from '../components/StatCards.vue'
import RecentDevices from '../components/RecentDevices.vue'
import { settingsService } from '../services/settingsService'
import ReleaseConfirmationModal from '../components/modals/ReleaseConfirmationModal.vue'
import Modal from '../components/shared/Modal.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'
import { useDevices } from '../composables/useDevices' // Import composable

interface Props {
  devices: Device[]
  scanInProgress: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  scanNetwork: []
  'view-details': [deviceId: string]
  'backup-device': [deviceId: string]
  'visit-device': [deviceId: string]
  'restore-device': [deviceId: string]
  'delete-device': [deviceId: string]
  'adopt-device': [deviceId: string, localName: string]
  'release-device': [deviceId: string]
  'refresh-devices': []
}>()

const onlineDevices = computed(() => props.devices.filter((d: Device) => {
  const status = (d.status || '').toLowerCase()
  // Count as online only if status is explicitly healthy (online, excellent, good)
  return status === 'online' || status === 'excellent' || status === 'good'
}).length)
const offlineDevices = computed(() => props.devices.length - onlineDevices.value)

const isBackingUp = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

// Release modal state
const showReleaseModal = ref(false)
const deviceToRelease = ref<{ id: string; name: string; mac: string }>({ id: '', name: '', mac: '' })
const isReleasing = ref(false)
const { releaseDevices, adoptDevices } = useDevices() // Use composable instead of direct service

// Adopt dialog state
const showAdoptDialog = ref(false)
const adoptDeviceData = ref<any>(null)
const newDeviceLocalName = ref('')
const isAdopting = ref(false)

const scanNetwork = () => {
  emit('scanNetwork')
}

const visitDevice = (deviceId: string) => {
  emit('visit-device', deviceId)
}

const restoreDevice = (deviceId: string) => {
  emit('restore-device', deviceId)
}

const getDeviceName = (device: Device): string => {
   return device.name || device.local_name || device.hostname || device.mac || 'Unknown Device'
}

const adoptDevice = (deviceId: string, localName?: string) => {
  if (localName) {
    // Name provided (e.g. from RecentDeviceActions modal), proceed directly
    performAdopt(deviceId, localName)
    return
  }

  // No name provided, open local modal
  const device = props.devices.find(d => d.device_id === deviceId || d.id === deviceId)
  
  if (device) {
    adoptDeviceData.value = device
    newDeviceLocalName.value = getDeviceName(device) // Pre-fill with existing name if any
    showAdoptDialog.value = true
  } else {
    console.error('Device not found:', deviceId)
  }
}

const performAdopt = async (deviceId: string, localName: string) => {
  const device = props.devices.find(d => d.device_id === deviceId || d.id === deviceId)
  const deviceName = device?.name || 'Unknown'

  try {
    isAdopting.value = true
    const result = await adoptDevices([{
      device_id: deviceId,
      local_device_name: localName
    }])
    console.log('Adopt successful:', result)
    
    showMessage(`Device ${deviceName} adopted successfully!`, 'success')
  } catch (error) {
    console.error('Adopt failed:', error)
    showMessage(`Adopt failed: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
  } finally {
    isAdopting.value = false
  }
}

const closeAdoptDialog = () => {
  showAdoptDialog.value = false
  adoptDeviceData.value = null
  newDeviceLocalName.value = ''
}

const handleAdoptConfirmed = async () => {
  if (!adoptDeviceData.value || !newDeviceLocalName.value.trim()) return
  
  const deviceId = adoptDeviceData.value.device_id || adoptDeviceData.value.id
  
  // Close dialog first
  closeAdoptDialog()
  
  await performAdopt(deviceId, newDeviceLocalName.value.trim())
}

const releaseDevice = (deviceId: string) => {
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
    await releaseDevices([deviceId])
    
    // Close the modal
    showReleaseModal.value = false
    
    showMessage('Device released successfully!', 'success')
  } catch (error) {
    console.error('Release failed:', error)
    showMessage(`Release failed: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
  } finally {
    isReleasing.value = false
  }
}

const viewDetails = (deviceId: string) => {
  emit('view-details', deviceId)
}

const backupDevice = (deviceId: string) => {
  emit('backup-device', deviceId)
}

const deleteDevice = (deviceId: string) => {
  emit('delete-device', deviceId)
}

const triggerBackup = async () => {
  try {
    isBackingUp.value = true
    await settingsService.triggerBackupEmail()
    showMessage('Backup email sent successfully', 'success')
  } catch (error) {
    console.error('Failed to trigger backup email:', error)
    showMessage('Failed to trigger backup email', 'error')
  } finally {
    isBackingUp.value = false
  }
}

const showMessage = (msg: string, type: 'success' | 'error') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 5000)
}
</script>

<template>
  <div>
    <div class="flex justify-between items-start mb-6">
      <DashboardHeader />
      <div class="flex flex-col items-end gap-2">
        <button 
          @click="triggerBackup" 
          :disabled="isBackingUp"
          class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 text-sm font-medium"
        >
          {{ isBackingUp ? 'Sending...' : 'Trigger Backup Email' }}
        </button>
        <div v-if="message" :class="`text-sm px-2 py-1 rounded ${messageType === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`">
          {{ message }}
        </div>
      </div>
    </div>

    <StatCards
      :total-devices="devices.length"
      :online-devices="onlineDevices"
      :offline-devices="offlineDevices"
      :scan-in-progress="scanInProgress"
    />

    <RecentDevices
      :devices="devices"
      :is-restoring="scanInProgress"
      @scan-network="scanNetwork"
      @view-details="viewDetails"
      @backup-device="backupDevice"
      @visit-device="visitDevice"
      @restore-device="restoreDevice"
      @delete-device="deleteDevice"
      @adopt-device="adoptDevice"
      @release-device="releaseDevice"
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
  </div>
</template>
