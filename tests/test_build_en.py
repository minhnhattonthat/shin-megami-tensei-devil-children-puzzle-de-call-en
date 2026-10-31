"""The English build passes build.verify (romdiff write log + allowed ranges, every string read back through its
pointer with its control codes, no stale pointer to a moved block), and no code hook swallows a branch target."""
import re
import sys
from pathlib import Path

import pytest
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import asm  # noqa: E402
import blocks  # noqa: E402
import build  # noqa: E402
import extract  # noqa: E402

pytestmark = pytest.mark.skipif(not build.ROM.is_file(), reason="no ROM dump in rom/")


@pytest.fixture(scope="module")
def orig():
    return build.ROM.read_bytes()


@pytest.fixture(scope="module")
def en():
    return extract.en_map()


@pytest.fixture(scope="module")
def rom(orig, en):
    return build.build(orig, en)


def test_verify_clean(orig, rom, en):
    assert build.verify(orig, rom, en) == []


def test_final_requires_all_translations(orig, rom, en):
    incomplete = {uid: value for uid, value in en.items() if uid != "names.000"}
    assert "names.000: missing English translation" in build.verify(orig, rom, incomplete)
    empty = dict(en, **{"names.000": ""})
    assert "names.000: missing English translation" in build.verify(orig, rom, empty)
    assert any("missing English" in p for p in build.verify(orig, blocks.Rom(orig), {}))
    assert build.verify(orig, blocks.Rom(orig), {}, mode="identity") == []


def test_verify_catches(orig, rom, en):
    bad = blocks.Rom(orig)
    bad.out, bad.writes, bad.free = bytearray(rom.out), list(rom.writes), rom.free
    bad.out[0x100] ^= 1  # a change with no write behind it
    bad.put(0x200, b"\x00", "stray")  # a write outside every range
    p = blocks.pointers(bytes(bad.out), "pause")[0]
    bad.out[p] ^= 1  # a built string that no longer decodes to its en
    errs = "\n".join(build.verify(orig, bad, en))
    assert "outside every allowed range" in errs and "0x000100" in errs and "pause.000" in errs


def test_hooks_keep_branch_targets(orig, rom):
    """No B/Bcc/BL within 4 KB of a hook lands strictly inside the bytes the hook wrote."""
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    cs.skipdata = True  # else disasm stops at the first literal pool word
    bad, seen = [], 0
    for off, _, new, who in rom.writes:
        if not who.startswith("hook"):
            continue
        lo = max(0, off - 0x1000)
        # the original code from the hook to where it jumps back ("b 0x0801D608") is dead; branches from it don't count
        skip = re.search(r"\bb (0x[0-9A-Fa-f]+)$", asm.HOOKS[off][0])
        dead = int(skip[1], 16) - blocks.ROM_BASE if skip else off + len(new)
        for ins in cs.disasm(orig[lo:off + 0x1000], blocks.ROM_BASE + lo):
            if ins.mnemonic.startswith("b") and ins.op_str.startswith("#"):
                t = int(ins.op_str[1:], 16) - blocks.ROM_BASE
                seen += 1
                if off < t < off + len(new) and not off <= ins.address - blocks.ROM_BASE < dead:
                    bad.append(f"{who}: {ins.address:#x} {ins.mnemonic} {ins.op_str}")
    assert bad == [] and seen > 1000  # seen: the scan really decoded the code around every hook
