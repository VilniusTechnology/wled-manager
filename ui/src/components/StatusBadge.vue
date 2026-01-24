<template>
  <span
    :class="badgeClasses"
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
  >
    <i :class="iconClass" class="mr-1"></i>
    {{ displayStatus }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status: 'running' | 'stopped' | 'error' | 'warning' | string
}

const props = defineProps<Props>()

const badgeClasses = computed(() => {
  switch (props.status?.toLowerCase()) {
    case 'running':
      return 'bg-green-100 text-green-800'
    case 'stopped':
      return 'bg-gray-100 text-gray-800'
    case 'error':
      return 'bg-red-100 text-red-800'
    case 'warning':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
})

const iconClass = computed(() => {
  switch (props.status?.toLowerCase()) {
    case 'running':
      return 'fas fa-play text-green-600'
    case 'stopped':
      return 'fas fa-stop text-gray-600'
    case 'error':
      return 'fas fa-exclamation-triangle text-red-600'
    case 'warning':
      return 'fas fa-exclamation-circle text-yellow-600'
    default:
      return 'fas fa-question text-gray-600'
  }
})

const displayStatus = computed(() => {
  switch (props.status?.toLowerCase()) {
    case 'running':
      return 'Running'
    case 'stopped':
      return 'Stopped'
    case 'error':
      return 'Error'
    case 'warning':
      return 'Warning'
    default:
      return props.status || 'Unknown'
  }
})
</script>