# a01 summary: Belgravian B148 to B156 (Nov 1962 to Aug 1965)

All 9 issues were covered. 160 findings are in `findings/a01.jsonl`. I checked the page images for every League table and name I used.

**Counts by type:** result 94, note 20, photo 19, race 11, fullname 9, correction 7.

## What each issue contained on the League
- **B148 (Nov 1962):** Nothing on the League beyond a passing mention that the first league matches were upon them.
- **B149 (Feb 1963):** Full 1962/63 senior report on pp26 and 28, covering Races 1 to 4, the final table and the scoring rules. p4 tells how the league began (Mitcham AC's proposal at the 3 Kings, Mitcham, May 1962). Adds:
  - dates (M1 27 Oct, M3 29 Dec 1962 in Richmond Park with 75 finishers)
  - M1 7th and 8th places (Palmer and Milner of Walton)
  - M3 10th Belgrave scorer: K. Miller, 29th
  - M4 times for 4th to 8th
  - two Walton corrections: Roath and Strange swapped, and "G. Winchester" rather than R.
  - provisional M2 team scores that differ from ours
- **B150 and B151 (May and Aug 1963):** No League content. Several good photos.
- **B152 (Dec 1963):** 1963/64 M1 (Wimbledon, 26 Oct 1963, about 150 starters).
  - Scoring positions for all 6 clubs.
  - A club handicap was run alongside the race. Its result list gives **actual times for 50 Belgrave finishers**: the 10 scorers plus 40 non-scorers, whose overall finishing places are not given.
  - Brighton relay team group photo with every runner named.
- **B153 (Apr 1964):** 1963/64 M2 (Esher, 14 Dec 1963), where we held only the winner.
  - Adds 2nd and 3rd overall (Collins of Surrey, Roath of Walton) and 9 more Belgrave positions.
  - Also covers M3 and M4 and the final table.
  - M4 corrections: our "Burt" (BEL, 24th) is T. Hart, and our "Cook" (27th) is D. Cocks.
- **B154 (Nov 1964):** Croydon join the league, and the 1964/65 venues are listed. No race report.
- **B155 (Feb 1965):** 1964/65 M1 to M3 in full.
  - Dates, finisher counts, and scoring positions for all 7 clubs.
  - Times for every Belgrave scorer.
  - M3 10th Belgrave scorer: N. Stairs, 56th.
  - M2 correction: Surrey scored 424 and Walton 442 (our data has them the other way round). Table after 3 matches.
- **B156 (Aug 1965):** 1964/65 final table with each club's score in every match.
  - Our M4 score for Walton (442) should be 506.
  - Hercules won the league by 16 points after a recount.
  - Individual winner: E. Caiger (Hercules), positions 9, 4, 6, 14.
  - Belgrave had 10 finishers in the first 28 at Morden.
  - No individual M4 list.

## Problems
- **Two kinds of position in this era.** Team lines give scoring positions, while some individual lists give actual finishing positions. For example, in 1964/65 M3 our held Belgrave list mixes the two. The `found` field says which kind each finding uses.
- **No 1965/66 League content** in these issues.
- **Lost writes, now fixed.** Early on, another agent overwrote the shared `add.py` helper, so one batch of my writes was lost. I re-added it and checked: the jsonl contains only my own lines, with no duplicates. My helpers now live in `work/a01/`.
- **Photos.** 22 crops were saved to `photos/`, all named `B15x-pN-<surname>`.
