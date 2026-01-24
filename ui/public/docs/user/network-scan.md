# Network Scan

The **Network Scan** feature allows you to discover WLED devices on your local network automatically. 

## How it Works

1. **Start Scan**: Initiate a scan of your local network subnet.
2. **Discovery**: The system looks for WLED devices, and after discovery, it connects to them to retrieve their configuration and creates [backups](#/docs/user/backups).
3. **Results**: Found devices are listed, they will be automatically added to your [Devices](#/docs/user/devices) page or visible in [Dashboard](#/docs/user/dashboard).

> [!NOTE]
> The scan relies on mDNS or IP range scanning. Ensure your firewall settings permit this traffic.

After discovery, you can [adopt devices](#/docs/user/adoption) to manage them with WLED Manager.

## Scan Configuration

You can customize the **Network Range** used for scanning:
1. Provide a CIDR range (e.g., `192.168.1.0/24`).
2. Click **Save Changes** to apply.
3. The scanner will limit its search to the specified IP address block.

> [!IMPORTANT]
> The default network range is set from the `NETWORK_RANGE` environment variable in your `.env` file. Once you save a custom value in the UI, it overrides the `.env` setting.

For more details on configuration loading priority, see [App Config](#/docs/user/app-config).

## Automatic Network Scans

Network scans can be scheduled to run periodically. Configure this in [Schedulers](#/docs/user/schedulers).

> [!TIP]
> After initial setup, run the network scan scheduler manually once to initialize it.

## Related

- [Device Adoption](#/docs/user/adoption) - Adopt and manage discovered devices
- [Devices](#/docs/user/devices) - Manage discovered devices
- [Schedulers](#/docs/user/schedulers) - Automate network scans
- [Dashboard](#/docs/user/dashboard) - View device status
