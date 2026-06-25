# Playfield Palette Mapping

For MAME setup, ROM verification, 1:1 screenshots, and the full palette debugging workflow, see [debugging_palette.md](debugging_palette.md).

Gauntlet playfield (floor/wall) tile colors come from **runtime palette RAM**, not from the tile ROM itself. Each 8×8 playfield tile stores 4-bit pixel indices (0–15); the game selects a 16-color group from palette RAM per tile.

## Capturing the palette dump

While Gauntlet is running in MAME (ideally on the level you want to rip), open the debugger and run:

```
save palette_raw.dump,910000:maincpu,800
```

This saves **2048 bytes** = **1024** 16-bit palette entries from CPU address `0x910000`.

| Index range | CPU address   | Count | Purpose            |
|-------------|---------------|-------|--------------------|
| 0–255       | 0x910000      | 256   | Text / alphanumeric |
| 256–511     | 0x910200      | 256   | Motion objects     |
| 512–767     | 0x910400      | 256   | **Playfield**      |
| 768–1023    | 0x910600      | 256   | Extra              |

Convert the dump with:

```
python3 scripts/convert_mame_palette_dump.py gfx/palette/palette_raw.dump
```

## IRGB_4444 format

Each 16-bit word is big-endian (68000 memory order):

```
15-12  11-8   7-4    3-0
  I     R      G      B
```

MAME decodes with intensity multiplication (`standard_irgb_decoder` in MAME `emupal.h`):

```python
def palexpand4(n): return (n << 4) | n

i = palexpand4(I)
R = (i * palexpand4(r)) >> 8
G = (i * palexpand4(g)) >> 8
B = (i * palexpand4(b)) >> 8
```

## Playfield color index formula

From MAME `gauntlet.cpp`:

```cpp
int color = 0x10 + (playfield_color_bank * 8) + ((data >> 12) & 7);
// final pen = 256 + 16 * color + tile_pixel_pen
```

For **Gauntlet** (`playfield_color_bank = 1`):

```
color_code      = 0x18 + palette_select     # palette_select = tile RAM bits 12-14 (0-7)
palette_index   = 256 + 16 * color_code + pen
                = 640 + 16 * palette_select + pen
```

Where `pen` is the 4-bit value from the tile graphics (0–15).

### Worked example (floor browns)

Palette select = 0, tile pen = 2:

```
color_code    = 0x18
palette_index = 256 + 16*24 + 2 = 642
raw word      = 0x9631
RGB           = #3C1E0A
```

Use the helper:

```
python3 scripts/convert_mame_palette_dump.py gfx/palette/palette_raw.dump --playfield-pen 0 2
python3 scripts/convert_mame_palette_dump.py gfx/palette/palette_raw.dump --color-code 0x18
python3 scripts/convert_mame_palette_dump.py gfx/palette/palette_raw.dump --lookup 642 514
```

## Two playfield palette halves (XOR 0x80)

Playfield palette RAM (512–767) behaves as **two 128-color banks**:

| Half   | Index range | Used when                          |
|--------|-------------|------------------------------------|
| Lower  | 512–639     | Bit 0x80 set in pixel palette index |
| Upper  | 640–767     | Gauntlet default (`color_code` 0x18–0x1F) |

MAME toggles bit 0x80 when a motion-object pixel with pen 1 draws over the playfield:

```cpp
pf[x] ^= 0x80;   // MO pen 1 clears PF color bit 0x80
```

So the same tile pen can appear darker or lighter depending on what drew above it:

```
642 ^ 0x80 = 514
#3C1E0A     -> #0D0602
```

Floor tiles look stippled because each 8×8 tile uses **multiple pens** (e.g. 2, 4, 6, 8) from the same 16-color group — not because of hardware dithering.

## Debugging tips

- Dump palette RAM **during gameplay** on the target level; values change at runtime.
- Green walls and brown floors use **different palette_select** values in playfield RAM (bits 12–14).
- Tile ROM stores indices only; always combine tile pens with the correct `palette_index` from the dump.
- Playfield tile indices in RAM are XOR'd with `0x800` for gfx lookup (separate from palette index).
