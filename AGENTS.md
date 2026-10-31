# Shin Megami Tensei: Devil Children - Puzzle de Call! (GBA) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `~/.claude/plugins/marketplaces/retro-translation/skills/translate-retro-game/SKILL.md`; `$SKILL` = that directory, `python tools/skill.py` prints it). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py` -> build/pdc_en.gba (checks the dump against `rom.sha1` first)
- Check:    `python -X utf8 tools/check.py` (pytest on tests/; the pre-commit hook runs it; hooks: `git config core.hooksPath tools/hooks`)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/pdc_en.gba --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 $SKILL/scripts/emu.py build/pdc_en.gba --out work/qa/warp --script tools/debug/warp.lua --var "SCENE='<name>'" --frames 900 --sheet` (scenes: `tools/debug/scenes.txt`; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Shin Megami Tensei Devil Children - Puzzle de Call! (Japan).gba` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: MesenCE 2.2.1 in `tools/mesen/` (https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; gitignored; needs `Firmware/gba_bios.bin` from `fetch_emu.py gba-bios`; settings copy in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/`. Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- `fetch_emu.py mesen` fails here with Python SSL CERTIFICATE_VERIFY_FAILED; download the zip with curl instead.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
