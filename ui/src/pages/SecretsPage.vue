<template>
  <div>
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Secrets Management</h1>
      <p class="text-gray-600 dark:text-gray-400">Manage your WLED device secrets</p>
    </div>

    <div class="bg-white dark:bg-gray-800 p-4 rounded shadow border border-gray-200 dark:border-gray-700">
      <div class="space-y-4">
        <!-- Header (hidden on mobile, visible on desktop) -->
        <div class="hidden sm:grid sm:grid-cols-12 gap-4 pb-2 border-b border-gray-200 dark:border-gray-700 font-medium text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">
          <div class="sm:col-span-3 px-4">Type</div>
          <div class="sm:col-span-9 px-4">Secret</div>
        </div>

        <!-- Items -->
        <div v-for="item in secretItems" :key="item.key" class="grid grid-cols-1 sm:grid-cols-12 gap-2 sm:gap-4 py-2 sm:border-b last:border-0 border-gray-100 dark:border-gray-700 items-center">
          <!-- Label -->
          <div class="sm:col-span-3 px-4 font-semibold text-gray-900 dark:text-gray-100">
            <span class="sm:hidden text-xs text-gray-500 dark:text-gray-400 uppercase mr-2">Type:</span>
            {{ item.label }}
          </div>
          
          <!-- Input & Actions -->
          <div class="sm:col-span-9 px-4">
            <div class="flex flex-col sm:flex-row gap-2 w-full">
              <input 
                :type="item.show ? 'text' : 'password'" 
                v-model="item.value" 
                class="flex-1 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 w-full sm:w-auto bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 outline-none focus:ring-2 focus:ring-blue-500" 
              />
              <div class="flex gap-2">
                <button 
                  @click="item.show = !item.show" 
                  class="px-3 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600 flex-1 sm:flex-none justify-center"
                >
                  {{ item.show ? 'Hide' : 'Show' }}
                </button>
                <button 
                  @click="handleSave(item)" 
                  class="px-4 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors flex-1 sm:flex-none justify-center"
                  :disabled="item.saving"
                >
                  {{ item.saving ? 'Saving...' : 'Save' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success/Error Message -->
    <div v-if="message.text" :class="`mt-4 p-4 rounded ${message.type === 'success' ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-100' : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-100'}`">
        {{ message.text }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { secretsService } from '../services/secretsService'
import type { Device } from '../types/device'

interface Props {
  devices: Device[]
  isLoading: boolean
  scanInProgress: boolean
}

defineProps<Props>()

const message = reactive({ text: '', type: '' })

const secretItems = ref([
  { key: 'wifi1', label: 'WiFi 1', value: '', show: false, saving: false },
  { key: 'wifi2', label: 'WiFi 2', value: '', show: false, saving: false },
  { key: 'mqtt', label: 'MQTT', value: '', show: false, saving: false }
])

const showMessage = (text: string, type: 'success' | 'error') => {
    message.text = text
    message.type = type
    setTimeout(() => {
        message.text = ''
    }, 3000)
}

onMounted(async () => {
    for (const item of secretItems.value) {
        try {
            const data = await secretsService.getSecret(item.key)
            if (data && data.password) {
                item.value = data.password
            }
        } catch (e) {
            // Ignore 404 or errors on load
        }
    }
})

const handleSave = async (item: any) => {
    item.saving = true
    try {
        await secretsService.saveSecret(item.key, item.value)
        showMessage(`${item.label} secret saved successfully`, 'success')
        
        // Refresh to get decrypted updated value (if needed, though we already have it in v-model)
        // Actually, store returns encrypted? No, backend returns decrypted in GET, or input value in POST response.
        // My POST implementation returns `req.password` (raw).
        // So we don't strictly need to re-fetch, but verifying persistence is good.
    } catch (e: any) {
        showMessage(`Error saving ${item.label}: ${e.message || e}`, 'error')
    } finally {
        item.saving = false
    }
}
</script>
