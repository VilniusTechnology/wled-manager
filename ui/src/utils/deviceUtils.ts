/**
 * Utility functions for device operations
 */

/**
 * Builds an Avahi name from a device name
 * @param deviceName The device name
 * @returns The Avahi hostname (e.g., "device-name.local")
 */
export function buildAvahiName(deviceName: string): string {
  if (!deviceName) return ''

  // Replace spaces with hyphens, make lowercase, remove invalid characters
  const avahiName = deviceName
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '')
    .replace(/-+/g, '-') // Replace multiple hyphens with single
    .replace(/^-|-$/g, '') // Remove leading/trailing hyphens

  return avahiName ? `${avahiName}.local` : ''
}

/**
 * Builds the full Avahi URL for a device
 * @param deviceName The device name
 * @returns The full URL (e.g., "http://device-name.local")
 */
export function buildAvahiUrl(deviceName: string): string {
  const avahiName = buildAvahiName(deviceName)
  return avahiName ? `http://${avahiName}` : ''
}
