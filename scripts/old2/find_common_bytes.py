#!/usr/bin/env python3

import argparse

# Function to search sequences in haystack
def search_sequences(needle_file, haystack_file, output_file, sequence_length):
    # Read the needle and haystack as binary data
    with open(needle_file, 'rb') as f:
        needle = f.read()

    with open(haystack_file, 'rb') as f:
        haystack = f.read()

    count = 1
    # Open the output file for writing the results
    with open(output_file, 'w') as output:
        found_sequences = set()  # Set to keep track of found byte sequences

        # Iterate over the needle file in sliding window of size 'sequence_length'
        for i in range(len(needle) - sequence_length + 1):
            # Extract a sequence from the needle
            sequence = needle[i:i + sequence_length]

            # If the sequence has already been found, skip it
            if sequence in found_sequences:
                continue

            # Search for the sequence in the haystack
            if sequence in haystack:
                # Convert to uppercase hex and format it into groups of 4 bytes (8 hex characters)
                hex_sequence = sequence.hex().upper()
                grouped_hex = ' '.join([hex_sequence[i:i+8] for i in range(0, len(hex_sequence), 8)])

                # Write the formatted hex sequence to the output
                output.write(f"Found sequence {grouped_hex}\n")
                found_sequences.add(sequence)  # Record the found sequence
                count += 1

    print(f"Found {count} occurances. Results saved to {output_file}")

    # count = 1
    # # Open the output file for writing the results
    # with open(output_file, 'w') as output:
    #     # Iterate over the needle file in sliding window of size 'sequence_length'
    #     for i in range(len(needle) - sequence_length + 1):
    #         # Extract a sequence from the needle
    #         sequence = needle[i:i + sequence_length]

    #         # Search for the sequence in the haystack
    #         index = haystack.find(sequence)
    #         if index != -1:
    #             # If found, write the sequence and its position to the output file
    #             output.write(f"Start {i}: found sequence {sequence.hex()} at position {index}\n")
    #             count += 1

    # print(f"Found {count} occurances. Results saved to {output_file}")

# Function to parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Search byte sequences from needle in haystack")
    parser.add_argument('-n', '--needle', type=str, default='needle.txt', help='Needle file (default: needle.txt)')
    parser.add_argument('-H', '--haystack', type=str, default='haystack.txt', help='Haystack file (default: haystack.txt)')
    parser.add_argument('-o', '--output', type=str, default='output.txt', help='Output file to save results (default: output.txt)')
    parser.add_argument('-l', '--sequence_length', type=int, default=4, help='Length of byte sequences to search for (default: 4)')
    return parser.parse_args()

# Main function to execute the script
def main():
    # Parse command-line arguments
    args = parse_args()

    # Call the search function
    search_sequences(args.needle, args.haystack, args.output, args.sequence_length)

if __name__ == "__main__":
    main()
