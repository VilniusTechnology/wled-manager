import { DeviceService } from './domain/DeviceService'
import { BackupService } from './domain/BackupService'
import { ConfigVersionService } from './domain/ConfigVersionService'
import { SettingsService } from './domain/SettingsService'
import { WLEDConfigService } from './domain/WLEDConfigService'
import { schedulerService } from './schedulerService'

export class ApiServiceRegistry {
  public readonly device = new DeviceService()
  public readonly backup = new BackupService()
  public readonly configVersion = new ConfigVersionService()
  public readonly settings = new SettingsService()
  public readonly wledConfig = new WLEDConfigService()
  public readonly scheduler = schedulerService
}

// Create singleton instance
export const apiServices = new ApiServiceRegistry()

// Export individual services for convenience
export const {
  device: deviceService,
  backup: backupService,
  configVersion: configVersionService,
  settings: settingsService,
  wledConfig: wledConfigService,
} = apiServices