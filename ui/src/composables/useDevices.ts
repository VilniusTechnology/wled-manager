import { computed, ref } from 'vue'
import { useDeviceStore } from '../stores/deviceStore'
import { buildApiUrl, API_ENDPOINTS } from '../utils/apiConfig'

export function useDevices() {
  const deviceStore = useDeviceStore()

  // Reactive references for backward compatibility
  const devices = computed(() => deviceStore.deviceList.map(d => d.device))
  const isLoading = computed(() => deviceStore.isLoading)
  const scanInProgress = computed(() => deviceStore.scanInProgress)

  // Fetch all devices (wrapper around store action)
  const fetchDevices = async (forceRefresh = false, polling = false) => {
    deviceStore.setLoading(true);
    if (!polling) {
      console.log('Fetching devices using central store...', forceRefresh ? '(with refresh)' : '')
    }

    try {
      await deviceStore.fetchDevices(forceRefresh, polling);
    } catch (err) {
      // Error handling is done in the store
    } finally {
      // Loading state is handled in the store
    }
  }

  // Polling interval reference
  const pollingInterval = ref<number | null>(null)

  const startPolling = (intervalMs = 30000) => {
    if (pollingInterval.value) return

    console.log(`Starting device polling every ${intervalMs}ms`)
    pollingInterval.value = window.setInterval(() => {
      fetchDevices(false, true)
    }, intervalMs)
  }

  const stopPolling = () => {
    if (pollingInterval.value) {
      console.log('Stopping device polling')
      clearInterval(pollingInterval.value)
      pollingInterval.value = null
    }
  }

  const scanNetwork = async () => {
    try {
      deviceStore.setScanInProgress(true)
      console.log('Starting network scan...')
      const response = await fetch(buildApiUrl(API_ENDPOINTS.SCAN_NETWORK_IMPORT), {
        method: 'GET'
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Network scan completed:', data)

      // Refresh devices list after scan without showing refresh loading
      await deviceStore.fetchDevices(true)

      return data
    } catch (error) {
      console.error('Failed to scan network:', error)
      throw error
    } finally {
      deviceStore.setScanInProgress(false)
      deviceStore.setLoading(false)
    }
  }

  const backupDevice = async (deviceId: string) => {
    try {
      console.log('Backing up device:', deviceId)
      const response = await fetch(buildApiUrl(API_ENDPOINTS.DEVICE_BACKUP(deviceId)), {
        method: 'POST'
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log('Backup successful:', result)

      // Refresh device data after backup
      await deviceStore.refreshDevice(deviceId)

      return result
    } catch (error) {
      console.error('Failed to backup device:', error)
      throw error
    }
  }

  const restoreDevice = async (deviceId: string, backupId: string, restoreConfig: boolean = true, restorePresets: boolean = true) => {
    try {
      console.log('Restoring device:', deviceId, 'from backup:', backupId)
      const response = await fetch(buildApiUrl(API_ENDPOINTS.DEVICE_RESTORE(deviceId)), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          backup_id: backupId,
          restore_config: restoreConfig,
          restore_presets: restorePresets
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log('Restore successful:', result)

      // Refresh device data after restore
      await deviceStore.refreshDevice(deviceId)

      return result
    } catch (error) {
      console.error('Failed to restore device:', error)
      throw error
    }
  }

  const updateDeviceConfig = async (deviceId: string, config: any) => {
    try {
      console.log('Updating device config:', deviceId)
      const response = await fetch(buildApiUrl(API_ENDPOINTS.DEVICE_CONFIG(deviceId)), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log('Config update successful:', result)

      // Refresh device data after config update
      await deviceStore.refreshDevice(deviceId)

      return result
    } catch (error) {
      console.error('Failed to update device config:', error)
      throw error
    }
  }

  const performOTAUpdate = async (deviceId: string, filename: string) => {
    try {
      console.log('Performing OTA update:', deviceId, filename)
      const response = await fetch(buildApiUrl(API_ENDPOINTS.DEVICE_OTA_UPDATE(deviceId)), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filename })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log('OTA update initiated:', result)

      // Refresh device data after OTA update
      setTimeout(() => {
        deviceStore.refreshDevice(deviceId)
      }, 10000) // Wait 10 seconds for OTA to complete

      return result
    } catch (error) {
      console.error('Failed to perform OTA update:', error)
      throw error
    }
  }

  const adoptDevices = async (devicesToAdopt: Array<{ device_id: string; local_device_name: string }>) => {
    try {
      console.log('Adopting devices:', devicesToAdopt)

      // Optimistic update
      for (const device of devicesToAdopt) {
        deviceStore.updateDeviceLocalState(device.device_id, {
          adopted: true,
          local_name: device.local_device_name,
          name: device.local_device_name
        })
      }

      const response = await fetch(buildApiUrl(API_ENDPOINTS.DEVICE_ADOPT), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(devicesToAdopt)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log('Adoption successful:', result)

      // Refresh all devices after adoption to confirm state
      await fetchDevices()

      return result
    } catch (error) {
      console.error('Failed to adopt devices:', error)
      // Revert/Refresh on error
      await fetchDevices()
      throw error
    }
  }

  const releaseDevices = async (deviceIds: string[]) => {
    try {
      console.log('Releasing devices:', deviceIds)

      // Optimistic update: Mark as released immediately
      for (const id of deviceIds) {
        deviceStore.updateDeviceLocalState(id, { adopted: false })
      }

      const response = await fetch(buildApiUrl(API_ENDPOINTS.DEVICE_RELEASE), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ device_ids: deviceIds })
      })

      if (!response.ok) {
        // If failed, revert optimistic update (could refetch or store previous state, but fetchDevices covers it)
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log('Release successful:', result)

      // Refresh all devices after release to confirm state
      try {
        await fetchDevices()
      } catch (e) {
        console.error('Background refresh failed after release (ignoring):', e)
      }

      return result
    } catch (error) {
      console.error('Failed to release devices:', error)
      // Revert/Refresh on error to ensure correct state
      try {
        await fetchDevices()
      } catch (e) {
        console.error('Revert refresh failed:', e)
      }
      throw error
    }
  }

  const performHealthcheck = async (ips: string[]) => {
    try {
      console.log('Performing healthcheck on IPs:', ips)
      const response = await fetch(buildApiUrl(API_ENDPOINTS.DEVICE_HEALTHCHECK), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ips })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log('Healthcheck completed:', result)

      // Refresh health status after healthcheck
      await deviceStore.fetchHealthStatus(true)

      return result
    } catch (error) {
      console.error('Failed to perform healthcheck:', error)
      throw error
    }
  }

  const visitDevice = (deviceId: string) => {
    const device = devices.value.find(d => d.device_id === deviceId || d.id === deviceId)
    if (!device) {
      console.error('Device not found:', deviceId)
      return
    }

    // Build URL - prefer mDNS, fallback to IP
    let url = ''
    if (device.hostname) {
      // Ensure we don't double-add .local if it's already there (though backend usually strips it)
      const hostname = device.hostname.endsWith('.local') ? device.hostname : `${device.hostname}.local`
      url = `http://${hostname}`
    } else {
      url = `http://${device.last_ip || device.ip_address}`
    }

    // Open in new tab
    window.open(url, '_blank')
  }

  const deleteDevice = async (deviceId: string) => {
    try {
      console.log(`Deleting device ${deviceId}...`)
      // Use the proper endpoint based on ID format
      // API expects the internal DB ID or device_id
      const response = await fetch(buildApiUrl(API_ENDPOINTS.DEVICE_DELETE(deviceId)), {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error(`Failed to delete device: ${response.statusText}`)
      }

      const result = await response.json()
      if (result.success) {
        console.log(`Device ${deviceId} deleted successfully`)
        // Remove from local state immediately for better UX
        deviceStore.removeDevice(deviceId)
        // Also refresh to ensure sync with server
        await fetchDevices(false)
      } else {
        throw new Error(result.message || 'Failed to delete device')
      }
    } catch (error) {
      console.error('Error deleting device:', error)
      throw error
    }
  }

  const addDevice = async (ip: string, localName: string) => {
    try {
      console.log(`Adding device at ${ip} with name ${localName}...`)
      const response = await fetch(buildApiUrl(API_ENDPOINTS.DEVICE_ADD), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ip,
          local_name: localName
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Failed to add device: ${response.statusText}`)
      }

      const result = await response.json()
      if (result.success) {
        console.log(`Device added successfully: ${result.device_id}`)
        await fetchDevices(false)
        return result
      } else {
        throw new Error(result.message || 'Failed to add device')
      }
    } catch (error) {
      console.error('Error adding device:', error)
      throw error
    }
  }

  return {
    devices,
    isLoading,
    scanInProgress,
    fetchDevices,
    startPolling,
    stopPolling,
    scanNetwork,
    backupDevice,
    restoreDevice,
    updateDeviceConfig,
    performOTAUpdate,
    adoptDevices,
    releaseDevices,
    performHealthcheck,
    visitDevice,
    deleteDevice,
    addDevice
  }
}
