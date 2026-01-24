<script setup lang="ts">
import { ref, computed } from 'vue'
import { buildApiUrl } from '../../utils/apiConfig'
import type { DeviceDetails } from '../../types/device'

interface OTAUpdateResult {
  success: boolean
  message: string
  device_id: string
  device_ip: string
  firmware_filename: string
  firmware_size: number
  upload_duration?: number
  device_response_status?: number
  device_response_text?: string
  steps_completed: string[]
  warnings: string[]
  timestamp: string
  total_duration?: number
}

interface Props {
  device: DeviceDetails
  deviceStatus?: string
}

const props = defineProps<Props>()

const isOTAOperationsDisabled = computed(() => {
  return props.deviceStatus === 'dead' || props.deviceStatus === 'Dead' || props.deviceStatus === 'Offline'
})

const selectedFile = ref<File | null>(null)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref<string>('')
const uploadError = ref<string>('')
const otaResult = ref<OTAUpdateResult | null>(null)
const showDetailedResults = ref(false)

const onFileSelected = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    // Validate file type (should be .bin for firmware)
    if (!file.name.toLowerCase().endsWith('.bin')) {
      uploadError.value = 'Please select a valid firmware file (.bin)'
      selectedFile.value = null
      target.value = ''
      return
    }
    
    // Validate file size (should be reasonable for firmware, max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      uploadError.value = 'Firmware file is too large. Maximum size is 5MB.'
      selectedFile.value = null
      target.value = ''
      return
    }
    
    selectedFile.value = file
    uploadError.value = ''
    uploadStatus.value = `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`
  }
}

const performOTAUpdate = async () => {
  if (!selectedFile.value) {
    uploadError.value = 'Please select a firmware file first.'
    return
  }
  
  try {
    isUploading.value = true
    uploadProgress.value = 0
    uploadError.value = ''
    uploadStatus.value = 'Preparing firmware upload...'
    
    // Create FormData for multipart upload
    const formData = new FormData()
    formData.append('firmware_file', selectedFile.value)
    formData.append('filename', selectedFile.value.name)
    
    uploadStatus.value = 'Uploading firmware to device...'
    
    const response = await fetch(buildApiUrl(`/devices/${props.device.device_id}/ota-update`), {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    const result: OTAUpdateResult = await response.json()
    otaResult.value = result
    
    uploadStatus.value = result.message
    uploadProgress.value = 100
    
    // Clear the file selection
    selectedFile.value = null
    const fileInput = document.getElementById('firmware-file') as HTMLInputElement
    if (fileInput) fileInput.value = ''
    
    // Show detailed results
    showDetailedResults.value = true
    
  } catch (error) {
    console.error('OTA update failed:', error)
    uploadError.value = error instanceof Error ? error.message : 'Unknown error occurred'
    uploadStatus.value = 'OTA update failed'
    
    // Try to parse error response for more details
    if (error instanceof Error && error.message.includes('HTTP')) {
      try {
        const errorResponse = JSON.parse(error.message.split('HTTP')[1].split(':')[1].trim())
        if (errorResponse.detail) {
          uploadError.value = errorResponse.detail
        }
      } catch (parseError) {
        // Ignore parse errors
      }
    }
  } finally {
    isUploading.value = false
  }
}

const clearSelection = () => {
  selectedFile.value = null
  uploadError.value = ''
  uploadStatus.value = ''
  otaResult.value = null
  showDetailedResults.value = false
  const fileInput = document.getElementById('firmware-file') as HTMLInputElement
  if (fileInput) fileInput.value = ''
}
</script>

<template>
  <div class="space-y-6">
    <!-- OTA Update Section -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">OTA Firmware Update</h3>
        <span
          :class="{
            'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200': !isOTAOperationsDisabled,
            'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200': isOTAOperationsDisabled
          }"
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
        >
          {{ isOTAOperationsDisabled ? 'Unavailable' : 'Available' }}
        </span>
      </div>

      <div class="space-y-4">
        <!-- File Selection -->
        <div>
          <label for="firmware-file" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Select Firmware File
          </label>
          <div class="flex items-center space-x-3">
            <input
              id="firmware-file"
              type="file"
              accept=".bin"
              @change="onFileSelected"
              :disabled="isOTAOperationsDisabled || isUploading"
              class="block w-full text-sm text-gray-500 dark:text-gray-400
                file:mr-4 file:py-2 file:px-4
                file:rounded-md file:border-0
                file:text-sm file:font-medium
                file:bg-blue-50 file:text-blue-700
                dark:file:bg-blue-900 dark:file:text-blue-200
                hover:file:bg-blue-100 dark:hover:file:bg-blue-800
                disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              v-if="selectedFile"
              @click="clearSelection"
              :disabled="isUploading"
              class="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Clear
            </button>
          </div>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Select a WLED firmware file (.bin) to upload. Maximum file size: 5MB.
          </p>
        </div>

        <!-- Detailed Results -->
        <div v-if="showDetailedResults && otaResult" class="rounded-md p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="ml-3 flex-1">
              <h4 class="text-sm font-medium text-green-800 dark:text-green-200 mb-2">
                OTA Update Details
              </h4>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span class="font-medium text-green-700 dark:text-green-300">Device:</span>
                  <span class="ml-2 text-green-600 dark:text-green-400">{{ otaResult.device_ip }}</span>
                </div>
                <div>
                  <span class="font-medium text-green-700 dark:text-green-300">Firmware:</span>
                  <span class="ml-2 text-green-600 dark:text-green-400">{{ otaResult.firmware_filename }}</span>
                </div>
                <div>
                  <span class="font-medium text-green-700 dark:text-green-300">File Size:</span>
                  <span class="ml-2 text-green-600 dark:text-green-400">{{ (otaResult.firmware_size / 1024 / 1024).toFixed(2) }} MB</span>
                </div>
                <div v-if="otaResult.upload_duration">
                  <span class="font-medium text-green-700 dark:text-green-300">Upload Time:</span>
                  <span class="ml-2 text-green-600 dark:text-green-400">{{ otaResult.upload_duration.toFixed(2) }}s</span>
                </div>
                <div v-if="otaResult.total_duration">
                  <span class="font-medium text-green-700 dark:text-green-300">Total Time:</span>
                  <span class="ml-2 text-green-600 dark:text-green-400">{{ otaResult.total_duration.toFixed(2) }}s</span>
                </div>
                <div v-if="otaResult.device_response_status">
                  <span class="font-medium text-green-700 dark:text-green-300">Device Response:</span>
                  <span class="ml-2 text-green-600 dark:text-green-400">HTTP {{ otaResult.device_response_status }}</span>
                </div>
              </div>
              
              <!-- Steps Completed -->
              <div v-if="otaResult.steps_completed.length > 0" class="mt-3">
                <h5 class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Steps Completed:</h5>
                <ul class="list-disc list-inside text-sm text-green-600 dark:text-green-400 space-y-1">
                  <li v-for="step in otaResult.steps_completed" :key="step">{{ step }}</li>
                </ul>
              </div>
              
              <!-- Warnings -->
              <div v-if="otaResult.warnings.length > 0" class="mt-3">
                <h5 class="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Warnings:</h5>
                <ul class="list-disc list-inside text-sm text-yellow-600 dark:text-yellow-400 space-y-1">
                  <li v-for="warning in otaResult.warnings" :key="warning">{{ warning }}</li>
                </ul>
              </div>
              
              <!-- Device Response Text -->
              <div v-if="otaResult.device_response_text" class="mt-3">
                <h5 class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Device Response:</h5>
                <pre class="text-xs text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-800 p-2 rounded overflow-x-auto">{{ otaResult.device_response_text }}</pre>
              </div>
            </div>
          </div>
        </div>

        <!-- Progress Bar -->
        <div v-if="isUploading" class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            class="bg-blue-600 h-2 rounded-full transition-all duration-300"
            :style="{ width: uploadProgress + '%' }"
          ></div>
        </div>

        <!-- Update Button -->
        <div class="flex justify-end">
          <button
            @click="performOTAUpdate"
            :disabled="!selectedFile || isOTAOperationsDisabled || isUploading"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <svg v-if="isUploading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isUploading ? 'Updating Firmware...' : 'Update Firmware' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Warning Section -->
    <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-yellow-800 dark:text-yellow-200">
            Important Safety Information
          </h3>
          <div class="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
            <ul class="list-disc list-inside space-y-1">
              <li>Ensure you have a backup of the current configuration before proceeding</li>
              <li>The device will restart automatically after the update completes</li>
              <li>Do not power off the device during the update process</li>
              <li>Use only official WLED firmware files to avoid bricking the device</li>
              <li>The update process may take several minutes to complete</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>