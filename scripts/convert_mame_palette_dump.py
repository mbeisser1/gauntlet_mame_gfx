#!/usr/bin/env python3
"""Convert a MAME Gauntlet palette RAM dump to RGB CSV and BMP previews.

Input: 2048-byte debugger save from 0x910000 (1024 big-endian IRGB_4444 words).

Example:
    python3 scripts/convert_mame_palette_dump.py gfx/palette/palette_raw.dump
    python3 scripts/convert_mame_palette_dump.py --lookup 642 644 646
    python3 scripts/convert_mame_palette_dump.py --color-code 0x18
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore[misc, assignment]

PALETTE_ENTRIES = 1024
ENTRY_BYTES = 2

SECTIONS = (
    ("palette_text.csv", 0, 256, "text"),
    ("palette_motion_object.csv", 256, 512, "motion object"),
    ("palette_playfield.csv", 512, 768, "playfield"),
    ("palette_extra.csv", 768, 1024, "extra"),
)


def palexpand4(nibble: int) -> int:
    """Replicate a 4-bit nibble into 8 bits (MAME palexpand<4>)."""
    n = nibble & 0xF
    return (n << 4) | n


def irgb_to_rgb(entry: int) -> tuple[int, int, int]:
    """Decode one IRGB_4444 word using MAME standard_irgb_decoder."""
    i = palexpand4(entry >> 12)
    r = (i * palexpand4(entry >> 8)) >> 8
    g = (i * palexpand4(entry >> 4)) >> 8
    b = (i * palexpand4(entry)) >> 8
    return r, g, b


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"{r:02X}{g:02X}{b:02X}"


def load_dump(path: Path) -> list[int]:
    data = path.read_bytes()
    expected = PALETTE_ENTRIES * ENTRY_BYTES
    if len(data) != expected:
        raise ValueError(f"expected {expected} bytes, got {len(data)} from {path}")

    entries: list[int] = []
    for offset in range(0, len(data), ENTRY_BYTES):
        entries.append(struct.unpack(">H", data[offset : offset + 2])[0])
    return entries


def decode_palette(entries: list[int]) -> list[tuple[int, int, int]]:
    return [irgb_to_rgb(entry) for entry in entries]


def write_csv(path: Path, rgb_values: list[tuple[int, int, int]], start: int = 0, end: int = PALETTE_ENTRIES) -> None:
    subset = rgb_values[start:end]
    with path.open("w", encoding="ascii") as outfile:
        for row in range(0, len(subset), 16):
            line = ", ".join(f"0x{rgb_to_hex(rgb)}" for rgb in subset[row : row + 16])
            outfile.write(line + "\n")


COLORS_PER_ROW = 16
SWATCH_SIZE = 8


def write_bmp(path: Path, rgb_values: list[tuple[int, int, int]], start: int = 0, end: int = PALETTE_ENTRIES) -> None:
    if Image is None:
        print(f"skipping {path.name}: Pillow not installed", file=sys.stderr)
        return

    subset = rgb_values[start:end]
    if len(subset) % COLORS_PER_ROW:
        raise ValueError(f"palette slice {start}:{end} is not a multiple of {COLORS_PER_ROW} entries")

    cols = COLORS_PER_ROW
    rows = len(subset) // cols
    img = Image.new("RGB", (cols * SWATCH_SIZE, rows * SWATCH_SIZE))
    pixels = img.load()

    for index, rgb in enumerate(subset):
        x0 = (index % cols) * SWATCH_SIZE
        y0 = (index // cols) * SWATCH_SIZE
        for y in range(SWATCH_SIZE):
            for x in range(SWATCH_SIZE):
                pixels[x0 + x, y0 + y] = rgb

    img.save(path)


def playfield_color_code(palette_select: int, color_bank: int = 1) -> int:
    """Gauntlet playfield color code from tile RAM bits 12-14."""
    return 0x10 + (color_bank * 8) + (palette_select & 7)


def palette_index(color_code: int, pen: int) -> int:
    """Final palette index for a 4BPP playfield/MO tile pixel."""
    return 256 + (16 * color_code) + (pen & 0xF)


def lookup_entries(entries: list[int], rgb_values: list[tuple[int, int, int]], indices: list[int]) -> None:
    for index in indices:
        if index < 0 or index >= len(entries):
            print(f"index {index}: out of range (0-{len(entries) - 1})", file=sys.stderr)
            continue
        raw = entries[index]
        rgb = rgb_values[index]
        xor_index = index ^ 0x80
        xor_rgb = rgb_values[xor_index]
        print(
            f"index {index:4d}: raw=0x{raw:04X}  #{rgb_to_hex(rgb)}"
            f"  xor128 -> index {xor_index}: #{rgb_to_hex(xor_rgb)}"
        )


def print_color_code_group(entries: list[int], rgb_values: list[tuple[int, int, int]], color_code: int) -> None:
    base = palette_index(color_code, 0)
    print(f"color_code 0x{color_code:02X}  palette indices {base}-{base + 15}")
    for pen in range(16):
        index = base + pen
        raw = entries[index]
        rgb = rgb_values[index]
        print(f"  pen {pen:2d}  index {index:4d}  raw=0x{raw:04X}  #{rgb_to_hex(rgb)}")


def convert_dump(input_path: Path, output_dir: Path, write_previews: bool) -> None:
    entries = load_dump(input_path)
    rgb_values = decode_palette(entries)
    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(output_dir / "palette_all.csv", rgb_values)
    for filename, start, end, label in SECTIONS:
        write_csv(output_dir / filename, rgb_values, start, end)
        print(f"wrote {filename} ({label}, indices {start}-{end - 1})")

    if write_previews:
        write_bmp(output_dir / "palette_all.bmp", rgb_values)
        for filename, start, end, label in SECTIONS:
            bmp_name = Path(filename).with_suffix(".bmp").name
            write_bmp(output_dir / bmp_name, rgb_values, start, end)
        print("wrote palette BMP previews")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="MAME palette dump (2048 bytes from save palette.bin,910000:maincpu,800)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("gfx/palette"),
        help="directory for CSV/BMP outputs (default: gfx/palette)",
    )
    parser.add_argument(
        "--no-bmp",
        action="store_true",
        help="skip BMP preview generation",
    )
    parser.add_argument(
        "--lookup",
        type=int,
        nargs="+",
        metavar="INDEX",
        help="print decoded RGB for palette indices",
    )
    parser.add_argument(
        "--color-code",
        type=lambda value: int(value, 0),
        metavar="CODE",
        help="print the 16 pens for a playfield/MO color code (e.g. 0x18)",
    )
    parser.add_argument(
        "--playfield-pen",
        type=int,
        nargs=2,
        metavar=("PALETTE_SELECT", "PEN"),
        help="show palette index for Gauntlet playfield (palette_select, tile_pen)",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    needs_dump = (
        args.input is not None
        or args.lookup is not None
        or args.color_code is not None
        or args.playfield_pen is not None
    )
    if not needs_dump:
        parser.error("input dump path is required")

    entries = load_dump(args.input)
    rgb_values = decode_palette(entries)

    convert_only = (
        args.lookup is None
        and args.color_code is None
        and args.playfield_pen is None
    )
    if convert_only:
        convert_dump(args.input, args.output_dir, write_previews=not args.no_bmp)

    if args.playfield_pen is not None:
        palette_select, pen = args.playfield_pen
        color_code = playfield_color_code(palette_select)
        index = palette_index(color_code, pen)
        print(f"palette_select={palette_select}, pen={pen}")
        print(f"color_code=0x{color_code:02X}, palette_index={index}")
        lookup_entries(entries, rgb_values, [index])

    if args.lookup is not None:
        lookup_entries(entries, rgb_values, args.lookup)

    if args.color_code is not None:
        print_color_code_group(entries, rgb_values, args.color_code)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
