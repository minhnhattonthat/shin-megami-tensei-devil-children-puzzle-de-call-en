# Text engine

Dump: `rom.sha1`. Addresses are file offsets unless written 08xxxxxx.

## ROM basics
- Header `DEBITIRUPUZL`, code `A8ZJ`, 4 MiB. Save: `EEPROM_V122` at 0x30C284.
- Data ends at 0x3529CF (end of the multiboot client image, literal 0x083529CC at 0x20BDC); 0x3529D0-0x3FFFFF
  (0xAD630 bytes) is all 0xFF. **Free space, verified**: no aligned u32 in the code area (< 0x30000) points into it (the
  ~100 hits elsewhere are inside graphics data, unaligned noise), and `tools/traptest.py` (watch.lua read hook on the
  range, routes Story / Puzzle / DeviDas to frame 12000) logged 0 reads; positive control on 0x30E414 caught the pause
  menu reader. Expanding to 8 MiB is also possible (EEPROM: check save still works).
- ROM layout (file offsets): code 0x0-~0x2FFFF; 8bpp sprite frames 0x30000-0x160697 (1355 pointers from tables in
  0x30C3xx-0x30C974, stride 0x1E60 = 0x20-byte palette + 121 8bpp tiles; sweep found no text); LZ77 blocks
  0x160698-0x2B159A (556 blocks, `work/lzscan.txt` from `tools/lz77.py scan`); data/text 0x2B1600-0x32B3A3; multiboot
  loader 0x32B3A4-0x32CED3 (`AGBJ` header); multiboot client 0x32CED4-0x3529CB (header `DEBITIRUPUZL A82J`, runs at
  0x02000000, so its pointers are 0x020xxxxx = offset - 0x32CED4; sent at 0x20BD0 for link play).

## Encoding (verified)
- One byte per character, 0x00-0xF7 = glyph index into a 16x16 4bpp font (128 bytes/glyph, tiles TL TR BL BR).
  Order: `tools/mk_jp_tbl.py` -> `tbl/jp.tbl`. 0x00 space, 01-0A digits, 0B-53 punctuation + 66 fixed kanji, 54-A4 hiragana
  (small ぃぅぇぉ slots hold the button letters A B L R; no ゐゑ), A5-F6 katakana incl. ヴ, F7 穴.
  Verified: decoded the on-screen lines 「ゲイル、この村でまちがいないのか？」 and 「ジンとアキラ、ランドとゲイルの一行は」, and
  the font sheet read from RAM matches every reading.
  **Fixed 2026-11-01** (font sheet + tutorial context 「石やドアがある」「出口」): 0x1E is 石 (was read as 右) and 0xF2 is 口
  (was ヮ; the font has no ヮ). No `jp` text had been extracted yet, so nothing to re-queue.
- Font: LZ77 (BIOS type 0x10) at **0x160698**, 31744 bytes = 248 glyphs, decompressed to EWRAM 0x02008000 (verified:
  decompressed block == RAM at frame 2990). `tools/lz77.py` (roundtrip selftest), `tools/fontsheet.py` renders it.
- 0xFF is the command prefix in story scripts: `FF xx args`. Lengths from the interpreter at 0801B338 (if-chain), verified
  by parsing all 29 scripts exactly to the next pointer, each ending `FF 00`: see `CMDS` in `tools/mk_jp_tbl.py`.
  `FF 09 FF` is the 3-byte form of FF 09 (face/speaker; 2 args otherwise). FF 01 = newline (sets slot 14), FF 03 xx = wait
  (00 = wait for button), FF 04 = clear box, FF 19 xx = box/page setup, FF 00 = end.

## Story scripts (verified)
- Pointer table **0x32A670**: 29 u32 pointers (0x08324AF0 ... 0x083298B9), indexed by byte [0x03000BF3]; text cursor
  offset u16 at [0x03000BA0]. Only xref: 0801B39C (the interpreter). Script data 0x324AF0-0x32A66F (~23 KB), packed
  back to back. Roundtrip test: `tests/test_story.py`.
- Scripts 0-14 and 15-28 look like two parallel routes (same command skeletons).

## Rendering (verified, frame 2999 of the boot route)
- Each character is one 16x16 OBJ sprite (4bpp, 1D mapping), glyph DMA'd from the RAM font: src = [0x03000B7C] + code*128,
  dst = [0x03000B78] + slot*128 (OBJ VRAM 0x06011840). 14 slots per line, 2 lines (slot 0-13, 14-27), sprites at x = 16 + 14*i,
  y = 126 / 142. So 14 full-width characters per line, 2 lines per page.
- English plan: VWF that renders a line into the 14 sprites as a bitmap at 16 px pitch (224 px/line, ~40 chars), hooked
  at the DMA in 0801B3B0. Engine spike = phase 5.

## Other text (mapped statically; pointer tables verified by code xrefs, contents decoded)
Same 1-byte encoding. String codes: `FF` end, `FE` newline, `FC` page break (wait for button), `FD xx` colour/voice
(`FD 02/03/04` seen, `FD 00` back to normal), `F9 xx` (guess: speaker/face; seen at string starts in 0x30CA34, 0x30DD70).
Found with `tools/textscan.py` (kana-run scan) and `tools/ptrtables.py` (u32 arrays whose targets decode as text);
short strings (< 3 kana) need these xrefs or a runtime hook, see "Readers" below.

| Range | Pointer table (xref) | Content |
|---|---|---|
| 0x30CA34-0x30DD6F | 0x30DBDC, ~101 u32, some 0 (code 0xAFA8, 0xAFD8) | demon rescue dialogue, 1-2 strings per demon, `FC` pages |
| 0x30DD70-0x30E223 | 0x30E224, 13 u32 (0x12100) | boss / encounter dialogue |
| 0x30E258-0x30E3D9 | 0x30E3DC, 14 u32 (many, 0xC8F8...) | save / record / return-to-title messages |
| 0x30E414-0x30E43D | 0x30E440, 8 u32 (0xBB2C, 0xCFAC, 0x16E60) | pause menu キャンセル もどす マップ デビライザー やりなおし はじめから やめる セーブ |
| 0x30E460-0x30E467 | 0x30E468, 2 u32 | いいえ / はい |
| 0x30E470-0x30E47F | 0x30E480, 3 u32 (0xDB68) | はじめから / ロード / やめる (leading space) |
| 0x30E48C-0x30E9C3 | fixed 8-byte FF-padded records, 167 (base 0x30E48C, 12 xrefs; 0x30E99C entry 162 = 8x0x1C placeholder) | demon names 0-161, then ジン アキラ ランド ゲイル; 8-char names have no FF |
| 0x30FD48-0x3111F7 | 0x3111F8, 3 u32 (0xF550) | あそびかた tutorial parts 1-3; own command set, `tools/tutorial.py` (parses exactly to the next pointer) |
| 0x32A7C0-0x32A92B | 0x32A92C, 13 u32 (0x1D924) | link trade messages, FF-padded fields |
| 0x28B0A4-0x28B0BF | 0x28B0A4 (0x1C214), 0x28B0B8 (0x1C218) | DeviDas trade menu キャンセル こうかん あげる もらう; いいえ はい (fixed fields, 00/FF padded) |
| 0x2AB7A4-0x2AB82F | 0x32B390, 5 u32 (0x20CC8) | link transfer messages (データをてんそうしています…) |
| 0x34FA48-0x34FB5F | client EWRAM ptrs 0x02022B74... | multiboot client: pause menu, link error / timeout messages |

Tutorial script (0x3111F8 table): `F8 xx` demo actions with args F8 00/01/0B = 1 byte, F8 02/05 = 2, others 0
(F8 03 04 06 07 08 09 0C); `FA xx` wait (frames, guess); `FC` page; `FD xx` colour; `FE` newline; `FF` end. Lengths are
parse-consistency only (all 3 scripts end exactly at the next pointer): confirm in the interpreter before insertion.

### Readers (verified by watch.lua)
- Pause menu strings 0x30E414.. are read by 0800B53A / 0800B588 (small 8 px OBJ font, LZ 0x161FD0, loaded to OBJ VRAM
  0x06015020: same code order as the big font). Hook these to log every small-font string drawn (leftover scan).
- Story text: 0801B3B0 (big font DMA, above).

### Still open
- No runtime string log yet for the whole game: build it on 0800B53A + 0801B3B0 once the debug tool (phase 2) reaches
  every screen; strings < 3 kana outside the tables above may exist (e.g. HUD values drawn as text).
