<template>
  <Modal :is-open="isOpen" :title="title" @close="closeDialog">
    <div class="space-y-4">
      <div class="flex items-start space-x-3">
        <div class="flex-shrink-0">
          <svg class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div class="flex-1">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ message }}
          </p>
          <div class="mt-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
            <div class="text-xs text-gray-500 dark:text-gray-400 space-y-1">
              <div><strong>Device:</strong> {{ device?.name || 'Unknown Device' }}</div>
              <div><strong>MAC:</strong> {{ device?.mac }}</div>
              <div><strong>IP Address:</strong> {{ device?.ip_address || device?.last_ip }}</div>
              <div><strong>Status:</strong> {{ device?.status }}</div>
            </div>
          </div>

          <!-- Backup Options -->
          <div class="mt-4">
            <p class="text-sm font-medium text-gray-900 dark:text-white mb-2">Backup Options:</p>
            <div class="space-y-2">
              <label class="flex items-center">
                <input
                  v-model="backupConfig"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Config File (cfg.json)</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="backupPresets"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Presets File (presets.json)</span>
              </label>
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
        @click="confirmBackup"
        :disabled="isBackingUp || (!backupConfig && !backupPresets)"
        class="ml-3 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <svg v-if="isBackingUp" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ isBackingUp ? 'Backing up...' : 'Start Backup' }}
      </button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import Modal from './Modal.vue'
import type { Device } from '../../types/device'

interface Props {
  isOpen: boolean
  device: Device | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  backup: [device: Device, options: { config: boolean; presets: boolean }]
}>()

const isBackingUp = ref(false)
const backupConfig = ref(true)
const backupPresets = ref(true)

const title = computed(() => {
  return 'Backup Device Configuration'
})

const message = computed(() => {
  return 'Create a backup of the selected device configuration files. This will download and store the current config and presets from the device.'
})

const closeDialog = () => {
  emit('close')
}

const confirmBackup = async () => {
  if (!props.device) return

  isBackingUp.value = true
  try {
    emit('backup', props.device, {
      config: backupConfig.value,
      presets: backupPresets.value
    })
  } finally {
    isBackingUp.value = false
    closeDialog()
  }
}

// Reset options when dialog opens
const resetOptions = () => {
  backupConfig.value = true
  backupPresets.value = true
}

// Watch for dialog opening to reset options
import { watch } from 'vue'
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    resetOptions()
  }
})
</script>