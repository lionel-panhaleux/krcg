# TODO — upstream watch list

What is left of the `krcg/scripts/fix_csv.py` audit against
`GiottoVerducci/vtescsv@main` (2026-08-22). The Anthology/set-tag findings are
fixed and their rationale now lives in the code; only the items that wait on
upstream are tracked here.

## Anthology `LARP`: the alias keys on the bare code

`SET_ADDITIONS[("Anthology", "")] = ("Ant1", "")` is what emits the `Ant1`
print, and it fires on the bare code only — that is exactly what keeps the 11
LARP-exclusive cards out of Anthology I.

The vtescsv PR series proposes marking **all 65** Anthology cards with `LARP`,
since the other 54 are in the EC Berlin edition too. **If that lands, `Ant1`
silently stops being generated for every card.** Not worth engineering around
today, but re-check the census after any upstream Anthology change:

| tag | cards | copies |
|---|---|---|
| bare `Anthology:<n>` | 54 | 89 = Anthology I size |
| `Anthology:LARP<n>` | 11 | 11 |
| **total** | **65** | **100** = EC Berlin Edition size |

## `fix_set_row`'s `Company` strip waits on the whitespace PR

Upstream `vtessets.csv` has 8 rows with whitespace *outside* the quotes, which
the CSV parser folds into the `Company` value:

- lines 26–28 (`DM`, `TU`, `AU`) end with `..."White Wolf Entertainment AB" `;
- lines 115–119 (five `Promo-*` rows) have `..., "Paradox Interactive AB"`.

`row["Company"].strip()` absorbs both. Keep it until the upstream whitespace PR
lands, then re-check.

Side effect worth knowing: because of these 8 rows, a plain
`csv.DictReader`/`DictWriter` round-trip of `vtessets.csv` is **not**
byte-identical — it silently normalises them. `vteslib.csv` and `vtescrypt.csv`
do round-trip byte-identically (verified, `QUOTE_ALL`, LF endings, no BOM).
Note krcg writes these files back with `utf-8-sig`, adding a BOM upstream does
not have.

## Pending upstream drift, not taken in this pass

Upstream now dates `NB2` (New Blood II) `20230801`; the packaged
`vtessets.csv` still says `20220801`. Left alone so the Anthology commit stays
reviewable — the next `just sync-cards` picks it up.

## `CARD_REFERENCES` path audit — done, nothing else to drop

`Path of Death and the Soul` was the only path-vs-card confusion: after removing
`102311` and `201771`, no card text carries a `<Path of …>` marker at all, so
`Path of Caine`, `Path of Power and the Inner Voice` and `Path of Cathari` are
clean. Re-run that grep if new `SV5` bundles are added.
