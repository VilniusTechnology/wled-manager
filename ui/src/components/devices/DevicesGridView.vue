<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
    <DeviceGridSkeleton v-if="isLoading" />
    <DeviceCard
      v-for="device in devices"
      :key="device.device_id"
      :device="device"
      :isAdopted="device.adopted || false"
      :isRestoring="props.isRestoring"
      @viewDetails="$emit('viewDetails', $event)"
      @backupDevice="$emit('backupDevice', $event)"
      @restoreDevice="$emit('restoreDevice', $event)"
      @visitDevice="$emit('visitDevice', $event)"
      @deleteDevice="$emit('deleteDevice', $event)"
      @adoptDevice="$emit('adoptDevice', $event)"
      @releaseDevice="$emit('releaseDevice', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import type { Device } from '../../types/device'
import DeviceCard from '../shared/DeviceCard.vue'
import DeviceGridSkeleton from './DeviceGridSkeleton.vue'

interface Props {
  devices: Device[]
  isLoading: boolean
  isRestoring: boolean
}

const props = defineProps<Props>()

defineEmits<{
  viewDetails: [deviceId: string]
  backupDevice: [deviceId: string]
  restoreDevice: [deviceId: string]
  visitDevice: [deviceId: string]
  deleteDevice: [deviceId: string]
  adoptDevice: [deviceId: string]
  releaseDevice: [deviceId: string]
}>()
</script>