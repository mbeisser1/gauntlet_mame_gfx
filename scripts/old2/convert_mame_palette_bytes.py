#!/usr/bin/env python3

import struct
import sys
from PIL import Image

def convert_palette(input_file):
    with open(input_file, 'rb') as infile:
        # Read the entire palette (assuming 16-bit entries)
        palette_data = infile.read()

    # Prepare to store the processed RGB values
    hex_data = []
    rgb_values = []

    # Process each 16-bit palette entry (2 bytes per entry)
    for i in range(0, len(palette_data), 2):
        # Unpack the 16-bit value from the file
        entry = struct.unpack('>H', palette_data[i:i+2])[0]

        # Extract the 4-bit components from the 16-bit entry
        intensity = (entry >> 12) & 0xF
        red = (entry >> 8) & 0xF
        green = (entry >> 4) & 0xF
        blue = entry & 0xF

         # Scale each component to 8 bits (0-255 range)
        #alpha_888 = alpha * 17
    
        intensity_scale = intensity / 15.0
        #  # Combine the components into a single RGB 888 value
        #  rgb888 = (red_888 << 16) | (green_888 << 8) | blue_888

        red_888 = int(red * 17 * intensity_scale)
        green_888 = int(green * 17 * intensity_scale)
        blue_888 = int(blue * 17 * intensity_scale)

        # # Convert to 8-bit components (shift left by 4 and replicate the value)
        # red = (red << 4) | red
        # green = (green << 4) | green
        # blue = (blue << 4) | blue

        # Combine the RGB values into a single hex tuple (RRGGBB)
        hex_tuple = (red_888, green_888, blue_888)
        hex_data.append(hex_tuple)
        rgb_values.append(hex_tuple)

    return hex_data, rgb_values

def write_csv(output_file, hex_data):
    with open(output_file, 'w') as outfile:
        for i in range(0, len(hex_data), 16):
            # Join 16 hex values with commas and ensure proper formatting
            line = ', '.join([f"{r:02X}{g:02X}{b:02X}" for r, g, b in hex_data[i:i+16]])
            outfile.write(line + '\n')

def write_bmp(output_file, rgb_values):
    # Calculate image dimensions (16 colors per row)
    width = 16
    height = len(rgb_values) // 16

    # Create a new image with the calculated dimensions
    img = Image.new('RGB', (width, height))

    # Populate the image with the RGB values
    img.putdata(rgb_values)

    # Save the image as a BMP file
    img.save(output_file)

def write_palette_raw(output_file, pixels):
        # Write the pixel data to a raw output file
        with open(output_file, 'wb') as f:
            for pixel in pixels:
                # Write each pixel as 3 bytes (RGB) to the file
                f.write(bytes(pixel))  # `bytes(pixel)` converts the tuple (r, g, b) into a bytes object

        print(f"Raw palette data written to {output_file} successfully!")

def main():
    if len(sys.argv) != 2:
        print("Usage: python convert_palette_to_hex_bmp.py <input_palette_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Derive output filenames
    base_name = input_file.rsplit('.', 1)[0]
    csv_output_file = base_name + '.csv'
    bmp_output_file = base_name + '.bmp'
    raw_output_file = base_name + '.raw'

    # Convert the palette
    hex_data, rgb_values = convert_palette(input_file)

    # Write outputs
    write_csv(csv_output_file, hex_data)
    write_bmp(bmp_output_file, rgb_values)
    write_palette_raw(raw_output_file, rgb_values)

    print(f"4 RGB to 8 RGB Palette conversion complete.")
    print(f"Hex palette data saved to {csv_output_file}")
    print(f"BMP palette image saved to {bmp_output_file}")
    print(f"Raw bytes saved to {raw_output_file}")

if __name__ == "__main__":
    main()
