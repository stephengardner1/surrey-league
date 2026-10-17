# n3 summary: findings a06 and a07 (1974/75 to 1978/79)

Ops file: `/home/claude/belgravian/ops/n3.jsonl` (426 lines). The builder script is `/home/claude/belgravian/work/n3/build.py`.

Every rename, time and add op was checked against the live `data.json`. Each rename's held name exists at that position for BEL, each time op targets a result that has no time, and each add position is free. No op failed the check and no op is duplicated.

## Counts
| Op | Count |
|---|---|
| rename | 221 |
| add | 169 |
| racemeta | 12 |
| note | 10 |
| time | 8 |
| div2 | 4 |
| flag | 2 |

### Renames by type
| Type | High confidence | Medium confidence |
|---|---|---|
| Initials to full name | 149 | 25 |
| Misread | 30 | 8 |
| Spelling | 6 | 3 |

### Adds by match
All adds are for Division 1 matches whose held data is missing.

| Match | Adds |
|---|---|
| 1974/75 M1 | 31 |
| 1974/75 M2 | 27 |
| 1974/75 M4 | 18 |
| 1975/76 M4 | 28 |
| 1976/77 M2 | 29 |
| 1976/77 M3 | 24 |
| 1978/79 M4 | 11 |
| 1978/79 M1 | 1 (C Pearson, 185th, who is missing from the held list) |

Opponents' 2nd and 3rd places were added where the magazine prints them:
- J Roberts (SLH)
- P Adams (AFD)
- L Presland (AFD)

Their names are kept in the archive's existing initial-plus-surname form for those clubs.

### Other ops
- **Times:** 8 ops add winners' times where none is held. This includes both of the =1 runners in 1974/75 M1 (27:54).
- **Racemeta:** 12 ops.
  - Exact dates for all 7 missing matches. 1976/77 M3 changes from "Jan" to 11th December 1976.
  - Finisher counts for 1974/75 M2 (143), 1976/77 M2 (153) and 1976/77 M3 (144).
  - Venue changes from "Croydon" to "Lloyd Park, Croydon" for 1974/75 M2 and 1976/77 M2. This follows the archive's existing venue alias.
- **div2:** the 4 Division 2 matches of 1977/78.
  - Each op has the date, venue, winner, finisher count (M2 has none printed), all 7 team scores and the Belgrave list: 118 result rows in total, including the winners.
  - They are not merged into the Division 1 races.
- **Notes:**
  - Magazine team scores for every missing match. No standings were touched.
  - Ranelagh's 1975/76 final total: the magazine prints 2142, but we hold 2124.
  - Minor time differences that were left alone.
- **Flags:**
  1. **1974/75 M3:** the Belgrave tail runs from 100 to 130. Held has A Harris, P Holman, D Langley and P Fitton, none of whom are in the magazine. The magazine has D.Davies, J.Kelly and R.Hall as Belgrave, but held has them under SLH, WAL and HHH. The held times also look shifted by one place.
  2. **1978/79 M1:** 9 held Belgrave positions differ by 2 to 18 places from the magazine's typed list, and many held times differ too.

## 1978/79 Matches 1 and 2 (garbled)
I re-checked the B198 p19 and p21 page images myself. Renames were applied at the held positions using the magazine's names. For example:
- A Blinck becomes Alan Black.
- G Voerth becomes Gerry North.
- K Mallinson becomes N Kirmatzis.
- A Kinchett becomes K Sinclair.
- P Langster becomes Ron Langheim.

Where the magazine's position differs from the held one, the rename still targets the held position. Those cases are listed in the 1978/79 M1 flag.

## Skipped, and why
- **Times that differ from held ones:** all the 1–60 second differences in 1975/76 M1–M3, 1976/77 M1 and 1978/79 M1–M2. These are minor, and rule 3 only fills missing times.
- **1975/76 M1, B Gorman:** the magazine says "60th" but we hold 65th. 60 is his scoring points (s=60), so the two agree. Covered by a note.
- **Small position differences:** G North 25th v 26th (1975/76 M2) and W Kerr 71st v 73rd (1975/76 M3). Both are ±1 or ±2, so not flagged.
- **1974/75 M1:** the magazine gives P.Adams 1st and B.Ford 2nd, but we hold a dead heat (=1). Left unchanged and noted.
- **1974/75 M3 names:** A Harris, P Holman, D Langley and P Fitton were not renamed to the magazine's Davies, Kelly and Hall. Those three are held under other clubs, so this goes to the flag.
- **Low-confidence identifications not applied:**
  - B Taylor as "Bob Taylor"
  - M Smith as "Bob Smith"
  - R Bale as "Reg Bale"
  - D Searle as "David J. Searle" from the members list (the Dave Searle form, which is high confidence from B198, was used instead)
  - D Bailey as "Dave Bailey" (that reference was to a junior race)
  - D Bonser / Don Bonsor spelling (left as initials)
- **Held initials with no full name in the findings, so left as they are:** S Martin, J Flynn, V Butcher, N Greaves, R Cullum, D Davies, J Myddleton, D Marlowe, R Coombs, D Baines, D McMillan, D Hurd, D Gordon, P Morris, A Grant, J Middleton, R Bailey, P Halliday, E Fisher, R Kerr, K Sinclair and R Lettins.
- **Name forms used:**
  - "Charlie Manning", "Michael Manning" and "Gerald Collins" are the forms the magazine prints.
  - Pat Newall becomes "Pat Newell" (prose spelling).
  - Eddie Thorp keeps the magazine's spelling "Thorp".
  - J Stratton becomes "J Stratten" (medium confidence).
- **Out of scope:** photos and youth-race notes. No women's material is in these issues.
