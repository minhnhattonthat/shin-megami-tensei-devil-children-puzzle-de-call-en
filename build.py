"""build.py: original ROM -> build/pdc_en.gba (+ build/writes.txt for romdiff.py --writes).

    python -X utf8 build.py
Unpacks every text and LZ block (tools/blocks.py), swaps in every translated unit (`en` in script/*.json, see
tools/text.py and tools/extract.py) and packs it back. With no `en`, the output is byte-identical to the original
(tests/test_identity.py).
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import asm  # noqa: E402
import blocks  # noqa: E402
import check_rom  # noqa: E402
import extract  # noqa: E402
import romdiff  # noqa: E402
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


# words that look like pointers into a moved block's old slot but are compressed data (checked: lz77.decompress)
NOT_POINTERS = {0x2579EC: "inside LZ 0x253B8C..0x259C1D", 0x2769D8: "inside ending picture LZ 0x276398..0x27D054"}


def allowed(orig, used_free):
    """[(lo, hi, what)] (hi exclusive): every range the build may write. Anything else is a bug (romdiff.py)."""
    out = [(blocks.PACKED[n][2], blocks.PACKED[n][0] + 4 * blocks.PACKED[n][1], n) for n in blocks.PACKED]
    out += [(s, s + c * z, n) for n, (s, c, z) in blocks.RECORDS.items()]
    out += [(o, o + ((blocks.unpack_lz(orig, n)[2] - o + 3) & ~3), n) for n, o in blocks.LZ.items()]
    out += [(blocks.FREE[0], used_free, "free space"), (asm.ENGINE, asm.END, "engine")]
    out += [r for s, lit in asm.NAME_SITES for r in ((s, s + 2, "names x16"), (lit, lit + 4, "names ptr"))]
    out += [(asm.NAME_162, asm.NAME_162 + 4, "name 162 ptr")]
    out += [(o, o + len(b) // 2, "hook") for o, (_, b) in asm.HOOKS.items()]
    return out


def verify(orig, rom, en):
    """ROM-level checks of a build (docs/re/build.md "Checks"); returns error lines."""
    out = bytes(rom.out)
    errs = romdiff.check(orig, out, set(), rom.writes)[0]  # every changed byte has a logged write, none overwritten
    ranges = allowed(orig, rom.free)
    for off, _, new, who in rom.writes:
        if not any(lo <= off and off + len(new) <= hi for lo, hi, _ in ranges):
            errs.append(f"{off:#x}+{len(new)} ({who}): outside every allowed range")
    if not en:
        return errs
    # every string read back through its (possibly moved) pointer: same skeleton, units = en, codes kept
    for name, (table, count, start, codec, base, _) in blocks.PACKED.items():
        t, te = blocks.table(codec), blocks.en_table(codec)
        for k, (jp_raw, en_raw) in enumerate(zip(blocks.unpack_packed(orig, name), blocks.unpack_packed(out, name))):
            want, u = [], 0
            for is_unit, piece in text.split(codec, t.decode(jp_raw, length=len(jp_raw))[0]):
                want.append(en.get(f"{name}.{k:03}.{u:02}", piece) if is_unit else piece)
                u += is_unit
            got = te.decode(en_raw, length=len(en_raw))[0]
            if got != "".join(want):
                errs.append(f"{name}.{k:03}: built bytes decode to {got[:60]!r}, want {''.join(want)[:60]!r}")
            skel = lambda s: [x for x in text.TOKEN.findall(s) if x.startswith("{") and x not in text.INLINE[codec]
                              and not text.COLOUR.match(x)]  # noqa: E731
            if skel(got) != skel(t.decode(jp_raw, length=len(jp_raw))[0]):
                errs.append(f"{name}.{k:03}: control codes differ from the original")
        moved = blocks.pointers(out, name)[0] != start
        if moved:  # nothing but the pointer table may point into the vacated slot
            # exact ROM / EWRAM words only: masking flag bits (& 0x0FFFFFFF) hits ~80 Thumb-code words, all noise
            words = struct.unpack_from("<%dI" % (len(orig) // 4), orig)
            for i, w in enumerate(words):
                a = w - base
                if start <= a < table and not table <= 4 * i < table + 4 * count and 4 * i not in NOT_POINTERS:
                    errs.append(f"{name}: word at {4 * i:#x} ({w:#010x}) points into the vacated slot")
    for k in range(167):
        uid, rec = f"names.{k:03}", out[asm.NAMES + k * asm.NAME_SIZE:asm.NAMES + (k + 1) * asm.NAME_SIZE]
        b = rec.split(b"\xff")[0]
        if uid in en and blocks.en_table("msg").decode(b, length=len(b))[0] != en[uid]:
            errs.append(f"{uid}: name table holds {rec.hex()}")
    for name in blocks.RECORDS:
        if name == "names":
            continue
        for e in text.units(out, "en")[name]:
            if e["id"] in en and e["jp"] != en[e["id"]]:
                errs.append(f"{e['id']}: record holds {e['jp']!r}, want {en[e['id']]!r}")
    return errs


def main():
    check_rom.check()
    en = extract.en_map()
    known = {e["id"] for us in text.units(ROM.read_bytes()).values() for e in us}
    if set(en) - known:
        sys.exit(f"script/: en for unknown unit ids {sorted(set(en) - known)[:5]}; re-run tools/extract.py")
    orig = ROM.read_bytes()
    rom = build(orig, en)
    print(f"{len(en)} translated units")
    errs = verify(orig, rom, en)
    if errs:
        sys.exit("\n".join(errs[:40] + [f"{len(errs)} build check errors; nothing written"]))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(rom.out)
    (OUT.parent / "writes.txt").write_text(rom.writes_log(), encoding="utf-8", newline="\n")
    print(f"{OUT.relative_to(ROOT)}: {len(rom.writes)} writes, free space used {rom.free - blocks.FREE[0]:#x} bytes")


if __name__ == "__main__":
    main()
