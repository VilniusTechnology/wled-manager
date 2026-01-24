import { inject, provide, type InjectionKey } from 'vue'
import type { ApiServiceRegistry } from '../ApiServiceRegistry'
import { apiServices } from '../ApiServiceRegistry'

// Create injection key for type safety
export const ApiServicesKey: InjectionKey<ApiServiceRegistry> = Symbol('ApiServices')

/**
 * Provide API services to child components
 */
export function provideApiServices(services: ApiServiceRegistry = apiServices) {
  provide(ApiServicesKey, services)
}

/**
 * Use API services in components
 * @throws Error if services are not provided
 */
export function useApiServices(): ApiServiceRegistry {
  const services = inject(ApiServicesKey)
  if (!services) {
    throw new Error('API services not provided. Make sure to call provideApiServices() in a parent component.')
  }
  return services
}

/**
 * Use device service
 */
export function useDeviceService() {
  return useApiServices().device
}

/**
 * Use backup service
 */
export function useBackupService() {
  return useApiServices().backup
}

/**
 * Use config version service
 */
export function useConfigVersionService() {
  return useApiServices().configVersion
}

/**
 * Use settings service
 */
export function useSettingsService() {
  return useApiServices().settings
}

/**
 * Use WLED config service
 */
export function useWLEDConfigService() {
  return useApiServices().wledConfig
}

/**
 * Use scheduler service
 */
export function useSchedulerService() {
  return useApiServices().scheduler
}