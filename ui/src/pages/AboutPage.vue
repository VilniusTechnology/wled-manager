<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { 
  BookOpen, 
  LayoutDashboard, 
  Cpu, 
  Network, 
  Save, 
  GitCompare, 
  FileDiff, 
  Calendar, 
  Lock, 
  Settings 
} from 'lucide-vue-next'
// @ts-ignore
import MarkdownIt from 'markdown-it'

const version = import.meta.env.VITE_APP_VERSION || '0.0.0'
const md = new MarkdownIt()

const docs = [
  { id: 'index', title: 'Introduction', icon: BookOpen },
  { id: 'dashboard', title: 'Dashboard', icon: LayoutDashboard },
  { id: 'devices', title: 'Devices', icon: Cpu },
  { id: 'network-scan', title: 'Network Scan', icon: Network },
  { id: 'backups', title: 'Backups', icon: Save },
  { id: 'compare-backups', title: 'Compare Backups', icon: GitCompare },
  { id: 'compare-configs', title: 'Compare Configs', icon: FileDiff },
  { id: 'schedulers', title: 'Schedulers', icon: Calendar },
  { id: 'secrets', title: 'Secrets', icon: Lock },
  { id: 'app-config', title: 'App Config', icon: Settings }
]

const currentDoc = ref('index')
const content = ref('')
const isLoading = ref(false)
const error = ref('')

// Parse doc ID from URL hash
const getDocIdFromHash = (): string => {
  const hash = window.location.hash
  if (hash.startsWith('#/docs/user/')) {
    const docId = hash.replace('#/docs/user/', '')
    if (docs.some(d => d.id === docId)) {
      return docId
    }
  }
  return 'index'
}

const loadDoc = async (docId: string, updateHash = true) => {
  isLoading.value = true
  error.value = ''
  currentDoc.value = docId
  
  // Update URL hash for browser history
  if (updateHash) {
    window.location.hash = `/docs/user/${docId}`
  }
  
  try {
    const response = await fetch(`/docs/user/${docId}.md`)
    if (!response.ok) throw new Error('Failed to load documentation')
    const text = await response.text()
    content.value = md.render(text)
  } catch (e) {
    error.value = 'Failed to load documentation. Please try again later.'
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

// Handle clicks on internal documentation links
const handleContentClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  const anchor = target.closest('a')
  
  if (anchor) {
    const href = anchor.getAttribute('href')
    // Check if it's an internal doc link (e.g., #/docs/user/dashboard)
    if (href && href.startsWith('#/docs/user/')) {
      event.preventDefault()
      const docId = href.replace('#/docs/user/', '')
      if (docs.some(d => d.id === docId)) {
        loadDoc(docId)
      }
    }
  }
}

// Handle browser back/forward navigation
const handleHashChange = () => {
  const docId = getDocIdFromHash()
  if (docId !== currentDoc.value) {
    loadDoc(docId, false) // Don't update hash again
  }
}

onMounted(() => {
  // Load doc based on initial hash, or default to index
  const initialDocId = getDocIdFromHash()
  loadDoc(initialDocId, initialDocId !== 'index')
  
  // Listen for hash changes (back/forward buttons)
  window.addEventListener('hashchange', handleHashChange)
})

onUnmounted(() => {
  window.removeEventListener('hashchange', handleHashChange)
})
</script>

<template>
  <div class="flex flex-col md:flex-row gap-6 md:h-[calc(100vh-100px)]">
    <!-- Sidebar -->
    <div class="w-full md:w-64 flex-shrink-0">
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-4 md:h-full overflow-y-auto">
        <div class="mb-6 border-b border-gray-200 dark:border-gray-700 pb-4 px-2">
          <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">About App</h4>
           <div class="text-sm text-gray-600 dark:text-gray-400">
            <p class="mb-2">Version: <span class="font-mono">{{ version }}</span></p>
            <div class="mt-4 mb-6">
              <a 
                href="https://github.com/VilniusTechnology/wled-manager.git" 
                target="_blank" 
                rel="noopener noreferrer"
                class="flex items-center text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd"></path></svg>
                GitHub Repository
              </a>
            </div>

            <div class="bg-slate-800 rounded-xl p-6 text-center border border-slate-700/50 shadow-lg relative overflow-hidden group">
              <div class="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              
              <h5 class="text-white font-bold text-lg mb-3 relative z-10">Support Development</h5>
              
              <p class="text-slate-300 text-sm mb-6 leading-relaxed relative z-10">
                If you find this tool useful, consider supporting its development. Your support helps maintain the project and implement new features.
              </p>
              
              <a 
                href="https://buymeacoffee.com/vilnius.technology" 
                target="_blank" 
                rel="noopener noreferrer"
                class="inline-flex items-center justify-center bg-[#FFDD00] hover:bg-[#FFEA00] text-slate-900 font-extrabold py-3 px-6 rounded-xl transition-all w-full shadow-md hover:shadow-lg transform hover:-translate-y-0.5 relative z-10"
              >
                <span class="mr-2 text-xl filter drop-shadow-sm">☕</span>
                Buy me a coffee
              </a>
              
              <p class="mt-6 text-[10px] text-slate-500 uppercase tracking-widest font-medium relative z-10">
                Created by Vilnius Technology • © 2024
              </p>
            </div>
          </div>
        </div>

        <h3 class="font-bold text-gray-900 dark:text-white mb-4 px-2">Documentation</h3>
        <nav class="space-y-1">
          <button
            v-for="doc in docs"
            :key="doc.id"
            @click="loadDoc(doc.id)"
            :class="[
              currentDoc === doc.id
                ? 'bg-indigo-50 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300'
                : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700',
              'w-full text-left px-3 py-2 text-sm font-medium rounded-md transition-colors flex items-center'
            ]"
          >
            <component :is="doc.icon" class="w-4 h-4 mr-3 flex-shrink-0" />
            {{ doc.title }}
          </button>
        </nav>
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 min-w-0 bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden flex flex-col">
      <div class="flex-1 overflow-y-auto p-6 md:p-8">
        <div v-if="isLoading" class="flex justify-center py-12">
          <svg class="animate-spin h-8 w-8 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        
        <div v-else-if="error" class="text-red-500 text-center py-12">
          {{ error }}
        </div>

        <div 
          v-else 
          class="prose dark:prose-invert max-w-none prose-headings:font-bold prose-h1:text-3xl prose-h2:text-2xl prose-h3:text-xl prose-p:text-gray-600 dark:prose-p:text-gray-300 prose-a:text-indigo-600 dark:prose-a:text-indigo-400 prose-img:rounded-lg"
          v-html="content"
          @click="handleContentClick"
        ></div>
      </div>
    </div>
  </div>
</template>
