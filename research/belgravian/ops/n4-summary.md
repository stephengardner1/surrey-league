# n4 summary: a08 + a09 findings (1979/80 to 1986/87)

Output file: `ops/n4.jsonl` (530 ops). Every rename, time and add was checked against the live data:
- Each rename's held name exists at that position for BEL.
- Each time op is for a held result with no time.
- Each add goes in a position that is free.
- No position is renamed twice.

## Counts by op
| op | men | women |
|---|---|---|
| rename | 372 | 1 |
| time | 5 | 0 |
| add | 1 | 77 |
| racemeta | 0 | 47 (26 dates, 15 finishers, 6 venues) |
| flag | 5 | 3 |
| note | 19 (no file) | |
| div2 / newrace | 0 | 0 |

## Decisions
- **Division II is out of scope (Steve's decision).** The 1979/80 and 1981/82 Belgrave men's Div II races (about 200 results) were not emitted. Two notes record why. Div II lists were used only to support full names (e.g. Mick Gleave).
- **Men's renames:** 62 initial→full-name mappings, applied to BEL results in Div I seasons, plus 8 single-position misreads:
  - R Mead → M Head
  - R Donoghue → M Donoghue
  - N Wilsher → M Wilsher
  - M Razire → M Bazire
  - K Graham → R Graham
  - B Hollingworth → D Hollingworth
  - J Herren → J Warren
  - S Zreveley → S Zeely
- **Other misread fixes:**
  - D Swann → Derek Slann
  - M Mouch → Mike Nouch
  - R Addington → George Piddington
  - G Mackie → Graham Macky
  - H J Gleave / M Hoad → Mick Gleave / Martyn Head
  - A Morfy → Alistair Morfey
- **Medium-confidence renames** come from new-member lists. They are applied only where the initial, surname, club and era all match and the name is unusual (e.g. Budarkiewicz, Fantham, Forrester, Osborne, the Chastons, Galvan, Ricks, Ludlow, Tiernan, Anthony).
- **Name forms:** the magazine's first-name forms are kept, e.g. Peter Gilbey (not the alias table's "Pete"), Stuart Paton and Graham Adams. The alias table conflicts are listed in a note.
- **Women's adds:** these are Belgrave senior (Inters/Seniors) results in races where the women's file holds only the winner. I checked every add position against the file's pos values and none were already held. From 1985/86 the Inters ran their own race, so those results are in a note only. Girls' and junior races were skipped.
- **Women's dates** are written in ISO form (e.g. `1984-11-03`), because that is the only full-date style the women's file uses. The held values were only month names.

## Skipped or not renamed, and why
- **M Lake:** Martin Lake and Mike Lake both raced, so it's ambiguous (as instructed).
- **F Ward:** the magazine prints both Francis and Frank. The alias table already has Frank Ward.
- **J Chaston:** sources conflict between Justin and Julien. The alias table already has Justin.
- **Jean Paul Wright:** sent as a flag, not a rename. The magazine prints "John Wright", but the site's canonical form is "John-Paul Wright", so Steve should choose.
- **Second S Williamson** at 1980/81 M1, 137th: identity unclear.
- **Not renamed (low confidence):** M Claxton/Chaston, M Waller/Walker, R Geehan/Patrick, G Beatty/Bratty, T Rodd/John Rodd, N Maugham, S Warren.
- **Not changed (positions):** the apparent position "offsets" in 1985/86 M1–M3 and 1986/87 M4 are not errors. The magazine prints the scoring position, which matches the held `s` field. The 1983/84 M1 double-printed positions are also left alone; the Apr 1984 issue agrees with the held data.
- **Not added:**
  - J Rayner at 1983/84 M2, 141st: that position is held but coded SLH, so it's flagged instead.
  - S Osborne at 1986/87 M2, 156th: held as "S Osbourn" (SLH), so it's flagged.
- **Team scores and standings:** none changed. The magazine's final tables are recorded in notes.
- **1982/83 M2 team totals** on a different scale: flagged.
- **Minor venue and score differences:** noted only (Petersham vs Richmond Park; 437 vs 435).
- **Not used:** photo findings and prose-only results without an overall position.
