<script setup lang="ts">
defineProps<{
  modelValue: any
}>()
</script>

<template>
  <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Hardware Settings</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Total LEDs
        </label>
        <input
          v-model.number="modelValue.led.total"
          type="number"
          min="1"
          max="1200"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Max Power (mA)
        </label>
        <input
          v-model.number="modelValue.led.maxpwr"
          type="number"
          min="0"
          max="65000"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Target FPS
        </label>
        <input
          v-model.number="modelValue.led.fps"
          type="number"
          min="1"
          max="255"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
    </div>
  </div>
</template>
