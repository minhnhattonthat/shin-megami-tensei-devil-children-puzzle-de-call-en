"""Debug-tool scene list: parses, names unique, valid states, and every story script 0-28 has a scene."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "debug"))
from warp_all import scenes  # noqa: E402


def test_scene_list():
    lines = [ln.split("#", 1)[0].split("|", 1)[0].split() for ln in
             (ROOT / "tools" / "debug" / "scenes.txt").read_text(encoding="utf-8").splitlines()]
    lines = [ln for ln in lines if ln]
    names = [ln[0] for ln in lines]
    assert len(names) == len(set(names)) == len(scenes())
    assert all(0 <= int(ln[1]) <= 11 for ln in lines)
    for ln in lines:  # poke/option syntax warp.lua accepts
        assert all(re.fullmatch(r"[\w]+=(0x[0-9A-Fa-f]+|\d+)(@\d+)?", t) for t in ln[2:]), ln
    scripts = {int(t.split("=")[1]) for ln in lines for t in ln[2:] if t.startswith("SCRIPT=")}
    assert scripts == set(range(29))
