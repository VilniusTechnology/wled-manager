<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
    <div class="flex flex-col lg:flex-row lg:items-end lg:justify-between space-y-4 lg:space-y-0 lg:space-x-4">
      <!-- Search Filter -->
      <div class="flex-1 max-w-md">
        <label for="search" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Search Devices
        </label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            id="search"
            v-model="searchQuery"
            type="text"
            placeholder="Search by device name or MAC..."
            class="block w-full pl-14 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            style="padding-left: 2.75rem"
            @input="updateFilters"
          />
        </div>
      </div>

      <!-- Date Range Filter -->
      <div class="flex-1 max-w-md">
        <label for="dateRange" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Date Range
        </label>
        <select
          id="dateRange"
          v-model="dateRange"
          class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          @change="updateFilters"
        >
          <option value="all">All time</option>
          <option value="today">Today</option>
          <option value="week">This week</option>
          <option value="month">This month</option>
          <option value="3months">Last 3 months</option>
          <option value="6months">Last 6 months</option>
          <option value="year">This year</option>
        </select>
      </div>

      <!-- Sort Options -->
      <div class="flex-1 max-w-md">
        <label for="sortBy" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Sort By
        </label>
        <select
          id="sortBy"
          v-model="sortBy"
          class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          @change="updateFilters"
        >
          <option value="newest">Newest first</option>
          <option value="oldest">Oldest first</option>
          <option value="device-asc">Device name A-Z</option>
          <option value="device-desc">Device name Z-A</option>
          <option value="mac-asc">MAC address A-Z</option>
          <option value="mac-desc">MAC address Z-A</option>
        </select>
      </div>

      <!-- Clear Filters -->
      <div class="flex items-end">
        <button
          @click="clearFilters"
          class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          Clear
        </button>
      </div>
    </div>

    <!-- Active Filters Summary -->
    <div v-if="hasActiveFilters" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
          <span>Active filters:</span>
          <span v-if="searchQuery" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
            Search: "{{ searchQuery }}"
          </span>
          <span v-if="dateRange !== 'all'" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
            Date: {{ getDateRangeLabel() }}
          </span>
          <span v-if="sortBy !== 'newest'" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300">
            Sort: {{ getSortLabel() }}
          </span>
        </div>
        <button
          @click="clearFilters"
          class="text-sm text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
        >
          Clear all
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  modelValue: {
    searchQuery: string
    dateRange: string
    sortBy: string
  }
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: { searchQuery: string; dateRange: string; sortBy: string }]
}>()

const searchQuery = ref(props.modelValue.searchQuery)
const dateRange = ref(props.modelValue.dateRange)
const sortBy = ref(props.modelValue.sortBy)

const hasActiveFilters = computed(() => {
  return searchQuery.value !== '' || dateRange.value !== 'all' || sortBy.value !== 'newest'
})

const updateFilters = () => {
  emit('update:modelValue', {
    searchQuery: searchQuery.value,
    dateRange: dateRange.value,
    sortBy: sortBy.value
  })
}

const clearFilters = () => {
  searchQuery.value = ''
  dateRange.value = 'all'
  sortBy.value = 'newest'
  updateFilters()
}

const getDateRangeLabel = () => {
  const labels: { [key: string]: string } = {
    today: 'Today',
    week: 'This week',
    month: 'This month',
    '3months': 'Last 3 months',
    '6months': 'Last 6 months',
    year: 'This year'
  }
  return labels[dateRange.value] || dateRange.value
}

const getSortLabel = () => {
  const labels: { [key: string]: string } = {
    newest: 'Newest first',
    oldest: 'Oldest first',
    'device-asc': 'Device name A-Z',
    'device-desc': 'Device name Z-A',
    'mac-asc': 'MAC address A-Z',
    'mac-desc': 'MAC address Z-A'
  }
  return labels[sortBy.value] || sortBy.value
}

// Watch for external changes to props
watch(() => props.modelValue, (newValue) => {
  searchQuery.value = newValue.searchQuery
  dateRange.value = newValue.dateRange
  sortBy.value = newValue.sortBy
}, { deep: true })
</script>