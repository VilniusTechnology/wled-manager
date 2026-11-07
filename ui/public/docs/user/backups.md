# Backups

The **Backups** section allows you to secure your device configurations.

## All Backups

View a history of all backups taken for your devices. You can:
- **Download**: Save a backup file to your local machine.
- **Restore**: Restore a device's configuration from a backup.
- **Delete**: Remove old or unnecessary backups.

### Restoring Backups

You can restore a device state from any saved backup. When restoring, you have two options:
1. **Restore Configuration**: Applies WiFi, LED, and UI settings.
2. **Restore Presets**: Restores saved presets and playlists.

Restoration can be initiated from:
- The **Backups** page (restore any device).
- The **Device Details > Backups** tab (restore specific to that device).

## Automatic Backups

Backups can be automated using [Schedulers](#/docs/user/schedulers). Configure the backup interval in the scheduler settings.

### Retention policy

Retained backups follow a Grandfather-Father-Son (time-machine) policy:

- Newer than 7 days: keep every backup.
- 7–30 days: keep one backup per day.
- 30–90 days: keep one backup per week.
- 90 days–1 year: keep one backup per month.
- Older than 1 year: keep one backup per year.

This guarantees a recent copy plus a backup from roughly one week, one month, three months, six months, and one year ago, and never deletes the only backup a device has.

> [!NOTE]
> After initial setup, you must run the backup scheduler manually once. See [Schedulers](#/docs/user/schedulers) for details.

## Backup Comparison

For advanced management, use the [Compare Backups](#/docs/user/compare-backups) tool to see differences between backup versions or [Compare Configs](#/docs/user/compare-configs) for device configuration differences. This is useful if one of the devices is "acting out" and others aren't—compare the problematic device with a working one. The issue might be in the device itself or in its configuration.

## Related

- [Schedulers](#/docs/user/schedulers) - Configure automatic backups
- [Devices](#/docs/user/devices) - View individual device details
