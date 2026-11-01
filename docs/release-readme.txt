Shin Megami Tensei: Devil Children - Puzzle de Call! (GBA)
Unofficial English translation v{{VERSION}}

Apply {{PATCH_NAME}} to your own clean Japanese dump using a BPS-compatible
patcher such as Floating IPS or Rom Patcher JS. Keep your original dump intact.
Start the patched game from a cold boot; old emulator savestates retain old code
and graphics and are not compatible. The ZIP contains only this README and the
patch, never a playable ROM. Do not distribute pre-patched ROMs.

Required original:
  Shin Megami Tensei Devil Children - Puzzle de Call! (Japan).gba
  Size: {{BASE_SIZE}} bytes
  CRC32: {{BASE_CRC32}}
  MD5: {{BASE_MD5}}
  SHA-1: {{BASE_SHA1}}
Patched ROM:
  CRC32: {{PATCHED_CRC32}}
  SHA-1: {{PATCHED_SHA1}}
BPS SHA-1: {{PATCH_SHA1}}

Translation status
  Story, both routes and endings: English.
  Demon names, rescue dialogue, bosses and tutorials: English.
  Menus, system messages, stage cards and visible HUD labels: English.
  Title logo: original Japanese (no official English logo).
  Link-only messages: translated; two-system link play is not runtime-tested.
  Name entry / voiced dialogue / staff roll: none identified in the game.

Tested with MesenCE 2.2.1 on Windows using the GBA BIOS. The build passes text
lint, roundtrip and ROM-write checks, cold-boot smoke, scene tours, visual QA and
chapter review. Other emulators and real hardware have not been verified.

Known limitations
  Link trade, multiboot client gameplay and two-GBA races need a link partner.
  Link-only layout budgets are conservative slot limits, not runtime proofs.
  The original fixed-cell race menu has wide English letter spacing.
  An unreferenced duplicate of the puzzle record labels retains Japanese.
  World-map labels shorten two names to fit: Tartarus, Fjorgyn.
  The Clear!! asset is translated but
  its floor-clear call-out has not been observed during the debug tours.
  Existing Japanese-game saves and save migration have not been certified.

Credits
  Original game: Atlus and the original development team.
  Translation, reverse engineering and tooling: this project's contributors,
  with extensive AI assistance from Anthropic Claude and OpenAI Codex.
  Original VWF/tiny glyphs and supplemental small glyphs: project contributors,
  MIT license; retained original menu glyphs remain part of the original game.
  Emulator: MesenCE. See the repository's docs/fonts.md for font details.

This is an unofficial fan project, not affiliated with or endorsed by Atlus.
Original game, art and Japanese text belong to their respective owners.
Project tools and original translation work are MIT licensed.

Source and bug reports:
https://github.com/minhnhattonthat/shin-megami-tensei-devil-children-puzzle-de-call-en
Please describe the scene, emulator and patch version; a savestate helps.
