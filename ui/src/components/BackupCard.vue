<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="flex-shrink-0">
            <svg class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ deviceName || `Device ${mac.slice(-4)}` }}
            </h2>
            <div class="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
              <span v-if="deviceName" class="font-medium">MAC:</span>
              <code class="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs font-mono">
                {{ formatMacAddress(mac) }}
              </code>
            </div>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="$emit('createBackup', mac)"
            class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Create Backup
          </button>
          
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="getStatusBadgeClass()">
            {{ getStatusText() }}
          </span>
        </div>
      </div>
    </div>

    <div class="divide-y divide-gray-200 dark:divide-gray-700">
      <BackupItem
        v-for="backup in sortedBackups"
        :key="backup.id"
        :backup="backup"
        @download-config="$emit('downloadConfig', backup)"
        @download-presets="$emit('downloadPresets', backup)"
        @restore="$emit('restore', backup)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BackupItem from './BackupItem.vue'
import { parseBackupDate } from '../utils/dateUtils'
import type { Backup } from '../types/backup'

interface Props {
  mac: string
  deviceName?: string
  backups: Backup[]
  sortBy: 'newest' | 'oldest'
}

const props = defineProps<Props>()

defineEmits<{
  downloadConfig: [backup: Backup]
  downloadPresets: [backup: Backup]
  restore: [backup: Backup]
  createBackup: [mac: string]
}>()

const sortedBackups = computed(() => {
  return [...props.backups].sort((a, b) => {
    const dateA = parseBackupDate(a.timestamp)
    const dateB = parseBackupDate(b.timestamp)

    if (props.sortBy === 'newest') {
      return dateB.getTime() - dateA.getTime()
    } else {
      return dateA.getTime() - dateB.getTime()
    }
  })
})

const getStatusBadgeClass = () => {
  const latestBackup = sortedBackups.value[0]
  if (!latestBackup) return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'

  const backupDate = parseBackupDate(latestBackup.timestamp)
  const now = new Date()
  const daysDiff = Math.floor((now.getTime() - backupDate.getTime()) / (1000 * 60 * 60 * 24))

  if (daysDiff <= 1) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
  if (daysDiff <= 7) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
  return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
}

const getStatusText = () => {
  const latestBackup = sortedBackups.value[0]
  if (!latestBackup) return 'No backups'

  const backupDate = parseBackupDate(latestBackup.timestamp)
  const now = new Date()
  const daysDiff = Math.floor((now.getTime() - backupDate.getTime()) / (1000 * 60 * 60 * 24))

  if (daysDiff <= 1) return 'Recent'
  if (daysDiff <= 7) return 'This week'
  if (daysDiff <= 30) return 'This month'
  return 'Outdated'
}

const formatMacAddress = (mac: string): string => {
  if (!mac) return ''
  // Remove any existing colons or dashes
  const cleanMac = mac.replace(/[:\-]/g, '')
  // Add colons every 2 characters
  return cleanMac.match(/.{1,2}/g)?.join(':').toUpperCase() || mac.toUpperCase()
}
</script>