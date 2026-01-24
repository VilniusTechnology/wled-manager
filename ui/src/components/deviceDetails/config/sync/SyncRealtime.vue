<script setup lang="ts">
defineProps<{
  syncConfig: any
}>()
</script>

<template>
  <!-- Realtime -->
  <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">Realtime</h4>
  <div class="space-y-4 border-b border-gray-200 dark:border-gray-600 pb-4 mb-4">
     <!-- Top Realtime Options -->
     <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex items-center">
           <input
             v-model="syncConfig.live.mso"
             type="checkbox"
             class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded"
           />
           <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Use main segment only</span>
        </div>
        <div class="flex items-center">
           <input
             v-model="syncConfig.live.en"
             type="checkbox"
             class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded"
           />
           <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Receive UDP Realtime</span>
        </div>
     </div>

     <!-- Network DMX Input -->
     <div class="mt-6">
       <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 italic mb-3">Network DMX input</h5>
       <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
           <div>
              <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">Type</label>
               <select v-model.number="syncConfig.live.dmx.type" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
                  <option :value="0">Disabled</option>
                  <option :value="1">E1.31 (sACN)</option>
                  <option :value="2">Art-Net</option>
                  <option :value="4">DDP</option>
               </select>
           </div>
           
           <div class="flex items-center mt-6">
               <input
                 v-model="syncConfig.live.mc"
                 type="checkbox"
                 class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded"
               />
               <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Multicast</span>
           </div>

           <div>
             <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">Start universe</label>
             <input v-model.number="syncConfig.live.dmx.uni" type="number" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white" />
           </div>

           <div class="flex items-center mt-6">
               <input
                 v-model="syncConfig.live.dmx.seqskip"
                 type="checkbox"
                 class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded"
               />
               <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Skip out-of-sequence packets</span>
            </div>

           <div>
             <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">DMX start address</label>
             <input v-model.number="syncConfig.live.dmx.addr" type="number" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white" />
           </div>

           <div>
             <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">DMX segment spacing</label>
             <input v-model.number="syncConfig.live.dmx.dss" type="number" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white" />
           </div>
           
           <div>
               <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">E1.31 port priority</label>
               <input v-model.number="syncConfig.live.dmx.e131prio" type="number" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white" />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">DMX mode</label>
               <select v-model.number="syncConfig.live.dmx.mode" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
                  <option :value="1">Single RGB</option>
                  <option :value="2">Single DRGB</option>
                  <option :value="3">Effect</option>
                  <option :value="4">Multi RGB</option>
                  <option :value="5">Dimmer + Multi RGB</option>
                  <option :value="6">Multi RGBW</option>
               </select>
           </div>
       </div>

       <!-- Bottom Realtime Settings -->
       <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
           <div>
               <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">Timeout (ms)</label>
               <input v-model.number="syncConfig.live.timeout" type="number" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white" />
           </div>
           
           <div class="flex items-center mt-6">
               <input
                 v-model="syncConfig.live.maxbri"
                 type="checkbox"
                 class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded"
               />
               <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Force max brightness</span>
            </div>
            
            <div class="flex items-center">
               <input
                 v-model="syncConfig.live['no-gc']"
                 type="checkbox"
                 class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded"
               />
               <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Disable realtime gamma correction</span>
            </div>
            
            <div>
               <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">Realtime LED offset</label>
               <input v-model.number="syncConfig.live.offset" type="number" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white" />
            </div>
       </div>
     </div>
  </div>
</template>
