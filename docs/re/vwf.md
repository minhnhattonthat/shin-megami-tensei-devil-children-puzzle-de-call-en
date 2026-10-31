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
