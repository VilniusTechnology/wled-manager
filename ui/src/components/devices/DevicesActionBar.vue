<template>
  <div class="flex flex-wrap justify-end items-center mb-6 gap-4">
    <div class="flex flex-wrap items-center gap-3 justify-end">
      <button
        @click="$emit('add-device')"
        class="px-3 py-1.5 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 flex items-center gap-2 hover:bg-gray-50 dark:hover:bg-gray-700"
        title="Manually add a WLED device"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600 dark:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>Add Device</span>
      </button>

      <div class="flex">
        <button
          @click="$emit('set-view-mode', 'list')"
          class="px-3 py-1.5 rounded-l border border-gray-300 dark:border-gray-600"
          :class="viewMode === 'list' ? 'bg-gray-200 dark:bg-gray-700' : 'bg-white dark:bg-gray-800'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
        </button>
        <button
          @click="$emit('set-view-mode', 'grid')"
          class="px-3 py-1.5 rounded-r border-t border-r border-b border-gray-300 dark:border-gray-600"
          :class="viewMode === 'grid' ? 'bg-gray-200 dark:bg-gray-700' : 'bg-white dark:bg-gray-800'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
        </button>
      </div>

      <button
        @click="$emit('refresh-devices')"
        :disabled="isLoading || scanInProgress"
        class="action-button px-3 py-1.5 rounded border border-gray-300 dark:border-gray-600 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed bg-white dark:bg-gray-800"
      >
        <LoadingSpinner v-if="isLoading" class="w-4 h-4" />
        <RefreshIcon v-if="!isLoading" class="w-5 h-5" />
        <span>{{ isLoading ? 'Refreshing...' : 'Refresh' }}</span>
      </button>

      <button
        @click="$emit('scan-network')"
        :disabled="isLoading || scanInProgress"
        class="action-button px-3 py-1.5 rounded border border-gray-300 dark:border-gray-600 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed bg-primary text-white"
      >
        <LoadingSpinner v-if="scanInProgress" class="w-4 h-4" />
        <SearchIcon v-if="!scanInProgress" class="w-5 h-5" />
        <span v-if="scanInProgress" class="flex items-center">
          Scanning<LoadingDots />
        </span>
        <span v-else>Scan Network</span>
      </button>

      <button
        v-if="selectedCount > 0"
        @click="$emit('mass-ota-update')"
        class="px-3 py-1.5 rounded border border-orange-300 dark:border-orange-600 bg-orange-600 text-white flex items-center gap-2 hover:bg-orange-700"
        title="Update selected devices with new firmware"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <span>Mass OTA ({{ selectedCount }})</span>
      </button>

      <div
        v-else
        class="px-3 py-1.5 rounded border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 flex items-center gap-2 cursor-not-allowed"
        title="Switch to list view and select devices to enable mass OTA"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <span>Mass OTA</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import LoadingSpinner from '../shared/LoadingSpinner.vue'
import LoadingDots from '../shared/LoadingDots.vue'
import SearchIcon from '../shared/SearchIcon.vue'
import RefreshIcon from '../shared/RefreshIcon.vue'

interface Props {
  viewMode: string
  isLoading: boolean
  scanInProgress: boolean
  selectedCount: number
}

defineProps<Props>()

defineEmits<{
  'set-view-mode': [mode: string]
  'refresh-devices': []
  'scan-network': []
  'mass-ota-update': []
  'add-device': []
}>()
</script>

<style scoped>
.action-button {
  min-width: 140px;
  justify-content: center;
}

/* Ensure consistent button width during state changes */
.action-button span {
  min-width: 80px;
  text-align: center;
}
</style>