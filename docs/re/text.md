# Text engine

Dump: `rom.sha1`. Addresses are file offsets unless written 08xxxxxx.

## ROM basics
- Header `DEBITIRUPUZL`, code `A8ZJ`, 4 MiB. Save: `EEPROM_V122` at 0x30C284.
- Data ends at 0x3529CF; 0x3529D0-0x3FFFFF (0xAD630 bytes) is all 0xFF: **candidate** free space (not yet trap-tested). Expanding to 8 MiB is also possible (EEPROM: check save still works).

## Encoding (verified)
- One byte per character, 0x00-0xF7 = glyph index into a 16x16 4bpp font (128 bytes/glyph, tiles TL TR BL BR).
  Order: `tools/mk_jp_tbl.py` -> `tbl/jp.tbl`. 0x00 space, 01-0A digits, 0B-53 punctuation + 66 fixed kanji, 54-A4 hiragana
  (small ぃぅぇぉ slots hold the button letters A B L R; no ゐゑ), A5-F6 katakana incl. ヮ ヴ, F7 穴.
  Verified: decoded the on-screen lines 「ゲイル、この村でまちがいないのか？」 and 「ジンとアキラ、ランドとゲイルの一行は」, and
  the font sheet read from RAM matches every reading.
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

## Other text (partly mapped, guess-level)
Same encoding, but not script format: fixed-width fields, `FF`-padded or `FF`-separated, `FE` = newline.
- 0x32A8xx-0x32AFxx: link-cable trade messages (このデビルをわたします…), FF-padded.
- 0x34FA3x: puzzle pause menu キャンセル/もどす/やりなおし/はじめから, FF-separated; then link error messages 0x34FAxx.
- 0x30E42F, 0x30E470: はじめから (title/menu?).
- Still to find: pause menu items マップ/デビライザー/やめる/セーブ, デビルいちらん list, demon names, あそびかた tutorial, title
  menu, save/load. Method: hook the per-character DMA (0801B3B0) and any other routine reading 0x02008000, log the string
  pointer, then decode offline.
