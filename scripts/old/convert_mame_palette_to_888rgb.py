#!/usr/bin/env python3

import struct
import sys

def convert_palette(input_file, output_file):
    with open(input_file, 'rb') as infile:
        # Read the entire palette (256 entries, 16 bits each)
        palette_data = infile.read()

    # Prepare to write the hex data
    hex_data = []

    # Process each 16-bit palette entry (2 bytes per entry)
    for i in range(0, len(palette_data), 2):
        # Unpack the 16-bit value from the file
        entry = struct.unpack('<H', palette_data[i:i+2])[0]

        # Extract the 4-bit components from the 16-bit entry
        intensity = (entry >> 12) & 0xF
        red = (entry >> 8) & 0xF
        green = (entry >> 4) & 0xF
        blue = entry & 0xF

        # Convert to 8-bit components (shift left by 4 and replicate the value)
        red = (red << 4) | red
        green = (green << 4) | green
        blue = (blue << 4) | blue

        # Combine the RGB values into a single hex tuple (RRGGBB)
        hex_tuple = f"{red:02X}{green:02X}{blue:02X}"
        hex_data.append(hex_tuple)

    # Write the hex data to the output file, 16 values per line
    with open(output_file, 'w') as outfile:
        for i in range(0, len(hex_data), 16):
            # Join 16 hex values with commas and ensure proper formatting
            line = ', '.join(hex_data[i:i+16])
            outfile.write(line + '\n')

    print(f"Palette conversion complete. Hex data saved to {output_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python convert_palette.py <input_palette_file> <output_hex_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_palette(input_file, output_file)

if __name__ == "__main__":
    main()
