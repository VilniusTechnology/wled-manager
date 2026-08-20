<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Menu from './components/Menu.vue'
import { useDevices } from './composables/useDevices'
import { useTheme } from './composables/useTheme'
import { useRouter } from 'vue-router'
import { provideApiServices } from './services/context/ApiServiceProvider'
import NotificationModal from './components/shared/NotificationModal.vue'

// Provide API services to all child components
provideApiServices()

const showMobileMenu = ref(false)

const tabs = [
  { name: 'Dashboard', route: '/dashboard', icon: 'dashboard' },
  { name: 'Devices', route: '/devices', icon: 'devices' },
  { name: 'Network Scan', route: '/network-scan', icon: 'network-scan' },
  { 
    name: 'Backups', 
    route: '/backups', 
    icon: 'backups',
    children: [
      { name: 'All Backups', route: '/backups', icon: 'backups' },
      { name: 'Compare Backups', route: '/backups/compare-backups', icon: 'backup-compare' },
      { name: 'Compare Configs', route: '/backups/compare-configs', icon: 'config-compare' }
    ]
  },
  { name: 'Schedulers', route: '/schedulers', icon: 'schedulers' },
  { name: 'Secrets', route: '/secrets', icon: 'secrets' },
  { name: 'App Config', route: '/app-config', icon: 'app-config' },
  { name: 'Serial Installer', route: '/serial-installer', icon: 'serial' },
  { name: 'About', route: '/about', icon: 'about' }
]

// Use the shared composables
const { isDark, toggleTheme } = useTheme()
const {
  devices,
  isLoading,
  scanInProgress,
  fetchDevices,
  scanNetwork,
  backupDevice,
  visitDevice,
  deleteDevice,
  addDevice,
  startPolling,
  stopPolling
} = useDevices()

// Use router for navigation
const router = useRouter()

// Notification modal state
const showNotificationModal = ref(false)
const notificationTitle = ref('')
const notificationMessage = ref('')
const notificationType = ref<'success' | 'error' | 'warning' | 'info'>('info')

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

const toggleDarkMode = () => {
  toggleTheme()
}

const refreshDevices = () => {
  console.log('App.vue - refreshDevices: Calling fetchDevices with forceRefresh=true')

  fetchDevices(true) // Pass forceRefresh=true to trigger scan-refresh
}

const setViewMode = (mode: string) => {
  // This will be handled in DevicesPage
  console.log('View mode set to:', mode)
}

const handleAddDevice = (ip: string, localName: string) => {
  addDevice(ip, localName)
}

const handleAdoptDevice = (deviceId: string, localName: string) => {
  // For now, just log - this will be handled by the adopt modal in DevicesPage
  console.log('Adopt device:', deviceId, 'with local name:', localName)
}

const handleReleaseDevice = (deviceId: string) => {
  // For now, just log - this will be handled by the release function in DevicesPage
  console.log('Release device:', deviceId)
}

const handleViewDetails = (deviceId: string) => {
  // Navigate to device details page
  router.push(`/devices/${deviceId}`)
}

const handleRestoreDevice = (deviceId: string) => {
  // Navigate to devices page with restore action parameters
  // The DevicesPage will handle opening the dialog
  router.push({
    path: '/devices',
    query: { 
      action: 'restore',
      deviceId: deviceId 
    }
  })
}

// Initialize devices on app mount
onMounted(() => {
  const version = import.meta.env.VITE_APP_VERSION || 'unknown'
  console.log(`WLED Manager UI version: ${version}`)
  console.log('App.vue - onMounted: Calling fetchDevices')
  
  // Initial fetch
  fetchDevices().then(async () => {
    console.log('App.vue - Devices after fetch:', devices.value)
    
    // Get polling interval from settings
    let pollingInterval = 120000; // Default 2 minutes
    try {
      const { settingsService } = await import('./services/settingsService')
      const settings = await settingsService.getSettings()
      if (settings.health_check_interval_seconds) {
        // Ensure minimum 10 seconds to value
        const configuredInterval = Math.max(10, settings.health_check_interval_seconds)
        pollingInterval = configuredInterval * 1000
        console.log(`App.vue - Using configured polling interval: ${pollingInterval}ms`)
      }
    } catch (e) {
      console.error('App.vue - Failed to load settings for polling interval, using default', e)
    }
    
    // Start polling for health updates
    startPolling(pollingInterval)
  })
})

import { onUnmounted } from 'vue'

onUnmounted(() => {
  stopPolling()
})

// Theme loading is handled automatically by useTheme composable
// Device fetching is handled automatically by useDevices composable
</script>

<template>
  <div class="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-white">
    <Menu
      :showMobileMenu="showMobileMenu"
      :isDark="isDark"
      :tabs="tabs"
      @toggle-mobile-menu="toggleMobileMenu"
      @toggle-dark-mode="toggleDarkMode"
    />

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-6">
      <router-view
        :devices="devices"
        :isLoading="isLoading"
        :scanInProgress="scanInProgress"
        @refresh-devices="refreshDevices"
        @scan-network="scanNetwork"
        @backup-device="backupDevice"
        @visit-device="visitDevice"
        @delete-device="deleteDevice"
        @add-device="handleAddDevice"
        @set-view-mode="setViewMode"
        @adopt-device="handleAdoptDevice"
        @release-device="handleReleaseDevice"
        @view-details="handleViewDetails"
        @restore-device="handleRestoreDevice"
      />
    </main>

    <!-- Global Notification Modal -->
    <NotificationModal
      :is-open="showNotificationModal"
      :title="notificationTitle"
      :message="notificationMessage"
      :type="notificationType"
      @close="showNotificationModal = false"
    />
  </div>
</template>

<style>
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
