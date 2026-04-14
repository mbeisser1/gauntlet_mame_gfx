# Planar Graphics: 2BPP Format Explained

## Overview

Planar graphics storage is a memory efficient encoding scheme that was prevalent in retro hardware.
It was used because graphics processors could implement the decoding logic directly on integrated circuits, enabling efficient sequential memory access, and allowing color depth scaling without changing the core decoding algorithm.

Unlike modern packed pixel formats (where all color bits for a single pixel are stored contiguously), the planar format organizes color data by bit significance rather than by pixel position.
In planar format, color information is stored in separate planes, with each plane containing all bits of the same significance across an entire region (e.g., a tile or scanline).

### Packed Format

In a linear bit per pixel encoding, the bits for a pixel are packed together, and arranged sequentially.
For example, 4 pixel of a linear 2bpp encoding scheme would look like the following:

**Packed (Modern):**
```
Pixel 0: [bit1 bit0]  Pixel 1: [bit1 bit0]  Pixel 2: [bit1 bit0]  Pixel 3: [bit1 bit0]
```

## Planar Core Concept

In planar graphics, each bit plane holds one bit of color information for all pixels in a region. 
For 2BPP:
- **Plane 0** stores the **lower (least significant) bit** of each pixel's color index
- **Plane 1** stores the **upper (most significant) bit** of each pixel's color index

By combining the bits from both planes, each pixel can represent one of 4 colors (2^2 = 4).

### Color Index Calculation
```
Pixel Color Index = (Plane1_Bit << 1) | Plane0_Bit
```

For example, if Plane0 bit = 1 and Plane1 bit = 1:
- Color index = (1 << 1) | 1 = 0b11 = **3**

## Memory Layout for 8×8 Tiles

A standard 8×8 tile in 2BPP planar format requires **16 bytes** of data:
- 8 bytes for **Plane 0** (bits 0 of all pixels)
- 8 bytes for **Plane 1** (bits 1 of all pixels)

### Organization

```
Memory Offset (bytes):
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ 0  │ 1  │ 2  │ 3  │ 4  │ 5  │ 6  │ 7  │ 8  │ 9  │ 10 │ 11 │ 12 │ 13 │ 14 │ 15 │
└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
 └──────── PLANE 0 (rows 0-7) ───────┘     └─────── PLANE 1 (rows 0-7) ───────┘
```

**Row and Bit Mapping:**

```
ROW MAPPING                          BIT MAPPING (within each byte)
──────────────────────────────────   ───────────────────────────────

Plane0           Plane1              Byte bits: [7][6][5][4][3][2][1][0]
Byte 0  +------+ Byte 8  -> Row 0    Pixel:      7  6  5  4  3  2  1  0
Byte 1  +------+ Byte 9  -> Row 1
Byte 2  +------+ Byte 10 -> Row 2    Each bit position in a byte
Byte 3  +------+ Byte 11 -> Row 3    corresponds to a pixel position
Byte 4  +------+ Byte 12 -> Row 4    in that row:
Byte 5  +------+ Byte 13 -> Row 5    - Bit 0 → Pixel 0
Byte 6  +------+ Byte 14 -> Row 6    - Bit 1 → Pixel 1
Byte 7  +------+ Byte 15 -> Row 7    - ... up to Bit 7 → Pixel 7
```

Each row combines one byte from Plane 0 and one byte from Plane 1. The diagram below shows how bits at matching positions from both planes combine to form the color index for each pixel in Row 0:

```
ROW 0 DECODING: Plane0[byte 0] + Plane1[byte 8]

Plane 0, Byte 0:  [bit7][bit6][bit5][bit4][bit3][bit2][bit1][bit0]
                    0     0     0     0     0     0     0     0
                    |     |     |     |     |     |     |     |
Plane 1, Byte 8:  [bit7][bit6][bit5][bit4][bit3][bit2][bit1][bit0]
                    0     0     0     0     0     0     0     0
                    |     |     |     |     |     |     |     |                    
Pixel Index:        7     6     5     4     3     2     1     0


Combination Formula:
Pixel N = (Plane1[bitN] << 1) | Plane0[bitN]
```

For each pixel position (0-7), extract the bit at that position from both Plane 0 and Plane 1 bytes, then combine them:
- **Pixel 0**: (Plane1[bit0] << 1) | Plane0[bit0]
- **Pixel 1**: (Plane1[bit1] << 1) | Plane0[bit1]
- **Pixel 2**: (Plane1[bit2] << 1) | Plane0[bit2]
- ... and so on through Pixel 7

### Example Data
```
Plane0[byte 0]: 0xA5 = 0b10100101 (binary, bit7 to bit0)
Plane1[byte 8]: 0x9B = 0b10011011 (binary, bit7 to bit0)
```

### Extraction Process

Extract bits at the same position from both planes and combine:

```
Pixel:  0  1  2  3  4  5  6  7
        ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓
Plane0: 1  0  1  0  0  1  0  1
Plane1: 1  0  0  1  1  0  1  1
        ── ── ── ── ── ── ── ──
Result: 3  0  2  2  2  1  2  3  (Pixel row: color indices)
```

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

for (int pixel = 0; pixel < 8; pixel++) {
    uint8_t bit0 = (plane0_row >> pixel) & 1;
    uint8_t bit1 = (plane1_row >> pixel) & 1;
    uint8_t color_index = (bit1 << 1) | bit0;
    // color_index is now in range [0, 3]
}
```

## Multi-Row Tiles

For complete 8×8 tile decoding:
```c
for (int row = 0; row < 8; row++) {
    uint8_t plane0_row = ROM[plane0_base + row];
    uint8_t plane1_row = ROM[plane1_base + row];
    
    for (int pixel = 0; pixel < 8; pixel++) {
        uint8_t bit0 = (plane0_row >> pixel) & 1;
        uint8_t bit1 = (plane1_row >> pixel) & 1;
        uint8_t color_index = (bit1 << 1) | bit0;
        tile[row][pixel] = color_index;
    }
}
```

## Extensions to Other Depths

The planar format generalizes to any color depth:

| Format | Bits per Pixel | Planes | Colors | Notes |
|--------|----------------|--------|--------|-------|
| 1BPP | 1 | 1 | 2 | Monochrome (black/white) |
| 2BPP | 2 | 2 | 4 | This document |
| 4BPP | 4 | 4 | 16 | Common in arcade systems |
| 8BPP | 8 | 8 | 256 | High color depth |

The decoding logic remains identical; only the number of planes and the resulting color range change.
