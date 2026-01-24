import { apiService } from './apiService';

export interface PasswordResponse {
  id?: number;
  key: string;
  password: string;
}

export const secretsService = {
  async getSecret(key: string): Promise<PasswordResponse> {
    try {
      return await apiService.get(`passwords/${key}`);
    } catch (e) {
      // If the secret doesn't exist, we might get a 404 or similar.
      // Return a default object or rethrow. 
      // Tasmota handled this in the component, but let's see.
      // If we rethrow, the component can handle it.
      throw e;
    }
  },

  async saveSecret(key: string, password: string): Promise<PasswordResponse> {
    return await apiService.post(`passwords/${key}`, { password, key });
  }
};
