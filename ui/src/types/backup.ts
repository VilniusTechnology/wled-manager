export interface Backup {
  id: string
  mac: string
  timestamp: string
  presets_path: string
  cfg_path: string
  cfg_size?: number
  presets_size?: number
}

export interface BackupGroup {
  [mac: string]: Backup[]
}