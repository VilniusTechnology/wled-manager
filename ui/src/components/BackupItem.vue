<template>
  <div class="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div class="flex-1 w-full sm:w-auto">
        <div class="flex items-start sm:items-center space-x-4">
          <div class="flex-shrink-0 mt-1 sm:mt-0">
            <svg class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 dark:text-white">
              Backup from {{ formatDate(backup.timestamp) }}
            </p>
            <p class="text-sm text-gray-600 dark:text-gray-400 break-all">
              ID: {{ backup.id }}
            </p>
            <div class="mt-2 flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
              <span>Created: {{ formatDateTime(backup.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row sm:items-center gap-3 w-full sm:w-auto">
        <!-- Config File -->
        <div class="text-sm text-gray-600 dark:text-gray-400">
          <span class="font-medium">Config:</span>
          <code class="ml-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs break-all inline-block max-w-[200px] sm:max-w-[150px] align-middle truncate">
            {{ getFileName(backup.cfg_path) }}
          </code>
          <span v-if="backup.cfg_size" class="text-xs text-gray-500 dark:text-gray-500 ml-2">
            ({{ formatFileSize(backup.cfg_size) }})
          </span>
        </div>

        <!-- Presets File -->
        <div class="text-sm text-gray-600 dark:text-gray-400">
          <span class="font-medium">Presets:</span>
          <code class="ml-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs break-all inline-block max-w-[200px] sm:max-w-[150px] align-middle truncate">
            {{ getFileName(backup.presets_path) }}
          </code>
          <span v-if="backup.presets_size" class="text-xs text-gray-500 dark:text-gray-500 ml-2">
            ({{ formatFileSize(backup.presets_size) }})
          </span>
        </div>

        <!-- Actions -->
        <div class="flex space-x-2 mt-2 sm:mt-0">
          <button
            @click="$emit('downloadConfig')"
            class="inline-flex items-center px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            title="Download Config File"
          >
            <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Config
          </button>

          <button
            @click="$emit('downloadPresets')"
            class="inline-flex items-center px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            title="Download Presets File"
          >
            <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Presets
          </button>

          <button
            @click="$emit('restore')"
            class="inline-flex items-center px-3 py-1 border border-red-300 dark:border-red-800 rounded-md text-sm font-medium text-red-700 dark:text-red-400 bg-white dark:bg-gray-800 hover:bg-red-50 dark:hover:bg-red-900/20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
            title="Restore Backup to Device"
          >
            <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Restore
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Backup } from '../types/backup'
import { formatDate, formatDateTime } from '../utils/dateUtils'

interface Props {
  backup: Backup
}

defineProps<Props>()

defineEmits<{
  downloadConfig: []
  downloadPresets: []
  restore: []
}>()

const getFileName = (filePath: string) => {
  return filePath.split('/').pop() || filePath
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>