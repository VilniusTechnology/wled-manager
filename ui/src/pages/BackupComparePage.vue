<template>
  <div>
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Backup Compare</h1>
      <p class="text-gray-600 dark:text-gray-400">Compare WLED device backup configurations across different versions</p>
    </div>

    <!-- Main Content -->
    <div>
      <!-- Device and Version Selection -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-8">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Select Backups to Compare</h2>
        </div>
        <div class="p-6">
          <BackupSelector
            @backups-selected="handleBackupsSelected"
            :is-loading="isLoadingBackups"
          />
        </div>
      </div>

      <!-- Comparison Results -->
      <div v-if="selectedBackups.length >= 2" class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Backup Comparison</h2>
          <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Comparing {{ selectedBackups.length }} backup configurations
          </p>
        </div>
        <div class="p-6">
          <BackupComparisonTable
            :backups="selectedBackups"
            :is-loading="isLoadingComparison"
          />
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-12">
        <div class="text-center">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-white">No backups selected</h3>
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Select at least 2 device backup configurations to compare them side by side.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BackupSelector from '../components/backup-compare/BackupSelector.vue'
import BackupComparisonTable from '../components/backup-compare/BackupComparisonTable.vue'
import type { SelectedBackup } from '../types/backupCompare'

const selectedBackups = ref<SelectedBackup[]>([])
const isLoadingBackups = ref(false)
const isLoadingComparison = ref(false)

const handleBackupsSelected = (backups: SelectedBackup[]) => {
  selectedBackups.value = backups
}
</script>