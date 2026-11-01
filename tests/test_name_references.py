"""Every aligned code literal into the original names must be relocated.

The boss HUD points inside the table, so a base-pointer-only scan missed it.
"""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

import asm
import build

pytestmark = pytest.mark.skipif(not build.ROM.is_file(), reason="no ROM dump in rom/")


def test_all_name_table_literals_are_accounted_for():
    original = build.ROM.read_bytes()
    actual = {off for off in range(0, len(original), 4)
              if 0x0830E48C <= struct.unpack_from("<I", original, off)[0] < 0x0830E48C + 167 * 8}
    expected = {lit for _, lit in asm.NAME_SITES} | {asm.NAME_162, asm.NAME_BOSS[1]}
    assert actual == expected
