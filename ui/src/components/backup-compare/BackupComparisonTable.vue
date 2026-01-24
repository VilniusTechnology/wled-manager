<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    </div>

    <!-- Comparison Table -->
    <div v-else-if="backups.length >= 2" class="overflow-hidden">
      <!-- Table Header -->
      <div class="mb-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">Configuration Comparison</h3>
          <div class="flex items-center space-x-2">
            <label class="text-sm text-gray-600 dark:text-gray-400">Show:</label>
            <select
              v-model="filterType"
              class="text-sm border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md"
            >
              <option value="all">All Properties</option>
              <option value="different">Different Values Only</option>
              <option value="same">Same Values Only</option>
            </select>
          </div>
        </div>
        <div class="text-sm text-gray-500 dark:text-gray-400">
          Comparing {{ backups.length }} backup configurations
        </div>
      </div>

      <!-- Comparison Table -->
      <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-auto max-h-[75vh]">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <!-- Table Header -->
            <thead class="bg-gray-50 dark:bg-gray-800 sticky top-0 z-20">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider sticky left-0 top-0 bg-gray-50 dark:bg-gray-800 z-30 border-b border-gray-200 dark:border-gray-700">
                  Property Path
                </th>
                <th 
                  v-for="backup in backups" 
                  :key="`header-${backup.backupId}`"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider min-w-64 sticky top-0 bg-gray-50 dark:bg-gray-800 z-20 border-b border-gray-200 dark:border-gray-700"
                >
                  <div class="space-y-1">
                    <router-link 
                      v-if="backup.deviceId"
                      :to="{ name: 'Device Details', params: { deviceId: backup.deviceId } }"
                      target="_blank"
                      class="font-semibold text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      {{ backup.deviceName }}
                    </router-link>
                    <div v-else class="font-semibold text-gray-900 dark:text-white">
                      {{ backup.deviceName }}
                    </div>
                    <div class="text-xs">{{ formatDate(backup.timestamp) }}</div>
                    <div class="text-xs font-mono">{{ backup.mac }}</div>
                  </div>
                </th>
              </tr>
            </thead>
            
            <!-- Table Body -->
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr 
                v-for="(comparison, index) in filteredComparisons" 
                :key="`row-${index}`"
                :class="[
                  index % 2 === 0 ? 'bg-white dark:bg-gray-900' : 'bg-gray-50 dark:bg-gray-800',
                  comparison.isDifferent ? 'border-l-4 border-orange-400' : ''
                ]"
              >
                <!-- Property Path -->
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white sticky left-0 z-10"
                    :class="[
                      index % 2 === 0 ? 'bg-white dark:bg-gray-900' : 'bg-gray-50 dark:bg-gray-800'
                    ]"
                >
                  <div class="flex items-center space-x-2">
                    <span 
                      class="font-semibold cursor-help border-b border-dotted border-gray-400"
                      @mouseenter="showTooltip($event, comparison.path)"
                      @mousemove="updateTooltipPosition"
                      @mouseleave="hideTooltip"
                    >
                      {{ getLabel(comparison.path) }}
                    </span>
                    <FileJson 
                      class="w-4 h-4 text-gray-400 hover:text-blue-500 cursor-help transition-colors"
                      @mouseenter="showTooltip($event, comparison.path)"
                      @mousemove="updateTooltipPosition"
                      @mouseleave="hideTooltip"
                    />
                    <span v-if="comparison.isDifferent" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">
                      Different
                    </span>
                  </div>
                </td>
                
                <!-- Configuration Values -->
                <td 
                  v-for="(backup, backupIndex) in backups" 
                  :key="`value-${backup.backupId}-${backupIndex}`"
                  class="px-6 py-4 text-sm text-gray-900 dark:text-white"
                >
                  <div class="max-w-xs">
                    <div v-if="comparison.values[backupIndex] !== undefined" class="space-y-1">
                      <!-- Value Display -->
                      <div 
                        :class="[
                          'font-mono text-xs p-2 rounded',
                          comparison.isDifferent && comparison.values[backupIndex] !== comparison.values[0] 
                            ? 'bg-red-50 border border-red-200 text-red-900 dark:bg-red-900/20 dark:border-red-800 dark:text-red-100'
                            : 'bg-gray-50 border border-gray-200 dark:bg-gray-800 dark:border-gray-600'
                        ]"
                      >
                        {{ formatValue(comparison.values[backupIndex]) }}
                      </div>
                      
                      <!-- Type Display -->
                      <div class="text-xs text-gray-500 dark:text-gray-400">
                        {{ getValueType(comparison.values[backupIndex]) }}
                      </div>
                    </div>
                    <div v-else class="text-gray-400 dark:text-gray-500 italic text-xs">
                      undefined
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
      </div>

      <!-- Statistics -->
      <div class="mt-6 grid grid-cols-3 gap-4">
        <div 
          @click="filterType = 'all'"
          :class="[
            'rounded-lg p-4 cursor-pointer transition-all duration-200',
            filterType === 'all' 
              ? 'bg-blue-100 dark:bg-blue-900/40 border-2 border-blue-400 dark:border-blue-600 ring-2 ring-blue-400/50' 
              : 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 hover:bg-blue-100 dark:hover:bg-blue-900/30'
          ]"
        >
          <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ comparisons.length }}</div>
          <div class="text-sm text-blue-600 dark:text-blue-400">Total Properties</div>
        </div>
        <div 
          @click="filterType = 'same'"
          :class="[
            'rounded-lg p-4 cursor-pointer transition-all duration-200',
            filterType === 'same' 
              ? 'bg-green-100 dark:bg-green-900/40 border-2 border-green-400 dark:border-green-600 ring-2 ring-green-400/50' 
              : 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 hover:bg-green-100 dark:hover:bg-green-900/30'
          ]"
        >
          <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ sameValuesCount }}</div>
          <div class="text-sm text-green-600 dark:text-green-400">Same Values</div>
        </div>
        <div 
          @click="filterType = 'different'"
          :class="[
            'rounded-lg p-4 cursor-pointer transition-all duration-200',
            filterType === 'different' 
              ? 'bg-orange-100 dark:bg-orange-900/40 border-2 border-orange-400 dark:border-orange-600 ring-2 ring-orange-400/50' 
              : 'bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 hover:bg-orange-100 dark:hover:bg-orange-900/30'
          ]"
        >
          <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ differentValuesCount }}</div>
          <div class="text-sm text-orange-600 dark:text-orange-400">Different Values</div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-white">No backups to compare</h3>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        Select at least 2 backup configurations to see the comparison table.
      </p>
    </div>
    <!-- Custom Fixed Tooltip -->
    <div 
      v-if="tooltip.visible"
      class="fixed z-[9999] px-2 py-1 text-xs font-mono text-white bg-gray-900 rounded shadow-lg pointer-events-none transform -translate-y-full -translate-x-1/2 mt-[-8px]"
      :style="{ top: `${tooltip.y}px`, left: `${tooltip.x}px` }"
    >
      {{ tooltip.text }}
      <div class="absolute bottom-[-4px] left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-[4px] border-l-transparent border-r-[4px] border-r-transparent border-t-[4px] border-t-gray-900"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { FileJson } from 'lucide-vue-next'
import { formatDateTime } from '../../utils/dateUtils'
import type { SelectedBackup, BackupComparison } from '../../types/backupCompare'
import { useConfigLabels } from '../../composables/useConfigLabels'

const props = defineProps<{
  backups: SelectedBackup[]
  isLoading?: boolean
}>()



const { getLabel } = useConfigLabels()

// Custom Tooltip State
const tooltip = ref({
  visible: false,
  text: '',
  x: 0,
  y: 0
})

const showTooltip = (e: MouseEvent, text: string) => {
  tooltip.value = {
    visible: true,
    text,
    x: e.clientX,
    y: e.clientY
  }
}

const hideTooltip = () => {
  tooltip.value.visible = false
}

const updateTooltipPosition = (e: MouseEvent) => {
  if (!tooltip.value.visible) return
  tooltip.value.x = e.clientX
  tooltip.value.y = e.clientY
}

const filterType = ref<'all' | 'different' | 'same'>('all')

// Computed properties
const comparisons = computed<BackupComparison[]>(() => {
  if (props.backups.length < 2) return []

  const allPaths = new Set<string>()
  
  // Collect all possible paths from all configs
  props.backups.forEach(backup => {
    const paths = getAllPaths(backup.config)
    paths.forEach(path => allPaths.add(path))
  })

  // Create comparisons for each path
  const result: BackupComparison[] = []
  
  allPaths.forEach(path => {
    const values = props.backups.map(backup => getValueAtPath(backup.config, path))
    const isDifferent = !values.every(value => JSON.stringify(value) === JSON.stringify(values[0]))
    
    result.push({
      path,
      values,
      isDifferent
    })
  })

  // Sort by path name
  return result.sort((a, b) => a.path.localeCompare(b.path))
})

const filteredComparisons = computed(() => {
  switch (filterType.value) {
    case 'different':
      return comparisons.value.filter(comp => comp.isDifferent)
    case 'same':
      return comparisons.value.filter(comp => !comp.isDifferent)
    default:
      return comparisons.value
  }
})

const sameValuesCount = computed(() => {
  return comparisons.value.filter(comp => !comp.isDifferent).length
})

const differentValuesCount = computed(() => {
  return comparisons.value.filter(comp => comp.isDifferent).length
})

// Helper functions
const getAllPaths = (obj: any, prefix = ''): string[] => {
  const paths: string[] = []
  
  if (obj === null || obj === undefined || typeof obj !== 'object') {
    return [prefix]
  }
  
  if (Array.isArray(obj)) {
    if (obj.length === 0) {
      return [prefix]
    }
    obj.forEach((item, index) => {
      const newPath = prefix ? `${prefix}[${index}]` : `[${index}]`
      paths.push(...getAllPaths(item, newPath))
    })
  } else {
    const keys = Object.keys(obj)
    if (keys.length === 0) {
      return [prefix]
    }
    keys.forEach(key => {
      const newPath = prefix ? `${prefix}.${key}` : key
      paths.push(...getAllPaths(obj[key], newPath))
    })
  }
  
  return paths
}

const getValueAtPath = (obj: any, path: string): any => {
  if (!path) return obj
  
  try {
    const parts = path.split(/\.|\[|\]/).filter(part => part !== '')
    let current = obj
    
    for (const part of parts) {
      if (current === null || current === undefined) {
        return undefined
      }
      
      if (Array.isArray(current)) {
        const index = parseInt(part)
        if (isNaN(index) || index < 0 || index >= current.length) {
          return undefined
        }
        current = current[index]
      } else if (typeof current === 'object') {
        current = current[part]
      } else {
        return undefined
      }
    }
    
    return current
  } catch (error) {
    console.error('Error getting value at path:', path, error)
    return undefined
  }
}

const formatValue = (value: any): string => {
  if (value === null) return 'null'
  if (value === undefined) return 'undefined'
  if (typeof value === 'string') return `"${value}"`
  if (typeof value === 'boolean') return value.toString()
  if (typeof value === 'number') return value.toString()
  if (Array.isArray(value)) return `[${value.length} items]`
  if (typeof value === 'object') return `{${Object.keys(value).length} keys}`
  return String(value)
}

const getValueType = (value: any): string => {
  if (value === null) return 'null'
  if (value === undefined) return 'undefined'
  if (Array.isArray(value)) return `array[${value.length}]`
  if (typeof value === 'object') return `object{${Object.keys(value).length}}`
  return typeof value
}

const formatDate = (timestamp: string): string => {
  try {
    return formatDateTime(timestamp, 'EU_NRML')
  } catch (error) {
    console.warn('Failed to format backup date:', timestamp, error)
    return timestamp
  }
}
</script>