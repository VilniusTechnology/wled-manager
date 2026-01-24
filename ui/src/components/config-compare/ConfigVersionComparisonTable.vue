<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="isLoading || isLoadingConfigs" class="text-center p-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Loading configuration comparison...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="loadError" class="text-center p-8">
      <div class="text-red-600 dark:text-red-400">
        <svg class="mx-auto h-12 w-12 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="text-lg font-medium">Error loading configurations</h3>
        <p class="mt-2 text-sm">{{ loadError }}</p>
      </div>
    </div>

    <!-- Comparison Results -->
    <div v-else-if="comparisonData.length > 0">
      <!-- Header with Filter -->
      <div class="mb-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">Configuration Comparison</h3>
          <div class="flex items-center space-x-2">
            <label class="text-sm text-gray-600 dark:text-gray-400">Show:</label>
            <select
              v-model="currentFilter.type"
              class="text-sm border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md"
            >
              <option value="all">All Properties</option>
              <option value="different">Different Values Only</option>
              <option value="same">Same Values Only</option>
            </select>
          </div>
        </div>
        <div class="text-sm text-gray-500 dark:text-gray-400">
           Comparing {{ versions.length }} configuration versions
        </div>
      </div>

      <!-- Comparison Table -->
      <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-auto max-h-[75vh]">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <!-- Table Header -->
            <thead class="bg-gray-50 dark:bg-gray-800 sticky top-0 z-20">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider sticky left-0 top-0 bg-gray-50 dark:bg-gray-800 z-30 border-b border-gray-200 dark:border-gray-700">
                  Configuration Path
                </th>
                <th
                  v-for="version in versions"
                  :key="version.version_id"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider min-w-64 sticky top-0 bg-gray-50 dark:bg-gray-800 z-20 border-b border-gray-200 dark:border-gray-700"
                >
                  <div class="space-y-1">
                    <router-link 
                      v-if="version.device_id"
                      :to="{ name: 'Device Details', params: { deviceId: version.device_id } }"
                      target="_blank"
                      class="font-semibold text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      {{ version.device_name }}
                    </router-link>
                    <div v-else class="font-semibold text-gray-900 dark:text-white">
                      {{ version.device_name }}
                    </div>
                    <div class="text-xs">{{ formatTimestamp(version.timestamp) }}</div>
                  </div>
                </th>
              </tr>
            </thead>
            <!-- Table Body -->
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="(comparison, index) in filteredComparisons"
                :key="comparison.path"
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

                <!-- Values for each version -->
                <td
                  v-for="(value, index) in comparison.values"
                  :key="index"
                  class="px-6 py-4 text-sm text-gray-900 dark:text-white"
                >
                  <div class="max-w-xs">
                    <div class="space-y-1">
                       <!-- Value Display -->
                       <div 
                        :class="[
                          'font-mono text-xs p-2 rounded',
                          comparison.isDifferent && comparison.values[index] !== comparison.values[0] 
                            ? 'bg-red-50 border border-red-200 text-red-900 dark:bg-red-900/20 dark:border-red-800 dark:text-red-100'
                            : 'bg-gray-100 border border-gray-200 dark:bg-gray-800 dark:border-gray-600'
                        ]"
                      >
                         <template v-if="typeof value === 'object' && value !== null">
                            <details class="cursor-pointer">
                                <summary class="text-xs text-blue-600 dark:text-blue-400 hover:underline focus:outline-none">
                                    {{ getObjectSummary(value) }}
                                </summary>
                                <pre class="mt-2 text-xs overflow-x-auto whitespace-pre-wrap">{{ JSON.stringify(value, null, 2) }}</pre>
                            </details>
                         </template>
                         <template v-else>
                            {{ formatValue(value) }}
                         </template>
                      </div>
                      
                      <!-- Type Display -->
                      <div class="text-xs text-gray-500 dark:text-gray-400">
                        {{ value === null ? 'null' : typeof value }}
                      </div>
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
          @click="currentFilter.type = 'all'"
          :class="[
            'rounded-lg p-4 cursor-pointer transition-all duration-200',
            currentFilter.type === 'all' 
              ? 'bg-blue-100 dark:bg-blue-900/40 border-2 border-blue-400 dark:border-blue-600 ring-2 ring-blue-400/50' 
              : 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 hover:bg-blue-100 dark:hover:bg-blue-900/30'
          ]"
        >
          <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ stats.total }}</div>
          <div class="text-sm text-blue-600 dark:text-blue-400">Total Properties</div>
        </div>
        <div 
          @click="currentFilter.type = 'same'"
          :class="[
            'rounded-lg p-4 cursor-pointer transition-all duration-200',
            currentFilter.type === 'same' 
              ? 'bg-green-100 dark:bg-green-900/40 border-2 border-green-400 dark:border-green-600 ring-2 ring-green-400/50' 
              : 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 hover:bg-green-100 dark:hover:bg-green-900/30'
          ]"
        >
          <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ stats.same }}</div>
          <div class="text-sm text-green-600 dark:text-green-400">Same Values</div>
        </div>
        <div 
          @click="currentFilter.type = 'different'"
          :class="[
            'rounded-lg p-4 cursor-pointer transition-all duration-200',
            currentFilter.type === 'different' 
              ? 'bg-orange-100 dark:bg-orange-900/40 border-2 border-orange-400 dark:border-orange-600 ring-2 ring-orange-400/50' 
              : 'bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 hover:bg-orange-100 dark:hover:bg-orange-900/30'
          ]"
        >
          <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ stats.different }}</div>
          <div class="text-sm text-orange-600 dark:text-orange-400">Different Values</div>
        </div>
      </div>
      
      <!-- No results message -->
      <div v-if="filteredComparisons.length === 0" class="text-center p-8 text-gray-600 dark:text-gray-400">
        No {{ currentFilter.type === 'all' ? '' : currentFilter.type }} properties found.
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center p-8 text-gray-600 dark:text-gray-400">
      <p>No configuration data to compare.</p>
      <div v-if="debugInfo" class="mt-4 text-left bg-gray-100 dark:bg-gray-800 p-2 rounded text-xs font-mono overflow-auto max-h-64">
        <p class="font-bold mb-1">Debug Info:</p>
        <pre>{{ debugInfo }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { FileJson } from 'lucide-vue-next'
import type { SelectedConfigVersion, ConfigComparison, ConfigCompareFilter, ConfigCompareStats } from '../../types/configCompare'
import { useConfigLabels } from '../../composables/useConfigLabels'
import { formatDateTime } from '../../utils/dateUtils'

const props = defineProps<{
  versions: SelectedConfigVersion[]
  isLoading?: boolean
}>()

const { getLabel } = useConfigLabels()

const comparisonData = ref<ConfigComparison[]>([])
const currentFilter = ref<ConfigCompareFilter>({ type: 'all' })
const loadError = ref<string | null>(null)
const isLoadingConfigs = ref(false)
const debugInfo = ref<string>('')

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

// Computed properties
const filteredComparisons = computed(() => {
  if (currentFilter.value.type === 'all') {
    return comparisonData.value
  }
  return comparisonData.value.filter(comparison => 
    currentFilter.value.type === 'different' ? comparison.isDifferent : !comparison.isDifferent
  )
})

const stats = computed((): ConfigCompareStats => {
  const total = comparisonData.value.length
  const different = comparisonData.value.filter(c => c.isDifferent).length
  const same = total - different
  
  return { total, same, different }
})



const loadAndCompareConfigs = async () => {
  try {
    isLoadingConfigs.value = true
    loadError.value = null
    
    // Load configurations for each version
    const versionsWithConfigs = await Promise.all(
      props.versions.map(async (version) => {
        const response = await fetch(`/api/config-versions/${version.version_id}/config`)
        if (!response.ok) throw new Error(`Failed to load config for version ${version.version_id}`)
        
        const data = await response.json()
        console.log(`Loaded config for ${version.version_id}:`, data.config ? 'Found config object' : 'No config object', data)
        
        let config = data.config || {}
        // Ensure config is an object
        if (typeof config === 'string') {
          try {
             config = JSON.parse(config)
          } catch (e) {
             console.error("Failed to parse config string", e)
             config = {}
          }
        }

        return {
          ...version,
          config // Unwrap the actual config content
        }
      })
    )
    
    // Generate comparison data
    comparisonData.value = generateComparisons(versionsWithConfigs)
    console.log('Comparison data generated:', comparisonData.value.length, 'entries')

    if (comparisonData.value.length === 0) {
      debugInfo.value = JSON.stringify(versionsWithConfigs.map(v => ({ 
        id: v.version_id, 
        configType: typeof v.config, 
        configKeys: v.config ? Object.keys(v.config) : [],
        raw: v.config
      })), null, 2)
    }
    
  } catch (error) {
    console.error('Error loading configurations:', error)
    loadError.value = error instanceof Error ? error.message : 'Unknown error occurred'
  } finally {
    isLoadingConfigs.value = false
  }
}

const generateComparisons = (versionsWithConfigs: SelectedConfigVersion[]): ConfigComparison[] => {
  const allPaths = new Set<string>()
  
  // Collect all possible paths from all configurations
  versionsWithConfigs.forEach(version => {
    if (version.config) {
      collectPaths(version.config, '', allPaths)
    }
  })
  
  // Generate comparison for each path
  // Generate comparison for each path
  const comparisons = Array.from(allPaths).map(path => {
    const values = versionsWithConfigs.map(version => 
      getValueByPath(version.config, path)
    )
    
    const isDifferent = !values.every(value => 
      JSON.stringify(value) === JSON.stringify(values[0])
    )
    
    return {
      path,
      values,
      isDifferent
    }
  })

  return comparisons.filter(c => !isContainerRow(c.values)).sort((a, b) => {
    // Sort by difference status, then by path
    if (a.isDifferent && !b.isDifferent) return -1
    if (!a.isDifferent && b.isDifferent) return 1
    return a.path.localeCompare(b.path)
  })
}

const isContainerRow = (values: any[]): boolean => {
  // Filter out null/undefined values to check actual content
  const presentValues = values.filter(v => v !== null && v !== undefined)
  
  // If all are null/undefined, keep it (edge case, likely won't happen due to path collection logic)
  if (presentValues.length === 0) return false
  
  // Check if we have any primitive values (string, number, boolean)
  const hasPrimitive = presentValues.some(v => typeof v !== 'object')
  if (hasPrimitive) return false // Mixed types or all primitives -> SHOW
  
  // Check if we have any empty objects/arrays
  const hasEmptyObject = presentValues.some(v => Object.keys(v).length === 0)
  if (hasEmptyObject) return false // Empty objects have no children to show -> SHOW
  
  // If we are here, all values are non-empty objects/arrays.
  // Their content will be displayed in their child rows.
  return true
}

const collectPaths = (obj: any, prefix: string, paths: Set<string>) => {
  if (obj === null || obj === undefined) return
  
  if (typeof obj === 'object') {
    if (Array.isArray(obj)) {
      obj.forEach((item, index) => {
        const currentPath = prefix ? `${prefix}[${index}]` : `[${index}]`
        paths.add(currentPath)
        collectPaths(item, currentPath, paths)
      })
    } else {
      Object.keys(obj).forEach(key => {
        const currentPath = prefix ? `${prefix}.${key}` : key
        paths.add(currentPath)
        collectPaths(obj[key], currentPath, paths)
      })
    }
  } else {
    if (prefix) paths.add(prefix)
  }
}

const getValueByPath = (obj: any, path: string): any => {
  if (!obj || !path) return undefined
  
  try {
    return path.split(/[.\[\]]/).filter(Boolean).reduce((current, key) => {
      return current?.[key]
    }, obj)
  } catch {
    return undefined
  }
}

const getObjectSummary = (value: any): string => {
  if (Array.isArray(value)) {
    return `Array [${value.length}]`
  }
  return `Object {${Object.keys(value).length}}`
}

const formatValue = (value: any): string => {
  if (typeof value === 'string') return `"${value}"`
  if (typeof value === 'boolean') return value.toString()
  if (typeof value === 'number') return value.toString()
  return JSON.stringify(value)
}

const formatTimestamp = (timestamp: string): string => {
  return formatDateTime(timestamp)
}

// Watch for version changes
watch(
  () => props.versions,
  async (newVersions) => {
    if (newVersions.length >= 2) {
      await loadAndCompareConfigs()
    } else {
      comparisonData.value = []
    }
  },
  { immediate: true }
)
</script>