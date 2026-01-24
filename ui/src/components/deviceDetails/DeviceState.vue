<script setup lang="ts">
interface DeviceDetails {
  device_id: string
  mac: string
  latest_state?: any
  state_on?: boolean
  brightness?: number
  current_preset?: number
}

interface Props {
  device: DeviceDetails
}

defineProps<Props>()

const getColorFromState = (seg: any) => {
  if (!seg || !seg.col) return null
  
  const colors = seg.col
  if (Array.isArray(colors) && colors.length > 0) {
    const primaryColor = colors[0]
    if (Array.isArray(primaryColor) && primaryColor.length >= 3) {
      return {
        r: primaryColor[0] || 0,
        g: primaryColor[1] || 0,
        b: primaryColor[2] || 0
      }
    }
  }
  return null
}

const formatColor = (color: any) => {
  if (!color) return 'rgb(0, 0, 0)'
  return `rgb(${color.r}, ${color.g}, ${color.b})`
}
</script>

<template>
  <div class="space-y-6">
    <!-- Current State Overview -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Current State</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Power State -->
        <div class="text-center">
          <div class="mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-2"
               :class="{
                 'bg-green-100 dark:bg-green-900': device.state_on,
                 'bg-red-100 dark:bg-red-900': device.state_on === false,
                 'bg-gray-100 dark:bg-gray-800': device.state_on === undefined
               }">
            <svg class="w-8 h-8" :class="{
              'text-green-600 dark:text-green-400': device.state_on,
              'text-red-600 dark:text-red-400': device.state_on === false,
              'text-gray-400': device.state_on === undefined
            }" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
            </svg>
          </div>
          <p class="text-sm font-medium text-gray-900 dark:text-white">Power</p>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            {{ device.state_on === true ? 'On' : device.state_on === false ? 'Off' : 'Unknown' }}
          </p>
        </div>

        <!-- Brightness -->
        <div class="text-center">
          <div class="mx-auto w-16 h-16 rounded-full bg-yellow-100 dark:bg-yellow-900 flex items-center justify-center mb-2">
            <svg class="w-8 h-8 text-yellow-600 dark:text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
            </svg>
          </div>
          <p class="text-sm font-medium text-gray-900 dark:text-white">Brightness</p>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            {{ device.brightness !== undefined ? `${device.brightness}/255 (${Math.round((device.brightness / 255) * 100)}%)` : 'Unknown' }}
          </p>
        </div>

        <!-- Preset -->
        <div class="text-center">
          <div class="mx-auto w-16 h-16 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center mb-2">
            <svg class="w-8 h-8 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
            </svg>
          </div>
          <p class="text-sm font-medium text-gray-900 dark:text-white">Active Preset</p>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            {{ device.current_preset !== undefined ? `#${device.current_preset}` : 'None' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Segments -->
    <div v-if="device.latest_state?.seg" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">LED Segments</h3>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div
          v-for="(segment, index) in device.latest_state.seg"
          :key="index"
          class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600 p-4"
        >
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-sm font-medium text-gray-900 dark:text-white">
              Segment {{ index }}
            </h4>
            <div
              v-if="getColorFromState(segment)"
              class="w-6 h-6 rounded border border-gray-300 dark:border-gray-600"
              :style="{ backgroundColor: formatColor(getColorFromState(segment)) }"
            ></div>
          </div>
          
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-300">Start:</span>
              <span class="text-gray-900 dark:text-white">{{ segment.start || 0 }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-300">Stop:</span>
              <span class="text-gray-900 dark:text-white">{{ segment.stop || 0 }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-300">Length:</span>
              <span class="text-gray-900 dark:text-white">{{ (segment.stop || 0) - (segment.start || 0) }} LEDs</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-300">Effect:</span>
              <span class="text-gray-900 dark:text-white">{{ segment.fx || 'Unknown' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-300">Speed:</span>
              <span class="text-gray-900 dark:text-white">{{ segment.sx || 0 }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-300">Intensity:</span>
              <span class="text-gray-900 dark:text-white">{{ segment.ix || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Raw State Data -->
    <div v-if="device.latest_state" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Complete State Data</h3>
      
      <div class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-4">
        <pre class="text-xs text-gray-800 dark:text-gray-200 overflow-x-auto whitespace-pre-wrap">{{
          JSON.stringify(device.latest_state, null, 2)
        }}</pre>
      </div>
    </div>

    <!-- No State Data -->
    <div v-else class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 48 48">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v6a2 2 0 002 2h6a2 2 0 002-2v-6m0 0V9a2 2 0 00-2-2h-6a2 2 0 00-2 2v4z"></path>
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No state data available</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        State information will appear here when the device is scanned.
      </p>
    </div>
  </div>
</template>