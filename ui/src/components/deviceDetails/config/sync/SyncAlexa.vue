<script setup lang="ts">
defineProps<{
  syncConfig: any
}>()
</script>

<template>
    <!-- Alexa Voice Assistant -->
    <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">Alexa Voice Assistant</h4>
    <div class="space-y-4 border-b border-gray-200 dark:border-gray-600 pb-4 mb-4">
       <div class="flex items-center mb-4">
          <input
            v-model="syncConfig.va.alexa"
            type="checkbox"
            class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded"
          />
          <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Emulate Alexa device</span>
       </div>
       
       <div v-if="syncConfig.va.alexa">
         <div class="flex items-center mb-4">
            <label class="w-48 text-sm font-medium text-gray-600 dark:text-gray-300">Alexa invocation name:</label>
            <input v-model="syncConfig.va.n" type="text" class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white" />
         </div>
         
         <div class="flex items-center mb-4">
             <label class="text-sm font-medium text-gray-600 dark:text-gray-300 mr-2">Also emulate devices to call the first</label>
             <input v-model.number="syncConfig.va.p" type="number" min="0" class="w-16 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white mx-2" />
             <span class="text-sm text-gray-600 dark:text-gray-400">presets</span>
         </div>
       </div>
    </div>
</template>
