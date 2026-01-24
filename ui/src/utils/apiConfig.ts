// API Configuration with defaults
const API_HOST = import.meta.env.VITE_API_HOST
const API_PORT = import.meta.env.VITE_API_PORT || '8000'
const API_PROTOCOL = import.meta.env.VITE_API_PROTOCOL || 'http'

// In development, we use Vite's proxy feature so we just need the path
const isDev = import.meta.env.DEV

/**
 * Build a full API URL from a relative path
 * @param path Relative API path
 * @returns Full API URL
 */
export const buildApiUrl = (endpoint: string): string => {
  // Remove leading slash if present
  const normalizedPath = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint

  if (isDev) {
    // In development, use relative path (Vite proxy will handle it)
    return `/api/${normalizedPath}`
  } else {
    // In production, check if we have custom API host configured
    // If not, use relative path (same origin as the UI)
    if (API_HOST && API_HOST !== 'localhost' && API_HOST !== '' && !API_HOST.includes('example.com')) {
      // Use full URL with configured host
      return `${API_PROTOCOL}://${API_HOST}:${API_PORT}/api/${normalizedPath}`
    } else {
      // Use relative path (same origin)
      return `/api/${normalizedPath}`
    }
  }
}

// API Endpoints
export const API_ENDPOINTS = {
  DEVICES: '/devices',
  DEVICE_SHORT_INFO: '/short-info',  // For initial load without refresh
  SCAN_REFRESH: '/scan-refresh',  // For refreshing device statuses
  SCAN_NETWORK_IMPORT: '/scan-network-import',
  DEVICE_BACKUP: (deviceId: string) => `/devices/${deviceId}/backup`,
  DEVICE_RESTORE: (deviceId: string) => `/devices/${deviceId}/restore`,
  DEVICE_CONFIG: (deviceId: string) => `/devices/${deviceId}/config`,
  DEVICE_DETAILS: (deviceId: string) => `/devices/${deviceId}/details`,
  DEVICE_TOGGLE: (deviceId: string) => `/devices/${deviceId}/toggle`,
  DEVICE_DETAILS_REFRESH: (deviceId: string) => `/devices/${deviceId}/details/refresh`,
  DEVICES_DETAILS_REFRESH_ALL: '/devices/details/refresh',
  BACKUPS: '/backups',
  BACKUP_DOWNLOAD: (backupId: string, fileType: string) => `/backups/download/${backupId}/${fileType}`,
  BACKUP_ALL_DEVICES: '/devices/backup-all',
  DEVICE_OTA_UPDATE: (deviceId: string) => `/devices/${deviceId}/ota-update`,
  DEVICE_OTA_UPDATE_MASS: '/devices/ota-update-mass',
  DEVICE_RELEASE: '/devices/release',
  DEVICE_ADOPT: '/devices/adopt',
  DEVICE_HEALTHCHECK: '/devices/healthcheck',
  DEVICE_DELETE: (deviceId: string) => `/devices/${deviceId}`,
  DEVICE_ADD: '/devices'
}

// Function to update API configuration (useful for runtime changes)
export const updateApiConfig = () => {
  console.warn('API configuration cannot be updated at runtime in development mode')
}