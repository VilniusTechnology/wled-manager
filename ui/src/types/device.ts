export interface Device {
  device_id: string
  mac: string
  last_ip?: string
  local_name?: string
  hostname?: string
  name?: string
  last_seen?: string
  lastSeen?: string
  signal_strength?: number
  state_on?: boolean
  status?: string
  ip_address?: string
  software_version?: string
  has_backups: boolean
  has_static_ip?: boolean  // Whether device has static IP configuration
  turn_on_after_power_up?: boolean
  discovery_date_time?: string  // Created timestamp from wled_devices table
  // WLED specific fields
  architecture?: string
  arch?: string
  brand?: string
  product?: string
  free_heap?: number
  uptime?: number
  led_count?: number
  wifi_sleep?: boolean // Whether device has wifi sleep enabled
  wifi_signal?: number // WiFi signal strength percentage
  // Keep old fields for compatibility
  id?: string
  adopted?: boolean
  version?: string
  signal?: string
  // wifiConnects?: number
  mqttConnects?: number
  location?: string
  created?: string
  updated?: string
  usermod_url?: string
}

export interface DeviceDetails extends Device {
  adopted: boolean
  has_static_ip?: boolean
  turn_on_after_power_up?: boolean
  latest_info?: any
  latest_state?: any
  latest_config?: any
  latest_timestamp?: string
  brightness?: number
  current_preset?: number
  led_count?: number
  uptime?: number
  free_heap?: number
  wifi_rssi?: number
  wifi_channel?: number
}

export interface DeviceProps {
  devices: Device[]
  isLoading: boolean
  scanInProgress: boolean
}

export interface MenuProps {
  showMobileMenu: boolean
  isDark: boolean
  tabs: Array<{
    name: string;
    route: string;
    icon: string;
    children?: Array<{ name: string; route: string; icon: string }>
  }>
}
