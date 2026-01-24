import json
import csv

def export_json(data, filepath):
    """Export data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Results exported to {filepath}")

def export_csv(data, filepath):
    """Export data to CSV file"""
    if not data:
        print("No data to export")
        return
    
    # Get all possible field names from all devices
    fieldnames = set()
    for device in data:
        if 'error' not in device:
            # Flatten nested dictionaries for CSV export
            flat_device = flatten_dict(device)
            fieldnames.update(flat_device.keys())
        else:
            fieldnames.update(['ip', 'error'])
    
    fieldnames = sorted(list(fieldnames))
    
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for device in data:
            if 'error' not in device:
                flat_device = flatten_dict(device)
                writer.writerow(flat_device)
            else:
                writer.writerow({'ip': device['ip'], 'error': device['error']})
    
    print(f"Results exported to {filepath}")

def flatten_dict(d, parent_key='', sep='_'):
    """Flatten nested dictionary for CSV export"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
