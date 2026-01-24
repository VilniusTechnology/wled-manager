<script setup lang="ts">
import IpConfigBadge from '../shared/IpConfigBadge.vue'
import DeviceNetworkActions from './DeviceNetworkActions.vue'
import type { DeviceDetails } from '../../types/device'

defineProps<{
  device: DeviceDetails
  deviceStatus?: string
}>()

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

const getSignalBars = (rssi?: number) => {
  if (!rssi) return 0
  
  if (rssi > -50) return 4
  if (rssi > -60) return 3
  if (rssi > -70) return 2
  return 1
}

const formatWiFiSecurity = (sec?: number) => {
  const securities: { [key: number]: string } = {
    0: 'Open',
    1: 'WEP',
    2: 'WPA_PSK',
    3: 'WPA2_PSK',
    4: 'WPA_WPA2_PSK',
    5: 'WPA2_ENTERPRISE'
  }
  
  return sec !== undefined ? (securities[sec] || `Unknown (${sec})`) : 'Unknown'
}
</script>

<template>
  <div class="space-y-6">
    <!-- Network Status Overview -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Connection Status -->
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Connection Status</h3>
        <div class="space-y-3">
          <!-- Signal Strength Indicator -->
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Signal:</span>
            <div class="flex items-center space-x-2">
              <!-- Signal bars visualization -->
              <div class="flex space-x-1">
                <div 
                  v-for="bar in 4"
                  :key="bar"
                  :class="{
                    'bg-gray-300 dark:bg-gray-600': bar > getSignalBars(device.wifi_rssi),
                    'bg-green-500': bar <= getSignalBars(device.wifi_rssi) && device.wifi_rssi && device.wifi_rssi > -50,
                    'bg-blue-500': bar <= getSignalBars(device.wifi_rssi) && device.wifi_rssi && device.wifi_rssi <= -50 && device.wifi_rssi > -60,
                    'bg-yellow-500': bar <= getSignalBars(device.wifi_rssi) && device.wifi_rssi && device.wifi_rssi <= -60 && device.wifi_rssi > -70,
                    'bg-red-500': bar <= getSignalBars(device.wifi_rssi) && device.wifi_rssi && device.wifi_rssi <= -70
                  }"
                  class="w-1 rounded"
                  :style="{ height: `${bar * 3 + 6}px` }"
                ></div>
              </div>
              <span :class="getSignalStrengthColor(device.wifi_rssi)" class="text-sm font-medium">
                {{ device.wifi_rssi ? `${device.wifi_rssi} dBm` : 'Unknown' }}
              </span>
            </div>
          </div>
          
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Quality:</span>
            <span :class="getSignalStrengthColor(device.wifi_rssi)" class="text-sm font-medium">
              {{ getSignalStrengthLabel(device.wifi_rssi) }}
            </span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Channel:</span>
            <span class="text-sm text-gray-900 dark:text-white">
              {{ device.wifi_channel || device.latest_info?.wifi?.channel || 'Unknown' }}
            </span>
          </div>
        </div>
      </div>

      <!-- IP Configuration -->
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">IP Configuration</h3>
          <IpConfigBadge :hasStaticIp="device.has_static_ip" size="sm" />
        </div>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">IP Address:</span>
            <span class="text-sm font-mono text-gray-900 dark:text-white">
              {{ device.last_ip || 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between" v-if="device.latest_config?.nw?.ins?.[0]">
            <span class="text-sm text-gray-600 dark:text-gray-300">Gateway:</span>
            <span class="text-sm font-mono text-gray-900 dark:text-white">
              {{ device.latest_config.nw.ins[0].gw ? device.latest_config.nw.ins[0].gw.join('.') : 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between" v-if="device.latest_config?.nw?.ins?.[0]">
            <span class="text-sm text-gray-600 dark:text-gray-300">Subnet Mask:</span>
            <span class="text-sm font-mono text-gray-900 dark:text-white">
              {{ device.latest_config.nw.ins[0].sn ? device.latest_config.nw.ins[0].sn.join('.') : 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Configuration:</span>
            <span class="text-sm text-gray-900 dark:text-white">
              {{ device.has_static_ip === true ? 'Static IP' : (device.has_static_ip === false ? 'DHCP' : 'Unknown') }}
            </span>
          </div>
        </div>
      </div>

      <!-- Device Identity -->
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Device Identity</h3>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">MAC:</span>
            <span class="text-sm font-mono text-gray-900 dark:text-white">{{ device.mac }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Hostname:</span>
            <span class="text-sm font-mono text-gray-900 dark:text-white">
              {{ device.hostname || device.latest_config?.id?.mdns || 'Not set' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">mDNS:</span>
            <span class="text-sm font-mono text-gray-900 dark:text-white">
              {{ device.latest_config?.id?.mdns ? `${device.latest_config.id.mdns}.local` : 'Not set' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- WiFi Information -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">WiFi Information</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Network SSID:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">
              {{ device.latest_info?.wifi?.ssid || device.latest_config?.wifi?.ssid || 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">BSSID:</span>
            <span class="text-sm font-mono text-gray-900 dark:text-white">
              {{ device.latest_info?.wifi?.bssid || 'Unknown' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Security:</span>
            <span class="text-sm text-gray-900 dark:text-white">
              {{ formatWiFiSecurity(device.latest_info?.wifi?.sec) }}
            </span>
          </div>
        </div>
        
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">TX Power:</span>
            <span class="text-sm text-gray-900 dark:text-white">
              {{ device.latest_config?.wifi?.pwr !== undefined ? `${device.latest_config.wifi.pwr} dBm` : 'Default' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">Sleep Mode:</span>
            <span class="text-sm text-gray-900 dark:text-white">
              {{ device.latest_config?.wifi?.sleep ? 'Enabled' : 'Disabled' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Network Actions -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Network Actions</h3>
      <DeviceNetworkActions :device="device" :device-status="deviceStatus" />
    </div>

    <!-- Advanced Network Settings -->
    <div v-if="device.latest_config" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Advanced Network Settings</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Static IP Configuration -->
        <div v-if="device.latest_config.nw?.ins?.[0]" class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-4">
          <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">Static IP Config</h4>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-300">Static IP:</span>
              <span class="font-mono text-gray-900 dark:text-white">
                {{ device.latest_config.nw.ins[0] }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-300">Gateway:</span>
              <span class="font-mono text-gray-900 dark:text-white">
                {{ device.latest_config.nw.gw }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-300">Subnet:</span>
              <span class="font-mono text-gray-900 dark:text-white">
                {{ device.latest_config.nw.mask }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- AP Mode Settings -->
        <div v-if="device.latest_config.ap" class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-4">
          <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">Access Point</h4>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-300">AP SSID:</span>
              <span class="text-gray-900 dark:text-white">
                {{ device.latest_config.ap.ssid || 'WLED-AP' }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-300">Channel:</span>
              <span class="text-gray-900 dark:text-white">
                {{ device.latest_config.ap.channel || 1 }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-300">Hidden:</span>
              <span class="text-gray-900 dark:text-white">
                {{ device.latest_config.ap.hide ? 'Yes' : 'No' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Raw Network Data -->
    <div v-if="device.latest_info?.wifi || device.latest_config?.nw || device.latest_config?.wifi" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Raw Network Data</h3>
      
      <div class="space-y-4">
        <div v-if="device.latest_info?.wifi">
          <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-2">WiFi Status</h4>
          <div class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-4 max-h-48 overflow-y-auto">
            <pre class="text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{{
              JSON.stringify(device.latest_info.wifi, null, 2)
            }}</pre>
          </div>
        </div>
        
        <div v-if="device.latest_config?.nw">
          <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-2">Network Config</h4>
          <div class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-4 max-h-48 overflow-y-auto">
            <pre class="text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{{
              JSON.stringify(device.latest_config.nw, null, 2)
            }}</pre>
          </div>
        </div>
        
        <div v-if="device.latest_config?.wifi">
          <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-2">WiFi Config</h4>
          <div class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-4 max-h-48 overflow-y-auto">
            <pre class="text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{{
              JSON.stringify(device.latest_config.wifi, null, 2)
            }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- No Network Data -->
    <div v-else class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 48 48">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"></path>
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No network data available</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Network information will appear here when the device is scanned.
      </p>
    </div>
  </div>
</template>