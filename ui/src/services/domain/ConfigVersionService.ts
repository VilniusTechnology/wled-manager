import { BaseApiService } from '../base/BaseApiService'

export interface ConfigVersion {
  version_id: string
  mac: string
  timestamp: string
  ip: string
  device_id: string
}

export interface ConfigVersionsByDevice {
  [mac: string]: ConfigVersion[]
}

export class ConfigVersionService extends BaseApiService {
  /**
   * Get all config versions grouped by MAC address
   */
  async getConfigVersions() {
    return this.get<ConfigVersionsByDevice>('/config-versions')
  }

  /**
   * Get config content for a specific version
   */
  async getConfigVersionContent(versionId: string) {
    return this.get(`/config-versions/${versionId}/config`)
  }

  /**
   * Get all config versions for a specific device
   */
  async getDeviceConfigVersions(deviceId: string) {
    return this.get<ConfigVersion[]>(`/devices/${deviceId}/config-versions`)
  }
}