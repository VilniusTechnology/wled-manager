<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { MenuProps } from '../types/device'
import { 
  LayoutDashboard, 
  Cpu, 
  Network, 
  Save, 
  GitCompare, 
  FileDiff, 
  Calendar, 
  Lock, 
  Settings, 
  Info
} from 'lucide-vue-next'

interface Props extends MenuProps {}

defineProps<Props>()

const emit = defineEmits<{
  'toggle-mobile-menu': []
  'toggle-dark-mode': []
}>()

const iconMap: Record<string, any> = {
  dashboard: LayoutDashboard,
  devices: Cpu,
  'network-scan': Network,
  backups: Save,
  'backup-compare': GitCompare,
  'config-compare': FileDiff,
  schedulers: Calendar,
  secrets: Lock,
  'app-config': Settings,
  about: Info
}

const toggleMobileMenu = () => {
  emit('toggle-mobile-menu')
}

const toggleDarkMode = () => {
  emit('toggle-dark-mode')
}
</script>

<template>
  <!-- Header -->
  <header class="bg-white dark:bg-gray-800 shadow border-b border-gray-200 dark:border-gray-700">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center py-2">
        <div class="flex items-center gap-2">
          <img src="/wled-logo.svg" alt="WLED Logo" class="h-10" />
        </div>

        <div class="hidden md:flex items-center space-x-4">
          <div class="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-sm flex items-center">
            <span class="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            API Connected
          </div>

          <button class="bg-gray-200 dark:bg-gray-700 p-2 rounded-md" @click="toggleDarkMode">
            <svg v-if="isDark" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
            </svg>
            <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
          </button>

          <div class="flex items-center border border-gray-300 dark:border-gray-600 rounded px-2 py-1">
            <img src="/us-flag.svg" alt="Language" class="w-5 h-5 mr-2" />
            <span>English</span>
          </div>
        </div>

        <button class="md:hidden p-2" @click="toggleMobileMenu">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>
          </svg>
        </button>
      </div>
    </div>
  </header>

  <!-- Navigation Tabs -->
  <nav class="hidden md:block bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
    <div class="container mx-auto px-4">
      <div class="flex overflow-visible pb-1"> <!-- changed overflow-x-auto to overflow-visible for dropdowns -->
        <template v-for="tab in tabs" :key="tab.name">
            <!-- Normal Tab -->
            <RouterLink
              v-if="!tab.children"
              :to="tab.route"
              :class="[
                'px-4 py-2 text-sm font-medium whitespace-nowrap flex items-center',
                $route.path === tab.route ?
                  'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400' :
                  'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-300'
              ]"
            >
              <component :is="iconMap[tab.icon]" class="w-5 h-5 flex-shrink-0" />
              <span class="hidden md:inline ml-2">{{ tab.name }}</span>
            </RouterLink>

            <!-- Dropdown Tab (Desktop) -->
            <div 
              v-else 
              class="relative group"
            >
              <button
                :class="[
                    'px-4 py-2 text-sm font-medium whitespace-nowrap flex items-center h-full',
                    ($route.path === tab.route || tab.children.some(child => $route.path === child.route)) ?
                      'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400' :
                      'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-300'
                ]"
              >
                  <component :is="iconMap[tab.icon]" class="w-5 h-5 flex-shrink-0" />
                  <span class="hidden md:inline ml-2">{{ tab.name }}</span>
                  <svg class="ml-1 w-4 h-4 hidden md:inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
              </button>
              
              <!-- Dropdown Menu -->
              <div class="absolute left-0 mt-0 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 z-50 hidden group-hover:block border border-gray-200 dark:border-gray-700">
                  <RouterLink
                    v-for="child in tab.children"
                    :key="child.name"
                    :to="child.route"
                    class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                    :class="$route.path === child.route ? 'bg-gray-50 dark:bg-gray-700 font-medium' : ''"
                  >
                     {{ child.name }}
                  </RouterLink>
              </div>
            </div>
        </template>
      </div>
    </div>
  </nav>

  <!-- Mobile Menu -->
  <div v-if="showMobileMenu" class="md:hidden bg-white dark:bg-gray-800 shadow-lg p-4">
    <div class="flex flex-col space-y-2">
      <template v-for="tab in tabs" :key="tab.name">
        <!-- Normal Mobile Item -->
        <RouterLink
          v-if="!tab.children"
          :to="tab.route"
          class="px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 rounded flex items-center"
          :class="$route.path === tab.route ? 'bg-gray-100 dark:bg-gray-700' : ''"
          @click="toggleMobileMenu"
        >
          <component :is="iconMap[tab.icon]" class="w-5 h-5 mr-3" />
          {{ tab.name }}
        </RouterLink>

        <!-- Nested Mobile Items -->
        <div v-else>
           <div class="px-4 py-2 text-left font-semibold text-gray-900 dark:text-white flex items-center">
              <component :is="iconMap[tab.icon]" class="w-5 h-5 mr-3" />
              {{ tab.name }}
           </div>
           <div class="pl-8 flex flex-col space-y-1">
             <RouterLink
                v-for="child in tab.children"
                :key="child.name"
                :to="child.route"
                 class="px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 rounded flex items-center text-sm"
                 :class="$route.path === child.route ? 'bg-gray-100 dark:bg-gray-700' : ''"
                 @click="toggleMobileMenu"
             >
               {{ child.name }}
             </RouterLink>
           </div>
        </div>
      </template>

      <hr class="border-gray-200 dark:border-gray-700">

      <div class="flex justify-between items-center">
        <div class="flex items-center space-x-2">
          <button class="bg-gray-200 dark:bg-gray-700 p-2 rounded-md" @click="toggleDarkMode">
            <svg v-if="isDark" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
            </svg>
            <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
          </button>

          <div class="flex items-center border border-gray-300 dark:border-gray-600 rounded px-2 py-1">
            <img src="/us-flag.svg" alt="Language" class="w-5 h-5 mr-2" />
            <span>English</span>
          </div>
        </div>

        <div class="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-sm flex items-center">
          <span class="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
          API Connected
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
