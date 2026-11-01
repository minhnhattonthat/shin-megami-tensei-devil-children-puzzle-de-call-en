# Shin Megami Tensei: Devil Children - Puzzle de Call! English translation

Unofficial English fan translation of the Game Boy Advance puzzle game published by Atlus in 2002.
This repository contains the translation and tools for building a patch. It contains no playable game ROM.

The release archive is built locally; no release is published automatically. Apply its BPS patch to your own
clean Japanese dump, following the included README, then cold-boot the patched game. Do not load old savestates.

| Part | Status |
|---|---|
| Story, both routes and endings | English |
| Demon names, rescues, bosses, tutorials | English |
| Menus, system messages, visible stage cards and HUD | English |
| Title logo | Original Japanese (decision D5) |
| Link-only messages | English; two-GBA play and client layouts unverified |
| Name entry, voiced dialogue, staff roll | None identified |

Known limitations: link features require a second GBA; original save migration is unverified; fixed-cell race
labels have wide spacing. Six unobserved story-area plate assets and an unreferenced puzzle-label duplicate
retain Japanese. The Clear!! graphic is translated but its call-out has not been observed in-game.
See [status](docs/status.md), [QA/release report](docs/release-review.md), and [graphics notes](docs/re/graphics.md).

Build with Python 3.12+, `pytest`, `Pillow`, `capstone`, and `keystone-engine`:

```sh
python -m pip install pytest Pillow capstone keystone-engine
# Supply your dump in rom/ using the filename below.
python -X utf8 build.py
python -X utf8 tools/check.py
```

Required dump: `rom/Shin Megami Tensei Devil Children - Puzzle de Call! (Japan).gba`, 4,194,304 bytes,
SHA-1 `e70fc457b56c8e27ab63e491706b88232f598452`. A different dump is rejected. Output: `build/pdc_en.gba`.

Emulator QA additionally needs the translate-retro-game skill (`python tools/skill.py`), MesenCE 2.2.1 in
`tools/mesen/`, and a GBA BIOS. `python -X utf8 tools/release.py --help` describes local packaging. The release
command builds, tests, smoke-boots, tours all registered scenes, checks every active visual/story manifest and
the polish checklist, reapplies the BPS and compares the output, then creates a ZIP containing only BPS + README.
It stops for missing review verdicts and never publishes. The build uses host-side Lua for QA warps; no debug
warp code is linked into the patched ROM.

Translation fixes belong in `script/` (`src` is authored English, `en` is rendered text). Names and style rules
are in [glossary.md](glossary.md). Reverse-engineering notes are indexed in [docs/re/README.md](docs/re/README.md).
Report bugs through the repository's Issues, including scene, emulator, version and a savestate if available.

Tools and original English translation work are MIT licensed. Original game, art, glyphs and Japanese text
belong to their respective owners. [Font details](docs/fonts.md). This project is not affiliated with Atlus.
Do not distribute pre-patched ROMs. Extensive AI assistance: Anthropic Claude and OpenAI Codex.

[Support the project on Ko-fi](https://ko-fi.com/minhnhattonthat).
