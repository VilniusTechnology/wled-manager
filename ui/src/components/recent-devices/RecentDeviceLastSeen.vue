<template>
  <p class="text-sm text-gray-600 dark:text-gray-400">{{ formattedLastSeen }}</p>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Device } from '../../types/device'
import { formatDateTime } from '../../utils/dateUtils'

interface Props {
  device: Device
}

const props = defineProps<Props>()

const formattedLastSeen = computed(() => {
  const lastSeen = props.device.last_seen || props.device.lastSeen
  return lastSeen ? formatDateTime(lastSeen, 'EU_NRML') : 'Never'
})
</script>