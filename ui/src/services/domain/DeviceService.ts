import { BaseApiService } from '../base/BaseApiService'
import type { Device } from '../../types/device'

export interface DeviceHealthCheckRequest {
  device_ids?: string[]
}

export interface DeviceHealthStatus {
  device_id: string
  status: string
  grade: number | null
  last_seen: string | null
  response_time: number | null
  last_checked: string | null
  error_message: string | null
}

export interface DeviceAdoptRequest {
  device_id: string
  local_device_name: string
}


export interface DeviceReleaseRequest {
  device_ids: string[]
}

export interface OTAUpdateRequest {
  device_ids: string[]
}

export interface DeviceConfigUpdateRequest {
  config: Record<string, any>
}

export class DeviceService extends BaseApiService {
  /**
   * Get all devices
   */
  async getDevices() {
    return this.get<Device[]>('/devices')
  }

  /**
   * Get device by MAC address
   */
  async getDeviceByMac(mac: string) {
    return this.get<Device>(`/devices/${mac}`)
  }

  /**
   * Get device details by ID
   */
  async getDeviceDetails(deviceId: string, refresh = false) {
    const endpoint = refresh
      ? `/devices/${deviceId}/details/refresh`
      : `/devices/${deviceId}/details`
    return this.get<Device>(endpoint)
  }

  /**
   * Get short info for all devices
   */
  async getDevicesShortInfo() {
    return this.get<Device[]>('/device/short-info')
  }

  /**
   * Update device
   */
  async updateDevice(mac: string, data: Partial<Device>) {
    return this.put<Device>(`/devices/${mac}`, data)
  }

  /**
   * Adopt devices
   */
  async adoptDevices(request: DeviceAdoptRequest[]) {
    return this.post('/devices/adopt', request)
  }

  /**
   * Release devices
   */
  async releaseDevices(request: DeviceReleaseRequest) {
    return this.post('/devices/release', request)
  }

  /**
   * Perform health check
   */
  async healthCheck(request?: DeviceHealthCheckRequest) {
    return this.post<DeviceHealthStatus[]>('/healthcheck', request)
  }

  /**
   * Refresh all devices by scanning their IPs
   */
  async refreshDevices() {
    return this.get('/scan-refresh')
  }

  /**
   * Refresh and get full device details for all devices
   */
  async refreshAllDeviceDetails() {
    return this.get<Device[]>('/devices/details/refresh')
  }

  /**
   * Perform OTA update on device
   */
  async performOTAUpdate(deviceId: string) {
    return this.post(`/devices/${deviceId}/ota-update`)
  }

  /**
   * Perform mass OTA update
   */
  async performMassOTAUpdate(request: OTAUpdateRequest) {
    return this.post('/devices/ota-update-mass', request)
  }

  /**
   * Perform mass OTA update with file upload
   */
  async performMassOTAUpdateWithFile(firmwareFile: File, deviceIds: string[]) {
    const formData = new FormData()
    formData.append('firmware_file', firmwareFile)
    formData.append('device_ids', JSON.stringify(deviceIds))

    return this.request('/devices/ota-update-mass', {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header for FormData, let browser set it with boundary
      headers: {}
    })
  }

  /**
   * Update device configuration
   */
  async updateDeviceConfig(deviceId: string, config: DeviceConfigUpdateRequest) {
    return this.post(`/devices/${deviceId}/config`, config)
  }

  /**
   * Scan network for devices
   */
  async scanNetwork() {
    return this.get('/scan-network-import')
  }

  /**
   * Process device by IP
   */
  async processDevice(ip: string) {
    return this.post('/process-device', { ip })
  }
}