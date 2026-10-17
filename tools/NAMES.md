# Runner names: how changes are kept, and what to do when new results arrive

Every approved name change is logged in `tools/name_changes.json` (who changed, why, and the evidence).
`tools/rename_athletes.py` applies the log to the results; it is safe to run again and again.

## When you import new results from surreyleague.org
1. Import the results as printed.
2. Run `python3 tools/rename_athletes.py` (then `--dry` again: it should report 0).
   Club-wide entries in the log (those with `"seasons": null`) also catch the same misspelling in new seasons,
   e.g. Kent's "Tom Huddiman" becomes Tom Muddiman again.
3. Known surreyleague.org misspellings are also listed in `athleteAliases` (data.json / data-women.json),
   so a new result joins the right runner's page even before step 2.

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

## One-off club corrections
- 2003/04 match 1 (men), 10th, James Jackson 27:01: club THH -> AFD (Steve approved, 17 Oct 2026).
  Athletics Weekly 22 Oct 2003 prints "10 J Jackson (AFD, M40) 27:01". The published team scores
  (Thames 208, Aldershot 321) only add up with him counted for Aldershot.

## Sources already searched
See `research/README.md`: The Belgravian, club archives, Surrey County XC champs 1961-2013 (`research/county-champs/`),
and Athletics Weekly winter issues (1998-2005 Oct-Feb text searched again in Oct 2026 for Aldershot names).
