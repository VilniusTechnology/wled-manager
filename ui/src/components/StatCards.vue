<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
    <StatCard
      title="Total Devices"
      :value="totalDevices"
      icon-bg-class="bg-blue-100 dark:bg-blue-900/30"
      icon-text-class="text-blue-600 dark:text-blue-400"
      icon-component="svg"
      :class="cardClass"
      @click="navigateToDevices()"
    >
      <template #icon-path>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </template>
    </StatCard>

    <StatCard
      title="Online"
      :value="onlineDevices"
      icon-bg-class="bg-green-100 dark:bg-green-900/30"
      icon-text-class="text-green-600 dark:text-green-400"
      icon-component="svg"
      :class="cardClass"
      @click="navigateToDevices('online')"
    >
      <template #icon-path>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </template>
    </StatCard>

    <StatCard
      title="Offline"
      :value="offlineDevices"
      icon-bg-class="bg-red-100 dark:bg-red-900/30"
      icon-text-class="text-red-600 dark:text-red-400"
      icon-component="svg"
      :class="cardClass"
      @click="navigateToDevices('offline')"
    >
      <template #icon-path>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </template>
    </StatCard>

    <StatCard
      title="Network Scan"
      :value="scanInProgress ? 'Running' : 'Ready'"
      icon-bg-class="bg-yellow-100 dark:bg-yellow-900/30"
      icon-text-class="text-yellow-600 dark:text-yellow-400"
      icon-component="svg"
      :class="cardClass"
      @click="navigateToScan()"
    >
      <template #icon-path>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </template>
    </StatCard>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import StatCard from './StatCard.vue'
import { useDeviceStore } from '../stores/deviceStore'

interface Props {
  totalDevices: number
  onlineDevices: number
  offlineDevices: number
  scanInProgress: boolean
}

const props = defineProps<Props>()

const router = useRouter()
const deviceStore = useDeviceStore()

const navigateToDevices = (filter?: string) => {
  if (filter) {
    router.push({ path: '/devices', query: { status: filter } })
  } else {
    router.push('/devices')
  }
}

const navigateToScan = async () => {
  router.push('/network-scan')
  // Only trigger scan if not already in progress
  if (!props.scanInProgress) {
    await deviceStore.scanNetwork()
  }
}

const cardClass = "cursor-pointer transition-transform hover:scale-105"
</script>