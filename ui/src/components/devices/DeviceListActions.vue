<template>
  <div class="flex gap-2 mt-1 items-center">
    <button
      @click="$emit('viewDetails', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-details"
      title="Details"
    >
      <Info class="w-4 h-4" />
    </button>
    <button
      @click="$emit('backupDevice', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-backup"
      title="Backup"
    >
      <Download class="w-4 h-4" />
    </button>
    <button
      @click="$emit('restoreDevice', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-restore"
      title="Restore"
    >
      <Loader2 v-if="props.isRestoring" class="w-4 h-4 animate-spin" />
      <Upload v-else class="w-4 h-4" />
    </button>
    <button
      @click="$emit('visitDevice', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-visit"
      title="Visit"
    >
      <ExternalLink class="w-4 h-4" />
    </button>
    <button
      @click="$emit('deleteDevice', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-delete"
      title="Delete"
    >
      <Trash2 class="w-4 h-4" />
    </button>
    <button
      v-if="!isAdopted"
      @click="$emit('adoptDevice', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-adopt"
      title="Adopt"
    >
      <Plus class="w-4 h-4" />
    </button>
    <button
      v-else
      @click="$emit('releaseDevice', deviceId)"
      :disabled="props.isRestoring"
      class="device-action device-action-release"
      title="Release"
    >
      <Minus class="w-4 h-4" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { Info, Download, Upload, ExternalLink, Trash2, Plus, Minus, Loader2 } from 'lucide-vue-next'

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