import { buildApiUrl } from '../../utils/apiConfig'

export interface ApiResponse<T = any> {
  data: T
  status: number
  message?: string
}

export interface ApiError {
  message: string
  status: number
  details?: any
}

export class BaseApiService {
  protected async request<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const isFormData = options.body instanceof FormData
      const headers = { ...options.headers } as Record<string, string>
      
      if (!isFormData && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json'
      } else if (isFormData && headers['Content-Type'] === 'application/json') {
        delete headers['Content-Type']
      }

      const response = await fetch(buildApiUrl(endpoint), {
        ...options,
        headers,
      })

      if (!response.ok) {
        throw new ApiError(
          `HTTP error! status: ${response.status}`,
          response.status
        )
      }

      const data = await response.json()
      return {
        data,
        status: response.status,
      }
    } catch (error) {
      if (error instanceof ApiError) {
        throw error
      }
      throw new ApiError(
        error instanceof Error ? error.message : 'Unknown error occurred',
        0
      )
    }
  }

  protected async get<T = any>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  protected async post<T = any>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  protected async put<T = any>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  protected async delete<T = any>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }

  protected async download(endpoint: string): Promise<Response> {
    const response = await fetch(buildApiUrl(endpoint))
    if (!response.ok) {
      throw new ApiError(`Download failed! status: ${response.status}`, response.status)
    }
    return response
  }
}

export class ApiError extends Error {
  public status: number
  public details?: any

  constructor(message: string, status: number, details?: any) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.details = details
  }
}