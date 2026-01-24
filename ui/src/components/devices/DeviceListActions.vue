<template>
  <div class="flex gap-2 mt-1">
    <button
      @click="$emit('viewDetails', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-details"
    >
      Details
    </button>
    <button
      @click="$emit('backupDevice', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-backup"
    >
      Backup
    </button>
    <button
      @click="$emit('restoreDevice', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-restore"
    >
      {{ props.isRestoring ? 'Loading...' : 'Restore' }}
    </button>
    <button
      @click="$emit('visitDevice', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-visit"
    >
      Visit
    </button>
    <button
      @click="$emit('deleteDevice', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-delete"
    >
      Delete
    </button>
    <button
      v-if="!isAdopted"
      @click="$emit('adoptDevice', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-adopt"
    >
      Adopt
    </button>
    <button
      v-else
      @click="$emit('releaseDevice', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-release"
    >
      Release
    </button>
  </div>
</template>

<script setup lang="ts">
interface Props {
  deviceId: string
  isAdopted: boolean
  isRestoring: boolean
}

const props = defineProps<Props>()

defineEmits<{
  viewDetails: [deviceId: string]
  backupDevice: [deviceId: string]
  visitDevice: [deviceId: string]
  restoreDevice: [deviceId: string]
  deleteDevice: [deviceId: string]
  adoptDevice: [deviceId: string]
  releaseDevice: [deviceId: string]
}>()
</script>