<template>
  <Modal 
    :isOpen="isOpen" 
    :title="'Release Device'"
    @close="$emit('close')"
  >
    <div class="mb-4">
      <p class="text-sm text-gray-500 dark:text-gray-400">
        Are you sure you want to release this device? The device will no longer be managed by WLED Manager.
      </p>
      <div v-if="deviceName" class="mt-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
        <p class="font-medium text-gray-900 dark:text-white">{{ deviceName }}</p>
        <p v-if="deviceMac" class="text-sm font-mono text-gray-500 dark:text-gray-400">{{ deviceMac }}</p>
      </div>
    </div>

    <template #footer>
      <button
        @click="$emit('close')"
        :disabled="isLoading"
        class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Cancel
      </button>
      <button
        @click="confirmRelease"
        :disabled="isLoading"
        class="ml-3 px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 rounded-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
      >
        <LoadingSpinner v-if="isLoading" />
        <span>{{ isLoading ? 'Releasing...' : 'Release' }}</span>
      </button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import Modal from '../shared/Modal.vue';

import LoadingSpinner from '../shared/LoadingSpinner.vue';

interface Props {
  isOpen: boolean;
  deviceId: string;
  deviceName?: string;
  deviceMac?: string;
  isLoading?: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  close: [];
  confirm: [deviceId: string];
}>();

const confirmRelease = () => {
  emit('confirm', props.deviceId);
};
</script>