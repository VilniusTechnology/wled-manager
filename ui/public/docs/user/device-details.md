# Device Details

The **Device Details** page is accessed by clicking on any device from the [Devices](#/docs/user/devices) page. It provides full control and visibility into a single WLED device.

## Header Actions

The header bar provides quick access to common actions:

- **Power Toggle**: Turn the device on or off.
- **Refresh (🔄)**: Fetch the latest device state from the network.
- **Adopt**: Available for unadopted devices—adds them to your managed device list.
- **Network Actions**: Restart device, open in browser, etc.
- **Jump To**: Quickly navigate between devices.

---

## Tabs

### 📊 Overview

The main dashboard for a single device.

- **Power & Brightness**: Toggle power and adjust global brightness.
- **Status**: View connection status, IP address, and signal strength.
- **Quick Actions**: Restart device, view in browser.
- **Presets**: Apply available presets.

> [!TIP]
> The **IP Address** in the overview is clickable and will open the device's native WLED interface in a new tab.

---

### 🔘 State

View and manage the current state of the device, including segments and active effects.

---

### ⚙️ Configuration

View and edit the device's configuration directly.

- **Refresh**: Reload the current configuration from the device.
- **Edit Config**: Modify settings such as WiFi, LED preferences, and user interface options.
- **Save**: Apply changes immediately to the device.

---

### 🔧 Hardware

Detailed hardware information including:

- MAC Address
- Filesystem usage
- Memory usage
- ESP chip information

---

### 💾 Backups

Manage backups specific to this device.

- **Create Backup**: Manually trigger a backup for this device.
- **Restore**: Restore a previous configuration or preset file.

---

### ☁️ OTA Update

Perform Over-The-Air firmware updates.

- Upload a binary firmware file (`.bin`) to update the device remotely.

---

## Related

- [Devices](#/docs/user/devices) - Manage all devices
- [Backups](#/docs/user/backups) - Backup device configurations
- [Dashboard](#/docs/user/dashboard) - View device status summary
