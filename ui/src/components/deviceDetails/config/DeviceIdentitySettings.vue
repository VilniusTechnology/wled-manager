<script setup lang="ts">
interface IdentityConfig {
  mdns: string
  name: string
  inv: string
}

defineProps<{
  modelValue: IdentityConfig
}>()
</script>

<template>
  <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Device Identity</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">

      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Friendly Name
        </label>
        <input
          v-model="modelValue.name"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Inventory Name
        </label>
        <input
          v-model="modelValue.inv"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
    </div>
  </div>
</template>
