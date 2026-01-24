<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { formatDate } from '../utils/dateUtils'
import type { Device } from '../types/device'
import Modal from '../components/shared/Modal.vue'


interface Props {
  device: Device
}

const props = defineProps<Props>()
const localName = computed(() => props.device.local_name)
const router = useRouter()

const navigateToDevice = () => {
  router.push(`/devices/${props.device.device_id}`)
}

const emit = defineEmits<{
  'adopt-device': [deviceId: string, localName: string]
}>()

const showAdoptDeviceModal = ref(false)
const newDeviceLocalName = ref('')

const openAdoptDeviceModal = () => {
  showAdoptDeviceModal.value = true
  // Use computed localName instead of direct access
  newDeviceLocalName.value = localName.value || ''
}

const closeAdoptDeviceModal = () => {
  showAdoptDeviceModal.value = false
  newDeviceLocalName.value = ''
}

const adoptDevice = () => {
  if (newDeviceLocalName.value.trim()) {
    // Emit with device ID and local name
    emit('adopt-device', props.device.device_id, newDeviceLocalName.value.trim())
    closeAdoptDeviceModal()
  }
}

const formatUptime = (seconds: number): string => {
  const days = Math.floor(seconds / (24 * 3600))
  const hours = Math.floor((seconds % (24 * 3600)) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) return `${days}d ${hours}h`
  if (hours > 0) return `${hours}h ${minutes}m`
  return `${minutes}m`
}

const formatMemory = (bytes: number): string => {
  const kb = bytes / 1024
  if (kb < 1024) return `${kb.toFixed(1)} KB`
  const mb = kb / 1024
  return `${mb.toFixed(1)} MB`
}



const discoveryDate = computed(() => {
  // Try discovery_date_time first, then created, then last_seen
  return props.device.discovery_date_time || props.device.created || props.device.last_seen
})
</script>

<template>
  <div 
    @click="navigateToDevice"
    class="flex flex-col sm:flex-row items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors gap-4"
    role="button"
    tabindex="0"
    @keydown.enter="navigateToDevice"
  >
    <div class="flex flex-col md:flex-row items-start md:items-center w-full sm:w-auto flex-grow gap-2 md:gap-0">
      <div class="flex-grow w-full">
        <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
          <p class="font-medium break-all">{{ device.name || device.local_name || device.device_id }}</p>
          <span v-if="device.hostname" class="text-sm text-blue-600 dark:text-blue-400 break-all">
            ({{ device.hostname }})
          </span>
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400 flex flex-wrap gap-x-2">
          <span>IP: {{ device.last_ip }}</span>
          <span class="hidden sm:inline">|</span>
          <span>MAC: {{ device.mac }}</span>
        </div>
        <div class="flex flex-wrap gap-x-4 mt-1 text-xs text-gray-500 dark:text-gray-400">
          <p v-if="device.signal_strength">Signal: {{ device.signal_strength }}%</p>
          <p v-if="device.software_version">Version: {{ device.software_version }}</p>
          <p v-if="device.led_count">LEDs: {{ device.led_count }}</p>
          <p v-if="device.brand && device.product">{{ device.brand }} {{ device.product }}</p>
          <p v-if="device.arch">{{ device.arch }}</p>
          <p v-if="discoveryDate" class="text-blue-600 dark:text-blue-400">
            Added: {{ formatDate(discoveryDate) }}
          </p>
        </div>
      </div>
      <div class="text-left md:text-right text-xs text-gray-500 dark:text-gray-400 w-full md:w-auto mt-2 md:mt-0">
        <p v-if="device.uptime">Uptime: {{ formatUptime(device.uptime) }}</p>
        <p v-if="device.free_heap">Memory: {{ formatMemory(device.free_heap) }}</p>
      </div>
    </div>
    <div class="flex items-center gap-3 w-full sm:w-auto justify-end">
      <button @click.stop="openAdoptDeviceModal" class="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 px-3 py-1 rounded-full text-sm hover:bg-blue-200 dark:hover:bg-blue-800/40 transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
      </button>
    </div>
  </div>

  <!-- Add Device Modal -->
  <Modal 
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