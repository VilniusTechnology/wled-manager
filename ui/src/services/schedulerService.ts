import { apiService } from './apiService'

export interface Scheduler {
  scheduler_id: string
  name: string
  friendly_name?: string
  state: 'running' | 'stopped' | 'error'
  interval_days: number
  last_run: string | null
  last_success: string | null
  next_run: string | null
  last_error: string | null
  last_error_time: string | null
  run_count: number
  success_count: number
  error_count: number
  success_rate: number
}

export interface SchedulerResponse {
  success: boolean
  message?: string
  scheduler?: Scheduler
  schedulers?: Scheduler[]
  results?: Record<string, boolean>
}

class SchedulerService {
  private readonly baseUrl = '/schedulers'

  async getAllSchedulers(): Promise<SchedulerResponse> {
    return await apiService.get(this.baseUrl)
  }

  async getScheduler(schedulerId: string): Promise<SchedulerResponse> {
    return await apiService.get(`${this.baseUrl}/${schedulerId}`)
  }

  async startScheduler(schedulerId: string): Promise<SchedulerResponse> {
    return await apiService.post(`${this.baseUrl}/${schedulerId}/start`)
  }

  async stopScheduler(schedulerId: string): Promise<SchedulerResponse> {
    return await apiService.post(`${this.baseUrl}/${schedulerId}/stop`)
  }

  async runSchedulerNow(schedulerId: string): Promise<SchedulerResponse> {
    return await apiService.post(`${this.baseUrl}/${schedulerId}/run`)
  }

  async startAllSchedulers(): Promise<SchedulerResponse> {
    return await apiService.post(`${this.baseUrl}/start-all`)
  }

  async stopAllSchedulers(): Promise<SchedulerResponse> {
    return await apiService.post(`${this.baseUrl}/stop-all`)
  }
}

export const schedulerService = new SchedulerService()