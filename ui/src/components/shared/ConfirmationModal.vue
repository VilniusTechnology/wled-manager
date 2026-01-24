<template>
  <Modal 
    :isOpen="isOpen" 
    :title="title"
    @close="$emit('close')"
  >
    <div class="mb-4">
      <p class="text-sm text-gray-500 dark:text-gray-400">
        {{ message }}
      </p>
      <slot />
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
        @click="$emit('confirm')"
        :disabled="isLoading"
        :class="[
          'ml-3 px-4 py-2 text-sm font-medium text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2',
          confirmColor === 'red' ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500' : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
        ]"
      >
        <LoadingSpinner v-if="isLoading" class="w-4 h-4" />
        <span>{{ isLoading ? loadingText : confirmText }}</span>
      </button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import Modal from './Modal.vue';
import LoadingSpinner from './LoadingSpinner.vue';

interface Props {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  loadingText?: string;
  confirmColor?: 'red' | 'blue';
  isLoading?: boolean;
}

withDefaults(defineProps<Props>(), {
  confirmText: 'Confirm',
  loadingText: 'Processing...',
  confirmColor: 'blue',
  isLoading: false
});

defineEmits<{
  close: [];
  confirm: [];
}>();
</script>