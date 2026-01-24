<template>
  <button
    :class="buttonClasses"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'sm' | 'md' | 'lg'
  variant?: 'primary' | 'outline'
  disabled?: boolean
  fullWidth?: boolean
  class?: string
}

const props = defineProps<Props>()

const buttonClasses = computed(() => [
  'bg-primary text-white rounded transition-colors',
  props.size === 'sm' ? 'px-3 py-1.5 text-sm' : props.size === 'lg' ? 'px-6 py-3' : 'px-4 py-2',
  props.variant === 'outline' ? 'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white' : '',
  props.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-primary-dark',
  props.fullWidth ? 'w-full' : '',
  props.class
].filter(Boolean).join(' '))

defineEmits<{
  click: [event: Event]
}>()
</script>
