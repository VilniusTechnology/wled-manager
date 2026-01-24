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
        <label class="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          <input
            v-model="filters.hasBackups"
            type="checkbox"
            class="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
          />
          Has Backups
        </label>
      </div>

      <!-- State On Filter -->
      <div class="flex items-center gap-2">
        <label class="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          <input
            v-model="filters.stateOn"
            type="checkbox"
            class="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
          />
          State On
        </label>
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
        <label class="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          <input
            v-model="filters.wifiSleep"
            type="checkbox"
            :true-value="true"
            :false-value="null"
            class="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
          />
          WiFi Sleep
        </label>
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

const filters = reactive<DeviceFilters>({
  status: '',
  search: '',
  hasBackups: false,
  stateOn: false,
  adopted: null,
  hasStaticIp: null,
  wifiSleep: null
})

const emit = defineEmits<{
  filtersChanged: [filters: DeviceFilters]
}>()

const clearFilters = () => {
  filters.status = ''
  filters.search = ''
  filters.hasBackups = false
  filters.stateOn = false
  filters.adopted = null
  filters.hasStaticIp = null
  filters.wifiSleep = null
  // The watch will automatically emit the changes
}

// Watch for filter changes and emit them
watch(filters, (newFilters) => {
  emit('filtersChanged', { ...newFilters })
}, { deep: true, immediate: true })

// Expose filters for parent component access
defineExpose({
  filters,
  clearFilters
})
</script>