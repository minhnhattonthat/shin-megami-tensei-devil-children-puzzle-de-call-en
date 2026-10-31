"""Translated units: every merged `src` re-renders to its `en` and passes every batch rule (width, pages, codes,
glossary). tools/batches.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import batches  # noqa: E402


def test_wrap_pages():
    en, probs = batches.render("story", "Short line. // " + "word " * 12, "x")
    assert not probs and en.count("{wait:00}{clr}{box:09}") == 1 and en.count("{n}") == 1
    _, probs = batches.render("story", "word " * 60, "x")
    assert any("lines" in p for p in probs)


def test_wrap_prefers_sentence_end():
    assert batches.wrap("There's only one place I can think of. It's gotta be Quadriga-ho.") == [
        "There's only one place I can think of.", "It's gotta be Quadriga-ho."]


def test_line_colour():
    jp = "{col:03}あれ{n}{col:03}まだ{page}{col:03}たぶん"
    assert batches.line_colour(jp, "msg") == "03"
    en, probs = batches.render("rescue", "Huh? // Maybe.", jp)
    assert en == "{col:03}Huh?{page}{col:03}Maybe." and not probs


def test_whole_run_terms():
    assert batches.has_term("デビルたち", "デビル") and not batches.has_term("デビルチルドレン", "デビル")


def test_raw_layout_gated():
    b, e = batches.by_id()["story.014.32"]
    assert any("px" in p for p in batches.problems(b, e, "=" + "W" * 200))
    assert any("lines" in p for p in batches.problems(b, e, "=one{n}two{n}three"))
    assert not batches.problems(b, e, e["src"])


def test_honorifics():
    b, e = batches.by_id()["rescue.068.00"]
    assert any("honorific" in p for p in batches.problems(b, e, "Please save Odin. // Search here again later."))
    assert not batches.problems(b, e, "Please save Odin-sama. // Search here again later.")
    b, e = batches.by_id()["rescue.028.00"]
    assert any("honorific" in p for p in batches.problems(b, e, "Huh, Tsunami hasn't been saved yet? // Later."))
    assert not batches.honorifics("カミさまはみてる", "カミ") and not batches.honorifics("オレさま", "オレ")
    assert batches.honorifics("オーディンさまを", "オーディン") == {"sama"}


def test_glossary_whole_words():
    b, e = batches.by_id()["story.005.01"]
    assert any("Jin" in p for p in batches.problems(b, e, "Jinx! Hey, it is Jinx!!"))
    assert not any("glossary" in p for p in batches.problems(b, e, "Jin! Hey, it's Jin's voice!!"))
    assert batches.has_en("the Rando kid", "rando") and not batches.has_en("Randolph", "Rand")


def test_lint_merged():
    assert batches.lint() == []
