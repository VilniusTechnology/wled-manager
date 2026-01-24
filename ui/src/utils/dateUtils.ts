// Date formatting utilities for the WLED Manager UI
import { useAppSettingsStore } from '../stores/appSettingsStore'

export type DateFormat = 'EU_NRML' | 'US_STANDARD' | 'ISO' | 'SHORT'

/**
 * Formats a timestamp string to a specific date/time format
 * @param timestamp - The timestamp string (e.g., "20250911_194346" or ISO string)
 * @param format - The desired format (default: 'EU_NRML')
 * @returns Formatted date/time string
 */
export const formatDateTime = (timestamp: string | null | undefined, format?: DateFormat): string => {
  if (!timestamp) return 'Unknown'

  try {
    let date: Date

    // Handle different timestamp formats
    if (timestamp.includes('_')) {
      // Format: "20250911_194346"
      const match = timestamp.match(/(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})/)
      if (match) {
        const [, year, month, day, hour, minute, second] = match
        date = new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}`)
      } else {
        throw new Error('Invalid timestamp format')
      }
    } else {
      // Assume ISO string or standard date string
      date = new Date(timestamp)
    }

    if (isNaN(date.getTime())) {
      throw new Error('Invalid date')
    }

    const store = useAppSettingsStore()
    const timeZone = store.timezone
    // Use provided format or fall back to store's configured format
    const effectiveFormat = format || (store.dateFormat as DateFormat) || 'EU_NRML'

    switch (effectiveFormat) {
      case 'EU_NRML':
        // YYYY-MM-DD HH:mm:ss format
        return new Intl.DateTimeFormat('sv-SE', {
          timeZone,
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        }).format(date)

      case 'US_STANDARD':
        return new Intl.DateTimeFormat('en-US', {
          timeZone,
          dateStyle: 'short',
          timeStyle: 'medium'
        }).format(date)

      case 'ISO':
        return date.toISOString()

      case 'SHORT':
        return new Intl.DateTimeFormat(undefined, {
          timeZone,
          dateStyle: 'short'
        }).format(date)

      default:
        return new Intl.DateTimeFormat(undefined, {
          timeZone,
          dateStyle: 'medium',
          timeStyle: 'medium'
        }).format(date)
    }
  } catch (error) {
    console.warn('Date formatting error:', error)
    return timestamp
  }
}

/**
 * Formats a timestamp to Y-m-d 24h format (YYYY-MM-DD HH:mm:ss)
 * @param timestamp - The timestamp string
 * @param format - The desired format (default: 'EU_NRML')
 * @returns Formatted date/time string
 */
export const formatDate = (timestamp: string | null | undefined, format: DateFormat = 'EU_NRML'): string => {
  // Alias to formatDateTime for consistency
  return formatDateTime(timestamp, format)
}

/**
 * Parses a backup timestamp string into a Date object
 * @param timestamp - The timestamp string (e.g., "20250911_194346")
 * @returns Date object or fallback date
 */
export const parseBackupDate = (timestamp: string): Date => {
  try {
    const match = timestamp.match(/(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})/)
    if (match) {
      const [, year, month, day, hour, minute, second] = match
      return new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}`)
    }
    return new Date(0)
  } catch {
    return new Date(0)
  }
}

/**
 * Gets a human-readable relative time string
 * @param date - The date to compare
 * @returns Relative time string (e.g., "2 hours ago")
 */
export const getRelativeTime = (date: Date): string => {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffSeconds < 60) return 'Just now'
  if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`
  if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`

  // For older dates, use standard formatting (which will use store timezone)
  // Convert Date object to ISO string to use our timezone-aware formatDateTime
  return formatDateTime(date.toISOString(), 'SHORT')
}