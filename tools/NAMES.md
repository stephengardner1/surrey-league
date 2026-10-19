# Runner names: how changes are kept, and what to do when new results arrive

Every approved name change is logged in `tools/name_changes.json` (who changed, why, and the evidence).
`tools/rename_athletes.py` applies the log to the results; it is safe to run again and again.

## When you import new results from surreyleague.org
1. Import the results as printed.
2. Run `python3 tools/rename_athletes.py` (then `--dry` again: it should report 0).
   Club-wide entries in the log (those with `"seasons": null`) also catch the same misspelling in new seasons,
   e.g. Kent's "Tom Huddiman" becomes Tom Muddiman again.
3. Winner records (`athletes` in data.json) have no season, so season-limited renames skip them. After a batch,
   check for athlete records whose name no longer appears in any result and rename them to match (Oct 2026: G Tuck,
   Chris Hensby, M Dent and others had become duplicate pages this way).
4. Known surreyleague.org misspellings are also listed in `athleteAliases` (data.json / data-women.json),
   so a new result joins the right runner's page even before step 2.

## Steve's alias sheet (Oct 2026)
The Aliases tab of the cms-template Google Sheet is no longer read by the site. Its rows were folded into the
change log and data.json, so nothing on the site depends on it. It is now an inbox: when Steve or a club contact
adds rows, check each against the evidence and turn it into a club-scoped entry in name_changes.json.

## Rules (Steve, Oct 2026)
- surreyleague.org is authoritative from 2013/14: only clear typos Steve has approved are changed there.
- **Married names are never overwritten.** Results keep the name they were printed under. The two names are
  joined with `athleteAliases` (the married name is the page name) and `athleteNee` gives the maiden name,
  e.g. Emily Alden (née Nelson), Stacey Ormerod (née Ward).
- **Nicknames are aliased, not renamed**, e.g. "Liv Stillman" joins Olivia Stillman's page.
- Before 2013/14 (names machine-read from photos): a magazine, county champs result or Athletics Weekly beats our
  name; an initial is the safe fallback when a full name has no source.
- Use `"seasons": [first, last]` when a fix only applies to some seasons, and `"races": [[season, match, position]]`
  when two real people share a raw name in the same season.
- Aliases are global (not per club), so only alias distinctive spellings; ordinary names that could belong to
  someone at another club stay as club-scoped renames in the log.

## Initial-only names (Oct 2026)
An initial (e.g. "D Fagan") is joined to a full name when the county champs give only that first name for
the initial at that club, the two forms never meet in one race, and the years fit. Not joined (left as initials):
initials whose years run well beyond the documented full name (possibly two runners), and pairs with no outside
source. Where our full name disagreed with the county champs (2+ mentions), the county champs name was used.

## One-off club corrections
- 2003/04 match 1 (men), 10th, James Jackson 27:01: club THH -> AFD (Steve approved, 17 Oct 2026).
  Athletics Weekly 22 Oct 2003 prints "10 J Jackson (AFD, M40) 27:01". The published team scores
  (Thames 208, Aldershot 321) only add up with him counted for Aldershot.

- Women's places added from Athletics Weekly whose club wasn't on the site (Oct 2026, Steve): new clubs added
  with no vest colours (grey) because their colours aren't known: Tadworth AC (TAD), Surrey Beagles (SYB),
  Redhill & Surrey Beagles (RSB), Sutton & Cheam (S&C), Chessington & Bookham (C&B), Dorking St Paul's (DSP),
  Camberley & District AC (CBY). AW's "M&S" for S Lanham, 1986/87 m3, is Mitcham (Sue Lanham).
  AW's "Craw" in 1992/93 m2 (K Sutton, J Mitchel) is a misprint for Croydon (Steve). Five places stay unknown: AW's "Runn", "TWH", "C'wood", "Phillips CS", "n/s".
- 1987/88 match 4 (men), 94th, M Head (Martyn Head) 5 Mar 1988: club RAN -> BEL (Steve approved, 19 Oct 2026). He ran
  for Belgrave in matches 1-3 that season and in 1989/90, and The Belgravian (Apr 1988) names him Belgrave's Section Secretary.

## Same surname, different runners (women, Steve 18 Oct 2026)
- Nicky Harvey (Herne Hill, 1990s-2000s) and Natalie Harvey (South London) are two runners. "N Harvey" at
  Herne Hill is Nicky. The old alias joining "N Harvey" to Natalie was removed.
- Caroline Letchford (South London, 1980s-early 90s, county champs) and Charlotte Letchford (South London,
  from 2017/18) are two runners. The 1980s "C Letchford" rows are Caroline. The old alias was removed.

## Croydon to Boxhill (men, 1986-87)
- Ken Penney: one runner, Croydon (1981-86) then Boxhill Racers (1987-97). County champs list him at Croydon to 1985
  and Boxhill from 1986. Norman Hemming (Croydon Harriers), email to Steve and Matthew Kiernan, 18 Oct 2026: Ken had
  moved on by the time he joined Croydon, and was running for Boxhill at the 1986/87 Surrey County XC. Already one page
  on the site ("K Penny" spellings joined).
- Still to confirm with Croydon: Steve/Steven Bishop, Gary Bishop and Ian Statter (same pattern, Croydon then Boxhill).

## Nicknames joined by alias (Steve, 19 Oct 2026)
- Tilly Heaton (BEL, 2010/11 m1) is Mathilde Heaton: alias in data-women.json athleteAliases. Alison Heaton (W/W) is a different runner (same race 2005/06 m1).

- Belal Ahmed (H/W, 2007-2019) also appears as B Aly, Belal Aly, Belal Ali and Beld Ali: one runner (family name Aly Ahmed; his clubmate H Aly Ahmed / Hussein Ahmed ran in the same races and stays separate). Joined by alias, printed names kept (Steve, 19 Oct 2026).

## Earlier names joined by alias (men)
- Andy Maud (C/C, 2013/14 m2-m4) is Andy Coley-Maud: same rule as married names, printed names kept, alias plus athleteNee in data.json so his page shows "(Andy Maud)" (Steve, 19 Oct 2026).

## Kept as they are (Steve, 19 Oct 2026)
- Mel Thorpe (BEL, 1963-66): The Belgravian's results print "R. Thorpe" but its prose and later results say Mel / M. Thorpe.
- Peter Adams (AFD, 1971-2003): one runner; AW prints "P Adams (AFD, M45)" in 1997 and 1999.

## Sources already searched
See `research/README.md`: The Belgravian, club archives, Surrey County XC champs 1961-2013 (`research/county-champs/`),
and Athletics Weekly winter issues (1998-2005 Oct-Feb text searched again in Oct 2026 for Aldershot names).

## Same surname, different runners (men)
- Lionel Mann (BEL, 1966-99) and his son Robert Mann (BEL, b. 1968; R Mann in 1985/86, 1986/87, 1989/90). The Belgravian names Lionel's sons as Robert and James. They ran in the same races, so they are kept apart (Steve, 19 Oct 2026).

## Winners-list first names matched to the race results (Steve, 19 Oct 2026)
The Mitchell Cup winners list and season individual tables were typed separately from the results, so a different
first name there linked to an empty page. Corrected in `mitchellCupWinners` and `individualRankings` (same winner,
name only):
- 1975/76 Roy Treadwell (CRO) -> Bob Treadwell: results print R Treadwell (already joined to Bob); county champs Bob Treadwell 2nd in 1975 and 1976.
- 1977/78 Mick Connolly (WAL) -> Malcolm Connelly: his places 3, 4, 4, 3; county champs Malcolm Connelly (Walton). His "M Connolly" and surname-only "Connelly" results were joined too (name_changes.json).
- 1978/79 Geoff Ribbons (E&E) -> Gary Ribbons: no Geoff in any result; county champs Gary Ribbons (Epsom & Ewell) 1976-84.
- 1986/87 John Wright (BEL) -> Jean Paul Wright: our results and The Belgravian's 1988 photo caption say Jean Paul; its 1986/87 report says John. The page is Jean Paul Wright; John Wright, J Wright and John-Paul Wright are aliases.
Same-name pages (nameCollisions, e.g. Dave Taylor HHH, Tom Foster G&G) are now linked from winner lists by club in index.html.
