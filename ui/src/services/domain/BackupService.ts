import { BaseApiService } from '../base/BaseApiService'

export interface Backup {
  id: string
  mac: string
  timestamp: string
  presets_path: string
  cfg_path: string
  device_id: string
}

export interface BackupsByDevice {
  [mac: string]: Backup[]
}

export interface RestoreRequest {
  backup_id: string
  restore_config?: boolean
  restore_presets?: boolean
}

export class BackupService extends BaseApiService {
  /**
   * Get all backups grouped by MAC address
   */
  async getBackups() {
    return this.get<BackupsByDevice>('/backups')
  }

  /**
   * Backup a specific device
   */
  async backupDevice(deviceId: string) {
    return this.post(`/devices/${deviceId}/backup`)
  }

  /**
   * Backup all devices
   */
  async backupAllDevices() {
    return this.post('/devices/backup-all')
  }

  /**
   * Restore a device from backup
   */
  async restoreDevice(deviceId: string, request: RestoreRequest) {
    return this.post(`/devices/${deviceId}/restore`, request)
  }

  /**
   * Download backup config file
   */
  async downloadBackupConfig(backupId: string): Promise<Response> {
    return this.download(`/backups/download/${backupId}/config`)
  }

  /**
   * Download backup presets file
   */
  async downloadBackupPresets(backupId: string): Promise<Response> {
    return this.download(`/backups/download/${backupId}/presets`)
  }

  /**
   * Get backup config content as JSON for comparison
   */
  async getBackupConfigContent(backupId: string) {
    return this.get(`/backups/${backupId}/config-content`)
  }
}