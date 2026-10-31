# English text engine (phase 5)

Code: `asm/vwf.s` (Thumb-1, assembled by `tools/asm.py` with keystone; `_asm` refuses any Thumb-2 encoding keystone
picks silently, e.g. `adds r2, r7, #13`). The build applies it whenever there is any `en` (`build.py`); with none the
ROM stays byte-identical. Engine + tables live at 0x3F0000-0x3F5A70 (`blocks.FREE` ends at 0x3F0000).

## Encoding (`tbl/en.tbl`)
One byte per glyph, codes 0x00-0x59, shared by every codec (`blocks.en_table(codec)` = the codec's control codes +
en.tbl). The codes match the game's 8x8 menu font, which already has `0-9` (01-0A), `A-Z` (20-39), `a-z` (3A-53),
`: ; ? ! _ / ~ ( ) + - = & *`; the rest (`, . ' " … ♥ % ♪ # < > [ ]`) overwrite Japanese glyphs at their codes
(`fonts/small.txt`). So a string shows in either font, and names work in both. English text never uses codes >=
0x5A, so it can't collide with FC-FF (msg) or F8/FA (tutorial) control bytes.

## Fonts
- **Big boxes**: `fonts/vwf.txt`, drawn for this project: caps 9 px, x-height 6, descenders 2, 1-7 px wide;
  `tools/vwf.py` adds a colour-2 shadow at (+1, +1) and an advance of width + 1 (space 4). Colours as the Japanese
  font: 1 = body (white in palette 10), 2 = edge (black). `vwf.width(text)` = px.
- **Menus**: the game's 8x8 font with the English glyphs moved to the tile's left edge; advance = ink width + 1, space
  3 (`tools/smallfont.py`, `smallfont.width`). The multiboot client's copy is untouched (its slot can't grow).

## Hooks (`tools/asm.py HOOKS`; each checks the original bytes)
| Site | Was | Now |
|---|---|---|
| 0801B3A4 | story: show slot, DMA glyph, slot++ | `story_char`: draws into the line's 14 sprites as one bitmap |
| 0801A93E | story sprite x = 16 + 14 * col | x = 12 + 16 * col: a line is 224 px (x 12-235) |
| 080062C0, 080069EC, 08006D98 | message / tutorial / 2nd message printer: one sprite per glyph, 14 px pitch, wrap at 16 | `msg_char`: sprites 16 px apart from where each colour run starts; at most 32 sprites per page |
| 0800B46C | menu font: x = col * pitch, col++ | `small_char`: with pitch 8 the column is a pen in px |
| 0800B510, 0800B582 | menu strings stop after 8 characters | after 16 |
| 080062B0, 080069DE, 08006D88 | `{name}` reads at most 8 bytes | 16 |
| 0801D598 | DeviDas name: one glyph per sprite, 8 sprites | `dd_name`: one bitmap over the 8 sprites (128 px) |
| 12 name-table reads (`NAME_SITES`) + 0800C344 | `id * 8 + 0830E48C` | `id * 16 + NAMES` (0x3F4C00): 15 glyphs + FF |

State the hooks keep in the game's own fields: story `[0x03000B70+0x32]` = 0 / 14 (line start, as the game's clear
and newline write) else `0x8000 | line << 8 | px`; message boxes `+0x23` (was the column) = pen x in px; menus
`ctx+0x23` = pen x in px. No new RAM.

## Not hooked (yet)
- Multiboot client (link play: `client_pause`, `client_link`, trade / transfer records): separate program with its
  own fixed 8 px printer; only reachable with a link partner.
- Graphics text (title menu, banners, labels): phase 7/8 graphics work (docs/re/graphics.md).

## Line limits (the width gate)
See "Measured budgets" below; the wrap check (phase 7) and translators use these px values, measured from zoomed
shots of the marker build (`tools/marker.py`), never from the Japanese length.

## Measured budgets
Machine-readable copy: `blocks.BUDGET` (test: every script block has one). Measured 2026-11-01 from the marker build
(`work/qa/mk`, 78/78 scenes), a menu stress build (`marker.py --out build/pdc_stress.gba --set ID=TEXT`,
`work/qa/stress`) and the torture build (`work/qa/torture`). x = screen px.

| Variant | Font | Budget | Notes |
|---|---|---|---|
| Story box (story) | big | 224 px/line, 2 lines/page; last line of a page 210 px | text x 12-235; page arrow at x 225-230, y of line 2 |
| Message box (boss, rescue, system) | big | 224 px, 2 lines; last line 210 px | text x 13-236; same arrow; `{name}` counts at its big-font width |
| Tutorial box (tutorial) | big | 224 px, 2 lines; last line 210 px | as message box (arrow assumed: same printer family) |
| Pause menu (pause) | small | 48 px | x 184 to the highlight bar's end 232; frame at 236 |
| Yes/No (yesno) | small | 24 px | x 208-232 |
| Title / game-over menu (titlemenu) | small | 40 px | x 100-140 (game-over shot) |
| Demon names (names) | small | 67 px, 15 glyphs | pause lists デビライザー x 88-155, デビルいちらん x 168-236; DeviDas name box x 108-228 (120 px) is roomier; in a message box the name takes its big-font width |
| Race menu (race_menu) | cell | 12 glyphs per row | not hooked (080205FE): 30 tiles in fixed 8 px cells from x 68, row 1 = bytes 0-15, row 2 = 16-29; a 13th glyph hits the selected row's highlight end, cells 14-16 draw over and past the frame (`work/qa/stress3`). English glyphs sit left in their cell (`R0. 0`): a proportional pen is phase-7 polish |
| DeviDas trade menu (devidas_menu) | cell | 5 / 4 bytes (slot) | guess: link-only screen, not reachable |
| Trade / transfer lines, multiboot client strings | cell | 14 bytes / slot | guess: client program, own fixed 8 px printer and untouched font, link-only |

Overflow: menu text is OBJ sprites, so too-long text draws past the frame instead of clipping. The pause screen
shares one OBJ pool: 3 x 15-glyph names + 16-glyph items ran it dry (the 4th list stopped after 7 glyphs); a
12-glyph name shows in full in both lists (`work/qa/stress2`). Re-check this screen with the longest real names.

## Marker tour verdict (2026-11-01)
`build/pdc_marker.gba`, 842 marker units: 78/78 scenes boot (`work/qa/mk`). Independent visual-QA pass (visual-qa
agent, `work/qa/verdicts/p5_marker.tsv`): no Japanese text left (only graphics), nothing cut by a frame, torture
lines clean. Its 2 issues, resolved: race menu garbled (wrong record split, fixed: 16 + 14 bytes, `work/qa/mk3`
shows `R0.0` / `R0.1`); ending_r0 おわり missing (timing: the marker credits type slower; `[s14.32a]` shows at
frame ~8900, `work/qa/mk3/end3`).

## Torture line
`marker.py --set story.000.00=TORTURE --set boss.001.00=TORTURE2` -> `build/pdc_torture.gba`. All printable ASCII
plus `… ♥ % ♪ # < > [ ] _ / ~ + = & *` and a double space render in the story box (`work/qa/torture/s0`) and the
message box (`work/qa/torture/_finals/boss_r0_a1.png`): every glyph present and distinct, spacing even, double
space kept. ♥ keeps the Japanese font's pink. The small font's own `q` reads like `9` (game glyph; redraw if a menu
word needs it).
