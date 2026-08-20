<template>
  <div class="p-4 sm:p-6 max-w-7xl mx-auto space-y-6 pb-24">
    <!-- Header Banner -->
    <div class="glass-panel p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 border border-gray-200/50 dark:border-gray-700/50 shadow-xl shadow-blue-500/5">
      <div class="space-y-1">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h1 class="text-2xl sm:text-3xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 dark:from-blue-400 dark:via-indigo-400 dark:to-purple-300">
            Serial Installer
          </h1>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400 font-medium pl-13">
          Flash WLED over WebSerial USB and provision WiFi directly via serial commands
        </p>
      </div>

      <!-- Quick Status Badges -->
      <div class="flex flex-wrap items-center gap-2">
        <span
          v-if="!isWebSerialSupported"
          class="px-3 py-1 text-xs font-bold rounded-full bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 border border-red-200 dark:border-red-800 flex items-center gap-1.5"
        >
          <span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
          WebSerial Unsupported
        </span>
        <span
          v-else-if="connectedChip"
          class="px-3 py-1 text-xs font-bold rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-700 flex items-center gap-1.5"
        >
          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
          Connected: {{ connectedChip.chipName }} ({{ connectedChip.macAddress }})
        </span>
        <span
          v-else
          class="px-3 py-1 text-xs font-bold rounded-full bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 border border-gray-200 dark:border-gray-700 flex items-center gap-1.5"
        >
          <span class="w-2 h-2 rounded-full bg-gray-400"></span>
          No Device Connected
        </span>

        <!-- Disconnect Button if connected -->
        <button
          v-if="connectedChip || isSerialConnected"
          @click="disconnectPort"
          class="px-3 py-1 text-xs font-bold text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/40 rounded-full border border-red-200 dark:border-red-800 transition-colors"
        >
          Disconnect
        </button>
      </div>
    </div>

    <!-- WebSerial Browser Notice -->
    <div
      v-if="!isWebSerialSupported"
      class="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 flex items-start gap-3"
    >
      <svg class="w-6 h-6 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <div>
        <h3 class="text-sm font-bold text-amber-800 dark:text-amber-200">WebSerial API Not Supported in this Browser</h3>
        <p class="text-xs text-amber-700 dark:text-amber-300 mt-0.5">
          WebSerial flashing requires a Chromium-based browser (Google Chrome, Microsoft Edge, Opera, Brave) served over HTTPS or localhost.
        </p>
      </div>
    </div>

    <!-- Global Connect Device -->
    <div class="glass-panel p-6 rounded-2xl space-y-4 border border-gray-200/60 dark:border-gray-800 mb-6 bg-white dark:bg-gray-800 shadow">
      <h2 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
        <span class="text-blue-500">🔌</span> Connect Device over USB
      </h2>
      <p class="text-sm text-gray-500 dark:text-gray-400">
        Plug in your ESP8266 / ESP32 device via USB cable and select the serial COM port.
      </p>

      <div class="space-y-3 pt-2">
        <div>
          <label class="block text-xs font-bold uppercase text-gray-500 dark:text-gray-400 mb-1">
            Baud Rate
          </label>
          <select
            v-model.number="selectedBaudRate"
            class="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
          >
            <option :value="115200">115200 (Standard / Recommended)</option>
            <option :value="460800">460800 (Fast Flashing)</option>
            <option :value="921600">921600 (High Speed)</option>
          </select>
        </div>

        <button
          @click="connectDevice"
          :disabled="isConnecting || !isWebSerialSupported"
          class="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-blue-500/20 disabled:opacity-50 flex items-center justify-center gap-2 transition-all"
        >
          <svg v-if="isConnecting" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span>{{ connectedChip ? 'Re-detect Device' : 'Select Serial Port & Connect' }}</span>
        </button>
      </div>

      <!-- Detected Chip Details -->
      <div v-if="connectedChip" class="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800/50 space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase text-emerald-700 dark:text-emerald-400">Target Chip Detected</span>
          <span class="px-2 py-0.5 text-xs font-bold rounded bg-emerald-200 dark:bg-emerald-800 text-emerald-800 dark:text-emerald-200">
            {{ connectedChip.chipName }}
          </span>
        </div>
        <div class="text-xs text-emerald-800 dark:text-emerald-300 font-mono space-y-0.5">
          <div>MAC Address: <span class="font-bold">{{ connectedChip.macAddress }}</span></div>
          <div>Flash Size: <span class="font-bold">{{ connectedChip.flashSize || 'Auto' }}</span></div>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex space-x-2 border-b border-gray-200 dark:border-gray-800 pb-1">
      <button
        @click="activeMainTab = 'wizard'"
        :class="[
          'px-5 py-2.5 text-sm font-bold rounded-xl transition-all duration-200 flex items-center gap-2',
          activeMainTab === 'wizard'
            ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
        ]"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Provisioning Wizard
      </button>

      <button
        @click="activeMainTab = 'terminal'"
        :class="[
          'px-5 py-2.5 text-sm font-bold rounded-xl transition-all duration-200 flex items-center gap-2',
          activeMainTab === 'terminal'
            ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
        ]"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        Serial Terminal Console
      </button>
    </div>

    <!-- TAB 1: STEP-BY-STEP WIZARD -->
    <div v-if="activeMainTab === 'wizard'" class="space-y-6">
      <!-- Wizard Progress Stepper -->
      <div class="glass-panel p-4 rounded-xl bg-white dark:bg-gray-800 shadow">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <div
            v-for="(step, idx) in wizardSteps"
            :key="step.id"
            @click="canJumpToStep(idx + 1) ? currentStep = idx + 1 : null"
            :class="[
              'p-3 rounded-lg flex items-center gap-3 transition-all',
              currentStep === idx + 1
                ? 'bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800'
                : currentStep > idx + 1
                ? 'bg-gray-50 dark:bg-gray-800/50 cursor-pointer'
                : 'opacity-50'
            ]"
          >
            <div
              :class="[
                'w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0',
                currentStep === idx + 1
                  ? 'bg-blue-600 text-white'
                  : currentStep > idx + 1
                  ? 'bg-emerald-500 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
              ]"
            >
              <svg v-if="currentStep > idx + 1" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
              <span v-else>{{ idx + 1 }}</span>
            </div>
            <div class="truncate">
              <p class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Step {{ idx + 1 }}</p>
              <p class="text-sm font-bold text-gray-900 dark:text-white truncate">{{ step.title }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- STEP 1: Firmware Selection -->
      <div v-if="currentStep === 1" class="space-y-6">
        <div class="max-w-2xl mx-auto">
          <div class="glass-panel p-6 rounded-2xl space-y-4 border border-gray-200/60 dark:border-gray-800 bg-white dark:bg-gray-800 shadow">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <span class="text-blue-500">📦</span> 1. Choose Firmware Binary
            </h2>

            <!-- Firmware Source Options -->
            <div class="flex p-1 bg-gray-100 dark:bg-gray-900 rounded-xl">
              <button
                @click="firmwareSourceMode = 'official'"
                :class="[
                  'flex-1 py-1.5 text-xs font-bold rounded-lg transition-all',
                  firmwareSourceMode === 'official'
                    ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-gray-500'
                ]"
              >
                Official GitHub Releases
              </button>
              <button
                @click="firmwareSourceMode = 'upload'"
                :class="[
                  'flex-1 py-1.5 text-xs font-bold rounded-lg transition-all',
                  firmwareSourceMode === 'upload'
                    ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-gray-500'
                ]"
              >
                Upload File
              </button>
            </div>

            <!-- Mode 1: Official Binaries -->
            <div v-if="firmwareSourceMode === 'official'" class="space-y-3">
              <div v-if="isLoadingReleases" class="py-4 text-center text-gray-500 dark:text-gray-400 text-sm">
                <svg class="w-5 h-5 animate-spin mx-auto mb-2" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                Fetching official releases from GitHub...
              </div>
              <div v-else-if="releasesError" class="py-4 text-center text-red-500 dark:text-red-400 text-sm">
                {{ releasesError }}
              </div>
              <div v-else>
                <div class="flex items-center justify-between bg-gray-50 dark:bg-gray-800/50 p-2 rounded-xl border border-gray-200 dark:border-gray-700 mb-2">
                  <span class="text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider pl-1">WLED Version</span>
                  <select
                    v-model="selectedReleaseTag"
                    class="bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1.5 text-xs font-bold focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                  >
                    <option v-for="rel in allOfficialReleases" :key="rel.tag_name" :value="rel.tag_name">
                      {{ rel.name || rel.tag_name }}
                    </option>
                  </select>
                </div>

                <div class="max-h-64 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
                  <div
                    v-for="asset in currentReleaseAssets"
                    :key="asset.name"
                    @click="isBinaryCompatible(asset) ? selectedOfficialBinary = asset : null"
                    :class="[
                      'p-3 rounded-xl border text-left transition-all relative',
                      !isBinaryCompatible(asset) 
                        ? 'opacity-40 cursor-not-allowed bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-800' 
                        : selectedOfficialBinary?.name === asset.name
                          ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-900/20 cursor-pointer'
                          : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 cursor-pointer'
                    ]"
                  >
                    <div class="flex items-center justify-between">
                      <span class="font-bold text-sm text-gray-900 dark:text-white">{{ asset.name }}</span>
                      <span class="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
                        {{ (asset.size / 1024 / 1024).toFixed(2) }} MB
                      </span>
                    </div>
                  </div>
                  <div v-if="currentReleaseAssets.length === 0" class="text-center py-4 text-xs text-gray-500">
                    No .bin files found for this release.
                  </div>
                </div>
              </div>
            </div>

            <!-- Mode 2: Local File Upload -->
            <div v-else-if="firmwareSourceMode === 'upload'" class="space-y-3">
              <div
                class="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-4 text-center cursor-pointer hover:border-blue-500 transition-colors"
                @click="triggerFileInput"
              >
                <input
                  ref="fileInputRef"
                  type="file"
                  accept=".bin"
                  class="hidden"
                  @change="handleFileUpload"
                />
                <svg class="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="text-xs font-bold text-gray-700 dark:text-gray-300">
                  {{ uploadedFileName || 'Click or drag WLED .bin file here' }}
                </p>
                <p class="text-[11px] text-gray-400 mt-0.5">Maximum size: 8MB</p>
              </div>
            </div>

            <!-- Flash Options -->
            <div class="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-gray-800">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" v-model="eraseFlash" class="rounded text-blue-600 focus:ring-blue-500" />
                <span class="text-xs font-medium text-gray-700 dark:text-gray-300">Erase all flash before writing</span>
              </label>
              <div class="flex items-center gap-2">
                <label class="text-xs font-medium text-gray-700 dark:text-gray-300">Offset:</label>
                <input type="text" v-model="flashOffsetHex" class="w-20 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-xs font-mono text-gray-900 dark:text-white" />
              </div>
            </div>
          </div>
        </div>

        <!-- Continue to Step 2 Button -->
        <div class="flex justify-end max-w-2xl mx-auto">
          <button
            @click="proceedToFlashing"
            :disabled="!canProceedToFlashing"
            class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg shadow-blue-500/25 disabled:opacity-50 flex items-center gap-2"
          >
            <span>Proceed to Flashing</span>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>
        </div>
      </div>

      <!-- STEP 2: Flashing Firmware -->
      <div v-else-if="currentStep === 2" class="glass-panel p-6 sm:p-8 rounded-2xl space-y-6 border border-gray-200/60 dark:border-gray-800 bg-white dark:bg-gray-800 shadow">
        <div class="max-w-xl mx-auto text-center space-y-4">
          <div class="w-16 h-16 rounded-2xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center mx-auto shadow-inner">
            <svg class="w-8 h-8 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>
          <div>
            <h2 class="text-xl font-bold text-gray-900 dark:text-white">Flashing Firmware over WebSerial</h2>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Do not disconnect USB cable or close this browser tab while writing.
            </p>
          </div>

          <!-- Progress Bar -->
          <div class="space-y-2">
            <div class="flex justify-between text-xs font-bold text-gray-600 dark:text-gray-300">
              <span>{{ flashProgress.statusText || 'Flashing...' }}</span>
              <span>{{ flashProgress.percentage }}%</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 h-3 rounded-full overflow-hidden">
              <div
                class="bg-gradient-to-r from-blue-500 to-indigo-600 h-full rounded-full transition-all duration-300"
                :style="{ width: `${flashProgress.percentage}%` }"
              ></div>
            </div>
          </div>

          <!-- Controls -->
          <div class="flex items-center justify-center gap-3 pt-4">
            <button
              v-if="flashProgress.currentPhase !== 'writing' && flashProgress.currentPhase !== 'done'"
              @click="startFlashOperation"
              class="px-6 py-2.5 bg-blue-600 text-white font-bold rounded-xl shadow hover:bg-blue-700"
            >
              Start Flash
            </button>
            <button
              v-if="flashProgress.currentPhase === 'done'"
              @click="currentStep = 3"
              class="px-6 py-2.5 bg-emerald-600 text-white font-bold rounded-xl shadow hover:bg-emerald-700 flex items-center gap-2"
            >
              <span>Continue to WiFi & Provisioning Setup</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Terminal Logs Drawer -->
        <div class="bg-gray-900 rounded-xl p-4 font-mono text-xs text-gray-300 max-h-48 overflow-y-auto space-y-1">
          <div v-for="(log, idx) in serialLogs" :key="idx" class="whitespace-pre-wrap">{{ log }}</div>
        </div>
      </div>

      <!-- STEP 3: WiFi Configuration & Serial Provisioning -->
      <div v-else-if="currentStep === 3" class="glass-panel p-6 sm:p-8 rounded-2xl space-y-6 border border-gray-200/60 dark:border-gray-800 bg-white dark:bg-gray-800 shadow">
        <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 pb-4">
          <div>
            <h2 class="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <span>📶</span> Push WiFi Settings via Serial
            </h2>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              These commands are pushed directly over the USB COM port into WLED as a JSON payload, bypassing the need for initial AP mode setup.
            </p>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Left Column: WiFi Settings -->
          <div class="space-y-4">
            <h3 class="text-sm font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wider">Network Credentials</h3>
            
            <div class="space-y-4">
              <div>
                <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1">WiFi SSID *</label>
                <input
                  v-model="provisionConfig.wifi.ssid"
                  type="text"
                  placeholder="MyHomeWiFi"
                  class="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1">WiFi Password</label>
                <input
                  v-model="provisionConfig.wifi.password"
                  type="password"
                  placeholder="••••••••"
                  class="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                />
              </div>
            </div>
            
            <div class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg text-xs text-blue-800 dark:text-blue-300">
              Note: This will push a standard WLED network configuration payload over serial. Your device should connect shortly after sending.
            </div>
          </div>

          <!-- Right Column: Command Preview & Execution -->
          <div class="space-y-4 flex flex-col justify-between">
            <div>
              <h3 class="text-sm font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wider mb-2">Generated Serial Command (JSON)</h3>
              <div class="bg-gray-900 rounded-xl p-4 font-mono text-xs text-emerald-400 break-all leading-relaxed shadow-inner max-h-48 overflow-y-auto">
                {{ computedWledCommand }}
              </div>
            </div>

            <div class="space-y-3 pt-4">
              <button
                @click="sendProvisioningToDevice"
                :disabled="isSendingProvisioning || !provisionConfig.wifi.ssid"
                class="w-full py-3.5 px-6 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-extrabold rounded-xl shadow-lg shadow-emerald-500/25 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <svg v-if="isSendingProvisioning" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>Push WiFi Configuration to Device</span>
              </button>

              <button
                @click="currentStep = 4"
                class="w-full py-2 text-xs font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                Skip to Summary / Terminal &rarr;
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- STEP 4: Completed -->
      <div v-else-if="currentStep === 4" class="glass-panel p-8 rounded-2xl text-center max-w-xl mx-auto space-y-6 border border-gray-200/60 dark:border-gray-800 bg-white dark:bg-gray-800 shadow">
        <div class="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900/40 text-emerald-600 dark:text-emerald-300 flex items-center justify-center mx-auto text-2xl shadow-lg">
          🎉
        </div>
        <div class="space-y-1">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Device Successfully Provisioned!</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Your WLED device is now connecting to <span class="font-bold text-gray-900 dark:text-white">{{ provisionConfig.wifi.ssid }}</span>.
          </p>
        </div>

        <div class="p-4 bg-gray-50 dark:bg-gray-800/60 rounded-xl text-left text-xs font-mono space-y-1 border border-gray-200 dark:border-gray-700">
          <div>Status: <span class="text-emerald-500 font-bold">Configured</span></div>
        </div>

        <div class="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <button
            @click="activeMainTab = 'terminal'"
            class="w-full sm:w-auto px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow"
          >
            Open Live Serial Console
          </button>
          <button
            @click="$router.push('/devices')"
            class="w-full sm:w-auto px-5 py-2.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 font-bold text-sm rounded-xl"
          >
            Go to Devices
          </button>
        </div>
      </div>
    </div>

    <!-- TAB 2: INTERACTIVE SERIAL TERMINAL -->
    <div v-else-if="activeMainTab === 'terminal'" class="space-y-4">
      <div class="glass-panel p-6 rounded-2xl space-y-4 border border-gray-200/60 dark:border-gray-800 bg-white dark:bg-gray-800 shadow">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-200 dark:border-gray-800 pb-3">
          <div class="flex items-center gap-3">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <span>💻</span> WebSerial Console Terminal
            </h2>
            <span
              :class="[
                'px-2.5 py-0.5 text-xs font-bold rounded-full',
                isSerialConnected
                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
              ]"
            >
              {{ isSerialConnected ? 'Connected (115200)' : 'Disconnected' }}
            </span>
          </div>

          <!-- Terminal Actions -->
          <div class="flex items-center gap-2">
            <button
              v-if="!isSerialConnected"
              @click="openSerialTerminal"
              class="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow"
            >
              Connect Terminal
            </button>
            <button
              v-else
              @click="disconnectPort"
              class="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white font-bold text-xs rounded-xl shadow"
            >
              Disconnect
            </button>
            <button
              @click="terminalLogs = []"
              class="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 font-bold text-xs rounded-xl border border-gray-300 dark:border-gray-600"
            >
              Clear
            </button>
          </div>
        </div>

        <!-- Quick Action Buttons -->
        <div class="flex flex-wrap items-center gap-2">
          <button
            v-for="cmd in quickCommands"
            :key="cmd.label"
            @click="sendQuickCommand(cmd.command)"
            class="px-3 py-1 bg-gray-100 dark:bg-gray-900 hover:bg-blue-50 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-400 text-gray-700 dark:text-gray-300 text-xs font-mono font-bold rounded-lg border border-gray-200 dark:border-gray-700 transition-colors"
          >
            {{ cmd.label }}
          </button>
        </div>

        <!-- Terminal Output Window -->
        <div
          ref="terminalWindowRef"
          class="bg-gray-900 rounded-xl p-4 font-mono text-xs text-emerald-400 h-96 overflow-y-auto select-text shadow-inner border border-gray-800"
        >
          <div v-if="terminalLogs.length === 0" class="text-gray-500 italic">
            No serial output yet. Click 'Connect Terminal' to begin streaming.
          </div>
          <div class="whitespace-pre-wrap leading-relaxed">{{ terminalLogs.join('') }}</div>
        </div>

        <!-- Terminal Input Line -->
        <div class="flex gap-2">
          <input
            v-model="terminalInput"
            @keyup.enter="sendTerminalInput"
            type="text"
            placeholder="Enter WLED JSON command (e.g. {'v':true})..."
            class="flex-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl px-4 py-2.5 text-sm font-mono focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
          />
          <button
            @click="sendTerminalInput"
            class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { webSerialService, type ChipInfo, type FlashProgress } from '../services/esptool-service'

// Types for GitHub API response
interface GithubAsset {
  name: string;
  size: number;
  browser_download_url: string;
}

interface GithubRelease {
  tag_name: string;
  name: string;
  assets: GithubAsset[];
}

// Main Navigation Tab
const activeMainTab = ref<'wizard' | 'terminal'>('wizard')

// WebSerial State
const isWebSerialSupported = computed(() => webSerialService.isSupported())
const isConnecting = ref(false)
const isSerialConnected = ref(false)
const selectedBaudRate = ref(115200)
const connectedChip = ref<ChipInfo | null>(null)

// Alerts (since WLED doesn't have the same Toast system universally exposed in components without imports)
// Wait, we can just use standard browser alerts or local state. We will use a local state for simple messages if needed, but for simplicity, console.log and alerts can work as a fallback.
const showToast = (msg: string) => {
  console.log('Toast:', msg);
  alert(msg);
}

const serialLogs = ref<string[]>([])
const terminalLogs = ref<string[]>([])
const terminalInput = ref('')
const terminalWindowRef = ref<HTMLElement | null>(null)

// Wizard Stepper State
const currentStep = ref(1)
const wizardSteps = [
  { id: 1, title: 'Choose Firmware Binary' },
  { id: 2, title: 'Flash over WebSerial' },
  { id: 3, title: 'WiFi & Provisioning' },
  { id: 4, title: 'Completed' }
]

// Firmware Selection State
const firmwareSourceMode = ref<'official' | 'upload'>('official')
const allOfficialReleases = ref<GithubRelease[]>([])
const selectedReleaseTag = ref<string>('')
const currentReleaseAssets = ref<GithubAsset[]>([])
const selectedOfficialBinary = ref<GithubAsset | null>(null)
const isLoadingReleases = ref(false)
const releasesError = ref('')

watch(selectedReleaseTag, (newTag) => {
  const release = allOfficialReleases.value.find(r => r.tag_name === newTag)
  if (release) {
    // Filter to only include .bin files
    currentReleaseAssets.value = release.assets.filter(a => a.name.endsWith('.bin'))
    if (currentReleaseAssets.value.length > 0) {
      selectedOfficialBinary.value = currentReleaseAssets.value[0]
    } else {
      selectedOfficialBinary.value = null
    }
  }
})

const uploadedFileBlob = ref<ArrayBuffer | null>(null)
const uploadedFileName = ref('')
const eraseFlash = ref(false)
const flashOffsetHex = ref('0x10000') // Default for ESP32 often 0x10000 for WLED, or 0x0 for ESP8266. Let's make it editable. WLED generally uses 0x0 for ESP8266 and 0x10000 for ESP32. We will default to 0x0 since esptool-js often figures it out or standard is 0. Wait, standard is 0x0.
const fileInputRef = ref<HTMLInputElement | null>(null)

watch(connectedChip, (chip) => {
    if (chip) {
        if (chip.chipName.toLowerCase().includes('esp32')) {
            flashOffsetHex.value = '0x10000'
        } else {
            flashOffsetHex.value = '0x0'
        }
    }
})

const isBinaryCompatible = (asset: GithubAsset) => {
  if (!connectedChip.value || !connectedChip.value.chipName) return true
  const chipName = connectedChip.value.chipName.toUpperCase()
  const assetName = asset.name.toUpperCase()
  
  if (chipName.includes('ESP32-C3')) return assetName.includes('ESP32C3') || assetName.includes('ESP32_C3')
  if (chipName.includes('ESP32-S3')) return assetName.includes('ESP32S3') || assetName.includes('ESP32_S3')
  if (chipName.includes('ESP32-S2')) return assetName.includes('ESP32S2') || assetName.includes('ESP32_S2')
  if (chipName.includes('ESP32')) return assetName.includes('ESP32') && !assetName.includes('C3') && !assetName.includes('S2') && !assetName.includes('S3')
  if (chipName.includes('ESP8266') || chipName.includes('ESP8285')) return assetName.includes('ESP8266')
  
  return true
}

// Flashing State
const flashProgress = reactive<FlashProgress>({
  percentage: 0,
  writtenBytes: 0,
  totalBytes: 0,
  currentPhase: 'writing',
  statusText: ''
})

// Provisioning Config State
const provisionConfig = reactive({
  wifi: {
    ssid: '',
    password: ''
  }
})
const isSendingProvisioning = ref(false)

// Quick Commands for Console
const quickCommands = [
  { label: 'Get Info {"v":true}', command: '{"v":true}' },
  { label: 'Reboot {"rb":true}', command: '{"rb":true}' }
]

// Computed WLED JSON command
const computedWledCommand = computed(() => {
  // Use WLED 0.14+ JSON format for WiFi config
  const payload = {
    nw: {
      ida: 0,
      ins: [
        {
          ssid: provisionConfig.wifi.ssid,
          psk: provisionConfig.wifi.password
        }
      ]
    }
  }
  return JSON.stringify(payload)
})

const canProceedToFlashing = computed(() => {
  if (firmwareSourceMode.value === 'official' && selectedOfficialBinary.value) return true
  if (firmwareSourceMode.value === 'upload' && uploadedFileBlob.value) return true
  return false
})

const canJumpToStep = (stepNumber: number) => {
  return stepNumber <= currentStep.value
}

// Attach logger to WebSerial service
webSerialService.setLogger((msg: string) => {
  serialLogs.value.push(msg)
  if (serialLogs.value.length > 300) serialLogs.value.shift()
})

// Load Official Releases
const loadOfficialReleases = async () => {
  isLoadingReleases.value = true
  releasesError.value = ''
  try {
    const res = await fetch('https://api.github.com/repos/Aircoookie/WLED/releases?per_page=15')
    if (!res.ok) throw new Error('Failed to fetch WLED releases')
    const releases: GithubRelease[] = await res.json()
    if (releases.length > 0) {
      allOfficialReleases.value = releases
      selectedReleaseTag.value = releases[0].tag_name
      currentReleaseAssets.value = releases[0].assets.filter(a => a.name.endsWith('.bin'))
      if (currentReleaseAssets.value.length > 0) {
        selectedOfficialBinary.value = currentReleaseAssets.value[0]
      }
    }
  } catch (err: any) {
    releasesError.value = 'Could not load official releases from GitHub. Please use File Upload instead.'
    console.error(err)
  } finally {
    isLoadingReleases.value = false
  }
}

// Connect Device & Detect MCU
const connectDevice = async () => {
  isConnecting.value = true
  try {
    const portSelected = await webSerialService.requestPort()
    if (!portSelected) {
      isConnecting.value = false
      return
    }

    const info = await webSerialService.connectAndDetect(selectedBaudRate.value)
    connectedChip.value = info
    showToast(`Detected ${info.chipName} (${info.macAddress})`)
  } catch (err: any) {
    showToast(err.message || 'Could not communicate with ESP bootloader')
  } finally {
    isConnecting.value = false
  }
}

const disconnectPort = async () => {
  await webSerialService.disconnect()
  connectedChip.value = null
  isSerialConnected.value = false
}

// Trigger File Upload
const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileUpload = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    uploadedFileName.value = file.name
    const reader = new FileReader()
    reader.onload = () => {
      if (reader.result instanceof ArrayBuffer) {
        uploadedFileBlob.value = reader.result
        showToast(`Loaded ${file.name} (${(file.size / 1024).toFixed(1)} KB)`)
      }
    }
    reader.readAsArrayBuffer(file)
  }
}

// Proceed to Flashing Step
const proceedToFlashing = () => {
  currentStep.value = 2
}

// Start Flash Operation
const startFlashOperation = async () => {
  try {
    let binaryData: ArrayBuffer | null = null

    if (firmwareSourceMode.value === 'official' && selectedOfficialBinary.value) {
      flashProgress.statusText = `Fetching ${selectedOfficialBinary.value.name}...`
      // Fetch binary directly from Github
      // Note: github provides CORS headers for asset downloads usually, but if not we might need a proxy.
      // Usually github releases direct URLs are CORS enabled for browser downloads.
      const res = await fetch(selectedOfficialBinary.value.browser_download_url)
      if (!res.ok) throw new Error('Failed to download binary from GitHub')
      binaryData = await res.arrayBuffer()
    } else if (firmwareSourceMode.value === 'upload' && uploadedFileBlob.value) {
      binaryData = uploadedFileBlob.value
    }

    if (!binaryData) {
      throw new Error('No firmware binary available to flash')
    }

    // Ensure we are connected
    if (!connectedChip.value) {
      await connectDevice()
    }
    
    const offset = parseInt(flashOffsetHex.value, 16) || 0;

    await webSerialService.flashFirmware(
      new Uint8Array(binaryData),
      offset,
      eraseFlash.value,
      (progress: FlashProgress) => {
        Object.assign(flashProgress, progress)
      }
    )

    showToast('WLED firmware was successfully written and device restarted.')
  } catch (err: any) {
    flashProgress.currentPhase = 'error'
    flashProgress.statusText = `Flashing error: ${err.message || err}`
    showToast(err.message || 'Error writing firmware over WebSerial')
  }
}

// Send Provisioning Commands via WebSerial
const sendProvisioningToDevice = async () => {
  isSendingProvisioning.value = true
  try {
    // Open serial terminal stream
    await webSerialService.startSerialTerminal(115200, (data: string) => {
      terminalLogs.value.push(data)
      nextTick(() => {
        if (terminalWindowRef.value) {
          terminalWindowRef.value.scrollTop = terminalWindowRef.value.scrollHeight
        }
      })
    })
    isSerialConnected.value = true

    // Small delay to allow ESP boot text
    await new Promise((r) => setTimeout(r, 1000))

    // Send WLED JSON command
    await webSerialService.sendSerialCommand(computedWledCommand.value)
    
    // Also send a reboot command just in case network settings don't apply immediately
    setTimeout(async () => {
        await webSerialService.sendSerialCommand('{"rb":true}')
    }, 1000)

    showToast('WiFi credentials pushed to WLED over serial!')

    currentStep.value = 4
  } catch (err: any) {
    showToast(err.message || 'Could not send commands via serial')
  } finally {
    isSendingProvisioning.value = false
  }
}

// Open Serial Terminal
const openSerialTerminal = async () => {
  try {
    if (!webSerialService.hasPort()) {
      const portSelected = await webSerialService.requestPort()
      if (!portSelected) return
    }
    
    await webSerialService.startSerialTerminal(115200, (data: string) => {
      terminalLogs.value.push(data)
      // Cap at ~1000 chunks to prevent memory bloat
      if (terminalLogs.value.length > 1000) {
        terminalLogs.value.shift()
      }
      nextTick(() => {
        if (terminalWindowRef.value) {
          terminalWindowRef.value.scrollTop = terminalWindowRef.value.scrollHeight
        }
      })
    })
    isSerialConnected.value = true
  } catch (err: any) {
    showToast(err.message || 'Could not open serial terminal')
  }
}

const sendTerminalInput = async () => {
  if (!terminalInput.value.trim()) return
  try {
    await webSerialService.sendSerialCommand(terminalInput.value)
    terminalLogs.value.push(`> ${terminalInput.value}\n`)
    terminalInput.value = ''
  } catch (err: any) {
    showToast(err.message || 'Error sending command')
  }
}

const sendQuickCommand = async (cmd: string) => {
  try {
    if (!isSerialConnected.value) {
      await openSerialTerminal()
    }
    await webSerialService.sendSerialCommand(cmd)
    terminalLogs.value.push(`> ${cmd}\n`)
  } catch (err: any) {
    showToast(err.message)
  }
}

onMounted(() => {
  loadOfficialReleases()
})

onUnmounted(() => {
  webSerialService.disconnect()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.4);
  border-radius: 4px;
}
</style>
