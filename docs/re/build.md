# Build and identity

`build.py` unpacks every block listed in `tools/blocks.py` from the original ROM and packs it back into a copy;
`tests/test_identity.py` asserts the result equals the original (phase 3, verified 2026-11-01: 60 writes, romdiff clean,
smoke boots). Later phases swap edited entries in between unpack and pack.

## Block kinds
- **PACKED** (story, rescue, boss, system, pause, yesno, titlemenu, tutorial, client_pause, client_link): strings back to
  back from the first pointer, 00 padding to 4, then the u32 pointer table (referenced by code, never moves). Verified
  for all 10: pointers unique + ascending, each string ends exactly at the next pointer (codec per block: story = jp.tbl
  `{end}`, tutorial = `tools/tutorial.py`, msg = FF end with FD/F9 one-arg), padding all 00. Pack: same slot if it fits
  (rest 00-filled), else the whole block moves to free space 0x3529D0+ and the table is repointed. Client blocks (pointer
  base 0x02000000 - 0x32CED4) can't leave the multiboot image: overflow is an error.
- **RECORDS** (fixed size, in place): demon names 167 x 8; link trade 13 x 0x1C (two 14-byte lines, FF padded, stale
  bytes after FF); link transfer 5 x 0x1C; DeviDas trade menu 0x28B0A4 0x1C bytes. Phase 4 defines their fields.
- **LZ** (36 blocks: fonts + every graphics-text block in graphics.md): recompressed in place, slot = original length
  rounded up to 4; a bigger result is an error until that block gets relocation (repoint its xrefs).

## LZ77 compressor (verified)
`tools/lz77.py compress(data, min_disp)` = greedy longest match, nearest on ties, 4096 window, pad 00 to 4. It
reproduces **all 556 blocks** in `work/lzscan.txt` byte for byte: 276 need min_disp 1 (graphics), the rest min_disp 2
(fonts and blocks with no distance-1 match). `lz77.mode()` picks the setting per block; edits reuse it, so a block the
game unpacks with the VRAM routine stays VRAM-safe.
