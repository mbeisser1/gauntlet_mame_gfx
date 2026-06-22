#!/usr/bin/env python3
"""
Convert Gauntlet alphanumeric / text EPROM to interleaved tiles. Tiles are
8x8, 2 bits per pixel, with the tile data being written sequentially.

Output written to `gauntlet_alpha_numeric_2bpp_linear_tiles.bin`.
"""
import os, sys

INPUT_FILE = "../rom/136037-104.6p"
OUTPUT_REL = "gauntlet_alpha_numeric_2bpp_linear_tiles.bin"

def read_file(path: str) -> bytes:
    """Read and return the entire contents of a binary file.
    """
    try:
        with open(path, "rb") as f:
            return f.read()
    except Exception as e:
        sys.exit(f"Error reading {path}: {e}")

def write_file(path: str, data: bytes) -> None:
    """Write raw bytes to a file (overwriting if it exists).

    Args:
        path: Destination file path.
        data: Bytes to write.
    """
    try:
        with open(path, "wb") as f:
            f.write(data)
    except Exception as e:
        sys.exit(f"Error writing {path}: {e}")

def interleave_tiles(data: bytes) -> bytearray:
    out = bytearray(len(data))
    for i in range(len(data)):
        src = data[i]
        pixels = []
        for px in range(4):
            plane0 = (src >> px) & 1
            plane1 = (src >> (px + 4)) & 1
            pixels.append(plane0 | (plane1 << 1))
        out[i] = pixels[0] | (pixels[1] << 2) | (pixels[2] << 4) | (pixels[3] << 6)
    return out

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    in_path = os.path.normpath(os.path.join(script_dir, INPUT_FILE))
    out_path = os.path.normpath(os.path.join(script_dir, OUTPUT_REL))

    data = read_file(in_path)
    inter = interleave_tiles(data)
    write_file(out_path, inter)
    print(f"Wrote: {out_path} {len(data)} bytes, {len(data) // 16} tiles")

if __name__ == "__main__":
    main()
