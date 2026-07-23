<script setup lang="ts">
import { watch } from 'vue'

const props = defineProps<{
  modelValue: any
}>()

defineEmits<{
  'update:modelValue': [value: any]
}>()

// WLED LED Types Mapping
const ledTypes = [
  { id: 22, name: 'WS281x (WS2812B, WS2811)' },
  { id: 30, name: 'SK6812 RGBW' },
  { id: 26, name: 'TM1814' },
  { id: 29, name: 'WS2814 (44DD)' },
  { id: 50, name: 'WS2801 (SPI)' },
  { id: 51, name: 'APA102 (SPI)' },
  { id: 52, name: 'LPD8806 (SPI)' },
  { id: 41, name: 'PWM White' },
  { id: 42, name: 'PWM CCT' },
  { id: 43, name: 'PWM RGB' },
  { id: 44, name: 'PWM RGBW' },
  { id: 45, name: 'PWM RGB+CCT' },
  { id: 80, name: 'On/Off Relay' },
  { id: 81, name: 'DDP Network' },
]

// WLED Color Orders
const colorOrders = [
  { id: 0, name: 'GRB' },
  { id: 1, name: 'RGB' },
  { id: 2, name: 'BRG' },
  { id: 3, name: 'RBG' },
  { id: 4, name: 'GBR' },
  { id: 5, name: 'BGR' },
]

// White Management Options
const whiteManagementOptions = [
  { id: 0, name: 'None' },
  { id: 1, name: 'Brighter' },
  { id: 2, name: 'Accurate' },
  { id: 3, name: 'Dual' },
]

// Button Types
const buttonTypes = [
  { id: 0, name: 'Pushbutton' },
  { id: 1, name: 'Switch (Toggle)' },
  { id: 2, name: 'PIR Sensor' },
  { id: 3, name: 'Touch' },
  { id: 4, name: 'Analog' },
]

// IR Types
const irTypes = [
  { id: 0, name: 'Remote Disabled' },
  { id: 1, name: '24-key RGB' },
  { id: 2, name: '24-key with CT' },
  { id: 3, name: '40-key Blue' },
  { id: 4, name: '44-key RGB' },
  { id: 5, name: '21-key RGB' },
  { id: 6, name: '6-key Black' },
  { id: 7, name: '9-key Red' },
  { id: 8, name: 'JSON Remote' },
]

// Helper to ensure 'ins' array exists for LED
const ensureLedIns = () => {
  if (!props.modelValue.hw.led.ins) {
    props.modelValue.hw.led.ins = []
  }
}

// Helper to ensure 'ins' array exists for Buttons
const ensureBtnIns = () => {
  if (!props.modelValue.hw.btn.ins) {
    props.modelValue.hw.btn.ins = []
  }
}

const addOutput = () => {
  ensureLedIns()
  // Default to WS281x, GRB, pin 2, start after last segment or 0
  const lastOut = props.modelValue.hw.led.ins[props.modelValue.hw.led.ins.length - 1]
  const start = lastOut ? lastOut.start + lastOut.len : 0
  
  props.modelValue.hw.led.ins.push({
    start: start,
    len: 1,
    pin: [2],
    order: 0,
    rev: false,
    skip: false,
    off: false,
    type: 22,
    ref: false
  })
}

const removeOutput = (index: number) => {
  props.modelValue.hw.led.ins.splice(index, 1)
}

const addButton = () => {
  ensureBtnIns()
  props.modelValue.hw.btn.ins.push({
    type: 0,
    pin: [0],
    macros: [0, 0, 0] // Short, Long, Double
  })
}

const removeButton = (index: number) => {
  props.modelValue.hw.btn.ins.splice(index, 1)
}


// Convert pin array to single number for simple types (editing usually handles single pin for non-SPI)
const getPin = (output: any, index: number = 0) => {
  if (Array.isArray(output.pin)) {
    return output.pin[index]
  }
  return output.pin
}

const setPin = (output: any, val: number, index: number = 0) => {
  if (Array.isArray(output.pin)) {
     output.pin[index] = val
  } else {
    output.pin = val
  }
}

// Helper for button macros
const getMacro = (btn: any, index: number) => {
   if (Array.isArray(btn.macros)) return btn.macros[index]
   return 0
}

const setMacro = (btn: any, val: number, index: number) => {
   if (!Array.isArray(btn.macros)) btn.macros = [0, 0, 0]
   btn.macros[index] = val
}

// Auto-calculate totals
watch(() => props.modelValue.hw.led.ins, (newIns) => {
  if (newIns) {
    let total = 0
    newIns.forEach((o: any) => total += (o.len || 0))
    props.modelValue.hw.led.total = total
  }
}, { deep: true })

</script>

<template>
  <div class="space-y-6">
    <!-- Global Settings -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Global LED Settings</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
            Total LEDs
          </label>
          <input
            v-model.number="modelValue.hw.led.total"
            type="number"
            disabled
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-gray-100 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed"
          />
          <p class="text-xs text-gray-500 mt-1">Calculated from outputs</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
            Max Power (mA)
          </label>
          <input
            v-model.number="modelValue.hw.led.maxpwr"
            type="number"
            min="0"
            max="65000"
             class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
          <p class="text-xs text-gray-500 mt-1">0 for unlimited</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
            Target FPS
          </label>
          <input
            v-model.number="modelValue.hw.led.fps"
            type="number"
             class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
        <div>
           <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
            White Management
          </label>
          <select
            v-model.number="modelValue.hw.led.rgbwm"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option v-for="opt in whiteManagementOptions" :key="opt.id" :value="opt.id">{{ opt.name }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- LED Outputs -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">LED Outputs</h3>
        <button
          @click="addOutput"
          class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
        >
          + Add Output
        </button>
      </div>

      <div class="space-y-4">
        <div
          v-for="(output, index) in modelValue.hw.led.ins"
          :key="index"
          class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-4 relative"
        >
          <div class="absolute top-4 right-4">
             <button
              @click="removeOutput(Number(index))"
              class="text-red-500 hover:text-red-700"
              title="Remove Output"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>

          <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-3">Output {{ Number(index) + 1 }}</h4>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <!-- Type -->
             <div class="col-span-1 md:col-span-2">
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Type</label>
              <select
                v-model.number="output.type"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
              >
                <option v-for="t in ledTypes" :key="t.id" :value="t.id">{{ t.name }}</option>
              </select>
            </div>

            <!-- Color Order -->
             <div>
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Color Order</label>
              <select
                v-model.number="output.order"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
              >
                <option v-for="c in colorOrders" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>

            <!-- Length -->
             <div>
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Length</label>
               <input
                v-model.number="output.len"
                type="number"
                min="1"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
              />
            </div>

            <!-- Start -->
             <div>
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Start Address</label>
               <input
                v-model.number="output.start"
                type="number"
                min="0"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
              />
            </div>

            <!-- GPIO Pin(s) -->
             <div>
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">GPIO Pin</label>
               <input
                :value="getPin(output)"
                @input="e => setPin(output, Number((e.target as HTMLInputElement).value))"
                type="number"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
              />
            </div>
            
            <!-- Flags -->
            <div class="flex items-center space-x-4 mt-6">
                <label class="flex items-center space-x-2 cursor-pointer">
                    <input type="checkbox" v-model="output.rev" class="rounded text-blue-600 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600" />
                    <span class="text-sm text-gray-700 dark:text-gray-300">Reverse</span>
                </label>
                <label class="flex items-center space-x-2 cursor-pointer">
                    <input type="checkbox" v-model="output.skip" class="rounded text-blue-600 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600" />
                    <span class="text-sm text-gray-700 dark:text-gray-300">Skip First</span>
                </label>
                <label class="flex items-center space-x-2 cursor-pointer">
                    <input type="checkbox" v-model="output.off" class="rounded text-blue-600 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600" />
                    <span class="text-sm text-gray-700 dark:text-gray-300">Off Refresh</span>
                </label>
            </div>

          </div>
        </div>
        <div v-if="!modelValue.hw.led.ins || modelValue.hw.led.ins.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-4">
             No LED outputs configured.
        </div>
      </div>
    </div>
    
    <!-- Defaults & Transitions -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Defaults -->
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Defaults</h3>
        <div class="space-y-4">
           <div class="flex items-center justify-between">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Turn on after power up</label>
             <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="modelValue.def.on" class="sr-only peer">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
           </div>
           
           <div>
             <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">Default Brightness (0-255)</label>
             <input
               v-model.number="modelValue.def.bri"
               type="number"
               min="0"
               max="255"
               class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
             />
           </div>

           <div>
             <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">Apply Preset ID at Boot</label>
             <input
               v-model.number="modelValue.def.ps"
               type="number"
               min="0"
               class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
             />
             <p class="text-xs text-gray-500 mt-1">0 for none</p>
           </div>
        </div>
      </div>

      <!-- Transitions -->
       <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Transitions</h3>
         <div class="space-y-4">
           <div class="flex items-center justify-between">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Enable Transitions</label>
             <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="modelValue.light.tr.mode" class="sr-only peer">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
           </div>

           <div>
             <label class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">Transition Time (x 100ms)</label>
             <input
               v-model.number="modelValue.light.tr.dur"
               type="number"
               min="0"
               class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
             />
             <p class="text-xs text-gray-500 mt-1">Value of 7 = 700ms</p>
           </div>
           
           <div class="flex items-center justify-between">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Palette Transitions</label>
             <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="modelValue.light.tr.pal" class="sr-only peer">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
           </div>

         </div>
      </div>
    </div>
    
    <!-- Hardware: Buttons, IR, Relay -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Hardware Setup</h3>
      
      <!-- Buttons -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-sm font-medium text-gray-700 dark:text-gray-200">Buttons</h4>
          <button @click="addButton" class="text-xs px-2 py-1 bg-blue-600 text-white rounded">+ Add Button</button>
        </div>
        <div class="space-y-3">
           <div v-for="(btn, idx) in modelValue.hw.btn.ins" :key="idx" class="flex flex-col md:flex-row gap-3 items-start md:items-center bg-white dark:bg-gray-800 p-3 rounded border border-gray-200 dark:border-gray-600">
              <div class="w-full md:w-auto flex-1">
                 <label class="block text-xs text-gray-500 mb-1">GPIO</label>
                 <input type="number" :value="getPin(btn)" @input="e => setPin(btn, Number((e.target as HTMLInputElement).value))" class="w-full text-sm px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
              </div>
              <div class="w-full md:w-auto flex-1">
                 <label class="block text-xs text-gray-500 mb-1">Type</label>
                 <select v-model.number="btn.type" class="w-full text-sm px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                    <option v-for="t in buttonTypes" :key="t.id" :value="t.id">{{t.name}}</option>
                 </select>
              </div>
               <!-- Macros -->
               <div class="w-full md:w-auto flex flex-col sm:flex-row gap-2 flex-[2]">
                 <div class="flex-1">
                   <label class="block text-xs text-gray-500 mb-1">Short (Preset)</label>
                   <input type="number" :value="getMacro(btn, 0)" @input="e => setMacro(btn, Number((e.target as HTMLInputElement).value), 0)" class="w-full text-sm px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
                 </div>
                  <div class="flex-1">
                   <label class="block text-xs text-gray-500 mb-1">Long</label>
                   <input type="number" :value="getMacro(btn, 1)" @input="e => setMacro(btn, Number((e.target as HTMLInputElement).value), 1)" class="w-full text-sm px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
                 </div>
                  <div class="flex-1">
                   <label class="block text-xs text-gray-500 mb-1">Double</label>
                   <input type="number" :value="getMacro(btn, 2)" @input="e => setMacro(btn, Number((e.target as HTMLInputElement).value), 2)" class="w-full text-sm px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
                 </div>
               </div>
              <button @click="removeButton(idx)" class="text-red-500 hover:text-red-700 mt-4 md:mt-0">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
           </div>
        </div>
      </div>
      
      <!-- IR & Relay -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
           <h4 class="text-sm font-medium text-gray-700 dark:text-gray-200 mb-3">IR Receiver</h4>
           <div class="grid grid-cols-2 gap-3">
             <div>
                <label class="block text-xs text-gray-500 mb-1">GPIO</label>
                <input v-model.number="modelValue.hw.ir.pin" type="number" class="w-full text-sm px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
             </div>
             <div>
                <label class="block text-xs text-gray-500 mb-1">Type</label>
                <select v-model.number="modelValue.hw.ir.type" class="w-full text-sm px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                   <option v-for="t in irTypes" :key="t.id" :value="t.id">{{t.name}}</option>
                </select>
             </div>
           </div>
        </div>
        
        <div>
           <h4 class="text-sm font-medium text-gray-700 dark:text-gray-200 mb-3">Relay</h4>
           <div class="flex items-end gap-3">
             <div class="flex-1">
                <label class="block text-xs text-gray-500 mb-1">GPIO</label>
                <input v-model.number="modelValue.hw.relay.pin" type="number" class="w-full text-sm px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
             </div>
             <div class="flex-1 pb-2">
                 <label class="flex items-center space-x-2 cursor-pointer">
                    <input type="checkbox" v-model="modelValue.hw.relay.rev" class="rounded text-blue-600 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600" />
                    <span class="text-sm text-gray-700 dark:text-gray-300">Invert</span>
                </label>
             </div>
           </div>
        </div>
      </div>

    </div>

  </div>
</template>
