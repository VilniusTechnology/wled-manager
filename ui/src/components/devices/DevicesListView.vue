<template>
  <div class="mb-8">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
      <!-- Mass Actions Bar -->
      <div v-if="selectedDevices.size > 0" class="bg-orange-50/50 dark:bg-orange-900/10 px-6 py-3 border-b border-orange-100 dark:border-orange-800/30">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div class="flex items-center text-orange-700 dark:text-orange-300 font-medium">
            <span class="bg-orange-100 dark:bg-orange-800 py-0.5 px-2 rounded text-xs font-bold mr-2">{{ selectedDevices.size }}</span>
            <span>selected</span>
          </div>
          <div class="flex flex-wrap gap-2 justify-center sm:justify-end">
            <button
              @click="$emit('massOtaUpdate')"
              class="px-3 py-1.5 text-xs flex items-center rounded border border-orange-300 dark:border-orange-600 bg-orange-600 text-white hover:bg-orange-700"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="-ml-1 mr-1.5 h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Mass OTA
            </button>
            <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1"></div>
            <button
              @click="$emit('clearSelection')"
              class="px-3 py-1.5 text-xs flex items-center rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Clear
            </button>
          </div>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <DeviceListHeader 
            :select-all="selectAll"
            :has-devices="devices.length > 0"
            :sort-field="sortField"
            :sort-direction="sortDirection"
            @toggle-select-all="$emit('toggleSelectAll')"
            @sort="handleSort"
          />
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <DeviceListRow
              v-for="device in sortedDevices"
              :key="device.device_id"
              :device="device"
              :is-restoring="props.isRestoring"
              :is-selected="selectedDevices.has(device.device_id)"
              @viewDetails="$emit('viewDetails', $event)"
              @backupDevice="$emit('backupDevice', $event)"
              @restoreDevice="$emit('restoreDevice', $event)"
              @visitDevice="$emit('visitDevice', $event)"
              @deleteDevice="$emit('deleteDevice', $event)"
              @adoptDevice="$emit('adoptDevice', $event)"
              @releaseDevice="$emit('releaseDevice', $event)"
              @toggle-selection="$emit('toggleDeviceSelection', device.device_id)"
            />
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Device } from '../../types/device'
import DeviceListHeader from './DeviceListHeader.vue'
import DeviceListRow from './DeviceListRow.vue'


interface Props {
  devices: Device[]
  isLoading: boolean
  isRestoring: boolean
  selectedDevices: Set<string>
  selectAll: boolean
}

const props = defineProps<Props>()

// Sorting state
const sortField = ref<string>('name')
const sortDirection = ref<'asc' | 'desc'>('asc')

const emit = defineEmits<{
  viewDetails: [deviceId: string]
  backupDevice: [deviceId: string]
  restoreDevice: [deviceId: string]
  visitDevice: [deviceId: string]
  deleteDevice: [deviceId: string]
  adoptDevice: [deviceId: string]
  releaseDevice: [deviceId: string]
  toggleDeviceSelection: [deviceId: string]
  toggleSelectAll: []
  massOtaUpdate: []
  clearSelection: []
  sortChanged: [sortData: { field: string, direction: 'asc' | 'desc' }]
}>()

// Handle sort event from header
const handleSort = (field: string) => {
  if (sortField.value === field) {
    // If already sorting by this field, toggle direction
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    // Sort by new field in ascending order
    sortField.value = field
    sortDirection.value = 'asc'
  }
  
  // Emit the sort change event
  emit('sortChanged', { field: sortField.value, direction: sortDirection.value })
}

// Compute sorted devices
const sortedDevices = computed(() => {
  if (!props.devices || props.devices.length === 0) return []
  
  return [...props.devices].sort((a, b) => {
    // Handle different field types
    let valueA, valueB
    
    // Special case for device name (use name, local_name or hostname in that order)
    if (sortField.value === 'name') {
      valueA = a.name || a.local_name || a.hostname || ''
      valueB = b.name || b.local_name || b.hostname || ''
    } else if (sortField.value === 'ip') {
      valueA = a.last_ip || a.ip_address || ''
      valueB = b.last_ip || b.ip_address || ''
    } else if (sortField.value === 'mac') {
      valueA = a.mac || ''
      valueB = b.mac || ''
    } else if (sortField.value === 'status') {
      valueA = a.status || ''
      valueB = b.status || ''
    } else {
      // Default to the specified field or empty string
      valueA = (a as any)[sortField.value] || ''
      valueB = (b as any)[sortField.value] || ''
    }
    
    // Compare the values
    if (typeof valueA === 'string' && typeof valueB === 'string') {
      return sortDirection.value === 'asc' 
        ? valueA.localeCompare(valueB) 
        : valueB.localeCompare(valueA)
    } else {
      // For numeric or boolean values
      if (valueA < valueB) return sortDirection.value === 'asc' ? -1 : 1
      if (valueA > valueB) return sortDirection.value === 'asc' ? 1 : -1
      return 0
    }
  })
})
</script>