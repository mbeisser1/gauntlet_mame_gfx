# Debugging Palette With MAME

This guide walks through verifying Gauntlet ROMs, capturing a trustworthy reference frame, dumping palette RAM, and using the repo scripts to decode colors. For playfield index math (`color_code`, XOR `0x80`, and pen mapping), see [playfield_palette_mapping.md](playfield_palette_mapping.md).

## What you need

- [MAME](https://www.mamedev.org/) with the `gauntlet` romset (unzipped or as `gauntlet.zip`)
- This repo cloned locally
- Python 3 and Pillow (`pip install pillow`) for BMP previews

Place ROM files under `rom/` at the repo root (gitignored) or point MAME at your romset with `-rompath`.

Gauntlet uses a 16 KiB alphanumeric EPROM (`136037-104.6p`). Older dumps with an 8 KiB `6p` file will fail verification on current MAME; see the [MAME 0.191 compatibility note](../README.md#mame).

## Step 1: List and verify ROM info

These commands do not start the game. They tell you which files MAME expects and whether your romset matches.

```bash
# List required ROM chips, sizes, and CRC32 for gauntlet
mame -listroms gauntlet

# Verify files on disk (exit 0 = all good)
mame -rompath rom -verifyroms gauntlet

# Full machine metadata (ROM regions, addresses, merges) as XML
mame -listxml gauntlet > gauntlet_rom_info.xml
```

Useful fields in `-listroms` / `-listxml`:

| MAME region   | Example file        | Purpose                          |
|---------------|---------------------|----------------------------------|
| `chars`       | `136037-104.6p`     | Alphanumeric / text tiles (2bpp) |
| `spr_tiles`   | `136037-111.1a` …   | Motion object sprite tiles (4bpp)|
| `maincpu`     | `136037-1307.9a` …  | 68000 program code               |
| `audiocpu`    | `136037-119.16s` …  | Audio CPU code                   |
| `proms`       | `74s472-…`          | Motion object timing PROMs       |

To identify an unknown dump file:

```bash
romident path/to/suspicious.bin
```

Cross-check region layout and filenames against MAME source [`gauntlet.cpp`](https://github.com/mamedev/mame/blob/master/src/mame/atari/gauntlet.cpp) or the ROM block quoted in the [README](../README.md#verify-eproms-with-mame).

### Extract ROM files from a zip

If you only have `gauntlet.zip`:

```bash
mkdir -p rom
unzip -j gauntlet.zip -d rom
mame -rompath rom -verifyroms gauntlet
```

The scripts in this repo read graphics EPROMs directly from `rom/` (for example `../rom/136037-104.6p` relative to `scripts/`).

## Step 2: Capture a 1:1 reference screenshot

Use an in-emulator screenshot—not a YouTube frame—for color matching. Video re-encoding adds blended pixels that do not exist in the hardware palette.

1. Start the game and reach the level you want to rip:

   ```bash
   mame -rompath rom gauntlet
   ```

2. Disable scaling and post-processing (exact menu names vary by MAME version):
   - Integer scaling or **window size = native resolution**
   - No bilinear filtering
   - No HLSL / shader passes (or use a raw/unfiltered view)

3. Pause on the frame you want.

4. Press **F12** (default) to save a screenshot to MAME's `snap/` directory.

Native Gauntlet resolution is **336×240**. The screenshot should be that size (or an exact integer multiple, e.g. 672×480). If width/height are odd non-multiples, something is still scaling the output.

Keep this screenshot for visual comparison only. Tile decoding still comes from ROM + palette RAM, not from the PNG.

## Step 3: Dump palette RAM from the debugger

Palette colors are **runtime state**. Dump them on the same frame as your screenshot.

1. With the game paused on the target level, open the MAME debugger (**Tab** by default).
2. Run:

   ```
   save palette_raw.dump,910000:maincpu,800
   ```

   This writes **2048 bytes** (1024 big-endian 16-bit IRGB entries) starting at CPU address `0x910000`.

3. Copy the file into this repo:

   ```bash
   cp snap/palette_raw.dump gfx/palette/palette_raw.dump
   ```

### Palette RAM map

| Index range | CPU address | Count | Purpose              |
|-------------|-------------|-------|----------------------|
| 0–255       | `0x910000`  | 256   | Text / alphanumeric  |
| 256–511     | `0x910200`  | 256   | Motion objects       |
| 512–767     | `0x910400`  | 256   | **Playfield**        |
| 768–1023    | `0x910600`  | 256   | Extra                |

Source: [`gfx/palette/palette.txt`](../gfx/palette/palette.txt) (from MAME address map).

**Important:** Floor and wall tiles use the **playfield** section (512–767), not motion object (256–511). A brown floor can look olive when several brown pens are dithered together; that is not the same as the bright greens in the MO palette.

## Step 4: Convert the dump

From the repo root:

```bash
python3 scripts/convert_mame_palette_dump.py gfx/palette/palette_raw.dump
```

Outputs in `gfx/palette/`:

- `palette_all.csv`, `palette_text.csv`, `palette_motion_object.csv`, `palette_playfield.csv`, `palette_extra.csv` — hex colors as `0xRRGGBB`, 16 per row
- `palette_all.bmp` and per-section BMP previews — 16 swatches per row, each swatch 8×8 pixels

Skip BMP generation:

```bash
python3 scripts/convert_mame_palette_dump.py gfx/palette/palette_raw.dump --no-bmp
```

Custom output directory:

```bash
python3 scripts/convert_mame_palette_dump.py gfx/palette/palette_raw.dump -o /tmp/palette_out
```

## Step 5: Look up indices and color codes

The converter includes helpers for playfield debugging:

```bash
# Decode specific palette indices (compare with palette_all.bmp row/col)
python3 scripts/convert_mame_palette_dump.py gfx/palette/palette_raw.dump --lookup 642 514

# Show all 16 pens for playfield color_code 0x18 (typical brown floor group)
python3 scripts/convert_mame_palette_dump.py gfx/palette/palette_raw.dump --color-code 0x18

# Given palette_select (tile RAM bits 12-14) and tile pen (0-15)
python3 scripts/convert_mame_palette_dump.py gfx/palette/palette_raw.dump --playfield-pen 0 2
```

For Gauntlet, default playfield color codes are **`0x18`–`0x1F`** (palette select 0–7). Index `642` (floor brown pen 2) XOR `0x80` → `514` (darker stipple half).

## MAME UI tools (quick checks)

Press **F4** during gameplay to open the [tile / palette viewer](https://wiki.mamedev.org/index.php/Using_the_GFX/TileMap_viewer_(F4)).

- Cycle palettes with arrow keys to see text, motion object, and playfield banks.
- Tile viewer colors are useful for tile shapes but can be misleading for final on-screen colors—always prefer a palette RAM dump from the same frame.

See [README — Tile Palettes](../README.md#tile-palettes) for example screenshots of the three main palette regions.

## Recommended workflow

1. `mame -rompath rom -verifyroms gauntlet`
2. Play to the target level; pause.
3. Debugger: `save palette_raw.dump,910000:maincpu,800`
4. F12 screenshot at native resolution (same frame).
5. `python3 scripts/convert_mame_palette_dump.py gfx/palette/palette_raw.dump`
6. Use `--color-code` / `--lookup` to tie tile pens to swatches in `palette_playfield.bmp`.
7. Decode tile ROM pens separately (see [4bpp_planar_graphics.md](4bpp_planar_graphics.md) for sprites; playfield uses the same 4bpp pen idea).

## Common pitfalls

| Problem | Cause |
|---------|--------|
| Hundreds of colors in an 8×8 tile capture | Source was scaled or recompressed (e.g. YouTube), not raw hardware pens |
| Floor color not in motion object BMP | Wrong palette bank—use playfield indices 512–767 |
| Same tile, two brightnesses | Playfield XOR `0x80` bank (MO pen 1 draws over playfield) |
| Colors don't match an old dump | Palette RAM changes during gameplay; re-dump on the exact level/frame |
| `-verifyroms` fails on `6p` | EPROM size mismatch; need 16 KiB `136037-104.6p` for current MAME |

## Related docs

- [playfield_palette_mapping.md](playfield_palette_mapping.md) — formulas, XOR bank, worked examples
- [4bpp_planar_graphics.md](4bpp_planar_graphics.md) — motion object tile ROM layout
- [2bpp_planar_graphics.md](2bpp_planar_graphics.md) — alphanumeric tile ROM layout
- [README — Verify EPROMs With MAME](../README.md#verify-eproms-with-mame)
