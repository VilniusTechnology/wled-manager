<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
    <RecentDevicesHeader />
    <RecentDevicesEmptyState
      v-if="devices.length === 0"
      @scan-network="handleScanNetwork"
    />
    <RecentDevicesList
      v-else
      :devices="recentDevices"
      :is-restoring="$props.isRestoring"
      @view-details="handleViewDetails"
      @backup-device="handleBackupDevice"
      @visit-device="handleVisitDevice"
      @restore-device="handleRestoreDevice"
      @delete-device="handleDeleteDevice"
      @adopt-device="handleAdoptDevice"
      @release-device="handleReleaseDevice"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Device } from '../types/device'
import RecentDevicesHeader from './recent-devices/RecentDevicesHeader.vue'
import RecentDevicesEmptyState from './recent-devices/RecentDevicesEmptyState.vue'
import RecentDevicesList from './recent-devices/RecentDevicesList.vue'

interface Props {
  devices: Device[]
  isRestoring?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  scanNetwork: []
  'view-details': [deviceId: string]
  'backup-device': [deviceId: string]
  'visit-device': [deviceId: string]
  'restore-device': [deviceId: string]
  'delete-device': [deviceId: string]
  'adopt-device': [deviceId: string, localName: string]
  'release-device': [deviceId: string]
}>()

const recentDevices = computed(() => props.devices.slice(0, 5))

const handleScanNetwork = () => {
  emit('scanNetwork')
}

const handleVisitDevice = (deviceId: string) => {
  emit('visit-device', deviceId)
}

const handleRestoreDevice = (deviceId: string) => {
  emit('restore-device', deviceId)
}

const handleAdoptDevice = (deviceId: string, localName: string) => {
  emit('adopt-device', deviceId, localName)
}

const handleReleaseDevice = (deviceId: string) => {
  emit('release-device', deviceId)
}

const handleViewDetails = (deviceId: string) => {
  emit('view-details', deviceId)
}

const handleBackupDevice = (deviceId: string) => {
  emit('backup-device', deviceId)
}

const handleDeleteDevice = (deviceId: string) => {
  emit('delete-device', deviceId)
}
</script>