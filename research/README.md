# Research archive (not part of the website)

What we have already found in club magazines, Athletics Weekly and club archives, so no session
has to trawl them again. Steve's decisions on each finding live in two review pages (artifact databases):
- **Belgravian Findings**: https://claude.ai/artifact/C7xh59MUnrQYAb8XgN5m64
- **Club Archive Findings**: https://claude.ai/artifact/NEQhEHUfaFVcRtpu6WiZyj

Read those (ArtifactData) for what Steve approved or rejected.

**Status of the Belgravian changes (17 Oct 2026): applied.** The keys of every applied item are in
`belgravian/applied-2026-10-17.json`. Applied: 1,199 high-confidence name changes, 773 missing results
(non-scoring, at free positions only), 534 times, 157 dates/venues/finisher counts, and 13 initials upgraded to
full names. Items skipped were already done, already present one place apart (printing difference), or had
changed since. **Still to do:** `belgravian/medium-confidence-names.json` holds 341 medium-confidence name
changes. They're for the names session to cross-check against other sources before bringing the strong ones to Steve.

Full texts of the magazines are NOT kept here (this repo is public, and they're copyright).
Re-download them from the URL lists and convert them with `pdftotext -layout`.

## belgravian/  (The Belgravian, Belgrave Harriers' magazine; 139 issues, from belgraveharriers.info)
- `manifest_raw.json`: every issue, with its label, number, year and PDF URL. Our issue codes `B148`... are `B` + issue number.
- `findings/a01–a15.jsonl`: 3,727 raw findings (type, season, match, club, held name, name found, position, time,
  evidence quote, page, confidence, checkedImage), with a summary per batch.
- `ops/n1–n6.jsonl`: those findings turned into exact change operations against the data (rename 1,599, add 894,
  time 545, racemeta 187, note 129, flag 58, div2 4), following `RULES.md`. These are what Steve reviewed.
- `BRIEF.md`, `RULES.md`: the instructions the reading agents followed (Steve's rules).
- `overrides.json`, `photo-shortlist-summary.md`: portrait photo work from the same trawl.

## clubs/  (other club archives, Surrey County champs and Athletics Weekly)
- `BRIEF.md`: the trawl instructions.
- `<club>/findings.jsonl`: name and result findings (afd 61, hhh 70, kent 86, thh 80, aw-hhh 12).
- `<club>/photos.jsonl`: photos of named runners (with URLs) for the portrait work.
- `top-*.txt`: the target runner lists used for the photo search.
- See also the project doc `claude/club-archives.md` for the list of archives and who holds offline ones.

## athletics-weekly/
Athletics Weekly's free online archive (athleticsweekly.com/archives) has PDF issues. Winter issues searched so far:
- `winter-1974-1987.txt`: 336 issues, with PDF URLs.
- `winter.txt`: 465 issues from 1987–2005 (issue pages), plus `pdfs.txt` (94 direct PDF links).
To search again: download the PDFs, run `pdftotext -layout`, then grep for the surname and club. The full text of
all ~800 issues is about 600 MB.

## Most useful free source for initials → full names
Surrey County XC Championships results from 1962/63, with full names and clubs:
https://www.surreyathletics.uk/crosscountry/index.php (athlete pages: /database/profile.php?N=…&G=M).
