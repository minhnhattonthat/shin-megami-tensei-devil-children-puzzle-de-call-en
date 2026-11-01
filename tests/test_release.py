"""Release safety: help has no side effects, polish blocks, ZIP patch reapplies."""
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import bps
import release


def test_help_does_not_build(monkeypatch):
    monkeypatch.setattr(release, "run", lambda *args: pytest.fail("help ran a build"))
    with pytest.raises(SystemExit) as result:
        release.main(["--help"])
    assert result.value.code == 0


def test_existing_release_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(release, "ROOT", tmp_path)
    (tmp_path / "release").mkdir()
    (tmp_path / "release" / (release.STEM + "1.0.zip")).write_bytes(b"existing")
    monkeypatch.setattr(release, "run", lambda *args: pytest.fail("overwriting build started"))
    with pytest.raises(SystemExit) as result:
        release.main([])
    assert result.value.code == 2


def test_polish_blocks(tmp_path):
    path = tmp_path / "polish.md"
    path.write_text("- [ ] pending\n")
    with pytest.raises(ValueError, match="unticked"):
        release.polish_gate(path)
    path.write_text("- [x] fixed\n")
    release.polish_gate(path)


def test_zip_patch_reapplies(tmp_path, monkeypatch):
    monkeypatch.setattr(release, "ROOT", tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/release-readme.txt").write_text("Version {{VERSION}}, {{BASE_SHA1}} -> {{PATCHED_SHA1}}")
    original, translated = b"original data" * 100, b"English data" * 100
    archive = release.package(original, translated, "1.0", tmp_path / "release")
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist()) == 2
        assert bps.apply(original, z.read(release.STEM + "1.0.bps")) == translated
        assert "{{" not in z.read("README.txt").decode()
