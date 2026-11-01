# Local release verification — 2026-11-01

Phase 9 local release verification is complete. No release has been published and repository visibility is unchanged.
The final ROM SHA-1 is `bd858d3c1f07e0e1516de1f9185cd87e5a22fcc5`.

## Fixes and coverage

- External phase 7 Important finding fixed in `f41ab0e`: lint checks actual English without requiring `src`,
  and final builds require every nonempty original unit. Empty authoring fields cannot silently restore Japanese.
- Both external Minors fixed: short final-line rejection and explicit, reasoned outer-spacing exceptions.
- 56 line-specific polish changes; remaining optional wording suggestions have individual dispositions in
  `docs/polish.md`. All seven chapters passed a fresh read-only Codex review of 671 marked entries plus context
  (`docs/story-review.md`), with no Critical or Important findings.
- Corrected the rescue tour's demon-ID/message-ID confusion. It now selects all 100 distinct rescue messages
  and verifies the actual message pointer at runtime; the previous sweep missed 19 messages.
- Corrected tutorial capture: A-mashing skipped the automatic demonstrations, so earlier tutorial-labelled
  shots mostly showed the prologue. The final no-input tour explicitly selects and completes all three parts;
  all 56 sheets pass, and a regression test rejects the old skip-to-prologue log.
- Fresh visual QA found the boss HUD reading an unrelocated interior pointer into the old demon-name table.
  Relocated its pointer and stride; the runtime probe fails on the old English ROM and passes on the corrected
  one. All aligned original-ROM literals into that table are covered by a regression test (`docs/re/vwf.md`).
- The dormant boss.000 placeholder was rendered through the normal printer with an explicit host-side probe;
  Mecci's symbols and Quetza/Teskarot's rescue mapping were checked in the emulator.
- The final-ROM pause menu passes the longest-real-name sprite-capacity check: every visible name slot is
  Jack Frost, with all names and menu items complete (`work/qa/name_stress/final.png`).

## Release procedure

`tools/release.py` builds, tests, cold-boots, runs the 78-scene tour, refreshes story review inputs, checks every
active QA manifest and the fully ticked polish checklist, makes a BPS, reapplies it to the pinned clean original,
then reopens the ZIP and reapplies its patch again. It refuses existing version files unless `--force` is explicit.
The playable image remains in `build/`; the ZIP contains only BPS and README. Debug scripts are host-side Lua,
never linked into the release ROM. Full text-tour and scene-tour receipts must match the candidate ROM hash.

English reuses the Japanese character codes, so a generic kana-byte scan would flag English as Japanese.
Instead, the build reads every reachable translated unit back through its pointer and compares the encoded
English, checks coverage, scans for stale pointers, and combines that with runtime/visual review.

The old `work/qa/text_v1/manifest.tsv` was a superseded snapshot pointing at subsequently regenerated files;
it was archived as `manifest.superseded.tsv`. The active text/text3 manifests retain the earlier accepted QA,
and the full phase 9 tour is separately required. Changed images invalidate prior verdicts. Exact byte-identical
images alone may inherit acceptance through `tools/qa_reuse.py`; frozen review snapshots retain their own hashes.

After the final-ROM recapture passed, `visual_remaining/manifest.tsv` was archived as
`manifest.superseded.tsv`: it held earlier-timing story images and the skipped tutorial route. Final story,
boss/ending and rescue reviews supersede it. `polish/retired-final-rows.tsv` retains 49 retired rows: 48
skipped-tutorial sheets replaced by the 56 complete-demo sheets, plus one obsolete trailing story sheet after
recapture produced fewer sheets. The before-reconciliation manifest is retained alongside it.

Eight focused images in `work/qa/final_evidence` resolve punctuation capture gaps and the short story.013 run
ending while its successor begins. These are complete-page screenshots from the same ROM, not text fixes.
Five rescue breaks flagged by visual reviewers (018/019/050/061/065) were compared with their Japanese
`{page}` boundaries and match exactly; all pages render fully. One optional story.009.03 three-beat pacing choice
is explicitly retained in `docs/polish.md`.

## Known limits

The README discloses untested two-GBA link play, original-save migration, real hardware and other emulators;
wide fixed-cell race-menu spacing; the retained Japanese title logo; six unobserved area plates and an
unreferenced duplicate graphic; and the translated but unobserved Clear!! call-out. No claims of link-runtime
or physical-hardware certification are made.

## Final results

`python -X utf8 tools/release.py --version 1.0 --skip-tour` completed successfully; its log is
`work/release-verified.log`. The existing scene, full-text and tutorial receipts match the final ROM hash.

- 43 tests passed, including incomplete-translation, boss-name pointer, skipped-tutorial and package regressions.
- Cold boot passed in MesenCE 2.2.1; the final 78-scene warp tour and 144-run full dialogue capture completed.
- All three no-input tutorials reached their actual end markers; all 56 tutorial sheets passed visual review.
- Every active QA manifest passed with zero missing, failing or stale verdicts. Primary final coverage is
  `p9` (85 images), `polish` (554 sheets), `tutorial_final` (56 sheets), `final_evidence` (8 targeted proofs)
  and `story` (7 chapters); frozen story/boss reviews and earlier accepted manifests also passed.
- The standalone BPS was applied to the verified clean original and byte-compared with the final ROM.
  The ZIP was reopened and its BPS independently reapplied and compared again.
- The ZIP contains exactly `Devil_Children_Puzzle_de_Call_EN_v1.0.bps` and `README.txt`; no ROM or save data.

| Local artifact | SHA-1 |
| --- | --- |
| `build/pdc_en.gba` | `bd858d3c1f07e0e1516de1f9185cd87e5a22fcc5` |
| `release/Devil_Children_Puzzle_de_Call_EN_v1.0.bps` | `6972f9fe5e2c06f8dda5a06337dd8ac035f32b5e` |
| `release/Devil_Children_Puzzle_de_Call_EN_v1.0.zip` | `d7ec8a2bb63d93d98f4652b7b2ab48f21fe91264` |

The playable ROM and release artifacts remain local and gitignored. The clean base ROM SHA-1 is
`e70fc457b56c8e27ab63e491706b88232f598452`; patched CRC32 is `DA52065B`. The archive README contains these
identifiers, application instructions, credits and the limitations above. No remaining Critical or Important
finding blocks this local release.
