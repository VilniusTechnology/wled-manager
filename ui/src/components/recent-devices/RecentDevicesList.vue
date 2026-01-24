<template>
  <div class="space-y-4">
    <RecentDeviceItem
      v-for="device in devices"
      :key="device.device_id"
      :device="device"
      :is-restoring="$props.isRestoring"
      @view-details="$emit('view-details', $event)"
      @backup-device="$emit('backup-device', $event)"
      @visit-device="$emit('visit-device', $event)"
      @restore-device="$emit('restore-device', $event)"
      @delete-device="$emit('delete-device', $event)"
      @adopt-device="(deviceId, localName) => $emit('adopt-device', deviceId, localName)"
      @release-device="$emit('release-device', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import type { Device } from '../../types/device'
import RecentDeviceItem from './RecentDeviceItem.vue'

interface Props {
  devices: Device[]
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