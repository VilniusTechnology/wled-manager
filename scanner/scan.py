from wled_scan import get_local_ip, scan_network, retrieve_wled_full_info
from export_utils import export_json, export_csv
import ipaddress
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.settings_service import get_setting

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scan for WLED devices on the local network.")
    parser.add_argument('--json', action='store_true', help='Export results as JSON')
    parser.add_argument('--csv', action='store_true', help='Export results as CSV')
    parser.add_argument('--path', help='Path to save output file (optional, if not specified outputs to console)')
    default_timeout = get_setting("scan_timeout")
    parser.add_argument('--timeout', type=float, default=default_timeout, help=f'Timeout in seconds for network requests (default: {default_timeout})')
    args = parser.parse_args()

    if (args.json or args.csv) and not args.path:
        print("Error: You must specify --path when using --json or --csv.")
        exit(1)

    print("Scanning for WLED devices on your local network...")
    network_range = get_setting("network_range")
    if not network_range:
        local_ip = get_local_ip()
        network = ipaddress.IPv4Network(local_ip + '/24', strict=False)
        network_range = str(network)
        
    print(f"Scanning network: {network_range}")
    wled_ips = scan_network(network_range, timeout=args.timeout)
    print(f"Found {len(wled_ips)} WLED device(s):")
    results = []
    for ip in wled_ips:
        info = retrieve_wled_full_info(ip, timeout=args.timeout)
        results.append(info)
        if 'error' not in info:
            # Try to get hostname, fallback to info_full.name if not available
            info_full = info.get('info_full', {})
            cfg_full = info.get('cfg_full', {})
            hostname = cfg_full.get('id', {}).get('mdns')
            if not hostname:
                hostname = info_full.get('name', 'Unknown')
            print(f"WLED Device at {ip} ({hostname}):")
            print(f"  Name: {info_full.get('name', 'Unknown')}")
            print(f"  Version: {info_full.get('ver', 'Unknown')}")
            leds = info_full.get('leds', {})
            print(f"  LED Count: {leds.get('count', 0)}")
            print(f"  Power: {leds.get('pwr', 0)}W")
            state_full = info.get('state_full', {})
            print(f"  Status: {'ON' if state_full.get('on', False) else 'OFF'}")
            print(f"  Brightness: {state_full.get('bri', 0)}")
            print(f"  MAC: {info_full.get('mac', 'Unknown')}")
            wifi = info_full.get('wifi', {})
            print(f"  WiFi Signal: {wifi.get('signal', 0)} dBm")
            print()
        else:
            print(f"Error scanning {ip}: {info['error']}")
    
    if args.path:
        if args.json:
            json_path = args.path if args.json and not args.csv else args.path + '.json'
            export_json(results, json_path)
        if args.csv:
            csv_path = args.path if args.csv and not args.json else args.path + '.csv'
            export_csv(results, csv_path)

if __name__ == "__main__":
    main()
