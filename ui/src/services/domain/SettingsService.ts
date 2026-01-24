import { BaseApiService } from '../base/BaseApiService'

export interface AppSettings {
  scan_timeout: number
  info_timeout: number
  backup_info_timeout: number
  backup_download_timeout: number
  db_path: string
  backup_dir: string
  max_workers: number
  connection_pool_size: number
  max_retries: number
  scheduler_initial_delay: number
  [key: string]: any
}

export class SettingsService extends BaseApiService {
  /**
   * Get all app settings
   */
  async getAllSettings() {
    return this.get<{ settings: AppSettings }>('/settings')
  }

  /**
   * Set all app settings
   */
  async setAllSettings(settings: AppSettings) {
    return this.post('/settings', { settings })
  }

  /**
   * Get a specific setting
   */
  async getSetting(key: string) {
    return this.get(`/settings/${key}`)
  }

  /**
   * Set a specific setting
   */
  async setSetting(key: string, value: any) {
    return this.put(`/settings/${key}`, { value })
  }

  /**
   * Send a test email to verify SMTP configuration
   */
  async sendTestEmail() {
    return this.post('/email/test', {})
  }

  /**
   * Trigger sending the backup email with device links
   */
  async triggerBackupEmail() {
    return this.post('/email/backup', {})
  }
}