"""Identity build: unpack + repack every text and LZ block with no edits gives the original ROM byte for byte."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import blocks  # noqa: E402
import build  # noqa: E402
import lz77  # noqa: E402

pytestmark = pytest.mark.skipif(not build.ROM.is_file(), reason="no ROM dump in rom/")


@pytest.fixture(scope="module")
def orig():
    return build.ROM.read_bytes()


def test_identity(orig):
    rom = build.build(orig)
    assert rom.out == orig
    covered = sum(len(w[2]) for w in rom.writes)
    assert covered > 0x9000  # every block really went through pack (story alone is ~23 KB)


def test_grown_block_relocates(orig):
    rom = blocks.Rom(orig)
    entries = blocks.unpack_packed(orig, "pause")
    entries[0] = b"\x01" * 60 + b"\xff"
    blocks.pack_packed(rom, "pause", entries)
    ptrs = blocks.pointers(bytes(rom.out), "pause")
    assert ptrs[0] == blocks.FREE[0]
    for p, e in zip(ptrs, entries):
        assert rom.out[p:p + len(e)] == e
    assert rom.out[0x30E414:0x30E440] == orig[0x30E414:0x30E440]  # old slot untouched


def test_client_block_cannot_leave_image(orig):
    entries = blocks.unpack_packed(orig, "client_pause")
    entries[0] = b"\x01" * 40 + b"\xff"
    with pytest.raises(ValueError):
        blocks.pack_packed(blocks.Rom(orig), "client_pause", entries)


def test_edited_lz_roundtrips(orig):
    data, md, end = blocks.unpack_lz(orig, "title_menu")
    rom = blocks.Rom(orig)
    # grown past its slot: moves to word-aligned free space, every literal pointer follows, the old slot is untouched
    grown = bytes(b ^ 0x11 for b in data[:64]) + data[64:]
    blocks.pack_lz(rom, "title_menu", grown, md, end)
    refs = blocks.lz_xrefs(orig, blocks.LZ["title_menu"])
    new = struct.unpack_from("<I", rom.out, refs[0])[0] - blocks.ROM_BASE
    assert refs and new % 4 == 0 and new >= blocks.FREE[0] and lz77.decompress(bytes(rom.out), new)[0] == grown
    assert all(struct.unpack_from("<I", rom.out, r)[0] == new + blocks.ROM_BASE for r in refs)
    assert rom.out[blocks.LZ["title_menu"]:end] == orig[blocks.LZ["title_menu"]:end]
    rom = blocks.Rom(orig)
    edited = bytes(64) + data[64:]
    blocks.pack_lz(rom, "title_menu", edited, md, end)
    assert lz77.decompress(bytes(rom.out), blocks.LZ["title_menu"])[0] == edited
    assert struct.unpack_from("<I", rom.out, 0)[0] == struct.unpack_from("<I", orig, 0)[0]
