<script setup lang="ts">
defineProps<{
  nw: any
}>()
</script>

<template>
  <!-- Wireless ESP-NOW -->
  <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3 mt-6 pt-6 border-t border-gray-200 dark:border-gray-600">Wireless ESP-NOW</h4>
  <div class="flex items-center">
    <label class="flex items-center space-x-2 cursor-pointer">
    <input
      v-model="nw.espnow"
      type="checkbox"
      class="form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700"
    />
    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Enable ESP-NOW</span>
  </label>
  </div>
</template>
