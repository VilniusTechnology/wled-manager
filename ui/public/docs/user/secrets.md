# Secrets

The **Secrets** page is a secure vault for managing sensitive credentials used by your WLED devices. Why store credentials here? For bulk operations. If you need to change MQTT or WiFi credentials across multiple devices, you can store them here and apply them to all devices at once instead of entering them one by one.

## What to Store

- **WiFi Passwords**: Store network credentials so you can easily apply them to new devices.
- **MQTT Credentials**: Usernames and passwords for your MQTT broker.

## How to restore
In device details:
- **WiFi Passwords**: Edit Configuration > Network > WiFi Network 1 > WiFi Password > Paste (from secrets) > Save
- **MQTT Credentials**: Edit Configuration > Interfaces > MQTT > MQTT Password > Paste (from secrets) > Save

## Security Note

Secrets are stored securely in the backend database. They are only exposed when explicitly requested or applied to a device during configuration.
