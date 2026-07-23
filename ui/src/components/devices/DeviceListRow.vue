<template>
  <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
    <td class="px-6 py-4">
      <input
        type="checkbox"
        :checked="isSelected"
        @change="$emit('toggleSelection')"
        class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
      />
    </td>
    <td class="px-6 py-4">
      <div class="flex items-center">
        <div class="mr-3 flex items-center gap-2">
          <StatusBubble :status="device.status" />
          <span v-if="device.adopted" class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-800">
            Adopted
          </span>
        </div>
        <div>
          <template v-if="detailsHref">
            <a
              :href="detailsHref"
              class="font-medium text-blue-600 transition-colors hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
            >
              {{ deviceName }}
            </a>
          </template>
          <div v-else class="font-medium text-gray-900 dark:text-white">
            {{ deviceName }}
          </div>
          <div class="text-sm text-gray-500 dark:text-gray-400">
            {{ device.software_version || device.version }}
          </div>
        </div>
      </div>
    </td>
    <td class="px-6 py-4 whitespace-nowrap text-sm">
      <div class="flex flex-col gap-1">
        <a
          v-if="deviceIp && deviceIp !== 'Unknown'"
          :href="`http://${deviceIp}`"
          target="_blank"
          rel="noopener noreferrer"
          class="text-blue-600 dark:text-blue-400 hover:underline"
        >{{ deviceIp }}</a>
        <span v-else>{{ deviceIp }}</span>
        <IpConfigBadge :hasStaticIp="device.has_static_ip" size="sm" />
      </div>
    </td>
    <td class="px-6 py-4 whitespace-nowrap text-sm font-mono">
      <span>{{ formatMacAddress(device.mac || '') }}</span>
    </td>
    <td class="px-6 py-4 whitespace-nowrap">
      <StatusBadge :status="device.status" />
    </td>
    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
      <DeviceListActions
        :device-id="String(device.id || device.device_id || '')"
        :is-adopted="Boolean(device.adopted)"
        :is-restoring="props.isRestoring"
        @viewDetails="$emit('viewDetails', $event)"
        @backupDevice="$emit('backupDevice', $event)"
        @restoreDevice="$emit('restoreDevice', $event)"
        @visitDevice="$emit('visitDevice', $event)"
        @deleteDevice="$emit('deleteDevice', $event)"
        @adoptDevice="$emit('adoptDevice', $event)"
        @releaseDevice="$emit('releaseDevice', $event)"
      />
    </td>
  </tr>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Device } from '../../types/device'
import { getDeviceDetailsPath, getDeviceDisplayIp, getDeviceDisplayName, formatMacAddress } from '../../utils/deviceDisplay'
import StatusBubble from '../shared/StatusBubble.vue'
import StatusBadge from '../shared/StatusBadge.vue'
import IpConfigBadge from '../shared/IpConfigBadge.vue'
import DeviceListActions from './DeviceListActions.vue'

interface Props {
  device: Device
  isRestoring: boolean
  isSelected: boolean
}

const props = defineProps<Props>()

const deviceName = computed(() => getDeviceDisplayName(props.device))
const detailsHref = computed(() => getDeviceDetailsPath(props.device))
const deviceIp = computed(() => getDeviceDisplayIp(props.device))

defineEmits<{
  viewDetails: [deviceId: string]
  backupDevice: [deviceId: string]
  restoreDevice: [deviceId: string]
  visitDevice: [deviceId: string]
  deleteDevice: [deviceId: string]
  adoptDevice: [deviceId: string]
  releaseDevice: [deviceId: string]
  toggleSelection: []
}>()
</script>