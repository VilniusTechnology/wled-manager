<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 mb-4">
    <div class="flex flex-wrap items-center gap-4">
      <!-- Status Filter -->
      <div class="flex items-center gap-2">
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Status:</label>
        <select
          v-model="filters.status"
          class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Statuses</option>
          <option value="online">Online</option>
          <option value="offline">Offline</option>
          <option value="dead">Dead</option>
          <option value="very_slow">Very Slow</option>
          <option value="slow">Slow</option>
          <option value="good">Good</option>
          <option value="excellent">Excellent</option>
        </select>
      </div>

      <!-- Search Filter -->
      <div class="flex items-center gap-2">
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Search:</label>
        <input
          v-model="filters.search"
          type="text"
          placeholder="Search by name or IP..."
          class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
        />
      </div>

      <!-- Has Backups Filter -->
      <div class="flex items-center gap-2">
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Backups:</label>
        <select
          v-model="filters.hasBackups"
          class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option :value="null">All</option>
          <option :value="true">Has Backups</option>
          <option :value="false">No Backups</option>
        </select>
      </div>

      <!-- State On Filter -->
      <div class="flex items-center gap-2">
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300">State:</label>
        <select
          v-model="filters.stateOn"
          class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option :value="null">All States</option>
          <option :value="true">State On</option>
          <option :value="false">State Off</option>
        </select>
      </div>

      <!-- Adopted Filter -->
      <div class="flex items-center gap-2">
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Adopted:</label>
        <select
          v-model="filters.adopted"
          class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option :value="null">All Devices</option>
          <option :value="true">Adopted Only</option>
          <option :value="false">Unadopted Only</option>
        </select>
      </div>

      <!-- Static IP Filter -->
      <div class="flex items-center gap-2">
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300">IP Config:</label>
        <select
          v-model="filters.hasStaticIp"
          class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option :value="null">All Configs</option>
          <option :value="true">Static IP</option>
          <option :value="false">DHCP Only</option>
        </select>
      </div>

      <!-- WiFi Sleep Filter -->
      <div class="flex items-center gap-2">
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300">WiFi Sleep:</label>
        <select
          v-model="filters.wifiSleep"
          class="block w-32 pl-3 pr-10 py-1.5 text-base border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option :value="null">All</option>
          <option :value="true">Sleep Enabled</option>
          <option :value="false">Sleep Disabled</option>
        </select>
      </div>

      <!-- Clear Filters Button -->
      <button
        @click="clearFilters"
        class="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
      >
        Clear Filters
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import type { DeviceFilters } from '../../types/deviceFilters'

const savedFiltersStr = sessionStorage.getItem('deviceFilters')
let initialFilters: Partial<DeviceFilters> = {}
if (savedFiltersStr) {
  try {
    initialFilters = JSON.parse(savedFiltersStr)
  } catch (e) {
    console.error('Failed to parse saved device filters', e)
  }
}

const filters = reactive<DeviceFilters>({
  status: initialFilters.status ?? '',
  search: initialFilters.search ?? '',
  hasBackups: initialFilters.hasBackups ?? null,
  stateOn: initialFilters.stateOn ?? null,
  adopted: initialFilters.adopted !== undefined ? initialFilters.adopted : null,
  hasStaticIp: initialFilters.hasStaticIp !== undefined ? initialFilters.hasStaticIp : null,
  wifiSleep: initialFilters.wifiSleep !== undefined ? initialFilters.wifiSleep : null
})

const emit = defineEmits<{
  filtersChanged: [filters: DeviceFilters]
}>()

const clearFilters = () => {
  filters.status = ''
  filters.search = ''
  filters.hasBackups = null
  filters.stateOn = null
  filters.adopted = null
  filters.hasStaticIp = null
  filters.wifiSleep = null
  // The watch will automatically emit the changes
}

// Watch for filter changes, save to sessionStorage and emit them
watch(filters, (newFilters) => {
  sessionStorage.setItem('deviceFilters', JSON.stringify(newFilters))
  emit('filtersChanged', { ...newFilters })
}, { deep: true, immediate: true })

// Expose filters for parent component access
defineExpose({
  filters,
  clearFilters
})
</script>