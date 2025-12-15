#!/usr/bin/env python3

import datetime
from itertools import permutations

def write_bitplanes_to_4bpp(set_paths, output_file):
    # Open all files for reading
    set_files = [open(path, 'rb') for path in set_paths]

    try:
        bytes_written = 0
        while bytes_written < 9216:
            # Read one byte from each file in the set
            set_bytes = [file.read(1) for file in set_files]

            # If all files return empty bytes, we've finished processing
            if not any(set_bytes):
                break

            for byte in set_bytes:
                if byte:  # If byte is not empty (i.e., not EOF)
                    inverted_byte = ~byte[0] & 0xFF  # Invert the bits of the byte
                    output_file.write(bytes([inverted_byte]))         
                    # output_file.write(byte)
                    bytes_written += 1
                    if bytes_written >= 9216:
                        break
    finally:
        # Close all files
        for file in set_files:
            file.close()

def main():
    # Define the file paths for the bitplanes
    file_paths = [
        '../rom/gauntlet/136037-111.1a',
        '../rom/gauntlet/136037-112.1b',
        '../rom/gauntlet/136037-113.1l',
        '../rom/gauntlet/136037-114.1mn',
    ]

    # Generate all permutations of the file paths
    all_permutations = list(permutations(file_paths))
    
    for i, perm in enumerate(all_permutations):
        print(f" ".join(perm))

    # Generate timestamp in yy-mm-dd-hh-mm format
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H_%M")

    # Define the output file path for all permutations
    output_path = f'output_4bpp_all_permutations_inverted_{timestamp}.bin'

    # Open the output file for writing all permutations
    with open(output_path, 'wb') as output_file:
        for i, perm in enumerate(all_permutations):
            # Write permutation header for debugging purposes (optional)
            #header = f'Permutation {i + 1}: {" ".join(perm)}\n'.encode()
            #output_file.write(header)

            # Write the first 512 bytes of the current permutation
            write_bitplanes_to_4bpp(perm, output_file)

            # Write 512 bytes of 0x00 padding between permutations
            output_file.write(bytes([0x00] * 2304))            

if __name__ == "__main__":
    main()
