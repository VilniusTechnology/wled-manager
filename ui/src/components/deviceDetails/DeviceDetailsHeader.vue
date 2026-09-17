<template>
  <div class="bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-700 rounded-lg mb-6">
    <div class="px-4 sm:px-6 lg:px-8 py-4">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="flex items-center space-x-4">
          <button
            v-if="canGoBack"
            @click="$emit('goBack')"
            class="rounded-md p-2 text-gray-400 transition-colors hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
            </svg>
          </button>
          
          <div class="min-w-0 flex-1">
            <div class="flex flex-col gap-y-1">
              <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white break-words">{{ deviceName }}</h1>
              <div class="flex items-center gap-2 mt-1">
                <StatusBadge :status="deviceStatus" />
                <IpConfigBadge :hasStaticIp="device?.has_static_ip" size="md" />
                <MqttBadge :mqttEnabled="device?.mqtt_enabled" size="md" />
                <span class="break-all font-mono text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded border border-gray-200 dark:border-gray-600">{{ formatMacAddress(device?.mac) }}</span>
              </div>
            </div>
            <div class="mt-1 text-sm text-gray-500 dark:text-gray-400 flex flex-col gap-0.5">
              <span>Last seen: {{ lastSeenFormatted }}</span>
              <span>Discovered: {{ discoveryDateFormatted }}</span>
            </div>
          </div>
        </div>
        
        <div class="w-full sm:w-auto flex flex-wrap items-center justify-start sm:justify-end gap-3">
          <button
            @click="$emit('togglePower')"
            :disabled="isLoading"
            class="w-full sm:w-auto justify-center px-4 py-2 text-sm font-medium rounded-md transition-colors flex items-center gap-2"
            :class="[
              device?.state_on 
                ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-300 dark:hover:bg-yellow-900/50' 
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
            ]"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
            {{ device?.state_on ? 'On' : 'Off' }}
          </button>

          <button
            v-if="device && !device.adopted"
            @click="$emit('adopt')"

            :disabled="isLoading"
            class="p-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white rounded-md transition-colors flex items-center gap-2 px-3"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            <span class="hidden sm:inline">Adopt</span>
          </button>


          <DeviceNetworkActions 
            :device="device" 
            :device-status="deviceStatus" 
            :disabled="isLoading"
          >
            <button
              @click="$emit('refreshDevice')"
              :disabled="isLoading"
              class="p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-md transition-colors"
              :title="isLoading ? 'Refreshing...' : 'Refresh'"
              aria-label="Refresh"
            >
              <RefreshCw v-if="isLoading" class="animate-spin h-5 w-5" />
              <RefreshCw v-else class="h-5 w-5" />
            </button>
          </DeviceNetworkActions>

          <DeviceJumpTo
            :devices="availableDevices"
            :is-loading="isDeviceListLoading"
            @select-device="$emit('jumpToDevice', $event)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RefreshCw } from 'lucide-vue-next'
import type { Device, DeviceDetails } from '../../types/device'
import { getDeviceDisplayName, formatMacAddress } from '../../utils/deviceDisplay'
import { formatDateTime } from '../../utils/dateUtils'
import IpConfigBadge from '../shared/IpConfigBadge.vue'
import StatusBadge from '../shared/StatusBadge.vue'
import MqttBadge from '../shared/MqttBadge.vue'
import DeviceJumpTo from './DeviceJumpTo.vue'
import DeviceNetworkActions from './DeviceNetworkActions.vue'

interface Props {
  device: DeviceDetails | null
  deviceStatus: string
  isLoading: boolean
  availableDevices: Device[]
  isDeviceListLoading: boolean
  canGoBack: boolean
}

const props = defineProps<Props>()

const availableDevices = computed(() => props.availableDevices)
const isDeviceListLoading = computed(() => props.isDeviceListLoading)
const canGoBack = computed(() => props.canGoBack)

defineEmits<{
  goBack: []
  refreshDevice: []
  togglePower: []
  jumpToDevice: [deviceId: string]
  adopt: []
}>()




const deviceName = computed(() => getDeviceDisplayName(props.device))

const lastSeenFormatted = computed(() => {
  if (!props.device?.last_seen) return 'Never'
  return formatDateTime(props.device.last_seen)
})

const discoveryDateFormatted = computed(() => {
  if (!props.device?.discovery_date_time) return 'Unknown'
  return formatDateTime(props.device.discovery_date_time)
})

</script>