<script setup lang="ts">
interface DeviceDetails {
  device_id: string
  mac: string
  latest_info?: any
  latest_config?: any
  led_count?: number
  uptime?: number
  free_heap?: number
  software_version?: string
}

interface Props {
  device: DeviceDetails
}

defineProps<Props>()

const formatUptime = (seconds?: number) => {
  if (!seconds) return 'Unknown'
  
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  const parts = []
  if (days > 0) parts.push(`${days}d`)
  if (hours > 0) parts.push(`${hours}h`)
  if (minutes > 0) parts.push(`${minutes}m`)
  
  return parts.join(' ') || '0m'
}

const formatMemory = (bytes?: number) => {
  if (!bytes) return 'Unknown'
  
  const kb = bytes / 1024
  if (kb > 1024) {
    return `${(kb / 1024).toFixed(1)} MB`
  }
  return `${kb.toFixed(1)} KB`
}

const formatBytes = (bytes?: number) => {
  if (!bytes && bytes !== 0) return 'Unknown'
  
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(unitIndex > 0 ? 1 : 0)} ${units[unitIndex]}`
}

const getLedTypeDescription = (type?: number) => {
  const types: { [key: number]: string } = {
    22: 'WS2812B',
    23: 'WS2812B RGB',
    24: 'SK6812 RGBW',
    25: 'WS2801',
    26: 'APA102',
    27: 'LPD8806',
    28: 'P9813',
    29: 'TM1803',
    30: 'TM1804',
    31: 'TM1809',
    32: 'TM1812',
    33: 'TM1829',
    34: 'UCS1903',
    35: 'UCS1903B',
    36: 'UCS1904',
    37: 'UCS2903',
    38: 'WS2811',
    39: 'WS2812',
    40: 'WS2813',
    41: 'APA104',
    42: 'UCS8903',
    43: 'SK9822'
  }
  
  return type !== undefined ? (types[type] || `Type ${type}`) : 'Unknown'
}
</script>

<template>
  <div class="space-y-6">
    <!-- Hardware Overview -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- System Info -->
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">System Information</h3>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Version:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.software_version || 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Platform:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_info?.platform || 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Architecture:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_info?.arch || 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Core Version:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_info?.core || 'Unknown' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Memory Info -->
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Memory Usage</h3>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Free Heap:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ formatMemory(device.free_heap) }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Filesystem Used:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ formatBytes(device.latest_info?.fs?.u) }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Filesystem Total:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ formatBytes(device.latest_info?.fs?.t) }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Uptime:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ formatUptime(device.uptime) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Power Info -->
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Power & Performance</h3>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Max Current:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_config?.hw?.led?.maxpwr ? `${device.latest_config.hw.led.maxpwr} mA` : 'Not set' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Brand:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_info?.brand || 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Product:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_info?.product || 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Build ID:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_info?.build || 'Unknown' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- LED Configuration -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">LED Strip Configuration</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Total LEDs:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.led_count || device.latest_config?.hw?.led?.total || 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Data Pin:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_config?.hw?.led?.pin !== undefined ? `GPIO ${device.latest_config.hw.led.pin}` : 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">LED Type:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ getLedTypeDescription(device.latest_config?.hw?.led?.type) }}
            </span>
          </div>
        </div>
        
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Color Order:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_config?.hw?.led?.rgbwm || 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Reversed:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_config?.hw?.led?.rev ? 'Yes' : 'No' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Skip First LED:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_config?.hw?.led?.skip || 0 }}
            </span>
          </div>
        </div>
        
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Frequency:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_config?.hw?.led?.freq ? `${device.latest_config.hw.led.freq} Hz` : 'Default' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Clock Pin:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_config?.hw?.led?.clk !== undefined ? `GPIO ${device.latest_config.hw.led.clk}` : 'Not used' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">White Channel:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_config?.hw?.led?.white !== undefined ? `${device.latest_config.hw.led.white}%` : 'Not set' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Hardware Features -->
    <div v-if="device.latest_info" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Hardware Features</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Live LED Count</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_info.leds?.count !== undefined ? 'Yes' : 'No' }}
            </span>
          </div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Power Calc</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_info.leds?.pwr !== undefined ? 'Yes' : 'No' }}
            </span>
          </div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Max Segments</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_info.leds?.maxseg || 'Unknown' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Current Power Usage -->
      <div v-if="device.latest_info.leds?.pwr" class="mt-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div class="flex items-center">
          <svg class="h-5 w-5 text-blue-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
          </svg>
          <span class="text-sm font-medium text-blue-800 dark:text-blue-200">
            Current Power Usage: {{ device.latest_info.leds.pwr }} mA
          </span>
        </div>
      </div>
    </div>

    <!-- Raw Hardware Data -->
    <div v-if="device.latest_info || device.latest_config" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Raw Hardware Data</h3>
      
      <div class="space-y-4">
        <div v-if="device.latest_info">
          <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-2">Device Info</h4>
          <div class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-4 max-h-64 overflow-y-auto">
            <pre class="text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{{
              JSON.stringify(device.latest_info, null, 2)
            }}</pre>
          </div>
        </div>
        
        <div v-if="device.latest_config">
          <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-2">Hardware Config</h4>
          <div class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-4 max-h-64 overflow-y-auto">
            <pre class="text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{{
              JSON.stringify(device.latest_config?.hw || {}, null, 2)
            }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- No Hardware Data -->
    <div v-else class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 48 48">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="9 3v2m6-2v2m4-2v2M9 19v-2a2 2 0 012-2h8a2 2 0 012 2v2M9 19v4a2 2 0 002 2h8a2 2 0 002-2v-4M9 19h12"></path>
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No hardware data available</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Hardware information will appear here when the device is scanned.
      </p>
    </div>
  </div>
</template>