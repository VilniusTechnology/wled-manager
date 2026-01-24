# Schedulers

**Schedulers** automate periodic tasks like device backups, network scans, and health checks.

> [!IMPORTANT]
> **First Run Required**: After initial installation, all schedulers must be run **manually once** before they will execute automatically. Click "Run Now" on each scheduler to initialize them.

## Available Schedulers

- **Device Backup**: Automatically backs up device configurations at a set interval. See [Backups](#/docs/user/backups) for more details.
- **Network Scan**: Periodically scans your network for new WLED devices. See [Network Scan](#/docs/user/network-scan).
- **Device Refresh**: Refreshes device status and information. See [Devices](#/docs/user/devices).
- **Health Check**: Monitors device availability and reports offline devices.

## Configuration

1. **Interval**: Set how often the scheduler runs (hours or days).
2. **Enable/Disable**: Toggle auto-run without deleting configuration.
3. **Run Now**: Execute the scheduler immediately.

## Scheduler-Specific Settings

Each scheduler has its own configurable options:

### Device Backup

- **Interval (Hours)**: How often backups run automatically (default: 24 hours).
- **Retention Count**: Number of historical backups to keep per device. Older backups are automatically deleted.
- **Email Notification**: Toggle to send email notifications when backups complete. Requires SMTP configuration in [App Config](#/docs/user/app-config).

### Network Scan

- **Interval (Hours)**: How often the network is scanned for new WLED devices (default: 168 hours / 7 days).

> [!TIP]
> Network scans are resource-intensive. Weekly scans are recommended for most setups.

### Device Refresh

- **Interval (Hours)**: How often device status and information is refreshed (default: 1 hour).

### Health Check

- **Interval (Seconds)**: How often device availability is checked (default: 60 seconds, recommended: 30-120 seconds).

> [!NOTE]
> Shorter health check intervals provide more responsive online/offline status updates but increase network traffic.

## Management

- **Start/Stop**: Control whether a scheduler is actively running.
- **Auto-Run Toggle**: Enable or disable automatic execution without deleting configuration.
- **Run Now**: Execute the scheduler immediately, regardless of schedule.
- **Save Configuration**: Apply interval changes (new settings apply on page reload or scheduler restart).

## Related

- [Backups](#/docs/user/backups) - View and manage backup history
- [App Config](#/docs/user/app-config) - Configure scheduler-related settings
