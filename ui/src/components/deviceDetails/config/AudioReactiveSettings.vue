<script setup lang="ts">
import { computed, watch } from 'vue'

interface Props {
  modelValue: Record<string, any>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

// Default structure for AudioReactive
// Corrected based on WLED documentation and source analysis
const defaultAudioReactive = {
  enabled: false,
  analogmic: {
    pin: -1
  },
  digitalmic: {
    type: 1, // Generic I2S
    pin: [32, 15, 14, -1] // [SD, WS, SCK, MCLK]
  },
  config: {
    squelch: 10,
    gain: 60,
    AGC: 1
  },
  dynamics: {
    limiter: true,
    rise: 80,
    fall: 300
  },
  frequency: {
    scale: 1 // 1: Linear
  },
  sync: {
    port: 11988,
    mode: 0 // 0: None, 1: Send, 2: Receive
  }
}

const micTypes = [
  { id: 0, name: 'Analog' },
  { id: 1, name: 'Generic I2S' },
  { id: 2, name: 'ES7243' },
  { id: 3, name: 'SPH0645' },
  { id: 4, name: 'Generic I2S PDM' },
  { id: 5, name: 'MNx4466 (Analog)' }
]

const frequencyScales = [
  { id: 0, name: 'None' },
  { id: 1, name: 'Linear' },
  { id: 2, name: 'Square Root' },
  { id: 3, name: 'Logarithmic' }
]

// Accessor for the specific AudioReactive object within the user mods map
const audioConfig = computed({
  get: () => props.modelValue?.AudioReactive || null,
  set: (val) => {
    emit('update:modelValue', {
      ...props.modelValue,
      AudioReactive: val
    })
  }
})

// Enable function
const enableAudioReactive = () => {
    emit('update:modelValue', {
      ...props.modelValue,
      AudioReactive: { ...defaultAudioReactive, enabled: true }
    })
}

// Disable function (removes it or sets enabled: false)
const toggleEnabled = () => {
    if (!audioConfig.value) {
        enableAudioReactive()
        return
    }
    const newVal = { ...audioConfig.value, enabled: !audioConfig.value.enabled }
    // Update the full modelValue
    emit('update:modelValue', {
      ...props.modelValue,
      AudioReactive: newVal
    })
}

// Ensure defaults are populated for existing configurations that might miss new fields
const ensureDefaults = () => {
    const ar = props.modelValue?.AudioReactive
    if (!ar) return

    // Deep merge defaults where missing
    const newConfig = { ...ar }
    let hasChanges = false

    // Helper to merge nested objects
    const mergeSection = (sectionKey: string, sectionDefaults: any) => {
        if (!newConfig[sectionKey]) {
            newConfig[sectionKey] = { ...sectionDefaults }
            hasChanges = true
        } else {
             for (const [key, value] of Object.entries(sectionDefaults)) {
                if (newConfig[sectionKey][key] === undefined) {
                    newConfig[sectionKey][key] = value
                    hasChanges = true
                }
             }
        }
    }

    mergeSection('config', defaultAudioReactive.config)
    mergeSection('dynamics', defaultAudioReactive.dynamics)
    mergeSection('frequency', defaultAudioReactive.frequency)
    
    // Only valid if digitalmic exists to avoid overwriting wrong mic type setup
    if (!newConfig.digitalmic) {
         // If completely missing, we can probably safely default it?
         // But maybe it's an analog setup. 
         // Let's safe-guard: if analogmic exists and digitalmic doesn't, don't force digitalmic
         if (!newConfig.analogmic) {
             newConfig.digitalmic = { ...defaultAudioReactive.digitalmic }
             hasChanges = true
         }
    }

    if (hasChanges) {
        emit('update:modelValue', {
            ...props.modelValue,
            AudioReactive: newConfig
        })
    }
}

watch(() => props.modelValue?.AudioReactive, () => {
    ensureDefaults()
}, { immediate: true })

</script>

<template>
  <div class="space-y-6">
    
    <!-- Header / Toggle -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
                 <div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                    <svg class="w-6 h-6 text-purple-600 dark:text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                    </svg>
                 </div>
                 <div>
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white">Audio Reactive</h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Sync lights with music</p>
                 </div>
            </div>
             
            <button 
                type="button"
                role="switch"
                :aria-checked="audioConfig?.enabled"
                @click="toggleEnabled"
                :class="[
                  audioConfig?.enabled ? 'bg-purple-600' : 'bg-gray-200 dark:bg-gray-600',
                  'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2'
                ]"
            >
                <span
                  aria-hidden="true"
                  :class="[
                    audioConfig?.enabled ? 'translate-x-5' : 'translate-x-0',
                    'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                  ]"
                />
            </button>
        </div>
    </div>

    <!-- Configuration Settings (Only if enabled) -->
    <div v-if="audioConfig" :class="{'opacity-50 pointer-events-none': !audioConfig.enabled}" class="space-y-6 transition-opacity duration-200">
        
        <!-- Microphone Configuration -->
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
            <h4 class="text-base font-medium text-gray-900 dark:text-gray-100 mb-4 border-b border-gray-100 dark:border-gray-700 pb-2">Microphone</h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Type Selection -->
                 <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Type
                    </label>
                    <select
                        v-model.number="audioConfig.digitalmic.type"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-purple-500 focus:border-purple-500"
                    >
                        <option v-for="type in micTypes" :key="type.id" :value="type.id">
                            {{ type.name }}
                        </option>
                    </select>
                </div>

                <!-- I2S Pins -->
                 <div v-if="audioConfig.digitalmic.type !== 0 && audioConfig.digitalmic.type !== 5" class="col-span-1 md:col-span-2 space-y-4">
                     <p class="text-xs font-semibold text-gray-500 uppercase">I2S Digital Pins</p>
                     <div class="grid grid-cols-3 gap-4">
                        <div>
                             <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">SD Pin</label>
                             <input type="number" v-model.number="audioConfig.digitalmic.pin[0]" class="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white" />
                        </div>
                         <div>
                             <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">WS Pin</label>
                             <input type="number" v-model.number="audioConfig.digitalmic.pin[1]" class="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white" />
                        </div>
                         <div>
                             <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">SCK Pin</label>
                             <input type="number" v-model.number="audioConfig.digitalmic.pin[2]" class="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white" />
                        </div>
                     </div>
                 </div>

                 <!-- Analog Pin -->
                 <div v-if="audioConfig.digitalmic.type === 0 || audioConfig.digitalmic.type === 5">
                     <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Analog Pin
                    </label>
                    <input
                        type="number"
                        v-model.number="audioConfig.analogmic.pin"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-purple-500 focus:border-purple-500"
                    />
                 </div>
            </div>
        </div>

        <!-- Audio Processing -->
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
            <h4 class="text-base font-medium text-gray-900 dark:text-gray-100 mb-4 border-b border-gray-100 dark:border-gray-700 pb-2">Audio Processing</h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Squelch -->
                <div>
                     <label class="flex justify-between text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        <span>Squelch</span>
                        <span class="text-gray-500">{{ audioConfig.config.squelch }}</span>
                    </label>
                    <input 
                        type="range" 
                        min="0" 
                        max="255" 
                        v-model.number="audioConfig.config.squelch"
                        class="w-full"
                    />
                    <p class="text-xs text-gray-500 mt-1">Minimum volume threshold to trigger effects</p>
                </div>

                <!-- Gain -->
                <div>
                     <label class="flex justify-between text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        <span>Gain</span>
                        <span class="text-gray-500">{{ audioConfig.config.gain }}</span>
                    </label>
                    <input 
                        type="range" 
                        min="0" 
                        max="255" 
                        v-model.number="audioConfig.config.gain"
                        class="w-full"
                    />
                    <p class="text-xs text-gray-500 mt-1">Input signal amplification</p>
                </div>
                
                 <!-- AGC -->
                <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded border border-gray-100 dark:border-gray-600">
                    <div>
                        <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Automatic Gain Control (AGC)</label>
                        <p class="text-xs text-gray-500">Automatically adjust gain based on volume</p>
                    </div>
                    <select
                        v-model.number="audioConfig.config.AGC"
                        class="px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-purple-500 focus:border-purple-500"
                     >
                        <option :value="0">Off</option>
                        <option :value="1">Normal</option>
                        <option :value="2">Vivid</option>
                        <option :value="3">Lazy</option>
                     </select>
                </div>
            </div>
        </div>

        <!-- Frequency & Dynamics -->
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
            <h4 class="text-base font-medium text-gray-900 dark:text-gray-100 mb-4 border-b border-gray-100 dark:border-gray-700 pb-2">Frequency & Dynamics</h4>
            
            <div class="space-y-6">
                 <!-- Frequency Scale -->
                 <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Frequency Scaling
                    </label>
                    <select
                        v-model.number="audioConfig.frequency.scale"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-purple-500 focus:border-purple-500"
                    >
                        <option v-for="scale in frequencyScales" :key="scale.id" :value="scale.id">
                            {{ scale.name }}
                        </option>
                    </select>
                </div>

                <!-- Dynamics -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Limiter -->
                    <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded border border-gray-100 dark:border-gray-600 col-span-1 md:col-span-2">
                        <div>
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Dynamics Limiter</label>
                            <p class="text-xs text-gray-500">Limit rapid volume changes</p>
                        </div>
                        <button 
                            type="button"
                            role="switch"
                            :aria-checked="audioConfig.dynamics.limiter"
                            @click="audioConfig.dynamics.limiter = !audioConfig.dynamics.limiter"
                            :class="[
                              audioConfig.dynamics.limiter ? 'bg-purple-600' : 'bg-gray-200 dark:bg-gray-600',
                              'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2'
                            ]"
                        >
                            <span
                              aria-hidden="true"
                              :class="[
                                audioConfig.dynamics.limiter ? 'translate-x-5' : 'translate-x-0',
                                'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                              ]"
                            />
                        </button>
                    </div>

                    <!-- Rise Time -->
                    <div>
                         <label class="flex justify-between text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            <span>Rise Time</span>
                            <span class="text-gray-500">{{ audioConfig.dynamics.rise }} ms</span>
                        </label>
                        <input 
                            type="range" 
                            min="0" 
                            max="1000" 
                            step="10"
                            v-model.number="audioConfig.dynamics.rise"
                            class="w-full"
                        />
                    </div>

                    <!-- Fall Time -->
                     <div>
                         <label class="flex justify-between text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            <span>Fall Time</span>
                            <span class="text-gray-500">{{ audioConfig.dynamics.fall }} ms</span>
                        </label>
                        <input 
                            type="range" 
                            min="0" 
                            max="3000" 
                            step="10"
                            v-model.number="audioConfig.dynamics.fall"
                            class="w-full"
                        />
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Synchronization -->
        <div v-if="audioConfig.sync" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
            <h4 class="text-base font-medium text-gray-900 dark:text-gray-100 mb-4 border-b border-gray-100 dark:border-gray-700 pb-2">Synchronization</h4>
             <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                 <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Sync Mode
                    </label>
                    <select
                        v-model.number="audioConfig.sync.mode"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-purple-500 focus:border-purple-500"
                    >
                        <option :value="0">Disabled</option>
                        <option :value="1">Send</option>
                        <option :value="2">Receive</option>
                    </select>
                 </div>
                 
                 <div v-if="audioConfig.sync.mode !== 0">
                     <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        UDP Port
                    </label>
                    <input
                        type="number"
                        v-model.number="audioConfig.sync.port"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-purple-500 focus:border-purple-500"
                    />
                 </div>
             </div>
        </div>

    </div>
  </div>
</template>
