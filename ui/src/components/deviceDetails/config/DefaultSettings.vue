<script setup lang="ts">
defineProps<{
  modelValue: any
}>()
</script>

<template>
  <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Power On Behavior</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="flex items-center h-full pt-6">
        <label class="flex items-center cursor-pointer">
          <input
            type="checkbox"
            v-model="modelValue.on"
            class="sr-only peer"
          />
          <div class="w-11 h-6 bg-gray-300 dark:bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 relative"></div>
          <span class="ml-3 text-sm font-medium text-gray-900 dark:text-gray-300">
            Turn LEDs on after power up
          </span>
        </label>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Default Brightness (0-255)
        </label>
        <input
          v-model.number="modelValue.bri"
          type="number"
          min="0"
          max="255"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Apply Preset ID at boot (0 for none)
        </label>
        <input
          v-model.number="modelValue.ps"
          type="number"
          min="0"
          max="250"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
    </div>
  </div>
</template>
