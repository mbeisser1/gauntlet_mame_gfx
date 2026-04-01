#!/usr/bin/env python3
"""Convert Gauntlet alphanumeric ROM (anlayout) to 2bpp linear for tile editors."""

import sys


def main():
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <input_rom> <output_file>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        data = f.read()

    out = bytearray(len(data))
    for i in range(len(data)):
        src = data[i]
        pixels = []
        for px in range(4):
            plane0 = (src >> px) & 1
            plane1 = (src >> (px + 4)) & 1
            pixels.append(plane0 | (plane1 << 1))
        out[i] = pixels[0] | (pixels[1] << 2) | (pixels[2] << 4) | (pixels[3] << 6)

    with open(sys.argv[2], "wb") as f:
        f.write(out)

    print(f"Done: {len(data)} bytes, {len(data) // 16} tiles")


if __name__ == "__main__":
    main()

