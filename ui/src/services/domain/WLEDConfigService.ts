import { BaseApiService } from '../base/BaseApiService'

export interface WLEDConfigRequest {
  ip: string
  config: Record<string, any>
}

export class WLEDConfigService extends BaseApiService {
  /**
   * Set or update WLED device config
   */
  async updateWLEDConfig(request: WLEDConfigRequest) {
    return this.post('/wled/config', request)
  }
}