#!/usr/bin/env python3

from PIL import Image

def read_bmp_entire_image(file_path):
    # Open the BMP file using Pillow
    with Image.open(file_path) as img:
        # Convert image to RGB mode to ensure we're working with color data
        img = img.convert('RGB')

        # Get image dimensions
        width, height = img.size
        #print(f"Width: {width}, Height: {height}")

        line_colors = [["" for _ in range(64)] for _ in range(width)]
        line_color_counts = [[0 for _ in range(64)] for _ in range(width)]

        width_per_palette_color = 29 # pixels in bmp

        # Iterate through each row of the image
        for y in range(0, height, width_per_palette_color):
            # Read the pixels in the current row
            row = [img.getpixel((x, y)) for x in range(width)]

            # Convert the pixel colors to a hex string
            row_hex = [f"{pixel[0]:02x}{pixel[1]:02x}{pixel[2]:02x}" for pixel in row]
            #print(f"Row size: {len(row_hex)}")
            index = 0

            for i in range(len(row_hex)):
                pixel = row_hex[i]
                line_colors[y][index] = pixel
                line_color_counts[y][index] = line_color_counts[y][index] + 1
                
                if i == len(row_hex) - 1:
                    break

                next_pixel = row_hex[i + 1]

                # change in color
                if pixel != next_pixel:
                    index = index + 1    
                    #print(f"pixel [{pixel}] nex pixel [{next_pixel}] index [index]")

        #print(f"Total rows: {y}")

        print_16_colors_per_row(line_color_counts, line_colors)

def print_16_colors_per_row(line_color_counts, line_colors):
    for row in range(len(line_color_counts)):
        next_row = None
        if row != len(line_color_counts) - 1:
            next_row = row + 1

        if next_row is not None and line_colors[row] == line_colors[next_row]:
            continue

        result = []
        for col in range(len(line_color_counts[row])):       
          
            value = line_color_counts[row][col] // 56 # 
            if value == 0 or value == 64:
                continue

            # Append the uppercase color the specified number of times
            for i in range(value):
                result.append(str(line_colors[row][col]).upper())
                
                # Check if result has reached 8 items
                if len(result) == 8:
                    print(', '.join(result))  # Print the 16 items
                    result = []  # Reset result to accumulate next batch

        # Print any remaining items after the row completes
        if len(result) > 0:
            print(', '.join(result))  # Print the 16 items

# Example usage
read_bmp_entire_image('../gfx/palette/gauntlet_mame_screenshot_palette.bmp')        