<script setup lang="ts">
defineProps<{
  modelValue: any
}>()
</script>

<template>
  <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Light Settings</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Brightness Scale (%)
        </label>
        <input
          v-model.number="modelValue['scale-bri']"
          type="number"
          min="1"
          max="100"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Transition Duration (100ms)
        </label>
        <input
          v-model.number="modelValue.tr.dur"
          type="number"
          min="0"
          max="65535"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Nightlight Duration (min)
        </label>
        <input
          v-model.number="modelValue.nl.dur"
          type="number"
          min="1"
          max="255"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
    </div>
  </div>
</template>
