import { computed, type Ref } from 'vue'
import type { Device } from '../types/device'
import type { DeviceFilters } from '../types/deviceFilters'

export const useDeviceFilters = (devices: Ref<Device[]>, filters: Ref<DeviceFilters>) => {
  const toBool = (val: any): boolean => val === true || val === 1 || val === 'true' || val === '1'

  const filteredDevices = computed(() => {
    // If no devices, return empty array
    if (!devices.value || devices.value.length === 0) {
      return []
    }

    // If no filters are active, return all devices
    const hasActiveFilters =
      filters.value.status ||
      filters.value.search ||
      filters.value.hasBackups !== null ||
      filters.value.stateOn !== null ||
      filters.value.adopted !== null ||
      filters.value.hasStaticIp !== null ||
      filters.value.wifiSleep !== null

    if (!hasActiveFilters) {
      return devices.value
    }

    // Apply filters
    return devices.value.filter(device => {
      // Status filter
      if (filters.value.status) {
        if (filters.value.status === 'online') {
          // Show only devices with healthy status (online, excellent, good)
          const status = (device.status || '').toLowerCase()
          if (status !== 'online' && status !== 'excellent' && status !== 'good') {
            return false
          }
        } else if (filters.value.status === 'offline') {
          // Group 'dead' with 'offline' for filtering
          if (device.status !== 'offline' && device.status !== 'dead') {
            return false
          }
        } else if (device.status !== filters.value.status) {
          return false
        }
      }

      // Search filter (Name or IP)
      if (filters.value.search) {
        const searchTerm = filters.value.search.toLowerCase()

        // Name fields
        const deviceName = (device.name || '').toLowerCase()
        const localName = (device.local_name || '').toLowerCase()
        const hostname = (device.hostname || '').toLowerCase()

        // IP fields
        const ipAddress = (device.ip_address || '').toLowerCase()
        const lastIp = (device.last_ip || '').toLowerCase()
        const mac = (device.mac || '').toLowerCase()

        if (!deviceName.includes(searchTerm) &&
          !localName.includes(searchTerm) &&
          !hostname.includes(searchTerm) &&
          !ipAddress.includes(searchTerm) &&
          !lastIp.includes(searchTerm) &&
          !mac.includes(searchTerm)) {
          return false
        }
      }

      // Has Backups filter
      if (filters.value.hasBackups !== null && toBool(device.has_backups) !== filters.value.hasBackups) {
        return false
      }

      // State On filter
      if (filters.value.stateOn !== null && toBool(device.state_on) !== filters.value.stateOn) {
        return false
      }

      // Adopted filter
      if (filters.value.adopted !== null && toBool(device.adopted) !== filters.value.adopted) {
        return false
      }

      // Static IP filter
      if (filters.value.hasStaticIp !== null && toBool(device.has_static_ip) !== filters.value.hasStaticIp) {
        return false
      }

      // WiFi Sleep filter
      if (filters.value.wifiSleep !== null && toBool(device.wifi_sleep) !== filters.value.wifiSleep) {
        return false
      }

      return true
    })
  })

  return {
    filteredDevices
  }
}