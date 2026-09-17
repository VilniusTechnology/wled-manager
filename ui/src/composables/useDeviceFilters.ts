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
      filters.value.wifiSleep !== null ||
      filters.value.turnOnAfterPowerUp !== null ||
      filters.value.mqttEnabled !== null ||
      filters.value.architecture !== '' ||
      filters.value.softwareVersion !== ''

    if (!hasActiveFilters) {
      return devices.value
    }

    // Helper to extract mqtt_enabled if not directly defined on device
    const getDeviceMqttEnabled = (device: Device): boolean => {
      if (device.mqtt_enabled !== undefined && device.mqtt_enabled !== null) {
        return toBool(device.mqtt_enabled)
      }
      const anyDevice = device as any
      const cfgMqtt = anyDevice.latest_config?.if?.mqtt?.en ?? anyDevice.latest_config?.mqtt?.en ?? anyDevice.cfg_full?.if?.mqtt?.en ?? anyDevice.mqtt?.en
      if (cfgMqtt !== undefined && cfgMqtt !== null) {
        return toBool(cfgMqtt)
      }
      return false
    }

    // Apply filters
    return devices.value.filter(device => {
      // Status filter
      if (filters.value.status) {
        const status = (device.status || '').toLowerCase()
        if (filters.value.status === 'online') {
          // Show all devices that are online (exclude offline, dead, almost_offline)
          if (status === 'offline' || status === 'dead' || status === 'almost_offline') {
            return false
          }
        } else if (filters.value.status === 'offline') {
          // Group 'offline' with bad connectivity ('dead', 'almost_offline')
          if (status !== 'offline' && status !== 'dead' && status !== 'almost_offline') {
            return false
          }
        } else if (status !== filters.value.status) {
          // Exact match for other connection health statuses
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

      // Turn on after power up Filter
      if (filters.value.turnOnAfterPowerUp !== null) {
        if (toBool(device.turn_on_after_power_up) !== filters.value.turnOnAfterPowerUp) {
          return false
        }
      }

      // MQTT Enabled Filter
      if (filters.value.mqttEnabled !== null) {
        if (getDeviceMqttEnabled(device) !== filters.value.mqttEnabled) {
          return false
        }
      }

      // Architecture Filter
      if (filters.value.architecture) {
        const target = filters.value.architecture.toLowerCase()
        const brand = (device.brand || '').toLowerCase()
        const product = (device.product || '').toLowerCase()
        const arch = (device.arch || device.architecture || '').toLowerCase()
        if (brand !== target && product !== target && arch !== target) {
          return false
        }
      }

      // Software Version Filter
      if (filters.value.softwareVersion) {
        const ver = (device.software_version || device.version || '').toLowerCase()
        if (ver !== filters.value.softwareVersion.toLowerCase()) {
          return false
        }
      }

      return true
    })
  })

  return {
    filteredDevices
  }
}