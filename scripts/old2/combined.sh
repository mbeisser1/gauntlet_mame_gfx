#!/bin/bash

# Output file
output_file="combined.bin"
# Clear the output file
> "$output_file"

# Number of pixels per tile (8x8) = 64 pixels
# Loop through each byte for the number of tiles
for ((i=0; i<32768; i++)); do
    # Read each plane and output to the combined file in the right order
    for plane in {0..3}; do
        # Use dd to read a byte from each plane file
        dd if=plane"$plane".bin bs=1 count=1 skip=$i 2>/dev/null >> "$output_file"
    done
done