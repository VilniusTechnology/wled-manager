<template>
  <div class="space-y-6">
    <!-- Summary Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Devices</p>
            <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ totalDevices }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Backups</p>
            <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ totalBackups }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Filtered Results</p>
            <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ filteredDevices.length }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Backup Cards -->
    <BackupCard
      v-for="device in filteredDevices"
      :key="device.mac"
      :mac="device.mac"
      :device-name="device.deviceName || undefined"
      :backups="device.backups"
      :sort-by="filters.sortBy === 'newest' || filters.sortBy === 'oldest' ? filters.sortBy : 'newest'"
      @download-config="handleDownloadConfig"
      @download-presets="handleDownloadPresets"
      @restore="handleRestore"
      @create-backup="handleCreateBackup"
    />

    <!-- No Results -->
    <div v-if="filteredDevices.length === 0 && !isLoading" class="text-center py-12">
      <svg class="mx-auto h-24 w-24 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z M10 7v3m0 0v3m0-3h3m-3 0H7" />
      </svg>
      <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-white">No backups found</h3>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        {{ hasActiveFilters ? 'Try adjusting your filters to see more results.' : 'No device backups have been created yet.' }}
      </p>
      <button
        v-if="hasActiveFilters"
        @click="$emit('clearFilters')"
        class="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
      >
        Clear filters
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BackupCard from './BackupCard.vue'
import type { BackupGroup } from '../types/backup'
import type { Device } from '../types/device'
import { parseBackupDate } from '../utils/dateUtils'

interface Props {
  backups: BackupGroup
  devices: Device[]
  filters: {
    searchQuery: string
    dateRange: string
    sortBy: string
  }
  isLoading: boolean
  getDeviceName: (mac: string) => string | undefined
}

const props = defineProps<Props>()

const emit = defineEmits<{
  downloadConfig: [backup: any]
  downloadPresets: [backup: any]
  restore: [backup: any]
  createBackup: [mac: string]
  clearFilters: []
}>()

const totalDevices = computed(() => Object.keys(props.backups).length)

const totalBackups = computed(() => {
  return Object.values(props.backups).reduce((total, backups) => total + backups.length, 0)
})

const hasActiveFilters = computed(() => {
  return props.filters.searchQuery !== '' || props.filters.dateRange !== 'all' || props.filters.sortBy !== 'newest'
})

// Convert backup group to array with device info
const devicesWithInfo = computed(() => {
  return Object.entries(props.backups).map(([mac, backups]) => {
    const device: { mac: string; deviceName: string | undefined; backups: any[] } = {
      mac,
      deviceName: props.getDeviceName(mac),
      backups
    }
    return device
  })
})

// Filter devices based on search and date range
const filteredDevices = computed(() => {
  let filtered = devicesWithInfo.value

  // Search filter
  if (props.filters.searchQuery) {
    const query = props.filters.searchQuery.toLowerCase()
    filtered = filtered.filter(device =>
      device.mac.toLowerCase().includes(query) ||
      (device.deviceName && device.deviceName.toLowerCase().includes(query))
    )
  }

  // Date range filter
  if (props.filters.dateRange !== 'all') {
    const now = new Date()
    const cutoffDate = getCutoffDate(props.filters.dateRange, now)

    filtered = filtered.filter(device => {
      return device.backups.some(backup => {
        const backupDate = parseBackupDate(backup.timestamp)
        return backupDate >= cutoffDate
      })
    })
  }

  // Sort devices
  filtered.sort((a, b) => {
    switch (props.filters.sortBy) {
      case 'device-asc':
        const aName = a.deviceName || a.mac
        const bName = b.deviceName || b.mac
        return aName.localeCompare(bName)
      case 'device-desc':
        const aNameDesc = a.deviceName || a.mac
        const bNameDesc = b.deviceName || b.mac
        return bNameDesc.localeCompare(aNameDesc)
      case 'mac-asc':
        return a.mac.localeCompare(b.mac)
      case 'mac-desc':
        return b.mac.localeCompare(a.mac)
      case 'oldest':
        // Sort by oldest backup date
        const aOldest = Math.min(...a.backups.map(b => parseBackupDate(b.timestamp).getTime()))
        const bOldest = Math.min(...b.backups.map(b => parseBackupDate(b.timestamp).getTime()))
        return aOldest - bOldest
      case 'newest':
      default:
        // Sort by newest backup date
        const aNewest = Math.max(...a.backups.map(b => parseBackupDate(b.timestamp).getTime()))
        const bNewest = Math.max(...b.backups.map(b => parseBackupDate(b.timestamp).getTime()))
        return bNewest - aNewest
    }
  })

  return filtered
})

const handleDownloadConfig = (backup: any) => {
  emit('downloadConfig', backup)
}

const handleDownloadPresets = (backup: any) => {
  emit('downloadPresets', backup)
}

const handleRestore = (backup: any) => {
  emit('restore', backup)
}

const handleCreateBackup = (mac: string) => {
  emit('createBackup', mac)
}

// Helper functions

const getCutoffDate = (range: string, now: Date) => {
  const cutoff = new Date(now)

  switch (range) {
    case 'today':
      cutoff.setHours(0, 0, 0, 0)
      break
    case 'week':
      cutoff.setDate(cutoff.getDate() - 7)
      break
    case 'month':
      cutoff.setMonth(cutoff.getMonth() - 1)
      break
    case '3months':
      cutoff.setMonth(cutoff.getMonth() - 3)
      break
    case '6months':
      cutoff.setMonth(cutoff.getMonth() - 6)
      break
    case 'year':
      cutoff.setFullYear(cutoff.getFullYear() - 1)
      break
    default:
      return new Date(0)
  }

  return cutoff
}
</script>