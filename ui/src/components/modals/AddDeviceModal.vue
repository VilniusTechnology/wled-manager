<script setup lang="ts">
import { ref } from 'vue'
import Modal from '../shared/Modal.vue'

interface Props {
  isOpen: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  add: [ip: string, localName: string]
}>()

const ipAddress = ref('')
const localName = ref('')

const closeModal = () => {
  emit('close')
  // Reset form
  ipAddress.value = ''
  localName.value = ''
}

const handleAdd = () => {
  if (ipAddress.value.trim()) {
    emit('add', ipAddress.value.trim(), localName.value.trim())
    closeModal()
  }
}
</script>

<template>
  <Modal :is-open="isOpen" title="Add WLED Device" @close="closeModal">
    <div class="space-y-4">
      <div>
        <label for="deviceIp" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          IP Address / Hostname <span class="text-red-500">*</span>
        </label>
        <input
          id="deviceIp"
          v-model="ipAddress"
          type="text"
          placeholder="e.g., 192.168.1.50 or wled-lamp.local"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          @keyup.enter="handleAdd"
        />
        <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
          Enter the IP address or hostname of your WLED device.
        </p>
      </div>
      
      <div>
        <label for="localName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Local Name (Optional)
        </label>
        <input
          id="localName"
          v-model="localName"
          type="text"
          placeholder="e.g., Living Room Lamp"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          @keyup.enter="handleAdd"
        />
        <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
          A friendly name to identify this device in the manager. Use "wled-name" format to update various DNS settings.
        </p>
      </div>
    </div>

    <template #footer>
      <button
        @click="closeModal"
        class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
      >
        Cancel
      </button>
      <button
        @click="handleAdd"
        :disabled="!ipAddress.trim()"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        Add Device
      </button>
    </template>
  </Modal>
</template>
