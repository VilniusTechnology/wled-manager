<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { buildApiUrl, API_ENDPOINTS } from '../../utils/apiConfig'
import { useDeviceDetails } from '../../composables/useDeviceDetails'
import SecretActionModal from '../secrets/SecretActionModal.vue'
import DeviceIdentitySettings from './config/DeviceIdentitySettings.vue'
import NetworkSettings from './config/NetworkSettings.vue'
import LedConfiguration from './config/LedConfiguration.vue'
import LightSettings from './config/LightSettings.vue'
import SyncSettings from './config/SyncSettings.vue'
import UserModSettings from './config/UserModSettings.vue'
import AudioReactiveSettings from './config/AudioReactiveSettings.vue'

interface DeviceDetails {
  device_id: string
  mac: string
  latest_config?: any
}

interface Props {
  device: DeviceDetails
  disabled?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  configUpdated: []
}>()

const route = useRoute()
const router = useRouter()
const { refreshDeviceDetails } = useDeviceDetails()

const isSaving = ref(false)
const isRefreshing = ref(false)
const saveMessage = ref('')
const saveError = ref('')

const refreshConfig = async () => {
  if (!props.device.device_id) return
  
  isRefreshing.value = true
  saveMessage.value = ''
  saveError.value = ''
  
  try {
    const result = await refreshDeviceDetails(props.device.device_id)
    if (result) {
      if (result.latest_config) {
        // Force deep merge update
        // Reset to initial state first to clear any dirty state
        configForm.value = JSON.parse(JSON.stringify(INITIAL_CONFIG))
        
        // Force deep merge update
        configForm.value = deepMerge(configForm.value, result.latest_config)
        
        // Also ensure specific modules are updated if structure differs 
        if (result.latest_config.um) {
          configForm.value.um = JSON.parse(JSON.stringify(result.latest_config.um))
        }
        
        console.log('Final configForm.um:', configForm.value.um)
        
        saveMessage.value = 'Configuration successfully reloaded from device'
        // Clear message after 3 seconds
        setTimeout(() => { saveMessage.value = '' }, 3000)
      } else {
        saveError.value = 'Device is online but returned no configuration'
      }
    } else {
      saveError.value = 'Failed to load fresh configuration from device (Timeout or Connection Error)'
    }
  } catch (error) {
    console.error('Manual refresh failed:', error)
    saveError.value = 'Error refreshing configuration'
  } finally {
    isRefreshing.value = false
  }
}

// Secret Modal State
const secretModal = ref({
  isOpen: false,
  targetField: 'wifi' as 'wifi' | 'wifi2' | 'mqtt',
  action: 'copy' as 'copy' | 'paste',
  currentValue: ''
})

const activeTab = ref('general')

const tabs = [
  { id: 'general', name: 'General', description: 'Device identity and basic light settings' },
  { id: 'network', name: 'Network', description: 'WiFi, Ethernet and AP settings' },
  { id: 'leds', name: 'LEDs', description: 'LED outputs and hardware setup' },
  { id: 'interfaces', name: 'Interfaces', description: 'Sync, MQTT and other interfaces' },
  { id: 'audio', name: 'Audio', description: 'Configure Audio Reactive settings' },
  { id: 'usermods', name: 'User Mods', description: 'Configure installed user modules' },
  { id: 'raw', name: 'Raw Data', description: 'View complete configuration JSON' }
]

// Sync tab with URL
watch(() => route.query.subTab, (newTab) => {
  const rawTab = Array.isArray(newTab) ? newTab[0] : newTab
  if (rawTab && typeof rawTab === 'string' && tabs.find(t => t.id === rawTab)) {
    activeTab.value = rawTab
  }
}, { immediate: true })

watch(activeTab, (newTab) => {
  if (route.query.subTab !== newTab) {
    router.replace({ query: { ...route.query, subTab: newTab } })
  }
})


const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text).catch(err => {
    console.error('Failed to copy to clipboard:', err)
  })
}

const openSecretModal = (action: 'copy' | 'paste', field: 'wifi' | 'wifi2' | 'mqtt') => {
  secretModal.value.targetField = field
  secretModal.value.action = action
  secretModal.value.isOpen = true
  
  // For copy, set the current value
  if (action === 'copy') {
    if (field === 'wifi') {
      secretModal.value.currentValue = configForm.value.nw.ins[0].psk || ''
    } else if (field === 'wifi2') {
      secretModal.value.currentValue = configForm.value.nw.ins[1]?.psk || ''
    } else {
      secretModal.value.currentValue = configForm.value.if.mqtt.psk || ''
    }
  }
}

const handleSecretPaste = (value: string) => {
  if (secretModal.value.targetField === 'wifi') {
    configForm.value.nw.ins[0].psk = value
  } else if (secretModal.value.targetField === 'wifi2') {
    if (configForm.value.nw.ins[1]) {
      configForm.value.nw.ins[1].psk = value
    }
  } else {
    configForm.value.if.mqtt.psk = value
  }
}

// Form data structure based on WLED configuration
// Form data structure based on WLED configuration
const INITIAL_CONFIG = {
  // Device Identity
  id: {
    mdns: '',
    name: '',
    inv: ''
  },
  // Network Settings
  nw: {
    ins: [{
      ssid: '',
      pskl: 0,
      psk: '', // Field for sending new password
      ip: [0, 0, 0, 0],
      gw: [0, 0, 0, 0],
      sn: [0, 0, 0, 0]
    }, {
      ssid: '',
      pskl: 0,
      psk: '',
      ip: [0, 0, 0, 0],
      gw: [0, 0, 0, 0],
      sn: [0, 0, 0, 0]
    }],
    dns: [0, 0, 0, 0],
    espnow: false, // ESP-NOW enable (WLED expects boolean at nw.espnow)
    linked_remote: [] // ESP-NOW linked remote MAC addresses
  },
  // Access Point
  ap: {
    ssid: '',
    pskl: 0,
    psk: '', // Access Point password
    chan: 1,
    hide: 0,
    behav: 0,
    ip: [0, 0, 0, 0]
  },
  // WiFi
  wifi: {
    sleep: true,
    phy: false // Force 802.11g
  },
  // Ethernet
  eth: {
    type: 0
  },
  // Hardware
  hw: {
    led: {
      total: 0,
      maxpwr: 0,
      ledma: 0,
      cct: false,
      cr: false,
      cb: 0,
      fps: 0,
      rgbwm: 0,
      ld: false,
      ins: [{
        start: 0,
        len: 0,
        pin: [0],
        order: 0,
        rev: false,
        skip: 0,
        type: 0,
        ref: false,
        rgbwm: 0,
        freq: 0
      }]
    },
    btn: {
      max: 0,
      pull: true,
      tt: 0,
      mqtt: false,
      ins: []
    },
    ir: {
      pin: 0,
      type: 0,
      sel: true
    },
    relay: {
      pin: 0,
      rev: false
    },
    baud: 0,
    if: {
      'i2c-pin': [0, 0],
      'spi-pin': [0, 0, 0]
    }
  },
  // Light Settings
  light: {
    'scale-bri': 100,
    'pal-mode': 0,
    aseg: false,
    gc: {
      bri: 1,
      col: 2.8,
      val: 2.8
    },
    tr: {
      mode: true,
      dur: 7,
      pal: 0,
      rpc: 5
    },
    nl: {
      mode: 1,
      dur: 60,
      tbri: 0,
      macro: 0
    }
  },
  // Default Settings
  def: {
    ps: 0,
    on: false,
    bri: 128
  },
  // Interface Settings
  if: {
    sync: {
      port0: 21324,
      port1: 65506,
      recv: {
        bri: true,
        col: true,
        fx: true,
        grp: 0,
        seg: false,
        sb: false
      },
      send: {
        dir: false,
        btn: false,
        va: false,
        hue: true,
        macro: false,
        grp: 0,
        ret: 0,
        twice: false
      }
    },
    nodes: {
      list: true,
      bcast: true
    },
    live: {
      en: true,
      mso: false,
      port: 5568,
      mc: false,
      dmx: {
        uni: 1,
        seqskip: false,
        e131prio: 0,
        addr: 1,
        dss: 0,
        mode: 4,
        type: 1
      },
      timeout: 25,
      maxbri: false,
      'no-gc': true,
      offset: 0
    },
    va: {
      alexa: false,
      n: 'WLED',
      macros: [0, 0],
      p: 0
    },
    mqtt: {
      en: true,
      broker: '',
      port: 1883,
      user: '',
      pskl: 0,
      psk: '', // Field for sending new password
      cid: '',
      rtn: false,
      topics: {
        device: '',
        group: ''
      }
    },
    hue: {
      en: false,
      id: 1,
      iv: 25,
      recv: {
        on: true,
        bri: true,
        col: true
      },
      ip: [0, 0, 0, 0]
    },
    ntp: {
      en: false,
      host: '',
      tz: 0,
      offset: 0,
      ampm: false,
      ln: 0,
      lt: 0
    }
  },
  // Remote Settings
  remote: {
    remote_enabled: false,
    linked_remote: ''
  },
  // Overlay Settings
  ol: {
    clock: 0,
    cntdwn: false,
    min: 0,
    max: 29,
    o12pix: 0,
    o5m: false,
    osec: false
  },
  // Timers
  timers: {
    cntdwn: {
      goal: [0, 0, 0, 0, 0, 0],
      macro: 0
    },
    ins: []
  },
  // OTA Settings
  ota: {
    lock: false,
    'lock-wifi': false,
    pskl: 0,
    aota: true
  },
  // MQTT (legacy)
  mqtt: {
    en: true,
    broker: '',
    port: 1883,
    user: '',
    pskl: 0,
    cid: '',
    rtn: false,
    topics: {
      device: '',
      group: ''
    }
  },
  // User Modules
  um: {}
}

const configForm = ref(JSON.parse(JSON.stringify(INITIAL_CONFIG)))

// Helper for deep merging
const deepMerge = (target: any, source: any): any => {
  const result = { ...target }
  for (const key in source) {
    if (source[key] instanceof Object && !Array.isArray(source[key]) && target[key] && !Array.isArray(target[key])) {
      result[key] = deepMerge(target[key], source[key])
    } else {
      result[key] = source[key]
    }
  }
  return result
}

const loadConfigData = () => {
  if (props.device.latest_config) {
    // Deep merge the existing config with our form structure
    // We use a custom deep merge to ensure we preserve defaults for new fields (like if.live) 
    // that might not exist in the device's config yet.
    // Reset to initial state first to clear any dirty state
    configForm.value = JSON.parse(JSON.stringify(INITIAL_CONFIG))
    
    // Deep merge the existing config with our form structure
    // We use a custom deep merge to ensure we preserve defaults for new fields (like if.live) 
    // that might not exist in the device's config yet.
    configForm.value = deepMerge(configForm.value, props.device.latest_config)
    
    // VALIDATION FIX: Ensure 'um' is taken directly if available, as deepMerge might be tricky with dynamic keys
    // if the target is empty. Although deepMerge should handle it, this is safer for dynamic modules.
    if (props.device.latest_config.um) {
      configForm.value.um = JSON.parse(JSON.stringify(props.device.latest_config.um))
    }

    // Ensure nw.ins has at least 2 elements for Fallback WiFi
    if (configForm.value.nw?.ins && configForm.value.nw.ins.length < 2) {
      configForm.value.nw.ins.push({
        ssid: '',
        pskl: 0,
        psk: '',
        ip: [0, 0, 0, 0],
        gw: [0, 0, 0, 0],
        sn: [0, 0, 0, 0]
      })
    }
  }
}

const saveConfiguration = async () => {
  if (!props.device.device_id) return

  isSaving.value = true
  saveError.value = ''
  saveMessage.value = ''

  try {
    const response = await fetch(buildApiUrl(API_ENDPOINTS.DEVICE_CONFIG(props.device.device_id)), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(configForm.value),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Failed to update configuration')
    }

    const result = await response.json()
    saveMessage.value = result.message || 'Configuration updated successfully'
    emit('configUpdated')

  } catch (error) {
    console.error('Failed to save configuration:', error)
    saveError.value = error instanceof Error ? error.message : 'Unknown error occurred'
  } finally {
    isSaving.value = false
  }
}

const resetForm = () => {
  loadConfigData()
  saveMessage.value = ''
  saveError.value = ''
}

onMounted(() => {
  loadConfigData()
})

// Watch for configuration changes (e.g. async load)
watch(() => props.device.latest_config, () => {
  loadConfigData()
}, { deep: true })
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 sticky top-0 z-10 bg-white dark:bg-gray-800 py-4 -mx-6 px-6 border-b border-gray-200 dark:border-gray-700 shadow-sm">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
        Edit Configuration
      </h2>
      <div class="flex space-x-3 w-full sm:w-auto">
        <button
          @click="refreshConfig"
          :disabled="isRefreshing || isSaving || disabled"
          class="flex-1 sm:flex-none px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 text-sm rounded transition-colors text-center border border-gray-300 dark:border-gray-600 flex items-center justify-center gap-2"
          title="Reload configuration from device"
        >
          <svg v-if="isRefreshing" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
             <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
             <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span class="hidden sm:inline">Refresh</span>
        </button>
        <button
          @click="resetForm"
          class="flex-1 sm:flex-none px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white text-sm rounded transition-colors text-center"
        >
          Reset
        </button>
        <button
          @click="saveConfiguration"
          :disabled="isSaving || disabled"
          class="flex-1 sm:flex-none px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed text-white text-sm rounded transition-colors text-center"
        >
          {{ isSaving ? 'Saving...' : 'Save Configuration' }}
        </button>
      </div>
    </div>

    <!-- Status Messages -->
    <div v-if="saveMessage" class="p-4 bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded">
      <p class="text-green-800 dark:text-green-200">{{ saveMessage }}</p>
    </div>

    <div v-if="saveError" class="p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded">
      <p class="text-red-800 dark:text-red-200">{{ saveError }}</p>
    </div>

    <!-- Tabs Navigation -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-4 sm:space-x-8 overflow-x-auto" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- Description -->
    <p class="text-sm text-gray-500 dark:text-gray-400">
      {{ tabs.find(t => t.id === activeTab)?.description }}
    </p>

    <!-- Configuration Form -->
    <div class="space-y-8 mt-6">
      
      <!-- General Tab -->
      <div v-show="activeTab === 'general'" class="space-y-8">
        <DeviceIdentitySettings v-model="configForm.id" />
        <LightSettings v-model="configForm.light" />
      </div>

      <!-- Network Tab -->
      <div v-show="activeTab === 'network'" class="space-y-8">
        <NetworkSettings 
          :id="configForm.id"
          :nw="configForm.nw"
          :ap="configForm.ap"
          :wifi="configForm.wifi"
          :eth="configForm.eth"
          :openSecretModal="openSecretModal"
        />
      </div>

      <!-- LEDs Tab -->
      <div v-show="activeTab === 'leds'" class="space-y-8">
        <LedConfiguration v-model="configForm" />
      </div>

      <!-- Interfaces Tab -->
      <div v-show="activeTab === 'interfaces'" class="space-y-8">
        <SyncSettings 
          :syncConfig="configForm.if" 
          :hwConfig="configForm.hw" 
          :openSecretModal="openSecretModal" 
        />
      </div>

      <!-- Audio Tab -->
      <div v-show="activeTab === 'audio'" class="space-y-8">
        <AudioReactiveSettings v-model="configForm.um" />
      </div>

      <!-- User Mods Tab -->
      <div v-show="activeTab === 'usermods'" class="space-y-8">
        <UserModSettings v-model="configForm.um" />
      </div>

      <!-- Raw Data Tab -->
      <div v-show="activeTab === 'raw'" class="space-y-8">
        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">Complete Configuration (Preview)</h3>
            <button
              @click="copyToClipboard(JSON.stringify(configForm, null, 2))"
              class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
            >
              Copy JSON
            </button>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-600 p-4 max-h-[600px] overflow-y-auto">
            <pre class="text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{{
              JSON.stringify(configForm, null, 2)
            }}</pre>
          </div>
        </div>
      </div>

    </div>
    <!-- Secret Action Modal -->
    <SecretActionModal
      :isOpen="secretModal.isOpen"
      :action="secretModal.action"
      :currentValue="secretModal.currentValue"
      @close="secretModal.isOpen = false"
      @paste="handleSecretPaste"
    />
  </div>
</template>