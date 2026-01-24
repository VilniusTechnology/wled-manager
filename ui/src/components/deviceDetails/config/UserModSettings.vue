<script setup lang="ts">
interface Props {
  modelValue: Record<string, any>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

// Helper to check value types
const isBoolean = (val: any) => typeof val === 'boolean'
const isNumber = (val: any) => typeof val === 'number'
const isString = (val: any) => typeof val === 'string'
const isObject = (val: any) => val !== null && typeof val === 'object' && !Array.isArray(val)

const formatKey = (key: string) => {
  // Convert camelCase or snake_case to Title Case
  return key
    .replace(/([A-Z])/g, ' $1')
    .replace(/_/g, ' ')
    .replace(/^./, (str) => str.toUpperCase())
    .trim()
}

// Default configuration for AudioReactive if missing
const addAudioReactive = () => {
  // Always allow adding/resetting if called
  // Basic defaults based on common WLED AudioReactive user mod structures
    const defaults = {
      enabled: true,
      analogmic: {
        pin: -1
      },
      digitalmic: {
        type: 1,
        pin: [32, 15, 14, -1] // Common default pins
      },
      config: {
         squelch: 10,
         gain: 60,
         AGC: 1 
      }
    }
    // We need to update the prop. Since it's a reactive object passed by reference/v-model, 
    // we can try mutating it, but cleaner to emit update if possible.
    // However, modelValue is likely a ref from parent. 
    // Vue props are readonly. We should emit.
    const newVal = { ...props.modelValue, AudioReactive: defaults }
    emit('update:modelValue', newVal)
  }

  const filteredUserMods = computed(() => {
    const mods = { ...props.modelValue }
    delete mods.AudioReactive
    return mods
  })

  // Import computed
  import { computed } from 'vue'

</script>

<template>
  <div class="space-y-6">
    <div v-if="Object.keys(modelValue).length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <p>No User Mods configuration found.</p>
      <p class="text-sm mt-2 opacity-75">This device might not have any user mods installed or they don't expose configuration via JSON.</p>
      
      <!-- Manual Add Actions -->
      <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
        <p class="text-xs text-gray-500 mb-2">Don't see a mod you expect?</p>
        <!-- Removed AudioReactive button as it is now in its own tab -->
        <p class="text-xs text-gray-400 italic">Check the dedicated tabs for specific features like Audio Reactive.</p>
      </div>
    </div>

    <!-- Actions Bar (if mods exist but maybe AR is missing or empty) -->
    <div v-else class="space-y-6">
        <div v-if="!modelValue['AudioReactive'] || (typeof modelValue['AudioReactive'] === 'object' && Object.keys(modelValue['AudioReactive']).length === 0)" class="flex justify-end hidden">
             <button 
               @click="addAudioReactive"
               class="text-xs text-blue-600 hover:text-blue-500 dark:text-blue-400 flex items-center bg-blue-50 dark:bg-blue-900/20 px-3 py-1.5 rounded border border-blue-100 dark:border-blue-800 transition-colors"
            >
              <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
              Add AudioReactive Config
            </button>
        </div>
    </div>

    <!-- Mod Card List -->
    <div v-for="(modConfig, modName) in filteredUserMods" :key="modName" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
        {{ formatKey(String(modName)) }}
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Recursively render fields -->
        <template v-for="(val, key) in modConfig" :key="key">
            
            <!-- Boolean Field -->
            <div v-if="isBoolean(val)" class="flex flex-col justify-end h-full min-h-[60px]">
                <div class="flex items-center justify-between p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded">
                  <label :for="`${modName}-${key}`" class="text-sm font-medium text-gray-600 dark:text-gray-300">
                      {{ formatKey(String(key)) }}
                  </label>
                  <button 
                    :id="`${modName}-${key}`"
                    type="button"
                    role="switch"
                    :aria-checked="val"
                    @click="modConfig[key] = !val"
                    :class="[
                      val ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600',
                      'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                    ]"
                  >
                    <span
                      aria-hidden="true"
                      :class="[
                        val ? 'translate-x-5' : 'translate-x-0',
                        'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                      ]"
                    />
                  </button>
                </div>
            </div>

            <!-- Number Field -->
            <div v-else-if="isNumber(val)">
                <label :for="`${modName}-${key}`" class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
                    {{ formatKey(String(key)) }}
                </label>
                <input
                    :id="`${modName}-${key}`"
                    type="number"
                    v-model.number="modConfig[key]"
                    step="any"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                />
            </div>

            <!-- String Field -->
            <div v-else-if="isString(val)">
                <label :for="`${modName}-${key}`" class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
                    {{ formatKey(String(key)) }}
                </label>
                <input
                    :id="`${modName}-${key}`"
                    type="text"
                    v-model="modConfig[key]"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                />
            </div>

            <!-- Nested Object (Grouping full nested objects) -->
            <div v-else-if="isObject(val)" class="col-span-full bg-black/5 dark:bg-white/5 rounded p-4 mt-2">
                 <h4 class="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-3 border-b border-gray-200 dark:border-gray-600 pb-2">{{ formatKey(String(key)) }}</h4>
                 <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                     <div v-for="(subVal, subKey) in val" :key="subKey">
                         <!-- Boolean Sub-Field -->
                        <div v-if="isBoolean(subVal)" class="flex items-center justify-between p-2">
                            <label :for="`${modName}-${key}-${subKey}`" class="text-sm text-gray-600 dark:text-gray-300">
                                {{ formatKey(String(subKey)) }}
                            </label>
                            <input 
                                :id="`${modName}-${key}-${subKey}`"
                                type="checkbox" 
                                v-model="val[subKey]"
                                class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700" 
                            />
                        </div>
                         <!-- Number Sub-Field -->
                        <div v-else-if="isNumber(subVal)">
                            <label :for="`${modName}-${key}-${subKey}`" class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                                {{ formatKey(String(subKey)) }}
                            </label>
                             <input
                                :id="`${modName}-${key}-${subKey}`"
                                type="number"
                                v-model.number="val[subKey]"
                                class="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                            />
                        </div>
                         <!-- String Sub-Field -->
                        <div v-else-if="isString(subVal)">
                             <label :for="`${modName}-${key}-${subKey}`" class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                                {{ formatKey(String(subKey)) }}
                            </label>
                             <input
                                :id="`${modName}-${key}-${subKey}`"
                                type="text"
                                v-model="val[subKey]"
                                class="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                            />
                        </div>
                     </div>
                 </div>
            </div>
            
            <!-- Array Handling -->
            <div v-else-if="Array.isArray(val)" class="col-span-full">
                 <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
                    {{ formatKey(String(key)) }} (List)
                </label>
                <div class="text-xs text-gray-500 dark:text-gray-400 p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded">
                    {{ JSON.stringify(val) }}
                </div>
            </div>
            
        </template>
      </div>
    </div>
  </div>
</template>
