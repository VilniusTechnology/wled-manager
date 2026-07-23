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

  if (['offline', 'dead', 'almost_offline'].includes(status)) {
    return 'bg-red-500'
  } else if (['online', 'excellent', 'good', 'slow', 'very_slow'].includes(status)) {
    return 'bg-green-500'
  } else {
    return 'bg-gray-400'
  }
})
</script>