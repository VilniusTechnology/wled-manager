# App Config

**App Config** contains global settings for the WLED Manager application.

## Configuration Loading Priority

Settings are loaded in the following order (later sources override earlier ones):

1. **Code defaults** - Hardcoded fallback values
2. **Environment variables** (`.env` file) - Override certain defaults at startup
3. **Database storage** - Settings saved via the UI persist here and take priority

> [!NOTE]
> Settings configured via the UI are stored in the database and persist across restarts. Environment variables only set the *initial* defaults before any UI changes are made.

### Environment Variables That Set Defaults

The following `.env` variables influence initial settings:

| Variable | Affects |
|----------|---------|
| `NETWORK_RANGE` | Default network CIDR for scanning (e.g., `192.168.1.0/24`) |
| `BACKUP_DIR` | Directory for backup storage |
| `DATABASE_PATH` | Path to SQLite database |
| `DISABLE_NETWORK_SCAN` | Disable network scan scheduler (`true`/`false`) |
| `DISABLE_DEVICE_REFRESH` | Disable device refresh scheduler |
| `DISABLE_BACKUP` | Disable backup scheduler |
| `DISABLE_HEALTH_CHECK` | Disable health check scheduler |
| `BACKUP_EMAIL_ENABLED` | Enable/disable backup email notifications |

> [!TIP]
> Once you save settings in the UI, those values override the `.env` defaults. To reset to `.env` values, clear the database or use the API.

## Network Scan Settings

Tune the performance and behavior of the device discovery process.

- **Scan Timeout**: Maximum time (seconds) to wait for a device to respond during a basic scan.
- **Info Timeout**: Maximum time (seconds) to wait for detailed device information retrieval.
- **Backup Download Timeout**: Maximum time (seconds) allowed for downloading a device configuration backup.
- **Max Concurrent Workers**: Number of parallel threads used for scanning. Higher values speed up scans but increase load.
- **Connection Pool Size**: Maximum number of simultaneous network connections.
- **Max Retries**: Number of times to retry a failed connection.
- **Scheduler Initial Delay**: Delay (seconds) before starting the first scheduled scan after the application boots.

## Time Settings

- Timezone: Select the timezone for the application. This affects all date and time displays (logs, backup timestamps, etc.).

## Backup Settings

Backup frequency and retention policies are configured in the **[Schedulers](#/docs/user/schedulers)** section.

- **Interval**: How often the automated backup runs (e.g., every 24 hours).
- **Retention Count**: Number of historical backups to keep per device. Older backups are automatically rotated out.

## Email Backup Settings

Configure an SMTP server to receive email notifications when backups are completed.

- **SMTP Host**: The hostname of your email provider's SMTP server (e.g., `smtp.gmail.com`).
- **SMTP Port**: The port for the SMTP server (usually `587` for TLS or `465` for SSL).
- **SMTP User**: Your email username.
- **SMTP Password**: Your email password or app-specific password.
- **Sender Email**: The email address that notifications will come from.
- **Receiver Email**: The email address where notifications will be sent.

> [!TIP]
> Use the **Send Test Email** button to verify your configuration.
