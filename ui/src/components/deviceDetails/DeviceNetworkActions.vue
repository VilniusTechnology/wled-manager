<script setup lang="ts">
import { ref, computed } from 'vue'
import { ExternalLink, Activity, RotateCcw } from 'lucide-vue-next'
import { buildApiUrl } from '../../utils/apiConfig'
import type { DeviceDetails } from '../../types/device'
import ConfirmationModal from '../shared/ConfirmationModal.vue'

interface Props {
  device: DeviceDetails | null
  deviceStatus?: string
  disabled?: boolean
}

const props = defineProps<Props>()

const isNetworkActionsDisabled = computed(() => {
  return props.deviceStatus === 'dead' || props.deviceStatus === 'Dead'
})

const isRestartModalOpen = ref(false)
const isRestarting = ref(false)

const pingDevice = async () => {
  if (!props.device?.device_id) return

  try {
    const response = await fetch(buildApiUrl(`/devices/${props.device.device_id}/healthcheck`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) throw new Error('Ping failed')
    
    const result = await response.json()
    return result
  } catch (error) {
    console.error('Ping error:', error)
    return { status: 'error' }
  }
}

const visitDevice = (ip?: string) => {
  if (ip) {
    window.open(`http://${ip}`, '_blank')
  }
}

const handleRestartConfirm = async () => {
  if (!props.device?.device_id) return

  isRestarting.value = true
  try {
    const response = await fetch(buildApiUrl(`/devices/${props.device.device_id}/restart`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error('Failed to initiate restart')
    }
    
    isRestartModalOpen.value = false
  } catch (error) {
    console.error('Restart failed:', error)
    alert('Failed to restart device')
  } finally {
    isRestarting.value = false
  }
}
</script>

<template>
  <div class="flex flex-wrap gap-3">
    <button
      @click="pingDevice()"
      :disabled="disabled || !device?.last_ip || isNetworkActionsDisabled"
      :title="isNetworkActionsDisabled ? 'Ping Device (Offline)' : 'Ping Device'"
      class="px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white text-sm font-medium rounded-md transition-colors flex items-center justify-center"
    >
      <Activity class="w-4 h-4" />
    </button>

    <button
      @click="isRestartModalOpen = true"
      :disabled="disabled || isNetworkActionsDisabled"
      :title="isNetworkActionsDisabled ? 'Restart Device (Offline)' : 'Restart Device'"
      class="px-3 py-2 bg-orange-500 hover:bg-orange-600 disabled:bg-gray-400 text-white text-sm font-medium rounded-md transition-colors flex items-center justify-center"
    >
      <RotateCcw class="w-4 h-4" />
    </button>

    <button
      v-if="device?.latest_config?.id?.mdns"
      @click="visitDevice(`${device.latest_config.id.mdns}.local`)"
      :disabled="disabled || isNetworkActionsDisabled"
      :title="isNetworkActionsDisabled ? 'Visit via mDNS (Offline)' : 'Visit via mDNS'"
      class="px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white text-sm font-medium rounded-md transition-colors flex items-center justify-center"
    >
      <ExternalLink class="w-4 h-4" />
    </button>
    
    <slot />

    <ConfirmationModal
      :isOpen="isRestartModalOpen"
      title="Restart Device"
      message="Are you sure you want to restart this device? It will be temporarily unavailable."
      confirm-text="Restart"
      loading-text="Restarting..."
      confirm-color="red"
      :is-loading="isRestarting"
      @close="isRestartModalOpen = false"
      @confirm="handleRestartConfirm"
    />
  </div>
</template>
