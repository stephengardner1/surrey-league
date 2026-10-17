# n6 summary: findings a12 and a13 (1996/97 to 2008/09)

- **Ops file:** `/home/claude/belgravian/ops/n6.jsonl` (901 lines)
- **Builder script:** `/home/claude/belgravian/work/n6/build.py` (re-runnable; it validates against the live data as it writes)

Every op was checked against the live `data.json` and `data-women.json`, and none failed:
- Each rename's held name exists at that position and club.
- Each time op targets a result with no time.
- Each add position is free.
- No duplicates.

Following the coordinator's instruction, there are **no `div2` ops**. Women's Division 2 seasons are skipped.

## Counts
| Op | Men | Women | Total |
|---|---|---|---|
| rename | 514 | 32 | 546 |
| add | 9 | 187 | 196 |
| time | 32 | 24 | 56 |
| racemeta | 4 | 38 | 42 |
| flag | 15 | 2 | 17 |
| note | 15 | 29 | 44 |

### Men's renames
| Type | High confidence | Medium confidence |
|---|---|---|
| Initials to full name | 358 | 54 |
| Misread | 49 | 38 |
| Spelling | 12 | 3 |

- **Sources.** Initials were expanded season by season from:
  - prose and photo captions in B225 to B231 and eH04 to eH12;
  - the XC Plate tables B240, B254 and B263, which list every Belgrave League runner in 2005/06 to 2007/08.
- **Full-name corrections.** Each was applied only where the magazine is specific to that runner:
  - William/Will Lynch → Warren
  - Les Greatorex → Lee
  - Lawrence/Liam Hurst → Lee
  - Steve Connor → Sean
  - Moses/Martin Byansi → Malachi
  - Mark Kazimierski → Mike
  - Martin/Mark/Jason Webb (1999 to 2003, initial M) → Mike Webb
  - Justin Webb → Jason
  - Andrew Zawadski → Adam
  - Andy Graffin (2001/02 M4 2nd) → Allen
  - Jonathan Fairbourn → James
  - Paul Cross → Peter
  - Rob Stannard → Richard
  - Jules van der Toorn → Joe
  - Knut Sheridan → Knut Hegvold
  - Greg Maybank → Billington
  - Alex/Andy Maybank → Alex Marek
  - Ed Lyne → Eliot
  - James Charles → John
  - John Stevenson → Jamie
  - Mark Whiting → Matt
  - Peter Fallonius → Fallenius
  - J/Andrew Barden → Tony
- **Positional misreads**, for example:
  - N Dough → Mike Nouch
  - P Beaver → Dave Beaver
  - S Feisler → Steve Fowler
  - L Hunt/A Alsop/D Dehie/C Leimenacher/A Lowmeadow/N Bale → Hurst/Alsop/Ochse/Lemenager/Cowmeadow/Bale
  - J Craily → Junior Galley
  - P Ruckley → P Buckley
  - R Coulter → Rob Poulter
  - J Ellacott and I Hadfield → Tom
- **Guest-club rows renamed in place, club unchanged:** Nerurkar, Onoufrio, Ashe, Ward, Hegvold (2000/01 M2), O'Halloran, and Dan Stone → Darrell Stone.
- **Graham vs "Gerry" Adams.** The magazine itself uses both forms in the 1990s. Each match follows that issue's own usage, at medium confidence.

### Other men's ops
- **Times:** 32. These fill every Belgrave time for 1997/98 M2 and 2002/03 M4.
- **Adds:** 9.
  - 2007/08 M1: seven Belgrave runners at 131 to 169. Held results stop at 120, but the magazine says 170 finished.
  - 2007/08 M3: Rehn 143 and Cross 147.
- **Racemeta:** 4.
  - 1997/98 M4 finishers, 0 → 129
  - 1999/00 M2 date → 20th November 1999
  - 2000/01 M1 date → 14th October 2000
  - 1997/98 M3 venue → Sparrows Den, West Wickham
- **Flags:** 15.
  - Wrong team tables: 2000/01 M1, M3 and M4 (BOH 105 "winner"); 2001/02 M1 and M3.
  - 2005/06 M4: positions shifted by one from 41st down; BEL 369 vs 343.
  - 2006/07 M1: Bodin was a guest; BEL 314.
  - Belgrave runners held under other clubs: 1998/99 M4 (Herrington as AFD, Coughlan as RAN) and 2003/04 M1 (Poulter as SLH, Marcus as STR). Both also hold BEL names that are not in the magazine's list.
  - 2000/01 M3: R Hanson and B Corr.
  - 1998/99 M2: two times 2 minutes slow.
  - 2007/08 M1 and M3: finisher counts short.
  - 1971/72 M3: BEL and MIT scores look swapped.
  - 1972/73 M3: venue given as Streatham Common.

## Women
- **Adds:** 187. These are Belgrave women at positions the women's file did not hold, in Division 1 races only (1996/97 to 2008/09).
  - Already-held Belgrave women were de-duplicated: 2004/05 R1 (all 15 held, nothing added), 2004/05 R3, 2005/06 R1 and R4, 2006/07 R1 to R4, 2007/08 R1 and R2, 2008/09 R1 and R2.
  - The winner and 2nd and 3rd places were not added (only BEL rows), but held winners got a **time** op (24).
- **Racemeta:** 38. These are exact ISO dates (matching that file's format) replacing "Oct" and similar, plus finisher counts where the magazine gives them and the venue Newlands Corner for 2005/06 R3.
- **Renames:** 32. Initials expanded from the Plate tables, Christine → Catherine Eastham, Christine → Chrissie Wellington, and Matilda → Mathilde Heaton (medium confidence).
- **Notes:** one per race, carrying the magazine's team scores and final tables.

### Skipped and why
- **Division 2:** women's 1998/99 (all four races) and 2001/02 (all four races). Belgrave won Division 2 and was promoted both years.
- **1997/98 R1:** the Belgrave positions are for a combined Division 1 and 2 race, so they went in a note instead.
- **2002/03 R4:** the positions include a guest winner (E Fisher), so this is flagged.
- **2005/06 R1:** held Belgrave positions drift from the magazine's (7 vs 8 at the top, up to 69 vs 84), so this is flagged and nothing was renumbered.

## Skipped or not changed (men)
- **Shane vs Steve Kennefick:** the magazine prints only "S.Kennefick", so this is a note.
- **W Drey, T St Leger, G Reid, P Wytch, A Bicourt:** no first names found.
- **2002/03 M1, 34 J Estall:** not in the magazine's list, so this is a note.
- **2001/02 M2, 97 Rob Poulter:** not in the magazine's list, so this is a note.
- **2007/08 M2, 122 R Merrick:** held as GUEST but Belgrave in the magazine, so this is a note.
- **1999/00 M1:** the magazine's team scores were re-scored after Farah was removed; this is a note, and standings are unchanged.
- Low-confidence items were not applied.
