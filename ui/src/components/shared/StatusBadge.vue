<template>
  <span
    :class="badgeClasses"
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
  >
    {{ status }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status: string
}

const props = defineProps<Props>()

const badgeClasses = computed(() => {
  const status = props.status?.toLowerCase() || ''
  
  if (['online', 'excellent', 'good'].includes(status)) {
    return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  } else if (['slow', 'very_slow', 'almost_offline'].includes(status)) {
    return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
  } else if (['offline', 'dead'].includes(status)) {
    return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  } else {
    return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
  }
})
</script>