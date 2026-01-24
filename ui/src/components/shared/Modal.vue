<template>
  <Teleport to="body">
    <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center">
      <!-- Backdrop -->
      <div
        class="absolute inset-0 bg-black bg-opacity-50"
        @click="closeOnBackdrop ? $emit('close') : null"
      ></div>

      <!-- Modal -->
      <div
        class="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            <slot name="title">{{ title }}</slot>
          </h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Body -->
        <div class="p-4">
          <slot></slot>
        </div>

        <!-- Footer -->
        <div v-if="$slots.footer" class="flex items-center justify-end gap-3 p-4 border-t border-gray-200 dark:border-gray-700">
          <slot name="footer"></slot>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
interface Props {
  isOpen: boolean
  title?: string
  closeOnBackdrop?: boolean
}

withDefaults(defineProps<Props>(), {
  title: '',
  closeOnBackdrop: true
})

defineEmits<{
  close: []
}>()
</script>
