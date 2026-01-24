<template>
  <div class="flex items-center">
    <StatusBubble :status="device.status" class="mr-3" />
    <div>
      <template v-if="detailsHref">
        <a
          :href="detailsHref"
          class="font-medium text-blue-600 transition-colors hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
        >
          {{ deviceName }}
        </a>
      </template>
      <p v-else class="font-medium">{{ deviceName }}</p>
      <p class="text-sm text-gray-600 dark:text-gray-400">{{ ipAddress }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Device } from '../../types/device'
import { getDeviceDetailsPath, getDeviceDisplayIp, getDeviceDisplayName } from '../../utils/deviceDisplay'
import StatusBubble from '../shared/StatusBubble.vue'

interface Props {
  device: Device
}

const props = defineProps<Props>()

const deviceName = computed(() => getDeviceDisplayName(props.device))
const detailsHref = computed(() => getDeviceDetailsPath(props.device))
const ipAddress = computed(() => getDeviceDisplayIp(props.device))
</script>