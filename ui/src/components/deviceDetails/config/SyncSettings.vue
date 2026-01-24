<script setup lang="ts">
import SyncUdp from './sync/SyncUdp.vue'
import SyncRealtime from './sync/SyncRealtime.vue'
import SyncAlexa from './sync/SyncAlexa.vue'
import SyncHue from './sync/SyncHue.vue'
import SyncMqtt from './sync/SyncMqtt.vue'
import SyncSerial from './sync/SyncSerial.vue'

defineProps<{
  syncConfig: any
  hwConfig: any
  openSecretModal: (action: 'copy' | 'paste', field: 'wifi' | 'wifi2' | 'mqtt') => void
}>()
</script>

<template>
  <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 flex flex-col gap-6">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white">Sync Interfaces</h3>
    
    <SyncUdp :syncConfig="syncConfig" :hwConfig="hwConfig" />
    
    <SyncRealtime :syncConfig="syncConfig" />
    
    <SyncAlexa :syncConfig="syncConfig" />
    
    <SyncHue :syncConfig="syncConfig" />
    
    <SyncMqtt :syncConfig="syncConfig" :openSecretModal="openSecretModal" />
    
    <SyncSerial :hwConfig="hwConfig" />
  </div>
</template>
