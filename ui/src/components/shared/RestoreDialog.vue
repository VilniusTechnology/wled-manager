<template>
  <Modal :is-open="isOpen" :title="title" @close="closeDialog">
    <div class="space-y-4">
      <div class="flex items-start space-x-3">
        <div class="flex-shrink-0">
          <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div class="flex-1">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ message }}
          </p>
          <div class="mt-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
            <div class="text-xs text-gray-500 dark:text-gray-400 space-y-1">
              <div><strong>Target Device:</strong> {{ device?.name || 'Unknown Device' }}</div>
              <div><strong>MAC:</strong> {{ device?.mac }}</div>
              <div><strong>IP Address:</strong> {{ device?.ip_address || device?.last_ip }}</div>
              <div class="flex items-center">
                <strong>Status:</strong> 
                <span class="ml-1 inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium uppercase"
                      :class="device?.status === 'online' || device?.status === 'excellent' || device?.status === 'good' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                  {{ device?.status || 'Unknown' }}
                </span>
              </div>
            </div>
          </div>
          
          <div v-if="backup" class="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-md border border-blue-100 dark:border-blue-800">
             <div class="text-xs text-gray-500 dark:text-gray-400 space-y-1">
              <div class="font-medium text-blue-800 dark:text-blue-300 mb-1">Backup Source:</div>
              <div><strong>ID:</strong> <span class="font-mono">{{ backup.id }}</span></div>
              <div><strong>Date:</strong> {{ formatDateTime(backup.timestamp) }}</div>
            </div>
          </div>

          <!-- Restore Options -->
          <div class="mt-4">
            <p class="text-sm font-medium text-gray-900 dark:text-white mb-2">Restore Options:</p>
            <div class="space-y-2">
              <label class="flex items-center" :class="{ 'opacity-50 cursor-not-allowed': !hasConfig }">
                <input
                  v-model="restoreConfig"
                  type="checkbox"
                  :disabled="!hasConfig"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Restore Config File (cfg.json)
                  <span v-if="!hasConfig" class="text-xs text-red-500 ml-1">(Not available in backup)</span>
                </span>
              </label>
              <label class="flex items-center" :class="{ 'opacity-50 cursor-not-allowed': !hasPresets }">
                <input
                  v-model="restorePresets"
                  type="checkbox"
                  :disabled="!hasPresets"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Restore Presets File (presets.json)
                  <span v-if="!hasPresets" class="text-xs text-red-500 ml-1">(Not available in backup)</span>
                </span>
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
        @click="confirmRestore"
        :disabled="isRestoring || (!restoreConfig && !restorePresets)"
        class="ml-3 px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <svg v-if="isRestoring" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ isRestoring ? 'Restoring...' : 'Start Restore' }}
      </button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Modal from './Modal.vue'
import type { Device } from '../../types/device'
import type { Backup } from '../../types/backup'
import { formatDateTime } from '../../utils/dateUtils'

interface Props {
  isOpen: boolean
  device: Device | null
  backup: Backup | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  restore: [device: Device, backup: Backup, options: { restore_config: boolean; restore_presets: boolean }]
}>()

const isRestoring = ref(false)
const restoreConfig = ref(false)
const restorePresets = ref(false)

const hasConfig = computed(() => !!props.backup?.cfg_path)
const hasPresets = computed(() => !!props.backup?.presets_path)

const title = computed(() => 'Restore Device Confirmation')

const message = computed(() => {
  return 'Are you sure you want to restore this backup? This will OVERWRITE the current configuration on the device with the selected files. The device may reboot during this process.'
})

const closeDialog = () => {
  emit('close')
}

const confirmRestore = async () => {
  if (!props.device || !props.backup) return

  isRestoring.value = true
  try {
    emit('restore', props.device, props.backup, {
      restore_config: restoreConfig.value,
      restore_presets: restorePresets.value
    })
  } finally {
    isRestoring.value = false
    closeDialog()
  }
}

// Reset options when dialog opens/backup changes
watch(() => [props.isOpen, props.backup], ([isOpen]) => {
  if (isOpen) {
    restoreConfig.value = hasConfig.value
    restorePresets.value = hasPresets.value
  }
})
</script>