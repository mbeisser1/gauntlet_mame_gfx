# Planar Graphics: 4BPP Format Explained

## Overview

Planar graphics storage is a memory efficient encoding scheme that was prevalent in retro hardware.
It was used because graphics processors could implement the decoding logic directly on integrated circuits, enabling efficient sequential memory access, and allowing color depth scaling without changing the core decoding algorithm.

Unlike modern packed pixel formats (where all color bits for a single pixel are stored contiguously), the planar format organizes color data by bit significance rather than by pixel position.
In planar format, color information is stored in separate planes, with each plane containing all bits of the same significance across an entire region (e.g., a tile or scanline).

### Packed Format

In a linear bit per pixel encoding, the bits for a pixel are packed together, and arranged sequentially.
For example, 4 pixels of a linear 4bpp encoding scheme would look like the following:

**Packed (Modern):**
```
Pixel 0: [bit3 bit2 bit1 bit0]  Pixel 1: [bit3 bit2 bit1 bit0]  Pixel 2: [bit3 bit2 bit1 bit0]  Pixel 3: [bit3 bit2 bit1 bit0]
```

## Planar Core Concept

In planar graphics, each bit plane holds one bit of color information for all pixels in a region.
For 4BPP:
- **Plane 0** stores bit 0 of each pixel's color index
- **Plane 1** stores bit 1 of each pixel's color index
- **Plane 2** stores bit 2 of each pixel's color index
- **Plane 3** stores bit 3 of each pixel's color index

By combining the bits from all four planes, each pixel can represent one of 16 colors ($2^4 = 16$).

### Color Index Calculation
```
Pixel Color Index = (Plane3_Bit << 3) | (Plane2_Bit << 2) | (Plane1_Bit << 1) | Plane0_Bit
```

For example, if Plane0 = 1, Plane1 = 1, Plane2 = 0, and Plane3 = 1:
- Color index = (1 << 3) | (0 << 2) | (1 << 1) | 1 = 0b1011 = **11**

## Memory Layout for 8×8 Tiles

A standard 8×8 tile in 4BPP planar format requires **32 bytes** of data:
- 8 bytes for **Plane 0**
- 8 bytes for **Plane 1**
- 8 bytes for **Plane 2**
- 8 bytes for **Plane 3**

### Organization

```
Memory Offset (bytes):
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ 0  │ 1  │ 2  │ 3  │ 4  │ 5  │ 6  │ 7  │ 8  │ 9  │ 10 │ 11 │ 12 │ 13 │ 14 │ 15 │
├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
│ 16 │ 17 │ 18 │ 19 │ 20 │ 21 │ 22 │ 23 │ 24 │ 25 │ 26 │ 27 │ 28 │ 29 │ 30 │ 31 │
└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
 └──────── PLANE 0 (rows 0-7) ───────┘     └──────── PLANE 1 (rows 0-7) ───────┘
 └──────── PLANE 2 (rows 0-7) ───────┘     └──────── PLANE 3 (rows 0-7) ───────┘
```

**Row and Bit Mapping:**

```
ROW MAPPING
──────────────────────────────────────────────────────────────

Plane0           Plane1           Plane2           Plane3
Byte 0  +------+ Byte 8  +------+ Byte 16 +------+ Byte 24 -> Row 0
Byte 1  +------+ Byte 9  +------+ Byte 17 +------+ Byte 25 -> Row 1
Byte 2  +------+ Byte 10 +------+ Byte 18 +------+ Byte 26 -> Row 2
Byte 3  +------+ Byte 11 +------+ Byte 19 +------+ Byte 27 -> Row 3
Byte 4  +------+ Byte 12 +------+ Byte 20 +------+ Byte 28 -> Row 4
Byte 5  +------+ Byte 13 +------+ Byte 21 +------+ Byte 29 -> Row 5
Byte 6  +------+ Byte 14 +------+ Byte 22 +------+ Byte 30 -> Row 6
Byte 7  +------+ Byte 15 +------+ Byte 23 +------+ Byte 31 -> Row 7


BIT MAPPING (within each byte)
──────────────────────────────────────────────────────────────

Byte bits: [7][6][5][4][3][2][1][0]
Pixel:      7  6  5  4  3  2  1  0

Each bit position in a byte corresponds to a pixel position in that row:
- Bit 0 -> Pixel 0
- Bit 1 -> Pixel 1
- ... up to Bit 7 -> Pixel 7
```

Each row combines one byte from each of the four planes. The diagram below shows how bits at matching positions from all planes combine to form the color index for each pixel in Row 0:

```
ROW 0 DECODING: Plane0[byte 0] + Plane1[byte 8] + Plane2[byte 16] + Plane3[byte 24]

Plane 0, Byte 0:   [bit7][bit6][bit5][bit4][bit3][bit2][bit1][bit0]
                     0     0     0     0     0     0     0     0
                     |     |     |     |     |     |     |     |
Plane 1, Byte 8:   [bit7][bit6][bit5][bit4][bit3][bit2][bit1][bit0]
                     0     0     0     0     0     0     0     0
                     |     |     |     |     |     |     |     |
Plane 2, Byte 16:  [bit7][bit6][bit5][bit4][bit3][bit2][bit1][bit0]
                     0     0     0     0     0     0     0     0
                     |     |     |     |     |     |     |     |
Plane 3, Byte 24:  [bit7][bit6][bit5][bit4][bit3][bit2][bit1][bit0]
                     0     0     0     0     0     0     0     0
                     |     |     |     |     |     |     |     |
Pixel Index:         7     6     5     4     3     2     1     0


Combination Formula:
Pixel N = (Plane3[bitN] << 3) | (Plane2[bitN] << 2) | (Plane1[bitN] << 1) | Plane0[bitN]
```

For each pixel position (0-7), extract the bit at that position from all four plane bytes, then combine them:
- **Pixel 0**: (Plane3[bit0] << 3) | (Plane2[bit0] << 2) | (Plane1[bit0] << 1) | Plane0[bit0]
- **Pixel 1**: (Plane3[bit1] << 3) | (Plane2[bit1] << 2) | (Plane1[bit1] << 1) | Plane0[bit1]
- **Pixel 2**: (Plane3[bit2] << 3) | (Plane2[bit2] << 2) | (Plane1[bit2] << 1) | Plane0[bit2]
- ... and so on through Pixel 7

### Example Data
```
Plane0[byte 0]:  0xA5 = 0b10100101
Plane1[byte 8]:  0x9B = 0b10011011
Plane2[byte 16]: 0x3C = 0b00111100
Plane3[byte 24]: 0xE1 = 0b11100001
```

### Extraction Process

Extract bits at the same position from all planes and combine:

```
Pixel:   0   1   2   3   4   5   6   7
         ↓   ↓   ↓   ↓   ↓   ↓   ↓   ↓
Plane0:  1   0   1   0   0   1   0   1
Plane1:  1   0   0   1   1   0   1   1
Plane2:  0   0   1   1   1   1   0   0
Plane3:  1   0   0   0   0   1   1   1
         ─── ─── ─── ─── ─── ─── ─── ───
Result: 11   0   5   6   6  13  10  13  (Pixel row: color indices)
```

## Gauntlet in MAME

Gauntlet uses this 4BPP format for both the playfield graphics and the motion-object graphics that MAME exposes through the same 8x8 planar layout.
In the driver, the two relevant layouts are:

- `anlayout`: 8x8 tiles at 2BPP for the alphanumeric overlay
- `gfx_8x8x4_planar`: 8x8 tiles at 4BPP for playfield tiles and motion objects

At a high level, MAME's `gfx_8x8x4_planar` description says:

- the `gfx2` graphics region is divided into four equal quarters, one quarter per bitplane
- each tile is 8x8 pixels
- each tile row uses one byte from each plane
- the pixel bits are read across the byte positions for a row, then combined across the four planes to form a 4-bit palette index

That means Gauntlet's native 4BPP storage in MAME is **planar and quartered by plane**, not row-interleaved.
The full `gfx2` region is 0x40000 bytes, so each plane occupies 0x10000 bytes.

### EPROM to Plane Mapping

Gauntlet's motion-object and playfield graphics come from eight 32 KiB EPROMs, loaded sequentially into the `gfx2` region and interpreted as four planes:

| Plane | EPROM pair                     | Region slice    |
|-------|--------------------------------|-----------------|
| P0    | 136037-111.1a + 136037-112.1b  | 0x00000-0x0FFFF |
| P1    | 136037-113.1l + 136037-114.1mn | 0x10000-0x1FFFF |
| P2    | 136037-115.2a + 136037-116.2b  | 0x20000-0x2FFFF |
| P3    | 136037-117.2l + 136037-118.2mn | 0x30000-0x3FFFF |

This is the layout described by MAME's plane offsets: quarter 0 is Plane 0, quarter 1 is Plane 1, quarter 2 is Plane 2, and quarter 3 is Plane 3.
Each quarter holds 8 bytes per tile, so each plane contains 8192 tiles worth of row data.

### Row Interpretation in Gauntlet

Within a single plane byte, Gauntlet uses MSB-first pixel ordering:

- bit 7 is the leftmost pixel in the row
- bit 0 is the rightmost pixel in the row

So when reading a row from left to right on screen, you typically test bits in the order 7 down to 0, combining the four plane bits at each position into one 4-bit color index.

One row of one tile can be visualized like this:

```txt
Gauntlet row N after row-interleaving for inspection/export

byte order  ->  +--------+--------+--------+--------+
                |  P0[N] |  P1[N] |  P2[N] |  P3[N] |
                +--------+--------+--------+--------+

bit position ->    7  6  5  4  3  2  1  0
screen order ->  pix0 pix1 pix2 pix3 pix4 pix5 pix6 pix7

pixel color = { P3[bit], P2[bit], P1[bit], P0[bit] }
```

Although that row-interleaved view is convenient for explanation, MAME does not store the bytes that way in the ROM region. MAME stores all rows for Plane 0 first, then all rows for Plane 1, then Plane 2, then Plane 3.

### Why the Export Script Exists

The script `bitplane_roms_to_4bpp_planar_tiles.py` converts Gauntlet's native MAME-style plane storage into a format that tile editors and custom tooling can consume more easily.

At a high level it does three things:

1. Reconstruct the four 64 KiB planes by pairing the eight graphics EPROMs in the same order MAME uses.
2. Apply the same active-low to active-high inversion that MAME gets from `ROMREGION_INVERT`.
3. Re-emit the data tile-by-tile, row-by-row, as `[P0, P1, P2, P3]` for each of the 8 rows.

The result is still 4BPP planar data, but now it is arranged as **row-interleaved tiles** instead of **four contiguous plane quarters**.
That exported representation is often easier to inspect because each 8x8 tile becomes a contiguous 32-byte block:

- 8 rows per tile
- 4 bytes per row
- 32 bytes per tile
- 8192 tiles total
- 262,144 bytes in the final output file

This is why the export file is useful even though it is not the exact byte-for-byte layout found in Gauntlet's original ROM region: it preserves the same pixel values while reshaping the storage into a more tool-friendly order.

## Implementation Notes

### Bit Extraction
When decoding, extract the bit at position `N` from a byte:
```
bit = (byte >> N) & 1
```

For the example with Plane0 = 0xA5:
- Pixel 0: `(0xA5 >> 0) & 1 = 1`
- Pixel 1: `(0xA5 >> 1) & 1 = 0`
- Pixel 2: `(0xA5 >> 2) & 1 = 1`
- ...and so on

### Full Decode Loop (Pseudocode)
```c
// row is row index 0-7
uint8_t plane0_row = ROM[plane0_offset + row];
uint8_t plane1_row = ROM[plane1_offset + row];
uint8_t plane2_row = ROM[plane2_offset + row];
uint8_t plane3_row = ROM[plane3_offset + row];

for (int pixel = 0; pixel < 8; pixel++) {
    uint8_t bit0 = (plane0_row >> pixel) & 1;
    uint8_t bit1 = (plane1_row >> pixel) & 1;
    uint8_t bit2 = (plane2_row >> pixel) & 1;
    uint8_t bit3 = (plane3_row >> pixel) & 1;
    uint8_t color_index = (bit3 << 3) | (bit2 << 2) | (bit1 << 1) | bit0;
    // color_index is now in range [0, 15]
}
```

## Multi-Row Tiles

For complete 8×8 tile decoding:
```c
for (int row = 0; row < 8; row++) {
    uint8_t plane0_row = ROM[plane0_base + row];
    uint8_t plane1_row = ROM[plane1_base + row];
    uint8_t plane2_row = ROM[plane2_base + row];
    uint8_t plane3_row = ROM[plane3_base + row];

    for (int pixel = 0; pixel < 8; pixel++) {
        uint8_t bit0 = (plane0_row >> pixel) & 1;
        uint8_t bit1 = (plane1_row >> pixel) & 1;
        uint8_t bit2 = (plane2_row >> pixel) & 1;
        uint8_t bit3 = (plane3_row >> pixel) & 1;
        uint8_t color_index = (bit3 << 3) | (bit2 << 2) | (bit1 << 1) | bit0;
        tile[row][pixel] = color_index;
    }
}
```

## Relationship to Other Depths

The planar format generalizes cleanly across color depths:

| Format | Bits per Pixel | Planes | Colors | Tile Size (8x8) |
|--------|----------------|--------|--------|-----------------|
| 1BPP | 1 | 1 | 2 | 8 bytes |
| 2BPP | 2 | 2 | 4 | 16 bytes |
| 4BPP | 4 | 4 | 16 | 32 bytes |
| 8BPP | 8 | 8 | 256 | 64 bytes |

The decoding logic remains the same: extract one bit per plane for a given pixel position, shift each bit into its significance, then OR the values together to form the final palette index.