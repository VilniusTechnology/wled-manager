import type { Device } from '../types/device'

export type DeviceLike = Partial<Device> | null | undefined

export const getDeviceDisplayName = (device: DeviceLike, fallback = 'Unknown Device'): string => {
  if (!device) return fallback
  return device.name || device.local_name || device.hostname || device.mac || fallback
}

export const getDeviceDisplayIp = (device: DeviceLike, fallback = 'No IP'): string => {
  if (!device) return fallback
  return device.last_ip || device.ip_address || fallback
}

export const getDeviceDetailsPath = (device: DeviceLike): string | null => {
  if (!device) return null
  const id = device.device_id || device.id
  return id ? `/devices/${id}` : null
}

export const formatMacAddress = (mac?: string | null): string => {
  if (!mac) return 'Unknown'
  // Remove any existing colons or dashes
  const cleanMac = mac.replace(/[:-\s]/g, '').toUpperCase()
  // Add colons every 2 chars
  return cleanMac.match(/.{1,2}/g)?.join(':') || mac
}
