export interface SelectedBackup {
  backupId: string
  deviceId: string
  deviceName: string
  mac: string
  timestamp: string
  config: Record<string, any>
}

export interface BackupComparison {
  path: string
  values: any[]
  isDifferent: boolean
}

export interface BackupCompareFilter {
  type: 'all' | 'different' | 'same'
}

export interface BackupCompareStats {
  total: number
  same: number
  different: number
}