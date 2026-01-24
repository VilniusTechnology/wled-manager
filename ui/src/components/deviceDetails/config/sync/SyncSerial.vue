<script setup lang="ts">
defineProps<{
  hwConfig: any
}>()
</script>

<template>
    <!-- Serial -->
    <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-600">
        <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">Serial</h4>
        <div class="space-y-4">
           <div>
             <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
               Baud Rate
             </label>
             <select v-model.number="hwConfig.baud" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
                <option :value="1152">115200</option>
                <option :value="2304">230400</option>
                <option :value="4608">460800</option>
                <option :value="9216">921600</option>
                <option :value="1500">1500000</option>
             </select>
           </div>
        </div>
    </div>
</template>
