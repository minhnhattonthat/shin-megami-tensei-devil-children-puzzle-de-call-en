"""Every rescue string has a real selecting demon; the old direct-index tour did not."""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import extract
import qa_tour


@pytest.mark.skipif(not extract.ROM.is_file(), reason="no ROM")
def test_rescue_message_coverage():
    targets = qa_tour.rescue_targets()
    original = extract.ROM.read_bytes()
    assert set(targets) == set(range(1, 101))
    assert any(demon > 100 for demon in targets.values())
    for message, demon in targets.items():
        assert original[0x1626A5 + 2 * demon] + 1 == message
    assert targets[25] == 4  # Mecci's symbols; demon 25 actually uses message 47
    assert targets[66] == 33 and targets[67] == 83  # Quetza / Teskarot


def test_skipped_tutorial_is_not_coverage(tmp_path, monkeypatch):
    calls = []
    def fake_call(command, **kwargs):
        calls.append(command)
        return 0
    monkeypatch.setattr(qa_tour.subprocess, "call", fake_call)
    directory = tmp_path / "tutorial_2"
    directory.mkdir()
    # This is what the former mash-based tour actually did: left the tutorial
    # and played the prologue. A successful emulator exit is insufficient.
    (directory / "log.txt").write_text("STATE 7\nSTATE 0\nscript 0\nfinal frame 11000\n")
    item = ("tutorial_2", "tutorial_2", ["TUTORIAL_ID=1", "EXTRA_EVERY=30"], 60000, qa_tour.MSG_BOX)
    assert qa_tour.run(tmp_path / "candidate.gba", tmp_path, item) == ("tutorial_2", 1)
    assert len(calls) == 1  # no sheets certified for a skipped demo
    assert calls[0][calls[0].index("--mash") + 1] == "0"
    (directory / "log.txt").write_text("TUTORIAL_START 1\nTUTORIAL_DONE 1\n")
    assert qa_tour.run(tmp_path / "candidate.gba", tmp_path, item) == ("tutorial_2", 0)
