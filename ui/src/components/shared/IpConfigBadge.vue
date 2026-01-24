<template>
  <span
    v-if="props.hasStaticIp === true || props.hasStaticIp === false"
    :class="badgeClasses"
    class="inline-flex items-center gap-1 rounded-full"
    :title="tooltipText"
  >
    <!-- Static IP: Lock Icon -->
    <Lock
      v-if="props.hasStaticIp === true"
      :class="iconClasses"
    />

    <!-- Dynamic IP: Network/Globe Icon -->
    <Globe
      v-else
      :class="iconClasses"
    />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Lock, Globe } from 'lucide-vue-next'

interface Props {
  hasStaticIp?: boolean | null
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const tooltipText = computed(() => {
  if (props.hasStaticIp === true) return 'Static IP Configuration'
  if (props.hasStaticIp === false) return 'Dynamic IP Configuration'
  return 'IP Configuration Unknown'
})

const badgeClasses = computed(() => {
  const baseClasses = 'inline-flex items-center justify-center rounded-full transition-colors'
  const sizeClasses = {
    sm: 'p-0.5',
    md: 'p-0.5',
    lg: 'p-1'
  }
  
  let colorClasses = ''
  if (props.hasStaticIp === true) {
    colorClasses = 'bg-purple-100 text-purple-700 bg-opacity-50 dark:bg-purple-900/40 dark:text-purple-300'
  } else if (props.hasStaticIp === false) {
    colorClasses = 'bg-blue-100 text-blue-700 bg-opacity-50 dark:bg-blue-900/40 dark:text-blue-300'
  } else {
    colorClasses = 'hidden'
  }
    
  return `${baseClasses} ${sizeClasses[props.size]} ${colorClasses}`
})

const iconClasses = computed(() => {
  const sizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  }
  
  return `${sizeClasses[props.size]}`
})
</script>