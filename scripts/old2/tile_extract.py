#!/usr/bin/env python3

# def convert_to_4bpp(plane_files, output_file):
#     # Ensure the correct number of planes (4)
#     if len(plane_files) != 4:
#         raise ValueError("There should be exactly 4 plane files")

#     # Read the bitplane data
#     planes = []
#     for file in plane_files:
#         with open(file, 'rb') as f:
#             planes.append(f.read())  # Each plane is 16KB (8KB per ROM file)

#     # Ensure each plane is 16KB (2 * 8KB files for each plane)
#     plane_size = len(planes[0])
#     if any(len(plane) != plane_size for plane in planes):
#         raise ValueError("All planes must have the same size")
    
#     # Each plane should have 16KB of data
#     total_tiles = plane_size // 8  # 16KB / 8 = 2048 tiles per plane
    
#     # Open the output file
#     with open(output_file, 'wb') as out_f:
#         for tile_index in range(total_tiles):
#             # For each tile, we need to extract the corresponding 8 bytes from each plane
#             tile_data = bytearray(8)  # Each tile is 8 bytes (one byte per row of 8 pixels)
            
#             # Iterate over each row (there are 8 rows per tile)
#             for row in range(8):
#                 byte_value = 0
#                 # For each row, gather the 4 bits from the 4 planes (each plane gives 1 bit per pixel)
#                 for plane_index in range(4):
#                     # Get the byte for the current row from the current plane
#                     byte = planes[plane_index][tile_index * 8 + row]
#                     # Shift the byte to the correct position in the 4bpp format
#                     byte_value |= ((byte >> (7 - row)) & 1) << (3 - plane_index)
#                 # Store the 4bpp value for the row
#                 tile_data[row] = byte_value
            
#             # Write the reconstructed tile to the output file
#             out_f.write(tile_data)

# def main():
#     # Define the input plane files and the output file
#     plane_files = ['../rom/gauntlet/136037-111.1a', '../rom/gauntlet/136037-112.1b', 
#                    '../rom/gauntlet/136037-113.1l', '../rom/gauntlet/136037-114.1mn']
#     output_file = 'output_4bpp.bin'
    
#     # Convert the sprite data to 4bpp format
#     convert_to_4bpp(plane_files, output_file)
#     print(f"Conversion complete. Output written to {output_file}")

# if __name__ == "__main__":
#     main()

def combine_planes_to_4bpp(plane0, plane1, plane2, plane3, tile_size=(8, 8)):
    """
    Combine 4 planar graphics data into a single 4bpp linear format.

    :param plane0: Bytes from plane 0
    :param plane1: Bytes from plane 1
    :param plane2: Bytes from plane 2
    :param plane3: Bytes from plane 3
    :param tile_size: Tuple indicating the tile width and height (default is 8x8)
    :return: Combined 4bpp data as bytes
    """
    width, height = tile_size
    bytes_per_tile = width * height // 8

    combined_data = bytearray()

    # Iterate over all tiles
    for tile_offset in range(0, len(plane0), bytes_per_tile):
        for row in range(height):
            # Read one byte for the current row from each plane
            byte0 = plane0[tile_offset + row]
            byte1 = plane1[tile_offset + row]
            byte2 = plane2[tile_offset + row]
            byte3 = plane3[tile_offset + row]

            # Combine bits for the row into whole bytes
            combined_row = bytearray()
            for bit in range(width):
                pixel = ((byte3 >> (7 - bit) & 1) << 3 |
                         (byte2 >> (7 - bit) & 1) << 2 |
                         (byte1 >> (7 - bit) & 1) << 1 |
                         (byte0 >> (7 - bit) & 1))

                if bit % 2 == 0:
                    combined_row.append(pixel << 4)  # Upper nibble
                else:
                    combined_row[-1] |= pixel  # Lower nibble

            # Append the row to the combined data
            combined_data.extend(combined_row)

    return bytes(combined_data)

def main():

    # Example plane files (replace these with actual file reads)
    with open("../rom/gauntlet/136037-111.1a", "rb") as f0, \
         open("../rom/gauntlet/136037-112.1b", "rb") as f1, \
         open("../rom/gauntlet/136037-113.1l", "rb") as f2, \
         open("../rom/gauntlet/136037-114.1mn", "rb") as f3:
        plane0 = f0.read()
        plane1 = f1.read()
        plane2 = f2.read()
        plane3 = f3.read()

    # Combine planes into 4bpp
    combined_data = combine_planes_to_4bpp(plane0, plane1, plane2, plane3)

    # Write the combined data to an output file
    with open("output_4bpp.bin", "wb") as f_out:
        f_out.write(combined_data)


if __name__ == "__main__":
    main()
