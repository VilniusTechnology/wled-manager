<template>
  <div class="text-center py-8">
    <p class="text-gray-500 dark:text-gray-400">No devices found. Try scanning your network.</p>
    <button
      @click="$emit('scanNetwork')"
      class="mt-4 bg-primary text-white px-4 py-2 rounded hover:bg-primary-dark transition-colors"
    >
      Scan Network
    </button>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  scanNetwork: []
}>()
</script>