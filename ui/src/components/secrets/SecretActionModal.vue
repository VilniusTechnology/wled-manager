<script setup lang="ts">
import { ref, watch } from 'vue'
import { secretsService } from '../../services/secretsService'

// Available secret keys
const secretKeys = [
  { key: 'wifi1', label: 'WiFi 1' },
  { key: 'wifi2', label: 'WiFi 2' },
  { key: 'mqtt', label: 'MQTT' }
]

interface Props {
  isOpen: boolean
  action: 'copy' | 'paste'
  currentValue?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'paste', value: string): void
  (e: 'saved'): void
}>()

const selectedKey = ref('wifi1')
const isLoading = ref(false)
const error = ref('')
const success = ref('')

// Initialize or reset state when modal opens
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    selectedKey.value = 'wifi1'
    isLoading.value = false
    error.value = ''
    success.value = ''
  }
})

const handleAction = async () => {
  isLoading.value = true
  error.value = ''
  success.value = ''

  try {
    if (props.action === 'paste') {
      // Fetch the secret and emit it
      const data = await secretsService.getSecret(selectedKey.value)
      if (data && data.password) {
        emit('paste', data.password)
        emit('close')
      } else {
        error.value = 'No secret found for this key'
      }
    } else {
      // Copy (Save) to secrets
      if (!props.currentValue) {
        error.value = 'No value to save'
        return
      }
      await secretsService.saveSecret(selectedKey.value, props.currentValue)
      success.value = 'Secret saved successfully'
      emit('saved')
      setTimeout(() => {
        emit('close')
      }, 1000)
    }
  } catch (e: any) {
    error.value = e.message || 'An error occurred'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      
      <!-- Backdrop -->
      <div 
        @click="$emit('close')"
        class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
        aria-hidden="true"
      ></div>

      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

      <div class="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg w-full">
        <div class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white" id="modal-title">
                {{ action === 'copy' ? 'Save to Secrets' : 'Paste from Secrets' }}
              </h3>
              
              <div class="mt-4">
                <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  {{ action === 'copy' 
                    ? 'Select which secret storage slot you want to save this password to.' 
                    : 'Select which secret you want to paste into the configuration field.' 
                  }}
                </p>

                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Target Secret
                    </label>
                    <select 
                      v-model="selectedKey"
                      class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option v-for="item in secretKeys" :key="item.key" :value="item.key">
                        {{ item.label }}
                      </option>
                    </select>
                  </div>

                  <div v-if="error" class="text-xs text-red-600 dark:text-red-400">
                    {{ error }}
                  </div>
                   <div v-if="success" class="text-xs text-green-600 dark:text-green-400">
                    {{ success }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button 
            type="button"
            @click="handleAction"
            :disabled="isLoading"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
          >
            {{ isLoading ? 'Processing...' : (action === 'copy' ? 'Save' : 'Paste') }}
          </button>
          <button 
            type="button" 
            @click="$emit('close')"
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
