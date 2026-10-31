"""build.py: original ROM -> build/pdc_en.gba (+ build/writes.txt for romdiff.py --writes).

    python -X utf8 build.py
Unpacks every text and LZ block (tools/blocks.py), swaps in every translated unit (`en` in script/*.json, see
tools/text.py and tools/extract.py) and packs it back. With no `en`, the output is byte-identical to the original
(tests/test_identity.py).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import asm  # noqa: E402
import blocks  # noqa: E402
import check_rom  # noqa: E402
import extract  # noqa: E402
import text  # noqa: E402

ROM = ROOT / "rom" / "Shin Megami Tensei Devil Children - Puzzle de Call! (Japan).gba"
OUT = ROOT / "build" / "pdc_en.gba"


def build(orig, en=None):
    """Returns the Rom (output buffer + write log). en = {unit id: text}; None = no edits."""
    en = en or {}
    rom = blocks.Rom(orig)
    for name in blocks.PACKED:
        blocks.pack_packed(rom, name, text.packed_entries(orig, name, en))
    for name in blocks.RECORDS:  # names: in English they live in asm.NAMES (16 bytes each), below
        blocks.pack_record(rom, name, text.record_entries(orig, name, {} if name == "names" else en))
    lz = {name: blocks.unpack_lz(orig, name) for name in blocks.LZ}
    if en:
        asm.edit_lz(lz)
    for name in blocks.LZ:
        blocks.pack_lz(rom, name, *lz[name])
    if en:  # English needs the VWF engine (asm/vwf.s); no edits = the original ROM
        asm.apply(rom, text.wide_names(orig, en, asm.NAME_SIZE))
    return rom


def main():
    check_rom.check()
    en = extract.en_map()
    known = {e["id"] for us in text.units(ROM.read_bytes()).values() for e in us}
    if set(en) - known:
        sys.exit(f"script/: en for unknown unit ids {sorted(set(en) - known)[:5]}; re-run tools/extract.py")
    rom = build(ROM.read_bytes(), en)
    print(f"{len(en)} translated units")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(rom.out)
    (OUT.parent / "writes.txt").write_text(rom.writes_log(), encoding="utf-8", newline="\n")
    print(f"{OUT.relative_to(ROOT)}: {len(rom.writes)} writes, free space used {rom.free - blocks.FREE[0]:#x} bytes")


if __name__ == "__main__":
    main()
