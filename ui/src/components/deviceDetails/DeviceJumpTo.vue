<template>
  <div class="relative w-full sm:w-72">
    <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400 dark:text-gray-500">
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 1010.5 18.5a7.5 7.5 0 006.15-3.85z" />
      </svg>
    </span>

    <input
      v-model="searchTerm"
      type="search"
      :disabled="isLoading"
      @focus="handleFocus"
      @blur="handleBlur"
      @keydown.down.prevent="highlightNext"
      @keydown.up.prevent="highlightPrevious"
      @keydown.enter.prevent="selectHighlighted"
      @keydown.esc.prevent="closeDropdown"
      class="block w-full rounded-md border border-gray-300 bg-white py-2 pl-14 pr-3 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:bg-gray-100 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
      style="padding-left: 2.75rem"
      placeholder="Jump to device by name, IP, or MAC"
    />

    <span v-if="isLoading" class="pointer-events-none absolute inset-y-0 right-3 flex items-center">
      <svg class="h-4 w-4 animate-spin text-gray-400" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V1.5C5.201 1.5 1.5 5.201 1.5 10H4zm2 5.291A7.962 7.962 0 014 12H1.5c0 3.042 1.135 5.824 3 7.938L6 17.291z" />
      </svg>
    </span>

    <transition name="fade">
      <div
        v-if="showDropdown"
        class="absolute z-30 mt-1 w-full overflow-hidden rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800"
      >
        <ul class="max-h-64 overflow-y-auto py-1 text-sm text-gray-700 dark:text-gray-200">
          <li v-for="(result, index) in filteredResults" :key="result.id">
            <button
              type="button"
              @mousedown.prevent
              @click="selectDevice(result.id)"
              :class="[
                'flex w-full flex-col items-start gap-0.5 px-3 py-2 text-left transition-colors',
                index === highlightedIndex ? 'bg-blue-50 dark:bg-blue-900/40' : 'hover:bg-gray-100 dark:hover:bg-gray-700'
              ]"
            >
              <span class="font-medium text-gray-900 dark:text-gray-100">{{ result.primaryLabel }}</span>
              <span class="text-xs text-gray-500 dark:text-gray-400">
                <template v-if="result.secondaryLabel">{{ result.secondaryLabel }} · </template>{{ result.mac }}
                <template v-if="result.ip"> · {{ result.ip }}</template>
              </span>
            </button>
          </li>
        </ul>
        <div v-if="showNoResults" class="px-3 py-2 text-sm text-gray-500 dark:text-gray-400">
          No matching devices
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import type { Device } from '../../types/device'

type NormalizedDevice = {
  id: string
  primaryLabel: string
  secondaryLabel: string
  mac: string
  ip: string
  tokens: string[]
}

interface Props {
  devices: Device[]
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  devices: () => [],
  isLoading: false
})

const emit = defineEmits<{
  selectDevice: [deviceId: string]
}>()

const searchTerm = ref('')
const isFocused = ref(false)
const highlightedIndex = ref(-1)
let blurTimeout: number | null = null

const normalizedDevices = computed<NormalizedDevice[]>(() => {
  return props.devices
    .map(device => {
      const id = device.device_id || device.id
      if (!id) return null

      const primaryLabel = device.name || device.local_name || device.hostname || `Device ${device.mac}`
      const secondaryLabel = device.local_name && device.local_name !== device.name
        ? device.local_name
        : device.hostname && device.hostname !== device.name
          ? device.hostname
          : ''
      const ip = device.last_ip || device.ip_address || ''
      const mac = device.mac || ''

      const additionalTokens = [
        device.name,
        device.local_name,
        device.hostname,
        device.mac,
        device.mac?.replace(/:/g, ''),
        device.last_ip,
        device.ip_address,
        device.device_id,
        device.id
      ].filter(Boolean) as string[]

      const tokens = [primaryLabel, secondaryLabel, ip, mac, ...additionalTokens]
        .map(token => token.toLowerCase())

      return {
        id,
        primaryLabel,
        secondaryLabel,
        mac,
        ip,
        tokens
      }
    })
    .filter((item): item is NormalizedDevice => Boolean(item))
})

const filteredResults = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  if (!term) return []

  return normalizedDevices.value
    .filter(device => device.tokens.some(token => token.includes(term)))
    .slice(0, 10)
})

const showDropdown = computed(() => isFocused.value && (filteredResults.value.length > 0 || showNoResults.value))

const showNoResults = computed(() => {
  const term = searchTerm.value.trim()
  return term.length > 0 && filteredResults.value.length === 0 && !props.isLoading
})

watch(() => props.devices, () => {
  highlightedIndex.value = -1
})

watch(filteredResults, () => {
  if (highlightedIndex.value >= filteredResults.value.length) {
    highlightedIndex.value = filteredResults.value.length - 1
  }
})

watch(searchTerm, () => {
  highlightedIndex.value = filteredResults.value.length > 0 ? 0 : -1
})

const handleFocus = () => {
  if (blurTimeout) {
    window.clearTimeout(blurTimeout)
    blurTimeout = null
  }
  isFocused.value = true
}

const handleBlur = () => {
  blurTimeout = window.setTimeout(() => {
    isFocused.value = false
  }, 120)
}

const closeDropdown = () => {
  isFocused.value = false
  highlightedIndex.value = -1
}

const highlightNext = () => {
  if (filteredResults.value.length === 0) return
  highlightedIndex.value = (highlightedIndex.value + 1) % filteredResults.value.length
}

const highlightPrevious = () => {
  if (filteredResults.value.length === 0) return
  highlightedIndex.value =
    (highlightedIndex.value - 1 + filteredResults.value.length) % filteredResults.value.length
}

const selectDevice = (deviceId: string) => {
  if (!deviceId) return
  emit('selectDevice', deviceId)
  searchTerm.value = ''
  closeDropdown()
}

const selectHighlighted = () => {
  if (filteredResults.value.length === 0) return
  const index = highlightedIndex.value >= 0 ? highlightedIndex.value : 0
  const device = filteredResults.value[index]
  if (device) {
    selectDevice(device.id)
  }
}

onBeforeUnmount(() => {
  if (blurTimeout) {
    window.clearTimeout(blurTimeout)
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.12s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
