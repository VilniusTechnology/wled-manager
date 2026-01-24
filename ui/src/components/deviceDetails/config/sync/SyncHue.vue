<script setup lang="ts">
defineProps<{
  syncConfig: any
}>()
</script>

<template>
    <!-- Philips Hue -->
    <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">Philips Hue</h4>
    <div class="space-y-4 border-b border-gray-200 dark:border-gray-600 pb-4 mb-4">
       <div class="flex items-center">
          <input
            v-model="syncConfig.hue.en"
            type="checkbox"
            class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded"
          />
          <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Sync with Philips Hue</span>
       </div>
       <div v-if="syncConfig.hue.en" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                 <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
                  Poll Interval (ms)
                 </label>
                 <input
                  v-model.number="syncConfig.hue.iv"
                  type="number"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">Light ID</label>
                <input v-model.number="syncConfig.hue.id" type="number" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white" />
              </div>
          </div>
           <div>
               <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
                Bridge IP
               </label>
               <div class="grid grid-cols-4 gap-1">
                  <input v-model.number="syncConfig.hue.ip[0]" type="number" min="0" max="255" class="w-full px-1 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-center" />
                  <input v-model.number="syncConfig.hue.ip[1]" type="number" min="0" max="255" class="w-full px-1 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-center" />
                  <input v-model.number="syncConfig.hue.ip[2]" type="number" min="0" max="255" class="w-full px-1 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-center" />
                  <input v-model.number="syncConfig.hue.ip[3]" type="number" min="0" max="255" class="w-full px-1 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-center" />
               </div>
               <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  <p>Press the push-link button on the bridge, then click Authorize.</p>
                  <button type="button" class="mt-1 px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors">
                     Authorize
                  </button>
               </div>
            </div>
            <div class="flex flex-wrap gap-4">
                 <label class="flex items-center">
                    <input v-model="syncConfig.hue.recv.on" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
                    <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Receive On/Off</span>
                 </label>
                 <label class="flex items-center">
                    <input v-model="syncConfig.hue.recv.bri" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
                    <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Receive Brightness</span>
                 </label>
                 <label class="flex items-center">
                    <input v-model="syncConfig.hue.recv.col" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
                    <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Receive Color</span>
                 </label>
            </div>
       </div>
    </div>
</template>
