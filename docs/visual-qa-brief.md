# Visual-QA reviewer brief - Shin Megami Tensei: Devil Children - Puzzle de Call! (GBA)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- Optional: the original ROM's sheets (`work/qa/tour_jp/`, same ids) and `glossary.md`.

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png` and read that.
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.

## Judge
An `issue` is any of:
- Japanese still visible;
- text overflowing a box, clipped by a frame, or running off screen;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok` (the controller adds the game's own below):
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's sheet.
- Japanese drawn as graphics, not text: title screen and logo, title/story menu plates, area cards, banners
  (レースモード, デビダス), pause-list headers (デビライザー, デビルいちらん), DeviDas info labels (クラス 種族 属性 and
  their values), HUD labels (こうげき, タイム). Graphics are a later phase (docs/re/graphics.md); note them, `ok`.
- Marker builds (`build/pdc_marker.gba`): every line reads `[id] The quick brown fox...` filled to the box's measured
  line limit, so a line ending right at the box's inner edge is by design. The issue is a glyph cut by the frame or
  drawn past it. In the last line of a page, the page arrow (x 225-230) overlapping the line's last glyph is known
  (budget 210 px there, docs/re/vwf.md), `ok`.
- The yes/no box's `q` (marker id `q0.0`) is the game's own 8x8 `q`, which looks like `9`: `ok`, note it.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
