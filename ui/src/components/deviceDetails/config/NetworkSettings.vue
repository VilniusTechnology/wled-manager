<script setup lang="ts">
import NetworkMdns from './network/NetworkMdns.vue'
import NetworkWifi from './network/NetworkWifi.vue'
import NetworkAccessPoint from './network/NetworkAccessPoint.vue'
import NetworkEspNow from './network/NetworkEspNow.vue'
import NetworkWifiExperimental from './network/NetworkWifiExperimental.vue'
import NetworkEthernet from './network/NetworkEthernet.vue'

defineProps<{
  id: any
  nw: any
  ap: any
  wifi: any
  eth: any
  openSecretModal: (action: 'copy' | 'paste', field: 'wifi' | 'wifi2' | 'mqtt') => void
}>()
</script>

<template>
  <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 flex flex-col gap-6">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white">Network Settings</h3>
    
    <NetworkMdns :id="id" :nw="nw" />
    
    <NetworkWifi :nw="nw" :openSecretModal="openSecretModal" />
    
    <NetworkAccessPoint :ap="ap" />
    
    <NetworkEspNow :nw="nw" />

    <NetworkWifiExperimental :wifi="wifi" />
    
    <NetworkEthernet :eth="eth" />
  </div>
</template>
