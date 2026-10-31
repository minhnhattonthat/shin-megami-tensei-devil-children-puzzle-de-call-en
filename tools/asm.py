"""Code patches: assemble asm/vwf.s (keystone, Thumb) into the engine area and hook the game's text printers.

    python -X utf8 tools/asm.py        # selftest: assemble, check the hooks' original bytes, disassemble the hooks
Layout (file offsets, inside the free space; blocks.FREE stops below ENGINE): code at ENGINE, then the VWF tables.
docs/re/vwf.md has what each hook replaces.
"""
import re
import struct
import sys
from pathlib import Path

from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import smallfont  # noqa: E402
import vwf  # noqa: E402

ROM_BASE = 0x08000000
ENGINE = 0x3F0000
WIDTH = ENGINE + 0x800  # big-font advances
SMALLW = ENGINE + 0x900  # menu-font advances
FONT = ENGINE + 0xC00  # 256 x 64 bytes, to ENGINE + 0x4C00
NAMES = FONT + 256 * 64  # demon names, 167 x NAME_SIZE (was 8 bytes per name at 0x30E48C)
NAME_SIZE = 16  # 15 glyphs + FF (blocks.EN_MAX["names"])
END = NAMES + 167 * NAME_SIZE

# every place that reads the name table: (the `lsls rX, rY, #3` that scales the id, the literal 0830E48C)
NAME_SITES = [(0x62A4, 0x62BC), (0x69D2, 0x69E8), (0x6D7C, 0x6D94), (0xC2B6, 0xC2D0), (0xC2D4, 0xC2DC),
              (0xC772, 0xC79C), (0xC7A0, 0xC810), (0xE022, 0xE04C), (0xE050, 0xE068), (0xE16A, 0xE194),
              (0xE198, 0xE1B0), (0x1D586, 0x1D5E4)]
NAME_162 = 0xC344  # literal 0830E99C: name 162 (the 8 x 1C placeholder)

# hook site (file offset): (asm, original bytes it replaces: checked so a wrong ROM or a moved hook fails loudly)
HOOKS = {
    # story: from the visible flag + glyph DMA + slot++ to the cursor advance at 0801B3D6
    0x01B3A4: ("bl {story_char}\nb 0x0801B3D6", "688e0001296a0b184846"),
    # story sprite x: 16 + 14 * column -> 12 + 16 * column (one 224 px bitmap per line)
    0x01A93E: ("lsls r1, r0, #4\nadds r1, #12\nmov r8, r8\nmov r8, r8", "c100091a49001031"),
    # message box (rescue / boss / system): glyph DMA + sprite x/y/palette + column wrap -> 08006340
    0x0062C0: ("adds r0, r5, #0\nadds r1, r6, #0\nbl {msg_char}\nb 0x08006340", "2c1c22340023e3560020"),
    # menu font: one sprite per character -> proportional pen (small_char)
    0x00B46C: ("push {{lr}}\nbl {small_char}\npop {{r0}}\nbx r0", "70b584460906090e856a"),
    # menu strings: at most 8 characters (names had no FF at 8) -> 16 (names now always end in FF)
    0x00B510: ("cmp r6, #15", "072e"),
    0x00B582: ("cmp r6, #15", "072e"),
    # {name} in message boxes: read at most 8 bytes of the name -> 16
    0x0062B0: ("movs r0, #16", "0820"),
    0x0069DE: ("movs r0, #16", "0820"),
    0x006D88: ("movs r0, #16", "0820"),
    # DeviDas name: the 8-sprite glyph loop -> dd_name (r5 name, r4 tiles, r6 sprite records), then its epilogue
    0x01D598: ("adds r0, r5, #0\nadds r1, r4, #0\nadds r2, r6, #0\nbl {dd_name}\nb 0x0801D608",
               "0023134884462878fe2825d8"),
    # DeviDas element sprite 16x16 -> 32x8 (same 4 tiles, DMA and VRAM; English names need 32 px): also set the
    # horizontal shape bit in attr0. r4 (mask) is dead until 0801CB44, so it is no longer narrowed here.
    0x01CADA: ("ldrb r0, [r7, #0xb]\nands r0, r4\nmovs r1, #0x40\norrs r0, r1\nstrb r0, [r7, #0xb]\n"
               "ldrb r0, [r7, #9]\nands r0, r4\norrs r0, r1\nstrb r0, [r7, #9]", "f97a201c084040210843f872787a04407c72"),
    # tutorial box (r7 = struct, r1 = code) -> 08006A5A
    0x0069EC: ("adds r0, r7, #0\nbl {msg_char}\nb 0x08006A5A", "274a3c1c22340023e356"),
    # second message printer (r4 = struct, r1 = code) -> 08006E04
    0x006D98: ("adds r0, r4, #0\nbl {msg_char}\nb 0x08006E04", "251c22350023eb560020"),
}

_ks = Ks(KS_ARCH_ARM, KS_MODE_THUMB)


def _asm(src, addr):
    """Assemble; refuses Thumb-2 encodings (keystone picks them silently, the GBA's ARM7TDMI can't run them)."""
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    b = bytes(_ks.asm(src.replace(".ltorg", ".align 2\n.word 0x4C544F52\n.ltorg"), addr)[0])
    end = b.find(b"ROTL")  # the marker word ends the code; the literal pool follows
    end = len(b) if end < 0 else end
    for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(b[:end], addr):
        if i.size == 4 and i.mnemonic != "bl":
            raise ValueError(f"Thumb-2 instruction at {i.address:#x}: {i.mnemonic} {i.op_str}")
    return b


def engine():
    """(code bytes at ENGINE, {label: address})."""
    src = (ROOT / "asm" / "vwf.s").read_text(encoding="utf-8")
    src = re.sub(r"@.*", "", src)
    consts = {"WIDTH": WIDTH + ROM_BASE, "FONT": FONT + ROM_BASE, "SMALLW": SMALLW + ROM_BASE,
              "HEART": vwf.en_codes()["♥"]}
    for k, v in consts.items():
        src = src.replace("{%s}" % k, "0x%X" % v)
    code = _asm(src, ENGINE + ROM_BASE)
    if ENGINE + len(code) > WIDTH:
        raise ValueError(f"engine code {len(code):#x} bytes overruns the tables")
    # entry points: the branches at the top of asm/vwf.s
    return code, {"story_char": ENGINE + ROM_BASE, "msg_char": ENGINE + ROM_BASE + 2,
                  "small_char": ENGINE + ROM_BASE + 4, "dd_name": ENGINE + ROM_BASE + 6}


def edit_lz(lz):
    """English glyphs in the menu fonts: lz = {block: (data, min_disp, end)} from blocks.unpack_lz, edited in place."""
    data, md, end = lz["font_small"]
    lz["font_small"] = (smallfont.build(data)[0], md, end)
    # shortcut: the multiboot client's copy (client_font_small) keeps its Japanese punctuation: with the new glyphs
    # it recompresses 12 bytes past its slot, and the client image can't grow. Link-play text is phase 7 work.


def apply(rom, names):
    """Write the engine, its tables, the 16-byte name table (names: 167 records) and the hooks into rom (blocks.Rom)."""
    import blocks
    code, labels = engine()
    width, font = vwf.tables()
    rom.put(ENGINE, code, "engine")
    rom.put(WIDTH, width, "vwf width")
    rom.put(SMALLW, smallfont.build(blocks.unpack_lz(rom.orig, "font_small")[0])[1], "menu font width")
    rom.put(FONT, font, "vwf font")
    assert len(names) == 167 and all(len(n) == NAME_SIZE for n in names)
    rom.put(NAMES, b"".join(names), "names")
    for shift, lit in NAME_SITES:
        ins = struct.unpack_from("<H", rom.orig, shift)[0]
        if ins >> 11 != 0 or (ins >> 6) & 31 != 3 or struct.unpack_from("<I", rom.orig, lit)[0] != 0x0830E48C:
            raise ValueError(f"name site {shift:#x}/{lit:#x}: not lsls #3 + 0830E48C")
        rom.put(shift, struct.pack("<H", ins + (1 << 6)), "names x16")  # lsls #3 -> #4
        rom.put(lit, struct.pack("<I", NAMES + ROM_BASE), "names ptr")
    assert struct.unpack_from("<I", rom.orig, NAME_162)[0] == 0x0830E99C
    rom.put(NAME_162, struct.pack("<I", NAMES + 162 * NAME_SIZE + ROM_BASE), "name 162 ptr")
    for off, (src, orig) in HOOKS.items():
        b = _asm(src.format(**labels), off + ROM_BASE)
        if rom.orig[off:off + len(b)] != bytes.fromhex(orig)[:len(b)] or len(b) > len(orig) // 2:
            raise ValueError(f"hook {off:#x}: original bytes differ or patch too long")
        rom.put(off, b, f"hook {off:06X}")


if __name__ == "__main__":
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    code, labels = engine()
    print(f"engine {len(code):#x} bytes")
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    for off, (src, orig) in HOOKS.items():
        b = _asm(src.format(**labels), off + ROM_BASE)
        assert len(b) <= len(orig) // 2, off
        print(f"{off:06X}", "; ".join(f"{i.mnemonic} {i.op_str}" for i in cs.disasm(b, off + ROM_BASE)))
    ins = list(cs.disasm(code, ENGINE + ROM_BASE))
    assert sum(i.size for i in ins) == len(code), "engine does not disassemble cleanly up to its literal pool"
    print("selftest ok")
