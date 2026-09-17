<template>
  <span
    v-if="props.mqttEnabled === true || props.mqttEnabled === false"
    :class="badgeClasses"
    class="inline-flex items-center gap-1 rounded-full"
    :title="tooltipText"
  >
    <Radio
      :class="iconClasses"
    />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Radio } from 'lucide-vue-next'

interface Props {
  mqttEnabled?: boolean | null
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const tooltipText = computed(() => {
  if (props.mqttEnabled === true) return 'MQTT Enabled'
  if (props.mqttEnabled === false) return 'MQTT Disabled'
  return 'MQTT Status Unknown'
})

const badgeClasses = computed(() => {
  const baseClasses = 'inline-flex items-center justify-center rounded-full transition-colors'
  const sizeClasses = {
    sm: 'p-0.5',
    md: 'p-0.5',
    lg: 'p-1'
  }
  
  let colorClasses = ''
  if (props.mqttEnabled === true) {
    colorClasses = 'bg-emerald-100 text-emerald-700 bg-opacity-50 dark:bg-emerald-900/40 dark:text-emerald-300'
  } else if (props.mqttEnabled === false) {
    colorClasses = 'bg-gray-100 text-gray-500 bg-opacity-50 dark:bg-gray-700 dark:text-gray-400'
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
