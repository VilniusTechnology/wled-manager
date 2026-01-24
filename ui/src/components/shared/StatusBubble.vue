<template>
  <div class="w-3 h-3 rounded-full" :class="bubbleClass"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status?: string
}

const props = defineProps<Props>()

const bubbleClass = computed(() => {
  const status = props.status?.toLowerCase() || 'unknown'

  switch (status) {
    case 'excellent':
      return 'bg-green-500'
    case 'good':
    case 'online':
      return 'bg-green-400'
    case 'slow':
      return 'bg-yellow-400'
    case 'very_slow':
      return 'bg-orange-400'
    case 'dead':
    case 'offline':
      return 'bg-red-500'
    default:
      return 'bg-gray-400'
  }
})
</script>