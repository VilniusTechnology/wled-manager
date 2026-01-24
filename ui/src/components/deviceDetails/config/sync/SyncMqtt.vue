<script setup lang="ts">
defineProps<{
  syncConfig: any
  openSecretModal: (action: 'copy' | 'paste', field: 'wifi' | 'wifi2' | 'mqtt') => void
}>()
</script>

<template>
    <!-- MQTT -->
    <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">MQTT</h4>
    <div class="flex items-center mb-4">
       <input
         v-model="syncConfig.mqtt.en"
         type="checkbox"
         class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded"
       />
       <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Enable MQTT</span>
    </div>
    <div class="flex items-center mb-4">
       <input
         v-model="syncConfig.mqtt.rtn"
         type="checkbox"
         class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded"
       />
       <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Retain</span>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Broker
        </label>
        <input
          v-model="syncConfig.mqtt.broker"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Port
        </label>
        <input
          v-model.number="syncConfig.mqtt.port"
          type="number"
          min="1"
          max="65535"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Username
        </label>
        <input
          v-model="syncConfig.mqtt.user"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Password Length
        </label>
        <input
          v-model.number="syncConfig.mqtt.pskl"
          type="number"
          min="0"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
        <p class="text-xs text-gray-500 mt-1">Current length: {{ syncConfig.mqtt.pskl }} chars</p>
      </div>
    </div>
    <div class="mt-4">
      <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
        MQTT Password
      </label>
      <div class="flex gap-2">
        <input
          v-model="syncConfig.mqtt.psk"
          type="password"
          placeholder="Enter new password to change"
          class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
        <button
          type="button"
          @click="openSecretModal('paste', 'mqtt')"
          class="px-3 py-2 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 rounded text-gray-700 dark:text-gray-200 text-sm whitespace-nowrap"
          title="Paste from Secrets"
        >
          Paste
        </button>
        <button
          v-if="syncConfig.mqtt.psk"
          type="button"
          @click="openSecretModal('copy', 'mqtt')"
          class="px-3 py-2 bg-blue-100 dark:bg-blue-900 hover:bg-blue-200 dark:hover:bg-blue-800 rounded text-blue-700 dark:text-blue-200 text-sm whitespace-nowrap"
          title="Save to Secrets"
        >
          Save
        </button>
      </div>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
      <div class="col-span-1 md:col-span-2">
         <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Client ID
        </label>
        <input
          v-model="syncConfig.mqtt.cid"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Device Topic
        </label>
        <input
          v-model="syncConfig.mqtt.topics.device"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
          Group Topic
        </label>
        <input
          v-model="syncConfig.mqtt.topics.group"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
    </div>
</template>
