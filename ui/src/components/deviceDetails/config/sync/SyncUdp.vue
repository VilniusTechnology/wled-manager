<script setup lang="ts">
const props = defineProps<{
  syncConfig: any
  hwConfig: any
}>()

const toggleGroupBit = (type: 'send' | 'recv', bitIndex: number) => {
  const path = props.syncConfig.sync[type];
  const current = path.grp;
  // Toggle the bit at bitIndex (0-7 corresponding to groups 1-8)
  path.grp = current ^ (1 << bitIndex);
}

const hasGroupBit = (type: 'send' | 'recv', bitIndex: number) => {
  return (props.syncConfig.sync[type].grp & (1 << bitIndex)) !== 0;
}
</script>

<template>
  <div class="space-y-6">
    <!-- WLED Broadcast -->
    <div>
      <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">WLED Broadcast</h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
         <div>
          <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
            UDP Port
          </label>
          <input
            v-model.number="syncConfig.sync.port0"
            type="number"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
        <div>
           <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
            Replication Port
          </label>
          <input
            v-model.number="syncConfig.sync.port1"
            type="number"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
      </div>
      
       <div class="border-b border-gray-200 dark:border-gray-600 pb-4 mb-4">
          <label class="block text-sm font-medium text-gray-800 dark:text-gray-200 mb-2">Sync Groups</label>
          
          <!-- Grid header -->
          <div class="flex items-center gap-1 mb-2">
             <div class="w-16"></div> <!-- Label spacer -->
             <div v-for="i in 8" :key="i" class="w-8 text-center text-xs font-medium text-gray-500 dark:text-gray-400">
                {{ i }}
             </div>
          </div>
  
          <!-- Send Row -->
          <div class="flex items-center gap-1 mb-2">
             <div class="w-16 text-sm font-medium text-gray-600 dark:text-gray-300">Send:</div>
             <div v-for="i in 8" :key="`send-${i}`" class="w-8 flex justify-center">
                <input 
                   type="checkbox" 
                   :checked="hasGroupBit('send', i-1)"
                   @change="toggleGroupBit('send', i-1)"
                   class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded"
                />
             </div>
          </div>
  
          <!-- Receive Row -->
          <div class="flex items-center gap-1">
             <div class="w-16 text-sm font-medium text-gray-600 dark:text-gray-300">Receive:</div>
             <div v-for="i in 8" :key="`recv-${i}`" class="w-8 flex justify-center">
                 <input 
                   type="checkbox" 
                   :checked="hasGroupBit('recv', i-1)"
                   @change="toggleGroupBit('recv', i-1)"
                   class="form-checkbox h-4 w-4 text-orange-500 bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded checked:bg-orange-500 checked:border-orange-500 focus:ring-orange-500"
                />
             </div>
          </div>
       </div>
  
      <div class="space-y-4 border-b border-gray-200 dark:border-gray-600 pb-4 mb-4">
        <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300">Receive</h5>
        <div class="flex flex-wrap gap-4">
           <label class="flex items-center">
              <input v-model="syncConfig.sync.recv.bri" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Brightness</span>
           </label>
           <label class="flex items-center">
              <input v-model="syncConfig.sync.recv.col" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Color</span>
           </label>
           <label class="flex items-center">
              <input v-model="syncConfig.sync.recv.fx" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Effects</span>
           </label>
           <label class="flex items-center">
              <input v-model="syncConfig.sync.recv.seg" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Segment Options</span>
           </label>
           <label class="flex items-center">
              <input v-model="syncConfig.sync.recv.sb" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Segment Bounds</span>
           </label>
        </div>
  
        <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mt-2">Send Notifications On</h5>
        <div class="flex flex-wrap gap-4">
           <label class="flex items-center">
              <input v-model="syncConfig.sync.send.dir" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Direct Change</span>
           </label>
           <label class="flex items-center">
              <input v-model="syncConfig.sync.send.btn" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Button Press</span>
           </label>
           <label class="flex items-center">
              <input v-model="syncConfig.sync.send.va" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Alexa</span>
           </label>
           <label class="flex items-center">
              <input v-model="syncConfig.sync.send.hue" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Hue</span>
           </label>
           <label class="flex items-center">
              <input v-model="syncConfig.sync.send.macro" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Macro</span>
           </label>
           <label class="flex items-center">
              <input v-model="syncConfig.sync.send.twice" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Send notifications twice</span>
           </label>
        </div>
        
        <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mt-2">Hardware Sensors</h5>
        <div class="flex flex-wrap gap-4 mt-2">
           <label class="flex items-center">
              <input v-model="hwConfig.ir.sel" type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded" />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Infrared Receiver</span>
           </label>
        </div>
      </div>
  
      <!-- Instance List -->
      <div>
        <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">Instance List</h4>
        <div class="space-y-4 border-b border-gray-200 dark:border-gray-600 pb-4 mb-4">
          <div class="flex items-center">
             <input
                v-model="syncConfig.nodes.list"
                type="checkbox"
                class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded"
              />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Enable instance list</span>
          </div>
          <div v-if="syncConfig.nodes.list" class="flex items-center">
             <input
                v-model="syncConfig.nodes.bcast"
                type="checkbox"
                class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded"
              />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Broadcast to all neighbors</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
