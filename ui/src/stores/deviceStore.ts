import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { buildApiUrl, API_ENDPOINTS } from '../utils/apiConfig'
import type { Device } from '../types/device'

// Health status interface
export interface DeviceHealthStatus {
  device_id: string
  status: string
  grade: number | null
  last_seen: string | null
  response_time: number | null
  last_checked: string | null
  error_message: string | null
}

// Device data from central store
export interface DeviceStoreData {
  device: Device
  health_status: DeviceHealthStatus
  last_updated: string
  is_stale: boolean
}

export const useDeviceStore = defineStore('deviceStore', () => {
  // Load persisted scan results from localStorage
  const loadPersistedScanResults = (): DeviceStoreData[] => {
    try {
      const stored = localStorage.getItem('wled_scan_results')
      return stored ? JSON.parse(stored) : []
    } catch (e) {
      console.error('Failed to load persisted scan results:', e)
      return []
    }
  }

  // Save scan results to localStorage
  const persistScanResults = (results: DeviceStoreData[]) => {
    try {
      localStorage.setItem('wled_scan_results', JSON.stringify(results))
    } catch (e) {
      console.error('Failed to persist scan results:', e)
    }
  }

  // Reactive state
  const devices = ref<Map<string, DeviceStoreData>>(new Map())
  const healthStatus = ref<Map<string, DeviceHealthStatus>>(new Map())
  const scanResults = ref<DeviceStoreData[]>(loadPersistedScanResults())
  const isLoading = ref(false)
  const scanInProgress = ref(false)

  const lastFetch = ref<Date | null>(null)
  const error = ref<string | null>(null)

  // Computed properties
  // deviceList is for general device listing (DB)
  const deviceList = computed(() => Array.from(devices.value.values()))

  // networkScanDevices is ONLY for the network scan page, always shows latest scan results (sorted)
  const networkScanDevices = computed(() => {
    return [...scanResults.value].sort((a, b) => {
      // 1. Sort by adopted status (unadopted first)
      if (a.device.adopted !== b.device.adopted) {
        return a.device.adopted ? 1 : -1
      }

      // 2. Sort by discovery date (newest first)
      const dateA = a.device.discovery_date_time ? new Date(a.device.discovery_date_time).getTime() : 0
      const dateB = b.device.discovery_date_time ? new Date(b.device.discovery_date_time).getTime() : 0

      return dateB - dateA
    })
  })
  const deviceCount = computed(() => devices.value.size)
  const onlineDevices = computed(() =>
    deviceList.value.filter((d: DeviceStoreData) => d.health_status.status === 'online' || d.health_status.status === 'excellent' || d.health_status.status === 'good')
  )
  const offlineDevices = computed(() =>
    deviceList.value.filter((d: DeviceStoreData) => d.health_status.status === 'offline' || d.health_status.status === 'dead')
  )

  // Helper function to handle API errors
  const handleApiError = (err: any, operation: string) => {
    console.error(`Error in ${operation}:`, err)
    error.value = `${operation} failed: ${err.message || 'Unknown error'}`
    return null
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const setScanInProgress = (scanning: boolean) => {
    scanInProgress.value = scanning
  }

  const scanNetwork = async () => {
    if (scanInProgress.value) {
      console.log('[DEBUG] Scan already in progress, skipping')
      return
    }

    try {
      scanInProgress.value = true
      console.log('[DEBUG] Starting global network scan...')

      const response = await fetch(buildApiUrl(API_ENDPOINTS.SCAN_NETWORK_IMPORT))
      console.log('[DEBUG] Response status:', response.status)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('[DEBUG] Error response:', errorText)
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`)
      }

      const data = await response.json()
      console.log('[DEBUG] Raw scan response:', data)

      console.log('[DEBUG] Mapping scan results to device objects...')
      const newResults = data.devices.map((raw: any) => {
        console.log('[DEBUG] Processing device:', raw)
        const info = raw.info_full || {}
        const config = raw.cfg_full || {}

        // Map device_id for compatibility (prefer DB ID, fallback to MAC)
        const device_id = raw.device_id || raw.mac


        // Extract LED info from config
        const led_info = config.hw?.led || {}
        const network_info = info.wifi || {}

        // Map all expected fields
        const device: Device = {
          device_id,
          mac: raw.mac,
          last_ip: raw.ip,
          local_name: info.name,
          hostname: info.name,
          name: info.name,
          last_seen: raw.discovery_date_time,
          // Network info
          signal_strength: network_info.signal,
          state_on: true, // Will be updated by health check
          status: 'discovered',
          ip_address: raw.ip,
          // Device info
          software_version: info.version,
          has_backups: false,
          has_static_ip: raw.has_static_ip,
          discovery_date_time: raw.discovery_date_time,
          // Hardware info
          arch: info.arch,
          brand: info.brand,
          product: info.product,
          free_heap: info.freeheap,
          uptime: info.uptime,
          led_count: led_info.total || 0,
          // Legacy fields
          id: raw.mac,
          adopted: raw.adopted || false,
          version: info.version,
          signal: network_info.signal?.toString(),
          created: raw.discovery_date_time,
          updated: raw.discovery_date_time,
        };

        console.log('[DEBUG] Mapped device:', device);
        return {
          device,
          health_status: {
            device_id,
            status: 'discovered',
            grade: null,
            last_seen: new Date().toISOString(),
            response_time: null,
            last_checked: null,
            error_message: null
          },
          last_updated: new Date().toISOString(),
          is_stale: false
        };
      });

      scanResults.value = newResults
      persistScanResults(newResults)

      // Navigate to network scan page
      // window.location.href = '/network-scan'

      return data
    } catch (err: any) {
      console.error('Failed to scan network:', err)
      error.value = err.message || 'Failed to scan network'
      throw err
    } finally {
      scanInProgress.value = false
    }
  }

  // Fetch all devices from central store
  const fetchDevices = async (forceRefresh = false, polling = false) => {
    try {
      if (!polling) {
        isLoading.value = true
      }
      error.value = null

      // Always use scan-refresh when refreshing to ensure we get the latest device states
      if (forceRefresh) {
        console.log('Force refresh requested, using scan-refresh endpoint')
        const refreshResponse = await fetch(buildApiUrl(API_ENDPOINTS.SCAN_REFRESH))
        if (!refreshResponse.ok) {
          throw new Error(`HTTP error in refresh! status: ${refreshResponse.status}`)
        }
        const refreshData = await refreshResponse.json()
        console.log('Scan-refresh completed:', refreshData)

        // Always fetch full data after refresh to ensure we have the latest state
        const shortInfoUrl = buildApiUrl(API_ENDPOINTS.DEVICE_SHORT_INFO) + `?include_latest=true&_t=${Date.now()}`
        const shortInfoResponse = await fetch(shortInfoUrl)

        if (!shortInfoResponse.ok) {
          throw new Error(`HTTP error! status: ${shortInfoResponse.status}`)
        }

        const shortInfoData = await shortInfoResponse.json()

        // Clear existing data only on forced refresh
        devices.value.clear()

        // Process and store device data
        for (const device of shortInfoData) {
          const deviceData: DeviceStoreData = {
            device: device,
            health_status: {
              device_id: device.device_id || device.id,
              status: device.status || 'unknown',
              grade: null,
              last_seen: device.last_seen,
              response_time: null,
              last_checked: new Date().toISOString(),
              error_message: null
            },
            last_updated: new Date().toISOString(),
            is_stale: false
          }
          devices.value.set(device.device_id || device.id, deviceData)
        }

        return // Exit after processing refreshed data
      }

      // Use short-info endpoint to get the latest data
      const url = buildApiUrl(API_ENDPOINTS.DEVICE_SHORT_INFO) + `?include_latest=true&_t=${Date.now()}`
      const response = await fetch(url)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      if (!polling) {
        console.log('Devices fetched from short-info endpoint:', data)
      }

      // Create a set of IDs currently in the response
      const currentIds = new Set<string>()

      // Process and store/update device data
      for (const device of data) {
        const id = device.device_id || device.id
        currentIds.add(id)

        const existingData = devices.value.get(id)

        const deviceData: DeviceStoreData = {
          device: device,
          health_status: {
            device_id: id,
            status: device.status || 'unknown',
            grade: null,
            last_seen: device.last_seen,
            response_time: null,
            last_checked: existingData?.health_status.last_checked || null,
            error_message: null
          },
          last_updated: new Date().toISOString(),
          is_stale: false
        }

        devices.value.set(id, deviceData)
      }

      // Remove devices that are no longer in the response
      for (const id of devices.value.keys()) {
        if (!currentIds.has(id)) {
          devices.value.delete(id)
        }
      }

      lastFetch.value = new Date()
      if (!polling) {
        console.log(`Successfully loaded ${devices.value.size} devices from short-info endpoint`)
      }

    } catch (err: any) {
      handleApiError(err, 'fetchDevices')
    } finally {
      isLoading.value = false
    }
  }

  // DEPRECATED: Fetch specific device data - Central Store removed
  const fetchDevice = async (_deviceId: string, _forceRefresh = false) => {
    throw new Error('Central Store removed. Use /api/devices endpoints.')
  }

  // Refresh single device data
  const refreshDevice = async (deviceId: string) => {
    try {
      const url = buildApiUrl(API_ENDPOINTS.DEVICE_DETAILS_REFRESH(deviceId))
      const response = await fetch(url)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const device = await response.json()

      // Update store
      const id = device.device_id || device.id || deviceId

      const deviceData: DeviceStoreData = {
        device: device,
        health_status: {
          device_id: id,
          status: device.status || 'unknown',
          grade: null,
          last_seen: device.last_seen,
          response_time: null,
          last_checked: new Date().toISOString(),
          error_message: null
        },
        last_updated: new Date().toISOString(),
        is_stale: false
      }

      devices.value.set(id, deviceData)
      return device
    } catch (err: any) {
      handleApiError(err, 'refreshDevice')
      throw err
    }
  }

  // DEPRECATED: Update device data - Central Store removed
  const updateDevice = async (_deviceId: string, _updates: Partial<Device>) => {
    throw new Error('Central Store removed. Use PUT /api/devices/{mac}.')
  }

  // DEPRECATED: Fetch health status - Central Store removed
  const fetchHealthStatus = async (_forceRefresh = false) => {
    throw new Error('Central Store removed. Use /api/devices endpoints.')
  }

  // Get device by ID
  const getDevice = (deviceId: string) => {
    return devices.value.get(deviceId)
  }

  // Get health status by device ID
  const getDeviceHealth = (deviceId: string) => {
    return healthStatus.value.get(deviceId)
  }

  // Clear all data
  const clearScanResults = () => {
    scanResults.value = []
    localStorage.removeItem('wled_scan_results')
    console.log('Scan results cleared')
  }

  const clearData = () => {
    devices.value.clear()
    healthStatus.value.clear()
    lastFetch.value = null
    error.value = null
    clearScanResults()
    console.log('Device store data cleared')
  }

  // Toggle device power
  const togglePower = async (deviceId: string) => {
    // Find device in local store for optimistic update
    const deviceData = devices.value.get(deviceId)
    const originalState = deviceData?.device.state_on

    try {
      // Optimistic update
      if (deviceData) {
        deviceData.device.state_on = !originalState
        // Force reactivity update if needed (Map values are reactive but nested properties might need trigger)
        devices.value.set(deviceId, { ...deviceData })
      }

      isLoading.value = true
      error.value = null

      const url = buildApiUrl(API_ENDPOINTS.DEVICE_TOGGLE(deviceId))
      const response = await fetch(url, {
        method: 'POST',
      })

      if (!response.ok) {
        // Revert optimistic update on error
        if (deviceData && originalState !== undefined) {
          deviceData.device.state_on = originalState
          devices.value.set(deviceId, { ...deviceData })
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      // Update with authoritative state from server
      if (deviceData && typeof data.state_on === 'boolean') {
        deviceData.device.state_on = data.state_on
        devices.value.set(deviceId, { ...deviceData })
      }

      console.log(`Successfully toggled power for device ${deviceId} to ${data.state_on}`)

      return { success: true, state: data.state_on }
    } catch (err: any) {
      // Revert optimistic update on error
      if (deviceData && originalState !== undefined) {
        deviceData.device.state_on = originalState
        devices.value.set(deviceId, { ...deviceData })
      }
      handleApiError(err, 'togglePower')
      return { success: false }
    } finally {
      isLoading.value = false
    }
  }

  // DEPRECATED: Invalidate cache - Central Store removed
  const invalidateCache = async (_deviceId?: string) => {
    throw new Error('Central Store removed.')
  }

  // DEPRECATED: Get cache stats - Central Store removed
  const getCacheStats = async () => {
    throw new Error('Central Store removed.')
  }

  // Remove device from store
  const removeDevice = (deviceId: string) => {
    if (devices.value.has(deviceId)) {
      devices.value.delete(deviceId)
      console.log(`Removed device ${deviceId} from local store`)
    }
  }

  // Perform optimistic local update
  const updateDeviceLocalState = (deviceId: string, updates: Partial<Device>) => {
    const data = devices.value.get(deviceId)
    if (data) {
      console.log(`[Optimistic] Updating device ${deviceId} locally:`, updates)
      // Create a shallow copy of the device object with updates
      const updatedDevice = { ...data.device, ...updates }

      // Update the store entry
      devices.value.set(deviceId, {
        ...data,
        device: updatedDevice,
        last_updated: new Date().toISOString()
      })
    }
  }

  return {
    // State
    devices,
    healthStatus,
    isLoading,
    scanInProgress,
    scanResults,
    lastFetch,
    error,

    // Computed
    deviceList,
    deviceCount,
    onlineDevices,
    offlineDevices,
    networkScanDevices,

    // Actions
    fetchDevices,
    fetchDevice,
    refreshDevice,
    updateDevice,
    updateDeviceLocalState, // Export new action
    fetchHealthStatus,
    getDevice,
    getDeviceHealth,
    clearData,
    clearScanResults,
    invalidateCache,
    setLoading,
    setScanInProgress,
    scanNetwork,
    togglePower,
    getCacheStats,
    removeDevice
  }
})