<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  id: any
  nw: any
}>()

const hasStaticIp = computed(() => {
  if (!props.nw.ins || !props.nw.ins[0]) return false
  const ip = props.nw.ins[0].ip
  return ip && ip.length === 4 && !ip.every((byte: number) => byte === 0)
})
</script>

<template>
  <div class="mb-6 border-b border-gray-200 dark:border-gray-600 pb-6">
    <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
      mDNS Address
    </label>
    <div class="flex items-center max-w-md">
        <span class="text-gray-500 bg-gray-100 dark:bg-gray-800 border border-r-0 border-gray-300 dark:border-gray-600 rounded-l px-3 py-2">http://</span>
        <input
        v-model="id.mdns"
        type="text"
        placeholder="wled"
        class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
        <span class="text-gray-500 bg-gray-100 dark:bg-gray-800 border border-l-0 border-gray-300 dark:border-gray-600 rounded-r px-3 py-2">.local</span>
    </div>
    <p class="text-xs text-gray-500 mt-1">Client IP: {{ hasStaticIp ? nw.ins[0].ip.join('.') : '(Refresh to see)' }}</p>
  </div>
</template>
