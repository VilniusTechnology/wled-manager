<script setup lang="ts">
import { formatMacAddress } from '../../utils/deviceDisplay'
import { formatDate } from '../../utils/dateUtils'

interface DeviceDetails {
  device_id: string
  mac: string
  name?: string
  last_ip?: string
  local_name?: string
  hostname?: string
  adopted: boolean
  status?: string
  last_seen?: string
  created?: string
  updated?: string
  has_backups: boolean
  software_version?: string
  signal_strength?: number
  state_on?: boolean
  brightness?: number
  current_preset?: number
  led_count?: number
  uptime?: number
  free_heap?: number
  wifi_rssi?: number
  wifi_channel?: number
  latest_timestamp?: string
  usermod_url?: string
}

interface Props {
  device: DeviceDetails
}

defineProps<Props>()

defineEmits<{
  'device-updated': []
}>()

const formatUptime = (seconds?: number) => {
  if (!seconds) return 'Unknown'
  
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m`
  } else if (hours > 0) {
    return `${hours}h ${minutes}m`
  } else {
    return `${minutes}m`
  }
}

const formatMemory = (bytes?: number) => {
  if (!bytes) return 'Unknown'
  
  const kb = bytes / 1024
  if (kb > 1024) {
    return `${(kb / 1024).toFixed(1)} MB`
  }
  return `${kb.toFixed(1)} KB`
}



const getSignalStrengthLabel = (rssi?: number) => {
  if (!rssi) return 'Unknown'
  
  if (rssi > -50) return 'Excellent'
  if (rssi > -60) return 'Good'
  if (rssi > -70) return 'Fair'
  return 'Poor'
}

const getSignalStrengthColor = (rssi?: number) => {
  if (!rssi) return 'text-gray-500'
  
  if (rssi > -50) return 'text-green-600 dark:text-green-400'
  if (rssi > -60) return 'text-blue-600 dark:text-blue-400'
  if (rssi > -70) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}
</script>

<template>
  <div class="space-y-6">
    <!-- Device Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Basic Info Card -->
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Device Information</h3>
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">Name:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white text-right truncate ml-2">
              {{ device.name || device.local_name || device.hostname || 'Unnamed' }}
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">MAC:</span>
            <span class="text-sm font-mono text-gray-900 dark:text-white text-right truncate ml-2">{{ formatMacAddress(device.mac) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">IP:</span>
            <a
              v-if="device.last_ip"
              :href="`http://${device.last_ip}`"
              target="_blank"
              rel="noopener noreferrer"
              class="text-sm font-mono text-blue-600 dark:text-blue-400 hover:underline text-right truncate ml-2"
            >{{ device.last_ip }}</a>
            <span v-else class="text-sm font-mono text-gray-900 dark:text-white text-right truncate ml-2">Unknown</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">Version:</span>
            <span class="text-sm text-gray-900 dark:text-white text-right truncate ml-2">{{ device.software_version || 'Unknown' }}</span>
          </div>
        </div>
      </div>

      <!-- Status Card -->
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Current Status</h3>
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">Power:</span>
            <span 
              :class="{
                'text-green-600 dark:text-green-400': device.state_on,
                'text-red-600 dark:text-red-400': device.state_on === false,
                'text-gray-500': device.state_on === undefined
              }"
              class="text-sm font-medium text-right truncate ml-2"
            >
              {{ device.state_on === true ? 'On' : device.state_on === false ? 'Off' : 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">Brightness:</span>
            <span class="text-sm text-gray-900 dark:text-white text-right truncate ml-2">
              {{ device.brightness !== undefined ? `${device.brightness}/255` : 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">Preset:</span>
            <span class="text-sm text-gray-900 dark:text-white text-right truncate ml-2">
              {{ device.current_preset !== undefined ? `#${device.current_preset}` : 'None' }}
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">Connection:</span>
            <span
              :class="{
                'text-green-600 dark:text-green-400': device.status === 'Online',
                'text-yellow-600 dark:text-yellow-400': device.status === 'Slow',
                'text-red-600 dark:text-red-400': device.status === 'Offline',
                'text-gray-500': !device.status || device.status === 'Unknown'
              }"
              class="text-sm font-medium text-right truncate ml-2"
            >
              {{ device.status || 'Unknown' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Hardware Card -->
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Hardware</h3>
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">LED Count:</span>
            <span class="text-sm text-gray-900 dark:text-white text-right truncate ml-2">{{ device.led_count || 'Unknown' }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">Free Memory:</span>
            <span class="text-sm text-gray-900 dark:text-white text-right truncate ml-2">{{ formatMemory(device.free_heap) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">Uptime:</span>
            <span class="text-sm text-gray-900 dark:text-white text-right truncate ml-2">{{ formatUptime(device.uptime) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">Adopted:</span>
            <span 
              :class="{
                'text-green-600 dark:text-green-400': device.adopted,
                'text-red-600 dark:text-red-400': !device.adopted
              }"
              class="text-sm font-medium text-right truncate ml-2"
            >
              {{ device.adopted ? 'Yes' : 'No' }}
            </span>
          </div>
        </div>
      </div>


    </div>

    <!-- Network Information -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Network Information</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">WiFi Signal:</span>
            <div class="flex items-center space-x-2 shrink-0 ml-2">
              <span :class="getSignalStrengthColor(device.wifi_rssi)" class="text-sm font-medium truncate">
                {{ device.wifi_rssi ? `${device.wifi_rssi} dBm` : 'Unknown' }}
              </span>
              <span class="text-xs text-gray-500 dark:text-gray-400 truncate">
                ({{ getSignalStrengthLabel(device.wifi_rssi) }})
              </span>
            </div>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">WiFi Channel:</span>
            <span class="text-sm text-gray-900 dark:text-white text-right truncate ml-2">{{ device.wifi_channel || 'Unknown' }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">Hostname:</span>
            <span class="text-sm font-mono text-gray-900 dark:text-white text-right truncate ml-2">{{ device.hostname || 'Not set' }}</span>
          </div>
        </div>
        
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">Local Name:</span>
            <span class="text-sm text-gray-900 dark:text-white text-right truncate ml-2">{{ device.local_name || 'Not set' }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-300 shrink-0">Has Backups:</span>
            <span 
              :class="{
                'text-green-600 dark:text-green-400': device.has_backups,
                'text-gray-600 dark:text-gray-400': !device.has_backups
              }"
              class="text-sm font-medium text-right truncate ml-2"
            >
              {{ device.has_backups ? 'Yes' : 'No' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Timestamps -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Timeline</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div>
          <span class="text-sm text-gray-600 dark:text-gray-300">First Seen:</span>
          <p class="text-sm font-medium text-gray-900 dark:text-white">{{ formatDate(device.created) }}</p>
        </div>
        <div>
          <span class="text-sm text-gray-600 dark:text-gray-300">Last Updated:</span>
          <p class="text-sm font-medium text-gray-900 dark:text-white">{{ formatDate(device.updated) }}</p>
        </div>
        <div>
          <span class="text-sm text-gray-600 dark:text-gray-300">Last Seen:</span>
          <p class="text-sm font-medium text-gray-900 dark:text-white">{{ formatDate(device.last_seen) }}</p>
        </div>
        <div>
          <span class="text-sm text-gray-600 dark:text-gray-300">Latest Data:</span>
          <p class="text-sm font-medium text-gray-900 dark:text-white">{{ formatDate(device.latest_timestamp) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>