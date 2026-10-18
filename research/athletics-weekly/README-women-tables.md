# Women's team scores and league tables from Athletics Weekly (Oct 2026)

- Team scores printed by AW were added to 77 women's races (1980/81-2004/05) that had none, as printed
  (`teamScoresSource` on each race). Existing team scores were never changed; where AW listed extra clubs they were added.
- Through the 1980s-2000/01 the women's league was decided by **league points**, not aggregate scores: 10 points for
  winning a match down to 1 for 10th, most points wins, ties split on total team score. AW's printed final tables
  confirm this. Seasons built this way carry `"scoring": "points"` and a `tableNote`; the site shows "Pts" and keeps them
  out of the lowest-winning-total and closest-margin records, which are for aggregate seasons.
- Built: 1993/94 and 1995/96 (calculated from AW's match team placings; 1995/96 matches AW's final table exactly,
  1993/94 matches for 2nd-5th), 1996/97, 1997/98, 1998/99, 1999/00, 2000/01 (AW's printed final tables).
- Not built: 1990/91 (AW's final totals use a different points scale), 1991/92 and 1992/93 (a match's team results
  missing), 1994/95 (calculating puts Stragglers top, but our records and AW's after-two-matches table have Herne Hill
  ahead, so something in AW's team results for the 3rd/4th matches is incomplete), 1980s (only the top 3-4 clubs printed).
- From 2002/03 the women's tables we hold are aggregate scores (lowest wins).

## Update (Steve asked, 18 Oct 2026): The Belgravian check and scorers
- 1994/95 built from AW's printed final table (it was in AW's notes for the last match): Herne Hill 36, Stragglers 34 ...
  Herne Hill was missing from AW's printed team list for match 3; AW's after-three-matches table places them 5th.
  The Belgravian (No. 223) agrees Belgrave finished 7th.
- 1993/94: The Belgravian (No. 222) prints the same final table as AW, including Belgrave's impossible 59, but also gives
  Belgrave's match placings (2nd, 2nd, 1st, 2nd = 37), confirming the calculated table.
- 1985/86: top 8 of the final table from The Belgravian (No. 210), plus 2nd/3rd places, the winner's time and the team
  top three for match 4 (not in AW).
- 1990/91, 1991/92, 1992/93: The Belgravian has only Belgrave's own placings (Belgrave were in Division 2 in 1992/93),
  so these stay unbuilt.
- Scorers: where a club's first 4 or 5 finishers (5 from 1990/91) add up exactly to the printed team score, those runners
  are marked as scorers (`pts`). 134 club results, 374 runners, 1980/81-2005/06. Nothing was marked where the sum doesn't match.
