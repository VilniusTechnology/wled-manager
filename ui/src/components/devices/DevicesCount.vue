<template>
  <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
    {{ isLoading ? 'Loading devices...' : `Showing ${deviceCount} of ${totalCount} devices` }}
  </p>
</template>

<script setup lang="ts">
interface Props {
  deviceCount: number
  isLoading: boolean
  totalCount: number
}

defineProps<Props>()
</script>