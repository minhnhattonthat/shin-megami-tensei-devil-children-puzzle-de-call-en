# Graphics text survey (phase 1)

Sources: tour (`work/qa/tour_{story,puzzle,race,devidas}`, title `work/qa/t1`) + static sweep of every LZ77 block
(`tools/gfxsweep.py lz` at 4bpp, and `--bpp 8 --min 1000`; sheets in `work/sweep/lz*`, blocks dumped to
`work/lzblocks/`) and of the raw 8bpp sprite region 0x30000-0x160697 (`gfxsweep.py raw --bpp 8`: no text). Sheets were
read by read-only reviewer agents; every flagged block was then re-rendered and checked by eye (`work/sweep/c1-c4.png`).
Readings marked ~ are approximate: read them exactly from a tilemap render before redrawing.

Status column: **verified** = seen on screen and the source matched by `vramfind.py` from a VRAM dump; **sweep** =
found in the static sweep, on-screen location not yet seen.

## Fonts (text, not graphics work; listed so nothing is lost)
| Block | What | Status |
|---|---|---|
| LZ 0x160698 | main 16x16 font, 248 glyphs (story, dialogue, demon names) | verified (docs/re/text.md) |
| LZ 0x161FD0 | small 8x8 font: digits, Latin A-Z a-z, punctuation, hiragana, katakana; in OBJ VRAM 0x06015020 | verified (title VRAM, 246 tiles) |
| LZ 0x337B10 | multiboot client copy of the small font | sweep |
| LZ 0x33A2DC | client: bold kana font + スコア タイム, digits | sweep |

## Tile-drawn Japanese
| Screen | Element | Block (fmt) | Status |
|---|---|---|---|
| Title | logo 真・女神転生 / デビルチルドレン / パズルdeコール！ (no official English logo: translate per D5) | LZ 0x232A68 (8bpp BG tileset, logo in the last third) | verified (title VRAM) |
| Title | menu ストーリー パズル レース デビダス (+ highlighted copies) | LZ 0x23AEDC | verified (title VRAM) |
| Title / Story | submenu はじめから つづきから あそびかた (normal / highlighted) | LZ 0x23B1D8, 0x23B4AC | verified (title VRAM) |
| Title | emblem icons with a kanji-like mark (~白) | LZ 0x23B9A4 | verified (title VRAM); check if it is a character |
| Title | "PUSH START BUTTON", "© ATLUS 2003" (English already) | LZ 0x23AAFC, 0x23A9B0 | keep |
| Puzzle HUD / pause | デビルいちらん, デビライザー panel bars; ライフ, たおしたデビル, タマゴ, てかず labels; outlined katakana banner row (~キャラクターセレクト) | LZ 0x1C72B8 | sweep (seen on screen in pause menu) |
| Puzzle HUD | てかず / タマゴ / タイム (story HUD), てかず / さいこう / タイム (puzzle mode) | LZ 0x1C72B8 / 0x2AADE0 | sweep (seen on screen) |
| Puzzle HUD | スコア タイム てかず | LZ 0x2AADE0 | sweep |
| Puzzle mode select | パズルモード banner; かんたん ふつう むずかしい headers | LZ 0x2A8970 (51 runs, read as 4bpp) + 0x2AB324 on screen | block matched (warp `puzzle_select`); pin the exact tiles |
| Race mode | レースモード banner | LZ 0x2AB930 (45 runs) on screen | block matched (warp `race`) |
| DeviDas | デビダス banner | LZ 0x28C998 / 0x2A1658 / 0x28BD70 on screen | block matched (warp `devidas`); which one holds the banner: pin |
| Character select | キャラクターセレクト plate, ランド / ゲイル name plates | LZ 0x22E6D0 (41 runs; 380 tiles unmatched: likely more blocks) | block matched (warp `charselect`) |
| Area start card | area name + スタート! (e.g. エンジェルの森 スタート!) over each floor | guess: built at run time (70-90 OBJ tiles per `stage_*` warp found in no block); LZ 0x1C810C (outlined katakana) is on screen in all 12 but has no 森, so the names may come from another source | dump OAM of the card (`stage_*` at --frames 460) and trace its tile writer |
| Game over | GAME OVER (English already) + menu | LZ 0x201EB8 (warp `gameover`) | keep logo; check the menu text |
| Ending | picture + おわり | pictures LZ 0x276398 (route 0), 0x27D254 (route 1); おわり likely main font 0x160698 sprites | warps `ending_r0/r1`; confirm おわり source |
| DeviDas | クラス 種族 属性 labels | LZ 0x28C448 | sweep (seen on screen) |
| DeviDas | element kanji (光 火 氷 ...) | LZ 0x28C330 | sweep (seen on screen: 光) |
| DeviDas | class / race values (コモン マジュウ ...) | LZ 0x28BFB4 (map? tag, really tiles) | sweep (seen on screen) |
| DeviDas | "No. SAVE HP EASY NORM HARD", "STORY PUZZLE" (English already) | LZ 0x28BE74 | keep |
| Story text scenes? | six area / chapter name banners (~エンジェ…ヘヴン, ~ルフ…, ~メ…ドヘ, ~タルタ…, ~ノ…ルフ, ~ク…ドリガ) | LZ 0x28A59C 0x28A758 0x28A93C 0x28AACC 0x28ACE8 0x28AED8 | in VRAM in both ending warps (story-text state); seen top right in script 2 (tour f13500): the area label in story scenes |
| ? | bold 16 px kana strips (mode names / headers) | LZ 0x28C50C, 0x2B13E4, 0x33BB88 (client) | sweep |
| ? | big outlined katakana font-like sheet + same outlined row as 0x1C72B8 | LZ 0x1C810C | sweep |
| ? | stylised italic banner with gradient, 4 variants (~ゲームオーバー / クリア?) | LZ 0x22C408 0x22CD60 0x22D578 0x22DE80 | sweep |
| ? | outlined bubble lettering, 2 rows (JP or Latin unclear) | LZ 0x201EB8 | sweep |
| ? (link?) | 8bpp line of hiragana text (~がんばって … ここでデビ…) | LZ 0x2A8970 (8bpp) | sweep |

## Redrawn (phase 8, tools/gfx.py LABELS; checked in game, zoomed)
| Element | Block / tiles | English |
|---|---|---|
| Title menu (64x64 OBJ, pal 4; each item shows only its JP band, the cursor frame covers the gaps) | title_menu 0x23AEDC | STORY PUZZLE RACE DEMONARY (menu-font caps + outline) |
| Story submenu, no save / with save (composed at run time from 8 px strips of these) | title_sub 0x23B1D8, title_sub_hi 0x23B4AC | NEW GAME, (CONTINUE), TUTORIAL |
| Pause list headers (64x8 strips, OBJ pal 6) | hud 0x1C72B8 tiles 0x86-0x95 | Demon List, Demiloc |
| Stage HUD labels (32x8 OBJ) | hud tiles 0xBB 0xBF 0xC3 0xC7(64 px) 0xCF | MOVES TIME LIFE DEFEATED EGGS (fonts/tiny.txt) |
| Puzzle HUD labels | hud_puzzle 0x2AADE0 (3 x 32x8), hud_puzzle_obj 0x219630 tiles 0xA0-0xB3 (the set puzzle mode loads) | BEST TIME MOVES; MOVES TIME LIFE BEST SCORE |
| Area start cards (128x16) | outlined_kata 0x1C810C at 0x2800 + i * 0x400 | Embel Spring, Lucoppia Plain, Plekt Volcano, Tartarus Sea of Trees, Fjorgyn Snowfield, Quadriga (VWF font) |
The hud and hud_puzzle_obj blocks grow when recompressed: they move to free space (`blocks.pack_lz`, literal xrefs).

## Area start card (phase 8 finding)
エンベルの泉 etc.: 4 OBJ 32x16 sprites at y 40, tiles 0x240-0x25F. Source: block outlined_kata 0x1C810C at
0x2800 + area * 0x400 (128x16 as the four 32x16 sprites, 8 tiles each), DMA'd by 0800E632 from its EWRAM copy
(pointer table 0x081C93D0, index area_map 0x081FF868). Redrawn by `gfx.cards` (CARDS): the empty banner is the
per-pixel majority of the six originals away from the lettering, English in fonts/vwf.txt, white 15 with ring 6.
Names from the JP atwiki (devilchildren_pdc), glossary.md Places. Checked in game: `work/qa/cards/_finals`.
No スタート! sprite seen with the card.

## Not checked / weak spots (do in phase 2 / 8 with the debug tool)
- Phase 2 (2026-11-01): every screen below is now a warp scene (`tools/debug/scenes.txt`), VRAM dumps from
  `warp_all.py --ppu` in `work/qa/warp/<scene>/ppu_*`, vramfind summaries in `work/qa/vf/`. Matched by block (table
  above). Still to pin to exact tiles before redrawing: puzzle select, race, DeviDas banners, char select plates.
  No story map exists (the pause menu マップ is a floor overview); no stage-clear results screen seen (forced floor
  clear fades straight to the boss; a real clear may differ); no staff roll (`docs/re/debug.md`). Not reached: デビライザー screen (debug.md).
- Cleared by eye at 2x (`work/sweep/c5.png`): 0x1FBF7C family and 0x33B0F8 (window frames), 0x1FFC34 / 0x200238 family
  (panels + stripes), 0x3381CC (character art). Still unchecked closely: large blocks 0x1B67FC 0x1B9608 0x1BCBFC 0x1BEEE4
  0x1C1D28 0x1C40A0 (art; small scatter low in two of them); confirm when their screens are reached.
- Multiboot client (0x32CED4-0x3529CB) graphics can't be toured in one emulator: its blocks are listed above from the sweep.
