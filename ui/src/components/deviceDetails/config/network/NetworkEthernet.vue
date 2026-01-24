<script setup lang="ts">
defineProps<{
  eth: any
}>()
</script>

<template>
    <!-- Ethernet Settings -->
  <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3 mt-6 pt-6 border-t border-gray-200 dark:border-gray-600">Ethernet Type</h4>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div>
      <select
        v-model.number="eth.type"
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
      >
        <option :value="0">None</option>
        <option :value="1">ESP32-POE</option>
        <option :value="2">WESP32</option>
        <option :value="3">QuinLED-ESP32</option>
        <option :value="4">TwilightLord-ESP32</option>
        <option :value="5">ESP32DE</option>
        <option :value="6">ESP32-POE-ISO</option>
        <option :value="7">WT32-ETH01</option>
        <option :value="8">M5Stack Atom PoE</option>
      </select>
    </div>
  </div>
</template>
