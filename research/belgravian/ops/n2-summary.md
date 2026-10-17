# n2 summary: a04 + a05 (1969/70 to 1973/74), men only

The findings in these two files contain no women's results and no Division 2 races, so there are no `newrace` or `div2` ops. This follows Steve's decision to cover Division 1 only.

## Op counts (517 lines in total)

| Op | Count | What it covers |
|---|---|---|
| add | 300 | Belgrave non-scorers, plus scorers missing from our lists, at positions we don't hold, 1969/70 to 1972/73 (214). All Belgrave finishers for 1973/74: 78 positioned results (M1 35, M2 19, M3 14, M4 10). Places 2 and 3 for each 1973/74 match (8), with Hutchin as MPA (Met Police). |
| time | 165 | Times for held results that had none. Includes the four 1973/74 winners. |
| racemeta | 24 | 17 exact dates (every race 1969/70 to 1971/72, 1972/73 M3, and all of 1973/74), 6 finisher counts, and 1970/71 M2 venue changed from Croydon to Lloyd Park. |
| rename | 7 | Doug Brew to Dave Trow (1969/70 M4, 40th). Charlie Maning to Manning. R Dixon to Bob Dixon (3 matches). C Keane to Colm Keane (medium). D Carllson to David Carlsson (medium). |
| flag | 9 | 1971/72 M3 team scores attached to the wrong clubs. 1971/72 M4 H/W and MIT swapped. 1970/71 M4 MIT and CRO swapped. 1970/71 M4 Hart 22nd not 20th. Kortenray's club is Mitcham, not H/W (1969/70 M1 and M3). 1970/71 M2 Thresher time held as the winner's time. 1972/73 M3 winner's time 27:16 should be 22:55. 1972/73 M3 venue is Streatham Common, not Wimbledon. |
| note | 12 | 1973/74 team scores for each match and the final table (not applied, per rule 6). Uncertain results and spellings, listed below. |

## How names were chosen for adds

- Initials are expanded to a full first name only when there is support for it:
  - the same runner already appears in our data under that full name, or
  - the magazine prose or member lists of the era give it (for example Simon Holmes, Les Morris and Jim Heathfield in B184, Dave Trow in B173, John Kelly in B176, and Chris Barber).
- Otherwise the printed initial and surname are kept: A Trowell, E Pallant, P Pringle, R James, R Hamilton, M Clancy, M Elliott, L Callum, R Whickam, W Fairfield, D Hurd, J McKeown, R Hopkins, R Joicey, K Maylie, L Jones and R Beaumont.
- R Richardson is added as "Bob Richardson" to match the name we already hold for him. A note says the magazine lists him as a second-claim member (first club Blackheath), and the first name "Bob" is unconfirmed.

## Skipped, and why

- **1970/71 M2:** seven non-scorers the magazine prints with "?" around the position and time are not added. They are listed in a note.
- **1970/71 M2:** Hart 26:15 and Fernee 26:27 look misprinted (both faster than 5th place), so the times were not applied. They are in a note.
- **1969/70 M3 Holt tie:** already held as "=1", so no change. Places 1–7 and 9 of 1972/73 M3 were already held with matching times; only Presland's time differs, and that is flagged.
- **Spellings left unchanged:**
  - McMillan vs Macmillan: the magazine is inconsistent.
  - B Young vs D Young: low confidence.
  - Freullet vs Freullett: inconsistent.
  - These three are in notes.
- **Team-score notes not acted on:** printed-total vs position-sum discrepancies of ±3 to 7 (1969/70 M2, 1971/72 M2 and M4) and Mitcham 438/440, Walton 460/461 and Mitcham 469/470 are trivial differences, so no ops.
- **Ignored:** photo findings, title-count inconsistencies and other prose notes have no data impact.
- **Checks run:** every add was checked against the live data and its position is free. Every time and rename was checked against the held name, position and club, and every time op targets a result with no held time.

Scripts are in /home/claude/belgravian/work/n2/ (build.py generates the ops).
