import re
import sys

def extract_gz(header_path, output_path):
    with open(header_path, 'r') as f:
        content = f.read()
    
    # Find the array PAGE_index[] = { ... };
    match = re.search(r'const uint8_t PAGE_index\[\] PROGMEM = {\n?(.*?)\n?};', content, re.DOTALL)
    if not match:
        print("Could not find PAGE_index array")
        return
    
    # Extract hex values
    hex_str = match.group(1).replace('\n', '').replace('\r', '').replace(' ', '')
    hex_values = hex_str.split(',')
    
    # Write to binary file
    with open(output_path, 'wb') as out_f:
        for hex_val in hex_values:
            if hex_val.startswith('0x'):
                out_f.write(bytes([int(hex_val, 16)]))

if __name__ == '__main__':
    extract_gz('scratch/wled-ui-build/WLED/wled00/html_ui.h', 'scratch/index.htm.gz')
    print("Done extracting index.htm.gz")
