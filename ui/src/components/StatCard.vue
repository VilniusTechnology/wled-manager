<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center">
      <div class="p-2 rounded-lg" :class="iconBgClass">
        <component :is="iconComponent" class="w-6 h-6" :class="iconTextClass" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <slot name="icon-path"></slot>
        </component>
      </div>
      <div class="ml-4">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400">{{ title }}</p>
        <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ value }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  value: string | number
  iconBgClass: string
  iconTextClass: string
  iconComponent: string
}

defineProps<Props>()
</script>