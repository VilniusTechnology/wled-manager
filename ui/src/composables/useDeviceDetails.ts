import { ref } from 'vue'
import { buildApiUrl, API_ENDPOINTS } from '../utils/apiConfig'
import type { DeviceDetails } from '../types/device'
import { useDeviceStore } from '../stores/deviceStore'

export function useDeviceDetails() {
  const device = ref<DeviceDetails | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const deviceStore = useDeviceStore()

  const fetchDeviceDetails = async (deviceId: string): Promise<DeviceDetails | null> => {
    try {
      isLoading.value = true
      error.value = null

      console.log(`Fetching cached details for device ID: ${deviceId}`)

      const response = await fetch(buildApiUrl(API_ENDPOINTS.DEVICE_DETAILS(deviceId)))

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Device not found')
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      device.value = data
      console.log('Device details fetched from cache:', data)

      return data
    } catch (err) {
      console.error('Failed to fetch device details:', err)
      error.value = err instanceof Error ? err.message : 'Failed to load device details'
      return null
    } finally {
      isLoading.value = false
    }
  }

  const refreshDeviceDetails = async (deviceId: string): Promise<DeviceDetails | null> => {
    try {
      isLoading.value = true
      error.value = null

      console.log(`Refreshing device details for ID: ${deviceId}`)
      // Add timestamp to URL to prevent browser caching (double mitigation with cache: 'no-store')
      // Add timestamp to URL to prevent browser caching (double mitigation with cache: 'no-store')
      const url = new URL(buildApiUrl(API_ENDPOINTS.DEVICE_DETAILS_REFRESH(deviceId)), window.location.origin)
      url.searchParams.append('_t', new Date().getTime().toString())

      const response = await fetch(url.toString(), {
        cache: 'no-store',
        headers: {
          'Pragma': 'no-cache',
          'Cache-Control': 'no-cache'
        }
      })

      if (!response.ok) {
        if (response.status === 503) {
          console.warn(`Device ${deviceId} is unreachable (503), marking as offline.`)

          // Update local device state to offline
          if (device.value) {
            device.value = {
              ...device.value,
              status: 'offline'
            }
          }

          // Update the device store to reflect offline status
          const existingDevice = deviceStore.getDevice(deviceId)
          if (existingDevice) {
            const updatedDeviceData = {
              ...existingDevice,
              device: {
                ...existingDevice.device,
                status: 'offline'
              },
              health_status: {
                ...existingDevice.health_status,
                status: 'offline',
                last_checked: new Date().toISOString()
              },
              last_updated: new Date().toISOString()
            }
            deviceStore.devices.set(deviceId, updatedDeviceData)
            console.log('Device marked as offline in store')
          }

          error.value = 'Device is offline or unreachable'
          return device.value
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      device.value = result

      // Update the device store with the refreshed data so the device list reflects changes
      if (result) {
        console.log('Updating device store with refreshed device data')
        const existingDevice = deviceStore.getDevice(deviceId)

        if (existingDevice) {
          // Update the device in the store
          const updatedDeviceData = {
            ...existingDevice,
            device: {
              ...existingDevice.device,
              ...result,
              // Ensure critical fields are updated
              status: result.status,
              last_seen: result.last_seen,
              last_ip: result.last_ip || result.ip_address,
              signal_strength: result.signal_strength,
              state_on: result.state_on,
              software_version: result.software_version
            },
            health_status: {
              ...existingDevice.health_status,
              status: result.status || 'unknown',
              last_seen: result.last_seen || null,
              last_checked: new Date().toISOString()
            },
            last_updated: new Date().toISOString(),
            is_stale: false
          }

          deviceStore.devices.set(deviceId, updatedDeviceData)
          console.log('Device store updated successfully')
        }
      }
      return result
    } catch (err) {
      console.error('Failed to refresh device details:', err)
      error.value = err instanceof Error ? err.message : 'Failed to refresh device details'
      return null
    } finally {
      isLoading.value = false
    }
  }

  const refreshAllDeviceDetails = async (): Promise<DeviceDetails[]> => {
    try {
      isLoading.value = true
      error.value = null

      console.log('Refreshing all device details...')

      const response = await fetch(buildApiUrl(API_ENDPOINTS.DEVICES_DETAILS_REFRESH_ALL))

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('All device details refreshed:', data)

      return data
    } catch (err) {
      console.error('Failed to refresh all device details:', err)
      error.value = err instanceof Error ? err.message : 'Failed to refresh all device details'
      return []
    } finally {
      isLoading.value = false
    }
  }

  return {
    device,
    isLoading,
    error,
    fetchDeviceDetails,
    refreshDeviceDetails,
    refreshAllDeviceDetails
  }
}