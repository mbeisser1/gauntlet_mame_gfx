#!/usr/bin/env python3

import csv
from PIL import Image

file_name = "gauntlet_palette_rgb_888_16x32"
input_csv = f"{file_name}.csv"
output_file = f"{file_name}.raw"
output_bmp = f"{file_name}.bmp"

def palette_csv_to_pixels():
    # Read the CSV file
    with open(f"../gfx/palette/{input_csv}", newline='') as csvfile:
        reader = csv.reader(csvfile)
        hex_colors = []
        for row in reader:
            for color in row:
                # Strip spaces, and split by commas if necessary (e.g., "FEFEFE, DCDCDC")
                cleaned_colors = [c.strip() for c in color.split(',')]  # Split by commas and strip spaces
                hex_colors.extend(cleaned_colors)

        # for color in hex_colors[:32]:
        #     print(color)

        # Convert hex colors to RGB tuples and populate the image
        pixels = []
        for color in hex_colors:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            pixels.append((r, g, b))

        # return pixels

        # Reverse the pixels in groups of 8
        reversed_pixels = []
        for i in range(0, len(pixels), 8):
            chunk = pixels[i:i + 8]  # Take the next 8 pixels
            reversed_chunk = chunk[::-1]  # Reverse the chunk
            reversed_pixels.extend(reversed_chunk)  # Add to the new list

        return reversed_pixels

def write_palette_raw(pixels):
        # Write the pixel data to a raw output file
        with open(output_file, 'wb') as f:
            for pixel in pixels:
                # Write each pixel as 3 bytes (RGB) to the file
                f.write(bytes(pixel))  # `bytes(pixel)` converts the tuple (r, g, b) into a bytes object

        print(f"Raw palette data written to {output_file} successfully!")

def write_palette_bmp(pixels):
    width = 16
    height = 32

    # Create a new image with the given size and mode 'RGB'
    img = Image.new('RGB', (width, height))

    # Set the pixels in the image (assuming you want to set them row by row)
    img.putdata(pixels)

    # Save the image as a BMP
    img.save(output_bmp)

    print(f"BMP palette data written to {output_bmp} successfully!")

def main():
    pixels = palette_csv_to_pixels()
    write_palette_raw(pixels)
    write_palette_bmp(pixels)

if __name__ == "__main__":
    main()