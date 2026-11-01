# Fonts

| File | Source | Licence | Use |
|---|---|---|---|
| `fonts/vwf.txt` | Drawn for this project (file header) | MIT, repository LICENSE | Dialogue, names, graphics labels and area cards; shadow added by `tools/vwf.py` |
| `fonts/small.txt` | Drawn for this project (file header) | MIT, repository LICENSE | Supplemental 8x8 English glyphs, inserted into the game's small font |
| `fonts/tiny.txt` | Drawn for this project (file header) | MIT, repository LICENSE | Five-row capitals for HUD, class/race and element labels |

The small-font builder retains the original game's Latin glyphs and adds the supplemental glyphs above.
Those original glyphs are Atlus game assets, not newly licensed MIT artwork. The BPS is applied to the player's
own dump; the repository does not ship the original font block. No external TTF/OTF font is used.

The English VWF font has eleven body rows plus a shadow at (+1, +1), with one pixel of advance spacing.
Small menu glyph ink begins at tile column 1 so the original highlight bars cover the first letter.
