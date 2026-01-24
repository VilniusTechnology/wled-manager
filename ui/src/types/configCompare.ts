export interface ConfigVersion {
  version_id: string
  mac: string
  timestamp: string
  ip: string
  device_id?: string
  has_config: boolean
}

export interface SelectedConfigVersion {
  version_id: string
  device_mac: string
  device_name: string
  device_id: string // Added device_id
  timestamp: string
  config: Record<string, any> | null
}

export interface ConfigComparison {
  path: string
  values: any[]
  isDifferent: boolean
}

export interface ConfigCompareFilter {
  type: 'all' | 'different' | 'same'
}

export interface ConfigCompareStats {
  total: number
  same: number
  different: number
}