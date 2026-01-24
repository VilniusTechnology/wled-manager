# WLED Manager

<p align="center">
  <strong>A comprehensive management solution for WLED devices on your network</strong>
</p>

<p align="center"> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#documentation">Documentation</a> •
</p>

This project was born out of necessity: managing the quantity and instability of WLED ESP-based devices. Device duplication issues (when a device changes IP) occurred with other WLED management software. Imperfect handling of WLED device uniqueness in Home Assistant's WLED integration (when devices change IP) forced me to implement communication and management using mDNS and MAC addresses.

Most helpful and notable features:
- Create/restore backups and configurations for easy device recovery.
- Compare device configurations and backups.
- Device identification using MAC addresses (so all artifacts are linked to the device even if IP or name changes).

Use cases:
- Scan network for WLED devices.
- Backup existing configurations.
- Easily set up or change network/MQTT configurations by using secrets as passwords.
- Configure from a fast UI by having device configurations side by side.
- Compare configurations if one (or some) of the devices is "acting out" and others aren't.
- Deployable in your homelab using Docker or K8s with mDNS support.

---

## Features

- **🔍 Device Discovery** - Automatically detect WLED devices on your local network
- **📡 mDNS Support** - Resolve devices by hostname even when IPs change (DHCP-friendly)
- **📊 Dashboard** - Real-time overview of all your devices with status monitoring
- **💾 Automated Backups** - Schedule automatic backups of device configurations
- **🔄 Configuration Sync** - Compare and restore device configurations
- **📧 Email Notifications** - Get notified when backups complete, with last known mDns and IP links to devices.
- **📅 Schedulers Management** - Manage background tasks like backups and network scans
- **🔐 Secrets Management** - Securely manage WiFi and MQTT credentials for your devices
- **🎛️ Remote Control** - Toggle power, adjust brightness, and manage presets
- **📜 Version History** - Track configuration changes over time
- **🏥 Health Monitoring** - Automatic health checks for all devices
- **☸️ Kubernetes Ready** - Includes manifests for standard K8s or K3s deployment
- **🐳 Docker Ready** - Production-ready Docker Compose with configurable `.env` support

## Installation

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/VilniusTechnology/wled-manager.git
cd wled-manager

# Start with Docker Compose
docker compose up -d

# Access the application
# Web UI: http://localhost:5173
# API: http://localhost:8000
```

## Quick Start

1. **Run Network Scan** - Navigate to "Network Scan" in the UI to discover devices.
2. **Review Devices** - Check discovered devices on the "Devices" page.
3. **Initialize Schedulers** - Go to "Schedulers" and click "Run Now" on each scheduler to initialize them.
4. **Configure and manage Backups** - Set your preferred backup interval and retention settings in "App Config".
5. **Manage Devices** - Use "Devices" page to manage devices, including adding, removing, and updating device configurations.
6. **Compare device configs or backups** - Use "Compare Configs" page to compare device configs or backups.
7. **Control devices** - Use "Device details" page to control devices.

> **Important**: After installation, it is recommended to manually trigger schedulers once to ensure everything is working correctly.

## Configuration

Settings are configured via **two methods**:

1. **Environment Variables**: For deployment-specific settings (Timezone, Network Range, Security).
2. **Web UI Settings**: For application logic (Scanning intervals, Backup retention, Email settings, Timeouts).

### Environment Variables

Create a `.env` file in the project root (see `.env.example` for a full list):

```env
# Security (REQUIRED)
SECRET=change_this_to_a_secure_random_string

# Timezone
TIMEZONE=Europe/London

# Network Range (for scanning)
NETWORK_RANGE=192.168.1.0/24
```

## Documentation

- **[User Guide](ui/public/docs/user/)**: Detailed guides on using the dashboard, managing devices, and configuring backups.
They also can be found in app itself in section "About".
- **[Deployment Guide](docs/deployment/)**: Production deployment instructions for Docker and Kubernetes.
- **[Development Guide](DEVELOPMENT.md)**: Guide for contributors and developers wanting to build or modify the project.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [WLED](https://github.com/Aircoookie/WLED) - The amazing LED control firmware
