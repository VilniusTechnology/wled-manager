<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
    <div class="p-5 border-b border-gray-200 dark:border-gray-700 flex items-center">
      <div class="mr-3 flex items-center gap-2">
        <StatusBubble :status="device.status" />
        <span v-if="isAdopted" class="px-2 py-0.5 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-800">
          Adopted
        </span>
      </div>
      <div class="flex-1">
        <h3 class="font-semibold text-lg">{{ device.name || 'Unknown Device' }}</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm">{{ device.ip_address || device.last_ip }}</p>
      </div>
      <div class="flex flex-col gap-1">
        <Sun 
          :class="[
            'w-6 h-6 transition-colors duration-200',
            device.state_on 
              ? 'text-yellow-500 fill-yellow-500' 
              : 'text-gray-400 dark:text-gray-600'
          ]" 
        />
        <IpConfigBadge :hasStaticIp="device.has_static_ip" size="sm" />
      </div>
    </div>
    <div class="p-5">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <p class="text-gray-500 dark:text-gray-400 text-sm">MAC:</p>
          <p class="font-mono text-sm">{{ formatMacAddress(device.mac || '') }}</p>
        </div>
        <div>
          <p class="text-gray-500 dark:text-gray-400 text-sm">Version:</p>
          <p class="font-medium text-sm">{{ device.software_version || device.version }}</p>
        </div>
      </div>

      <div class="mt-4 grid grid-cols-2 gap-4">
        <div>
          <p class="text-gray-500 dark:text-gray-400 text-sm">Signal:</p>
          <p class="font-medium">{{ device.signal_strength ? `${device.signal_strength}dBm` : device.signal }}</p>
        </div>
        <div>
          <p class="text-gray-500 dark:text-gray-400 text-sm">Last Seen:</p>
          <p class="font-medium">{{ lastSeenFormatted }}</p>
        </div>
      </div>

      <div class="mt-5 flex flex-wrap gap-2 items-center">
        <button
          @click="$emit('viewDetails', device.device_id || '')"
          :disabled="props.isRestoring"
          class="device-action device-action-details"
          title="Details"
        >
          <Info class="w-4 h-4" />
        </button>
        <button
          @click="$emit('backupDevice', device.device_id || '')"
          :disabled="props.isRestoring"
          class="device-action device-action-backup"
          title="Backup"
        >
          <Download class="w-4 h-4" />
        </button>
        <button
          @click="$emit('restoreDevice', device.device_id || '')"
          :disabled="props.isRestoring"
          class="device-action device-action-restore"
          title="Restore"
        >
          <Loader2 v-if="props.isRestoring" class="w-4 h-4 animate-spin" />
          <Upload v-else class="w-4 h-4" />
        </button>
        <button
          @click="$emit('visitDevice', device.device_id || '')"
          :disabled="props.isRestoring"
          class="device-action device-action-visit"
          title="Visit"
        >
          <ExternalLink class="w-4 h-4" />
        </button>
        <button
          @click="$emit('deleteDevice', device.device_id || '')"
          :disabled="props.isRestoring"
          class="device-action device-action-delete"
          title="Delete"
        >
          <Trash2 class="w-4 h-4" />
        </button>
        <button
          v-if="!isAdopted"
          @click="handleAdopt"
          :disabled="props.isRestoring"
          class="device-action device-action-adopt"
          title="Adopt"
        >
          <Plus class="w-4 h-4" />
        </button>
        <button
          v-else
          @click="$emit('releaseDevice', device.device_id || '')"
          :disabled="props.isRestoring"
          class="device-action device-action-release"
          title="Release"
        >
          <Minus class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Device } from '../../types/device'
import { formatDateTime } from '../../utils/dateUtils'
import { formatMacAddress } from '../../utils/deviceDisplay'
import { computed } from 'vue'
import { Sun, Info, Download, Upload, ExternalLink, Trash2, Plus, Minus, Loader2 } from 'lucide-vue-next'
import StatusBubble from './StatusBubble.vue'
import IpConfigBadge from './IpConfigBadge.vue'

interface Props {
  device: Device
  isAdopted: boolean
  isRestoring: boolean
}

const props = defineProps<Props>()


const emit = defineEmits<{
  viewDetails: [deviceId: string]
  backupDevice: [deviceId: string]
  restoreDevice: [deviceId: string]
  visitDevice: [deviceId: string]
  deleteDevice: [deviceId: string]
  adoptDevice: [deviceId: string]
  releaseDevice: [deviceId: string]
}>()

const lastSeenFormatted = computed(() => {
  const lastSeen = props.device.last_seen || props.device.lastSeen
  return lastSeen ? formatDateTime(lastSeen, 'EU_NRML') : 'Never'
})

const handleAdopt = () => {
  const id = props.device.device_id || props.device.id || ''
  console.log('DeviceCard: Adopting device', { 
    id, 
    device_id: props.device.device_id, 
    raw_id: props.device.id,
    device: props.device 
  })
  emit('adoptDevice', id)
}
</script>
