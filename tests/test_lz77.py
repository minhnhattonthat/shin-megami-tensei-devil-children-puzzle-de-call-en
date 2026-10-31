import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lz77  # noqa: E402

ROM = ROOT / "rom" / "Shin Megami Tensei Devil Children - Puzzle de Call! (Japan).gba"


def test_lz77_roundtrip_synthetic():
    for data in (b"", b"a", b"abcabc" * 100, os.urandom(2000), bytes(4000)):
        assert lz77.decompress(lz77.compress(data))[0] == data


def test_lz77_font_block():
    if not ROM.is_file():
        return
    d = ROM.read_bytes()
    font, end = lz77.decompress(d, 0x160698)
    assert len(font) == 248 * 128
    assert lz77.decompress(lz77.compress(font))[0] == font
