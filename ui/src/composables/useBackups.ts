import { ref, computed } from 'vue'
import type { BackupGroup } from '../types/backup'
import { buildApiUrl } from '../utils/apiConfig'
import { useDeviceStore } from '../stores/deviceStore'

export function useBackups() {
  const backups = ref<BackupGroup>({})
  const isLoading = ref(false)
  const deviceStore = useDeviceStore()

  // Expose devices from store for compatibility
  const devices = computed(() => deviceStore.deviceList.map(d => d.device))

  const fetchBackups = async () => {
    try {
      isLoading.value = true
      console.log('Fetching backups from API...')
      const backupsResponse = await fetch(buildApiUrl('/backups'))
      if (!backupsResponse.ok) {
        throw new Error(`HTTP error! status: ${backupsResponse.status}`)
      }
      const backupsData = await backupsResponse.json()
      console.log('Backups data received:', backupsData)
      backups.value = backupsData
      console.log('Backups set to:', backups.value)

    } catch (error) {
      console.error('Failed to fetch backups:', error)
      // For demo purposes, add some mock data if needed, but for now we'll just log
    } finally {
      isLoading.value = false
    }
  }

  // Helper function to get device name by MAC using the central store
  const getDeviceName = (mac: string): string | undefined => {
    // Try to get from Map by ID (which is mostly MAC)
    const deviceData = deviceStore.getDevice(mac)
    if (deviceData?.device) {
      return deviceData.device.name || deviceData.device.hostname || deviceData.device.local_name
    }

    // Fallback: search in the list if keys don't match exactly
    const device = deviceStore.deviceList.find(d => d.device.mac === mac)?.device
    return device?.name || device?.hostname || device?.local_name
  }

  return {
    backups,
    devices,
    isLoading,
    fetchBackups,
    getDeviceName
  }
}