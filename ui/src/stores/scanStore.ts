import { defineStore } from 'pinia'
import { ref } from 'vue'
import { buildApiUrl, API_ENDPOINTS } from '../utils/apiConfig'
import type { Device } from '../types/device'

interface WLEDDevice {
  mac: string
  ip: string
  cfg_full: {
    id: {
      mdns?: string
      name?: string
    }
    hw?: {
      led?: {
        total?: number
      }
    }
  }
  info_full: {
    name?: string
    wifi?: {
      signal?: number
    }
    version?: string
    build?: string
    core?: string
    arch?: string
    brand?: string
    product?: string
    freeheap?: number
    uptime?: number
  }
  state_full?: {
    on?: boolean
  }
  has_static_ip?: boolean
  discovery_date_time?: string
}

export const useScanStore = defineStore('scanStore', () => {
  const scanResults = ref<Device[]>([])
  const isScanning = ref(false)
  const error = ref<string | null>(null)

  function mapWLEDDeviceToDevice(device: WLEDDevice): Device {
    return {
      device_id: device.mac,
      mac: device.mac,
      last_ip: device.ip,
      name: device.info_full?.name || `WLED Device ${device.mac}`,
      hostname: device.cfg_full?.id?.mdns,
      local_name: device.cfg_full?.id?.name,
      status: 'Online',
      has_backups: false,
      has_static_ip: device.has_static_ip || false,
      discovery_date_time: device.discovery_date_time,
      signal_strength: device.info_full?.wifi?.signal || 0,
      software_version: device.info_full?.version || device.info_full?.build || device.info_full?.core,
      arch: device.info_full?.arch,
      brand: device.info_full?.brand,
      product: device.info_full?.product,
      free_heap: device.info_full?.freeheap,
      uptime: device.info_full?.uptime,
      led_count: device.cfg_full?.hw?.led?.total,
      state_on: device.state_full?.on || false
    }
  }

  async function scanNetwork() {
    try {
      isScanning.value = true
      error.value = null

      const apiUrl = buildApiUrl(API_ENDPOINTS.SCAN_NETWORK_IMPORT)
      console.log('[DEBUG] Scan API URL:', apiUrl)
      console.log('[DEBUG] Starting network scan...')

      const response = await fetch(apiUrl)
      console.log('[DEBUG] Response status:', response.status)
      console.log('[DEBUG] Response headers:', Object.fromEntries(response.headers.entries()))
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('[DEBUG] Error response:', errorText)
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`)
      }

      const contentType = response.headers.get('content-type')
      console.log('[DEBUG] Content-Type:', contentType)

      if (!contentType?.includes('application/json')) {
        throw new Error(`Expected JSON response but got ${contentType}`)
      }

      const data = await response.json()
      console.log('[DEBUG] Raw API response:', data)

      if (!data.devices) {
        console.error('[DEBUG] Unexpected response format:', data)
        throw new Error('Unexpected response format: missing devices array')
      }
      
      scanResults.value = data.devices.map((device: WLEDDevice) => {
        const mapped = mapWLEDDeviceToDevice(device)
        console.log('[DEBUG] Mapped device:', mapped)
        return mapped
      })

      console.log(`[DEBUG] Found ${scanResults.value.length} devices`)

    } catch (err: any) {
      console.error('Scan error:', err)
      error.value = err.message || 'Failed to scan for devices'
    } finally {
      isScanning.value = false
    }
  }

  function clearScanResults() {
    scanResults.value = []
  }

  return {
    scanResults,
    isScanning,
    error,
    scanNetwork,
    clearScanResults
  }
})