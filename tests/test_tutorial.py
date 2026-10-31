"""Tutorial scripts (table 0x3111F8): the guessed command lengths parse each script exactly to the next pointer."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import tutorial  # noqa: E402

ROM = ROOT / "rom" / "Shin Megami Tensei Devil Children - Puzzle de Call! (Japan).gba"


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")
def test_tutorial_parses_to_next_pointer():
    d = ROM.read_bytes()
    ptrs = tutorial.scripts(d)
    assert ptrs[0] == 0x30FD48
    for k, p in enumerate(ptrs):
        _, end = tutorial.parse(d, p)
        assert end == (ptrs[k + 1] if k + 1 < len(ptrs) else tutorial.TABLE), k
