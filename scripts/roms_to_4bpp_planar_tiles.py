#!/usr/bin/env python3
import os, sys
from typing import List

ROM_SIZE = 0x8000      # 32 KiB per ROM
PLANE_SIZE = 0x10000   # 64 KiB per plane (two ROMs)
TILE_ROWS = 8
BYTES_PER_ROW = 4      # 4 planes
BYTES_PER_TILE = TILE_ROWS * BYTES_PER_ROW  # 32
TILES_PER_PLANE = PLANE_SIZE // TILE_ROWS   # 8192
INTERLEAVED_SIZE = TILES_PER_PLANE * BYTES_PER_TILE  # 262144

def read_file(path: str) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read()
    except Exception as e:
        sys.exit(f"Error reading {path}: {e}")

def write_file(path: str, data: bytes) -> None:
    try:
        with open(path, "wb") as f:
            f.write(data)
    except Exception as e:
        sys.exit(f"Error writing {path}: {e}")

def combine_roms_to_planes(roms8: List[str]) -> List[bytes]:
    if len(roms8) != 8:
        sys.exit("Expected 8 ROM paths in order: 111,112,113,114,115,116,117,118")
    rom_data = [read_file(p) for p in roms8]
    for p, d in zip(roms8, rom_data):
        if len(d) != ROM_SIZE:
            sys.exit(f"{p}: expected {ROM_SIZE} bytes, got {len(d)}")
    # Pair ROMs into planes: (111+112), (113+114), (115+116), (117+118)
    planes = [
        rom_data[0] + rom_data[1], # plane 0
        rom_data[2] + rom_data[3], # plane 1
        rom_data[4] + rom_data[5], # plane 2
        rom_data[6] + rom_data[7], # plane 3
    ]
    for i, pl in enumerate(planes):
        if len(pl) != PLANE_SIZE:
            sys.exit(f"Plane {i}: expected {PLANE_SIZE} bytes, got {len(pl)}")
    return planes

# (No longer supporting prebuilt plane inputs; helper removed)

def interleave_tiles(planes: List[bytes]) -> bytes:
    p0, p1, p2, p3 = planes
    out = bytearray(INTERLEAVED_SIZE)
    for tile in range(TILES_PER_PLANE):
        base0 = tile * TILE_ROWS
        base_out = tile * BYTES_PER_TILE
        for row in range(TILE_ROWS):
            b0 = p0[base0 + row]
            b1 = p1[base0 + row]
            b2 = p2[base0 + row]
            b3 = p3[base0 + row]
            off = base_out + row * BYTES_PER_ROW
            out[off + 0] = b0
            out[off + 1] = b1
            out[off + 2] = b2
            out[off + 3] = b3
    return bytes(out)

def main():
    # Fixed ROM paths (relative to this script's directory)
    roms8 = [
        '../rom/gauntlet/136037-111.1a',
        '../rom/gauntlet/136037-112.1b',
        '../rom/gauntlet/136037-113.1l',
        '../rom/gauntlet/136037-114.1mn',
        '../rom/gauntlet/136037-115.2a',
        '../rom/gauntlet/136037-116.2b',
        '../rom/gauntlet/136037-117.2l',
        '../rom/gauntlet/136037-118.2mn',
    ]

    # Resolve paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    roms8_abs = [os.path.normpath(os.path.join(script_dir, p)) for p in roms8]

    planes = combine_roms_to_planes(roms8_abs)

    inter = interleave_tiles(planes)

    # Fixed output path next to ROMs
    out_rel = '../rom/gauntlet/gauntlet_tiles_4bpp_interleaved.bin'
    out_path = os.path.normpath(os.path.join(script_dir, out_rel))
    write_file(out_path, inter)
    print(f"Wrote interleaved tiles: {out_path} ({len(inter)} bytes)")

    # Sanity notes
    # - interleaved file layout per 8x8 tile: for each row 0..7 -> [P0,P1,P2,P3]
    # - bit order is MSB-first in each byte (leftmost pixel = bit 7)

if __name__ == "__main__":
    main()