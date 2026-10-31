"""Story scripts: the pointer table at 0x32A670 covers 0x324AF0-0x32A66F exactly and every script roundtrips."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tbl import Table  # noqa: E402

ROM = ROOT / "rom" / "Shin Megami Tensei Devil Children - Puzzle de Call! (Japan).gba"


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")
def test_story_roundtrip():
    d = ROM.read_bytes()
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    ptrs = [struct.unpack_from("<I", d, 0x32A670 + 4 * i)[0] - 0x08000000 for i in range(29)]
    assert ptrs[0] == 0x324AF0
    for k, p in enumerate(ptrs):
        end = ptrs[k + 1] if k + 1 < len(ptrs) else 0x32A670
        s, n = t.decode(d, p, maxlen=0x10000)
        assert p + n == end, k
        assert t.encode(s) == d[p:end], k
