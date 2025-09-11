# WLED Scanner

A Python script to scan for WLED devices on your local network and export their information.

## Features

- Automatically detects WLED devices on your local network
- Retrieves detailed device information including:
  - Device name and version
  - LED strip configuration (count, power consumption)
  - Current state (on/off, brightness, effects)
  - Network information (IP, MAC, WiFi signal)
  - Available effects and palettes count
- Export results to JSON or CSV format

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```


## Changing Backup Location

By default, backups are saved in the `backups` directory. You can change the backup location by setting the `BACKUP_DIR` environment variable or by creating a `.env` file in the project root:

### Using a .env file
Create a file named `.env` in the project root with the following content:

```
BACKUP_DIR=/your/custom/backup/path
```

### Using an environment variable
You can also set the environment variable directly in your shell:

```bash
export BACKUP_DIR=/your/custom/backup/path
```

The application will use this path for saving WLED device backups.

## Usage


## API Server

You can launch the WLED Manager API (FastAPI) for programmatic access:

### Install dependencies
```bash
pip install -r requirements.txt
```

### Start the API server
```bash
uvicorn api.server:app --reload

nvm use 22.18.0 && npm --prefix ui run dev
```

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000)

Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Basic scan (console output only)
```bash
python scan.py
```

### Export to JSON
```bash
python scan.py --json --path wled_devices.json
```

### Export to CSV
```bash
python scan.py --csv --path wled_devices.csv
```

### Export to both formats
```bash
python scan.py --json --csv --path wled_devices
```

### Custom timeout
```bash
# Quick scan with 0.5 second timeout
python scan.py --timeout 0.5

# Thorough scan with 2 second timeout for slower networks
python scan.py --timeout 2.0

# Combined with export options
python scan.py --timeout 1.5 --json --path wled_devices
```

## Command Line Options

- `--json` - Export results to JSON format
- `--csv` - Export results to CSV format  
- `--path <filename>` - Specify output file path (required when using --json or --csv)
- `--timeout <seconds>` - Set timeout for network requests in seconds (default: 1.0)

## Output

The scanner will display information about each found WLED device:
- IP address
- Device name
- WLED version
- LED count and power consumption
- Current status and brightness
- MAC address
- WiFi signal strength

## WLED API Endpoints Used

The scanner uses the following WLED JSON API endpoints:
- `/json/info` - Device information
- `/json/state` - Current state
- `/json/effects` - Available effects list
- `/json/palettes` - Available color palettes list

## Network Requirements

- WLED devices must be on the same network segment (typically /24 subnet)
- WLED devices must have JSON API enabled (default)
- Network must allow HTTP requests on port 80
