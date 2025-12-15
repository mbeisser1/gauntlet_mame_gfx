# Gauntlet Graphics (4bpp Planar) — Docs and Tools

This reference focuses on how Atari's Gauntlet (1985) stores and renders its tile graphics, how the arcade EPROMs map into MAME, and how the helper Python script assembles those ROMs into a tile-interleaved binary suitable for tooling.

## Tile Layouts and Bitplanes

- The driver (`src/mame/atari/gauntlet.cpp`) registers two tile layouts: `anlayout` (8×8 at 2bpp) for the alphanumeric overlay and `gfx_8x8x4_planar` (8×8 at 4bpp) for playfield tiles and motion objects.
- Sprites and environment pieces are multi-tile composites built from these 8×8 cells. Four adjacent tiles form a 16×16 motion-object cell; larger enemies stitch multiple cells together.
- A 4bpp pixel pulls one bit from each plane (P0..P3) yielding 16-color palette indices.
- Each tile row consumes one byte per plane. An 8×8 tile therefore occupies 32 bytes (8 rows × 4 bytes).
- Bits are MSB-first within each byte; bit 7 represents the leftmost pixel.

The diagram below shows one tile row as it sits in ROM. Four consecutive bytes hold the plane data for that row; reading the bits vertically (from MSB to LSB) reassembles the four bitplanes into eight pixel indices.

```
Row N in memory (8 pixels)

byte offsets →  +--------+--------+--------+--------+
                |  P0[N] |  P1[N] |  P2[N] |  P3[N] |
                +--------+--------+--------+--------+

bit planes ↓      b7  b6  b5  b4  b3  b2  b1  b0
           P0 ─┬─┼───┼───┼───┼───┼───┼───┼───┼───┐
           P1 ─┼─┼───┼───┼───┼───┼───┼───┼───┼───┤  pixel color index = {P3,P2,P1,P0}
           P2 ─┼─┼───┼───┼───┼───┼───┼───┼───┼───┤  (MSB ←→ bit 7)
           P3 ─┴─┴───┴───┴───┴───┴───┴───┴───┴───┘

screen order →  pix0  pix1  pix2  pix3  pix4  pix5  pix6  pix7
```

## Palette Format (Explains the 0x00 High Byte)

- `PALETTE(...).set_format(palette_device::IRGB_4444, 1024)` configures 1,024 palette entries in IRGB 4-4-4-4 format.
- The production PCB ties the intensity nibble low, so palette words are effectively `0x0RGB`. The high byte carries only the 4-bit red value (`0x0R`), which is why raw dumps show leading `0x00` bytes.

## EPROM Map and Plane Pairing

The `gfx2` region consists of eight 32 KiB EPROMs loaded with `ROM_REGION(0x40000, "gfx2", ROMREGION_INVERT)`:

| Plane | EPROM pair | Offset range |
|-------|------------|--------------|
| P0    | 136037-111.1a + 136037-112.1b | 0x00000–0x0FFFF |
| P1    | 136037-113.1l + 136037-114.1mn | 0x10000–0x1FFFF |
| P2    | 136037-115.2a + 136037-116.2b | 0x20000–0x2FFFF |
| P3    | 136037-117.2l + 136037-118.2mn | 0x30000–0x3FFFF |

`ROMREGION_INVERT` mirrors the active-low EPROM wiring; MAME inverts bytes after loading so decode sees active-high data.

## Interleaved Tile Export

MAME stores planes contiguously, but external editors often expect row-interleaved data. The script `scripts/roms_to_4bpp_planar_tiles.py` performs the conversion:

1. Read the eight EPROM images from fixed relative paths.
2. Concatenate them into four 64 KiB planes in the order above.
3. For each tile (0–8191) and each row (0–7), emit bytes `[P0_row, P1_row, P2_row, P3_row]`.
4. Invert bytes to match MAME’s active-high representation.
5. Write the 262,144-byte result to `OUTPUT_REL`.

Resulting layout:
- Tiles are sequential by index.
- Tile *n* occupies bytes *n*×32 through *n*×32+31.
- Every row is four bytes in plane order.

## Usage

Place the EPROM dumps relative to the script:

```
../rom/gauntlet/136037-111.1a
../rom/gauntlet/136037-112.1b
../rom/gauntlet/136037-113.1l
../rom/gauntlet/136037-114.1mn
../rom/gauntlet/136037-115.2a
../rom/gauntlet/136037-116.2b
../rom/gauntlet/136037-117.2l
../rom/gauntlet/136037-118.2mn
```

Run:

```bash
python3 scripts/roms_to_4bpp_planar_tiles.py
```

The script creates `gauntlet_4bpp_planar_tiles.bin` (or the filename set in `OUTPUT_REL`). Verify the size (262,144 bytes) and inspect the first 32 bytes if you need to sanity-check tile zero.

## Reverse-Engineering Notes

- Plane ordering and ROM pairing were verified from the driver’s `ROM_REGION("gfx2")` definition.
- The interleave matches MAME’s `gfx_8x8x4_planar` decode path exactly.
- Byte inversion mirrors `ROMREGION_INVERT`, so downstream consumers see active-high pixel data with no extra steps.