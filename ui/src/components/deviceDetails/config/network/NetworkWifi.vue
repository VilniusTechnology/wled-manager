<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  nw: any
  openSecretModal: (action: 'copy' | 'paste', field: 'wifi' | 'wifi2' | 'mqtt') => void
}>()

const hasStaticIp = computed(() => {
  if (!props.nw.ins || !props.nw.ins[0]) return false
  const ip = props.nw.ins[0].ip
  return ip && ip.length === 4 && !ip.every((byte: number) => byte === 0)
})

const clearStaticIp = () => {
  if (props.nw.ins && props.nw.ins[0]) {
    props.nw.ins[0].ip = [0, 0, 0, 0]
    props.nw.ins[0].gw = [0, 0, 0, 0]
    props.nw.ins[0].sn = [0, 0, 0, 0]
    props.nw.dns = [0, 0, 0, 0]
  }
}
</script>

<template>
    <!-- WiFi 1 -->
    <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">WiFi Network 1 (Primary)</h4>
    <div v-if="nw.ins && nw.ins.length > 0" class="space-y-4 mb-8">
      <div class="border border-gray-200 dark:border-gray-600 rounded p-4">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-md font-medium text-gray-800 dark:text-gray-200">WiFi Network</h4>
          <button
            v-if="hasStaticIp"
            @click="clearStaticIp"
            type="button"
            class="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
          >
            Clear Static IP
          </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
              SSID
            </label>
            <input
              v-model="nw.ins[0].ssid"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
              Password Length
            </label>
            <input
              v-model.number="nw.ins[0].pskl"
              type="number"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
        </div>
        <div class="mt-4">
          <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
            WiFi Password
          </label>
          <div class="flex gap-2">
            <input
              v-model="nw.ins[0].psk"
              type="password"
              placeholder="Enter new password to change"
              class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <button
              type="button"
              @click="openSecretModal('paste', 'wifi')"
              class="px-3 py-2 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 rounded text-gray-700 dark:text-gray-200 text-sm whitespace-nowrap"
              title="Paste from Secrets"
            >
              Paste
            </button>
            <button
              v-if="nw.ins[0].psk"
              type="button"
              @click="openSecretModal('copy', 'wifi')"
              class="px-3 py-2 bg-blue-100 dark:bg-blue-900 hover:bg-blue-200 dark:hover:bg-blue-800 rounded text-blue-700 dark:text-blue-200 text-sm whitespace-nowrap"
              title="Save to Secrets"
            >
              Save
            </button>
          </div>
          <p class="text-xs text-gray-500 mt-1">Current length: {{ nw.ins[0].pskl }} chars (leave empty to keep current)</p>
        </div>
        

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
              IP Address
            </label>
            <input
              v-model.number="nw.ins[0].ip[0]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[0].ip[1]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[0].ip[2]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[0].ip[3]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
              Gateway
            </label>
            <input
              v-model.number="nw.ins[0].gw[0]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[0].gw[1]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[0].gw[2]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[0].gw[3]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
              Subnet Mask
            </label>
            <input
              v-model.number="nw.ins[0].sn[0]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[0].sn[1]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[0].sn[2]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[0].sn[3]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
              DNS Server
            </label>
            <input
              v-model.number="nw.dns[0]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.dns[1]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.dns[2]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.dns[3]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- WiFi 2 -->
    <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3 mt-6">WiFi Network 2 (Fallback)</h4>
    <div v-if="nw.ins && nw.ins.length > 1" class="space-y-4">
      <div class="border border-gray-200 dark:border-gray-600 rounded p-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
              SSID
            </label>
            <input
              v-model="nw.ins[1].ssid"
              type="text"
              placeholder="Optional"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
              Password Length
            </label>
            <input
              v-model.number="nw.ins[1].pskl"
              type="number"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
        </div>
        <div class="mt-4">
          <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
            WiFi Password
          </label>
          <div class="flex gap-2">
            <input
              v-model="nw.ins[1].psk"
              type="password"
              placeholder="Enter new password to change"
              class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <button
              type="button"
              @click="openSecretModal('paste', 'wifi2')"
              class="px-3 py-2 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 rounded text-gray-700 dark:text-gray-200 text-sm whitespace-nowrap"
              title="Paste from Secrets"
            >
              Paste
            </button>
            <button
              v-if="nw.ins[1].psk"
              type="button"
              @click="openSecretModal('copy', 'wifi2')"
              class="px-3 py-2 bg-blue-100 dark:bg-blue-900 hover:bg-blue-200 dark:hover:bg-blue-800 rounded text-blue-700 dark:text-blue-200 text-sm whitespace-nowrap"
              title="Save to Secrets"
            >
              Save
            </button>
          </div>
          <p class="text-xs text-gray-500 mt-1">Current length: {{ nw.ins[1].pskl }} chars</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
              IP Address
            </label>
            <input
              v-model.number="nw.ins[1].ip[0]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[1].ip[1]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[1].ip[2]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[1].ip[3]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
              Gateway
            </label>
            <input
              v-model.number="nw.ins[1].gw[0]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[1].gw[1]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[1].gw[2]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[1].gw[3]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
              Subnet Mask
            </label>
            <input
              v-model.number="nw.ins[1].sn[0]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[1].sn[1]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[1].sn[2]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">.</label>
            <input
              v-model.number="nw.ins[1].sn[3]"
              type="number"
              min="0"
              max="255"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
        </div>
        
      </div>
    </div>
</template>
