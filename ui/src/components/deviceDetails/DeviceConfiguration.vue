<script setup lang="ts">
import { computed } from 'vue'
import DeviceConfigurationForm from './DeviceConfigurationForm.vue'

interface DeviceDetails {
  device_id: string
  mac: string
  latest_config?: any
  usermod_url?: string
}

interface Props {
  device: DeviceDetails
  deviceStatus?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'config-updated': []
}>()

const isEditingDisabled = computed(() => {
  return props.deviceStatus === 'dead' || props.deviceStatus === 'Dead'
})

const onConfigUpdated = () => {
  // Emit event to parent to refresh device details
  emit('config-updated')
}
</script>

<template>
  <div class="space-y-6">
     <!-- Disabled State Banner -->
    <div v-if="isEditingDisabled" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
      <div class="flex items-center">
        <svg class="h-6 w-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
        </svg>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-yellow-800 dark:text-yellow-200">Editing Disabled</h3>
          <p class="mt-1 text-sm text-yellow-700 dark:text-yellow-300">
            Configuration editing is disabled because the device status is "{{ props.deviceStatus }}".
            The device must be online to modify its configuration.
          </p>
        </div>
      </div>
    </div>



    <!-- Configuration Form -->
    <!-- Always show form if not disabled, or if user wants to see it even if disabled? 
         Original logic detached form when disabled. Let's keep that behavior to avoid edits but maybe users want to see current config in the form?
         The 'View' tab was useful for seeing config when offline. 
         But request is "get rid of View Configuration tab at all".
         If I hide the form when disabled, they see nothing but the warning.
         Ideally, the form should be viewable but disabled (readonly).
         However, DeviceConfigurationForm doesn't seem to have a global 'disabled' prop.
         Let's stick to the previous behavior: If disabled, show banner. If active, show form.
         Wait, if I hide the form when disabled, the user cannot see the config at all now that View tab is gone.
         That seems wrong.
         The form populates from `device.latest_config`. It should be safe to render it even if offline, just prevent saving.
         `DeviceConfigurationForm` has `isSaving` state but no `disabled` prop for inputs.
         Let's show the form anyway, but maybe the SAVE button inside it should be disabled if offline?
         The user said "get rid of View Configuration tab", so the Form is the only way to see config.
         So I must render the form even if isEditingDisabled is true, but perhaps pass a prop to disable interactions?
         `DeviceConfigurationForm.vue` has `isEditingDisabled` logic? No, it's passed down or handled here?
         Checking `DeviceConfigurationForm.vue` again... it handles `saveConfiguration`.
         I can modify `DeviceConfigurationForm.vue` to accept `disabled` prop, or just let users look at it and fail to save (or hide save button).
         The current `DeviceConfiguration.vue` logic was:
         v-if="isEditingDisabled" -> Show Warning
         v-else -> Show Form.
         If I keep this, offline devices have no visible config.
         I will change it to: Show Warning (if offline) AND Show Form (always).
         But I need to prevent saving if offline. 
         `DeviceConfigurationForm` handles saving.
         Actually, the previous code hid the form completely when disabled:
         `<div v-else>` (is checking !activeTab=='view') -> 
           `if (isEditingDisabled)` -> warning
           `else` -> Form
         
         So yes, offline devices had no edit form access. They had View tab.
         Removing View tab means I SHOULD now allow the Form to be seen in read-only or at least visible state.
         I'll render the form always. I will update `DeviceConfigurationForm` to accept a `readonly` or `disabled` prop to disable the Save button.
    -->
    
    <DeviceConfigurationForm
      :device="device"
      :disabled="isEditingDisabled"
      @config-updated="onConfigUpdated"
    />

  </div>
</template>