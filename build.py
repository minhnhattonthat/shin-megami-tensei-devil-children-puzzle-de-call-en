"""build.py: original ROM -> build/pdc_en.gba (+ build/writes.txt for romdiff.py --writes).

    python -X utf8 build.py
Unpacks every text and LZ block (tools/blocks.py) and packs it back. Edited entries come in from later phases; with
none, the output is byte-identical to the original (tests/test_identity.py).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import blocks  # noqa: E402
import check_rom  # noqa: E402

ROM = ROOT / "rom" / "Shin Megami Tensei Devil Children - Puzzle de Call! (Japan).gba"
OUT = ROOT / "build" / "pdc_en.gba"


def build(orig):
    """Returns the Rom (output buffer + write log)."""
    rom = blocks.Rom(orig)
    for name in blocks.PACKED:
        blocks.pack_packed(rom, name, blocks.unpack_packed(orig, name))
    for name in blocks.RECORDS:
        blocks.pack_record(rom, name, blocks.unpack_record(orig, name))
    for name in blocks.LZ:
        blocks.pack_lz(rom, name, *blocks.unpack_lz(orig, name))
    return rom


def main():
    check_rom.check()
    rom = build(ROM.read_bytes())
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(rom.out)
    (OUT.parent / "writes.txt").write_text(rom.writes_log(), encoding="utf-8", newline="\n")
    print(f"{OUT.relative_to(ROOT)}: {len(rom.writes)} writes, free space used {rom.free - blocks.FREE[0]:#x} bytes")


if __name__ == "__main__":
    main()
