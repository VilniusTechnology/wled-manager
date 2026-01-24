import { buildApiUrl } from '../utils/apiConfig'

export class ApiService {
  private async handleResponse(response: Response) {
    if (!response.ok) {
      let errorMessage = `HTTP error! status: ${response.status}`
      try {
        const errorData = await response.json()
        if (errorData && errorData.detail) {
          errorMessage = errorData.detail
        }
      } catch (e) {
        // Could not parse error JSON, stick to generic message
      }
      throw new Error(errorMessage)
    }
    return await response.json()
  }

  async get(endpoint: string): Promise<any> {
    const response = await fetch(buildApiUrl(endpoint), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return this.handleResponse(response)
  }

  async post(endpoint: string, data?: any): Promise<any> {
    const response = await fetch(buildApiUrl(endpoint), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    })
    return this.handleResponse(response)
  }

  async put(endpoint: string, data?: any): Promise<any> {
    const response = await fetch(buildApiUrl(endpoint), {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    })
    return this.handleResponse(response)
  }

  async delete(endpoint: string): Promise<any> {
    const response = await fetch(buildApiUrl(endpoint), {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return this.handleResponse(response)
  }
}

export const apiService = new ApiService()