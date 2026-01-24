<template>
  <Modal :is-open="isOpen" :title="title" @close="closeDialog">
    <div class="space-y-4">
      <div class="flex items-start space-x-3">
        <div class="flex-shrink-0">
          <svg class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div class="flex-1">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ message }}
          </p>
          <div class="mt-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
            <div class="text-xs text-gray-500 dark:text-gray-400 space-y-1">
              <div v-if="backup"><strong>Device:</strong> {{ deviceName || `Device ${backup.mac.slice(-4)}` }}</div>
              <div v-if="backup"><strong>MAC:</strong> {{ backup.mac }}</div>
              <div v-if="backup"><strong>Backup Date:</strong> {{ formatDateTime(backup.timestamp) }}</div>
              <div><strong>File:</strong> {{ fileName }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <button
        @click="closeDialog"
        class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
      >
        Cancel
      </button>
      <button
        @click="confirmDownload"
        :disabled="isDownloading"
        class="ml-3 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <svg v-if="isDownloading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ isDownloading ? 'Downloading...' : 'Download' }}
      </button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import Modal from './Modal.vue'
import type { Backup } from '../../types/backup'
import { formatDateTime } from '../../utils/dateUtils'

interface Props {
  isOpen: boolean
  backup: Backup | null
  fileType: 'config' | 'presets'
  deviceName?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  download: [backup: Backup, fileType: 'config' | 'presets']
}>()

const isDownloading = ref(false)

const title = computed(() => {
  return `Download ${props.fileType === 'config' ? 'Config' : 'Presets'} File`
})

const message = computed(() => {
  return `Are you sure you want to download the ${props.fileType} file for this backup?`
})

const fileName = computed(() => {
  if (!props.backup) return `${props.fileType}.json`
  const path = props.fileType === 'config' ? props.backup.cfg_path : props.backup.presets_path
  return path.split('/').pop() || `${props.fileType}.json`
})

const closeDialog = () => {
  emit('close')
}

const confirmDownload = async () => {
  if (!props.backup) return

  isDownloading.value = true
  try {
    emit('download', props.backup, props.fileType)
  } finally {
    isDownloading.value = false
    closeDialog()
  }
}
</script>