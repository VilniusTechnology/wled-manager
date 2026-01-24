<script setup lang="ts">
defineProps<{
  ap: any
}>()
</script>

<template>
  <!-- Configure Access Point -->
  <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3 mt-6 pt-6 border-t border-gray-200 dark:border-gray-600">Configure Access Point</h4>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      <div>
      <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
        AP SSID
      </label>
      <input
        v-model="ap.ssid"
        type="text"
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
      />
    </div>
    <div class="flex items-center mt-6">
        <label class="flex items-center space-x-2 cursor-pointer">
          <input
            v-model.number="ap.hide"
            :true-value="1"
            :false-value="0"
            type="checkbox"
            class="form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700"
          />
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Hide AP name</span>
        </label>
    </div>
  </div>
  
  <div class="space-y-4">
      <div>
          <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
            AP Password
          </label>
          <input
          v-model="ap.psk" 
          type="password"
          placeholder="Leave empty for open" 
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
      
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
              <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
              AP IP
              </label>
              <div class="grid grid-cols-4 gap-1">
                <input v-model.number="ap.ip[0]" type="number" min="0" max="255" class="w-full px-1 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-center" />
                <input v-model.number="ap.ip[1]" type="number" min="0" max="255" class="w-full px-1 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-center" />
                <input v-model.number="ap.ip[2]" type="number" min="0" max="255" class="w-full px-1 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-center" />
                <input v-model.number="ap.ip[3]" type="number" min="0" max="255" class="w-full px-1 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-center" />
              </div>
          </div>
          <div>
              <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
              AP Channel
              </label>
              <select v-model.number="ap.chan" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
                <option v-for="n in 13" :key="n" :value="n">{{ n }}</option>
              </select>
          </div>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
            AP Behavior
          </label>
            <select v-model.number="ap.behav" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
                <option :value="0">Always open AP</option>
                <option :value="1">Only when disconnected</option>
                <option :value="2">Always open AP (safe mode)</option>
                <option :value="3">Only when disconnected (safe mode)</option>
            </select>
        </div>
  </div>
</template>
