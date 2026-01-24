<template>
  <div class="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg gap-4">
    <RecentDeviceInfo :device="device" />
    <div class="w-full sm:w-auto text-left sm:text-right">
      <RecentDeviceLastSeen :device="device" />
      <RecentDeviceActions
        :device-id="device.device_id"
        :is-adopted="device.adopted || false"
        :device-data="device"
        :is-restoring="$props.isRestoring"
        @view-details="$emit('view-details', $event)"
        @backup-device="$emit('backup-device', $event)"
        @restore-device="$emit('restore-device', $event)"
        @visit-device="$emit('visit-device', $event)"
        @delete-device="$emit('delete-device', $event)"
        @adopt-device="(deviceId, localName) => $emit('adopt-device', deviceId, localName)"
        @release-device="$emit('release-device', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Device } from '../../types/device'
import RecentDeviceInfo from './RecentDeviceInfo.vue'
import RecentDeviceActions from './RecentDeviceActions.vue'
import RecentDeviceLastSeen from './RecentDeviceLastSeen.vue'

interface Props {
  device: Device
  isRestoring?: boolean
}

defineProps<Props>()

defineEmits<{
  'view-details': [deviceId: string]
  'backup-device': [deviceId: string]
  'visit-device': [deviceId: string]
  'restore-device': [deviceId: string]
  'delete-device': [deviceId: string]
  'adopt-device': [deviceId: string, localName: string]
  'release-device': [deviceId: string]
}>()
</script>