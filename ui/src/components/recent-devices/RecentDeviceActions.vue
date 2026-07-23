<template>
  <div class="flex flex-wrap gap-2 mt-2 sm:mt-1 justify-start sm:justify-end">
    <button
      @click="$emit('view-details', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-details"
    >
      Details
    </button>
    <button
      @click="openBackupDialog"
      :disabled="props.isRestoring"
      class="device-action device-action-backup"
    >
      Backup
    </button>
    <button
      @click="openRestoreDialog"
      :disabled="props.isRestoring"
      class="device-action device-action-restore"
    >
      {{ props.isRestoring ? 'Loading...' : 'Restore' }}
    </button>
    <button
      @click="$emit('visit-device', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-visit"
    >
      Visit
    </button>
    <button
      @click="$emit('delete-device', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-delete"
    >
      Delete
    </button>
    <button
      v-if="!isAdopted"
      @click="openAdoptDialog"
      :disabled="props.isRestoring"
      class="device-action device-action-adopt"
    >
      Adopt
    </button>
    <button
      v-else
      @click="$emit('release-device', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-release"
    >
      Release
    </button>
  </div>

  <!-- Backup Dialog -->
  <BackupDialog
    :is-open="showBackupDialog"
    :device="deviceData || null"
    @close="closeBackupDialog"
    @backup="handleBackupConfirmed"
  />


  <!-- Adopt Dialog -->
  <Modal :is-open="showAdoptDialog" :title="`Adopt Device: ${deviceData?.name || 'Unknown Device'}`" @close="closeAdoptDialog">
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
        class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600"
      >
        Cancel
      </button>
      <button
        @click="handleAdoptConfirmed"
        :disabled="!newDeviceLocalName.trim()"
        class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Adopt Device
      </button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BackupDialog from '../../components/shared/BackupDialog.vue'
import Modal from '../../components/shared/Modal.vue'
import type { Device } from '../../types/device'
import type { Backup } from '../../types/backup'

interface Props {
  deviceId: string
  isAdopted: boolean
  deviceData?: Device
  availableBackups?: Backup[]
  isRestoring?: boolean
}

const props = defineProps<Props>()
const router = useRouter()


const emit = defineEmits<{
  'view-details': [deviceId: string]
  'backup-device': [deviceId: string]
  'visit-device': [deviceId: string]
  'restore-device': [deviceId: string]
  'delete-device': [deviceId: string]
  'adopt-device': [deviceId: string, localName: string]
  'release-device': [deviceId: string]
}>()

// Dialog state
const showBackupDialog = ref(false)
const showAdoptDialog = ref(false)
const newDeviceLocalName = ref('')

// Dialog methods
const openBackupDialog = () => {
  showBackupDialog.value = true
}

const closeBackupDialog = () => {
  showBackupDialog.value = false
}

const openRestoreDialog = () => {
  router.push(`/devices/${props.deviceId}?tab=backups`)
}


const openAdoptDialog = () => {
  showAdoptDialog.value = true
  newDeviceLocalName.value = ''
}

const closeAdoptDialog = () => {
  showAdoptDialog.value = false
  newDeviceLocalName.value = ''
}

// Event handlers
const handleBackupConfirmed = (_device: Device, _options: { config: boolean; presets: boolean }) => {
  emit('backup-device', props.deviceId)
  closeBackupDialog()
}

const handleAdoptConfirmed = () => {
  if (newDeviceLocalName.value.trim()) {
    emit('adopt-device', props.deviceId, newDeviceLocalName.value.trim())
    closeAdoptDialog()
  }
}
</script>