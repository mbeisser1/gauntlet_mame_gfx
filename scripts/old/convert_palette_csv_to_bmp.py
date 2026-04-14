#!/usr/bin/env python3

import struct
import sys
from PIL import Image

def convert_palette(input_file, bmp_file):
    with open(input_file, 'rb') as infile:
        # Read the entire palette (256 entries, 16 bits each)
        palette_data = infile.read()

    # Prepare the palette data
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

        # Add the RGB tuple to the hex_data list
        hex_data.append((red, green, blue))

    # Create the BMP image
    img_width = 16  # 16 pixels per row
    img_height = len(hex_data) // 16  # Number of rows

    # Create a new image with mode 'RGB' (each pixel is represented by a tuple of (R, G, B))
    img = Image.new('RGB', (img_width, img_height))

    # Fill the image with palette data
    for y in range(img_height):
        for x in range(img_width):
            color = hex_data[y * img_width + x]
            img.putpixel((x, y), color)

    # Save the image as BMP
    img.save(bmp_file)
    print(f"BMP file saved to {bmp_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python convert_palette_to_bmp.py <input_palette_file> <output_bmp_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    bmp_file = sys.argv[2]

    convert_palette(input_file, bmp_file)

if __name__ == "__main__":
    main()
