# n5 summary: findings a10 + a11 (1987/88 to 1995/96)

Ops file: /home/claude/belgravian/ops/n5.jsonl (698 lines). Generator: /home/claude/belgravian/work/n5/gen.py.
Every rename, time and add was checked against the live data. The held name matches at that position and club, add positions are free, there are no duplicate ops, and every op carries a source.

## Counts
| op | men | women |
|---|---|---|
| rename | 379 | 4 |
| time | 148 | 4 |
| add | 19 | 79 |
| racemeta | 9 | 22 |
| flag | 6 | 2 |
| note | 26 (no file) | |
| div2 / newrace | 0 | 0 |

## Steve's Division-1-only decision
- I emitted no `div2` ops.
- I skipped these Division 2 races:
  - Men 1988/89 Div II, all four matches.
  - Men 1993/94 Div 2, all four races.
  - Women 1992/93 Div 2, all four races.
- Each skipped season has a `note`.
- Names from the Div 2 lists were used only as supporting evidence. Examples are Graham Adams, Phil Carstairs, Matt Hillier and Kassa Tadesse.

## Main changes
- **1989/90 Match 4.** We previously held only 3 results. I added 18 Belgrave results plus J Barton (THH) in 2nd, all with times. I also added times for Rayner and Penney, and the date 10th February 1990. The team scores agree with ours (there is a note). The magazine gives no finisher count.
- **Garbled names fixed from the magazine lists.** Examples:
  - 1991/92: J Fanny → J Barry, J Martin → John Mather, M Sizir/Dizio/Biziu → Marcello Bizio, J Dicont/Bycourt → John Bicourt, L Cong → Leo Coy, K Bale → Rex Bale, A Pointe → A Painter.
  - 1992/93 M3: M Blake → Mike Lake.
  - 1994/95: C Tarisse → Kassa Tadesse, T Beikelet → B Tolla, I Mann → Lionel Mann, J Salley → J Galley.
  - 1995/96 M1: 13 garbles, e.g. J Eshun → Jim Estall, S Palm → Stuart Paton.
  - 1995/96 M4: J Hughes → Steve Hewes, D Clace → Alex Luce, G Ram → Mick Graham.
- **Owain Lewes** (confirmed spelling) replaces O Lewes, O Lewis, D Lewis and D Louis wherever they appear.
- **Mike Lake / Martin Lake.** I only split the two "M Lake"s where the magazine names them. That covers 1990/91 M1, 1991/92 M2, 1992/93 M1/M3/M4 and 1994/95 M1/M2. Other "M Lake" entries are unchanged.
- **Initials expanded to full names** where the magazine's prose, captions or team lists give the name in that era. The confidence is high when the source is in the same season, otherwise medium. Name forms follow the magazine:
  - Graham Adams (prose; the caption sometimes says "Gerry")
  - Frank Ward
  - Charlie Dickinson
  - Tony Stone
  - Trevor Williams
  - Mike Webb
  - Jim Estall
  - Roger Alsop
- **Times added** where ours were missing: 1991/92 M2 (whole Belgrave list), 1992/93 M1–M4, 1995/96 M1 and M3, and several top-3 times.
- **Finisher counts added**: 1994/95 M1–M3, 1995/96 M2–M4.
- **Date fix**: 1991/92 M3 changed to 18th January 1992 (a Saturday; we held 17 Jan).

## Women
- The women's file holds only the winner for these seasons. Every Belgrave position is therefore new, except the Collison wins. I de-duplicated against the file: there were no clashes.
- I added 79 Belgrave results across these seasons:
  - 1989/90 M2–M4
  - 1990/91 M1–M4
  - 1991/92 M2–M3
  - 1993/94 R1–R4
  - 1994/95 R1–R4
  - 1995/96 R1–R4
- 1989/90 and 1991/92 races were matched to our match numbers by venue and date. For example, 1989/90 Tilford is M2, Lloyd Park M3 and Brockwell M4.
- G Collison → Gabby Collison (4 wins), with times added.
- I added 22 exact dates in ISO form, matching the women's file style.
- **1994/95 R1** positions are the magazine's Division-1-only positions, which is consistent with our winner Collison. There is a note.

## Flags (Steve to decide)
- **1987/88 M4:** positions 93 and 94 look like swapped club codes. We hold P Lake as BEL and M Head as RAN; the magazine has 94 M.Head as Belgrave.
- **1987/88 M3/M4:** the magazine headings swap the venues. Low confidence.
- **1990/91 M3:** 122 "D Winsm" (H/W) is probably D Winson of Belgrave.
- **1991/92 M3 venue:** the magazine says Dorking (The Nower); we hold Box Hill.
- **1992/93 M3:** Belgrave positions from about 94th onward are one place lower in our data than in the magazine. The team score is 617 in the magazine vs 627 in ours. I attached times by name to our positions.
- **1995/96 M3 venue:** Wimbledon Common in the magazine vs Putney Vale in ours.
- **Women 1994/95 R2 venue:** Woking vs our Bagshot.
- **Women 1990/91 M3 venue:** Bagshot vs our Lightwater.

## Skipped, and why
- **Held times that differ** (1989/90 M3, 1991/92 M1, 1994/95 M4, 1995/96 M4): the differences are only seconds, so I made no op. Where I recorded them, they are in notes.
- **1991/92 M4 Belgrave times**: ours are seconds-only fragments (t is not empty), so I made no time ops. The magazine's full times are mentioned in a note.
- **1994/95 M1 and M3 position mismatches**: the magazine quotes scoring positions there, so nothing needs changing.
- **Low-confidence items** (no op or note only):
  - G Tiernan → Teahan (1990/91 M3)
  - T Watt and P Roach (note only)
  - J M Bart (left alone; a real runner)
  - K Duckett (note: the magazine says only "Guest")
- **Women's results with no overall position** (1995/96 R2: J Moore, A Walter) are in a note.
- **Women's 1995/96 R1, 40th N Mills**: added without a time, because the printed time duplicates the 25th-placed runner's.
- **Out of scope**: photos, relays, club championships, young athletes.
