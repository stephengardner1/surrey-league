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

## Athletics Weekly, re-searched Oct 2026
Oct-Feb issues 1998/99-2004/05 were downloaded and searched again for Aldershot names (findings added to
`clubs/afd/findings.jsonl`: James Jackson 2000-05, Paul Harwood; McCarthy, Haynes, Sheard and Cartailler appear with
initials only). Not stored, as before.

## county-champs/
All Surrey County XC Championships results 1961/62-2012/13 (downloaded 17 Oct 2026), one finisher per line. See its README.

## Most useful free source for initials → full names
Surrey County XC Championships results from 1962/63, with full names and clubs:
https://www.surreyathletics.uk/crosscountry/index.php (athlete pages: /database/profile.php?N=…&G=M).
- Oct 2026 (Jackson puzzle): AW winter issues Oct 1979-Apr 1987 (207 issues from `winter-1974-1987.txt`) and The Belgravian
  B199-B212 (1979-88) searched for Jackson. Findings in `clubs/afd/findings.jsonl`. Not stored.
- Oct 2026: AW winter issues 1987/88-1997/98 (289 issues) downloaded and searched for first names of initial-only runners
  (name printed next to the club). 12 applied (logged in tools/name_changes.json); 26 single mentions held for Steve.
  Text not stored; re-download with the issue pages in `winter.txt`.

## Race photos on the site
Race pages can show archive photos: add an entry to `RACE_PHOTOS` in `files/index.html`, keyed `'season|match'`
(e.g. `'1964/65|1'`), and put the image in `files/photos/races/`. Each entry has a caption, the photographer credit, and
a source name and link. Desktop shows the photo under the team scores; mobile shows a strip thumbnail beside the Individual/Teams toggle. Several photos per race are fine (the pop-up steps
through them); women's races use keys starting `w|`. `thumbPos` sets the strip crop.
Runner names in a caption link to their profiles automatically when they match a name in that race's results
(caption names go through the site's own aliases, so "Jim Estall" finds James Estall; add `links:{'Caption name':'Athlete name'}` if not). Clicking the photo opens it large with caption and credit.
Always credit and link the source (e.g. Alan Mead's belgraveharriers.info).

Added 19 Oct 2026: 1983/84 m4 and 1997/98 m3 (Athletics Weekly, Steve reviewing the risk), 1991/92 m1/m3/m4, 1998/99 m1,
1999/00 m1 (men and women), 2000/01 m1 (The Belgravian) and 2004/05 m1 (Alan Mead's site). Not used: The Belgravian
No. 158 p31 (1966) and No. 226 pp32-33 (1997/98) photos have no captions saying which race they're from.
Also 19 Oct 2026: 19 photos from the old belgraveharriers.com (2001-2014 site, via the Wayback Machine): men 2001/02 m3,
2003/04 m1, 2004/05 m1, 2005/06 m1-2, 2006/07 m1, 2008/09 m2, 2009/10 m1; women 2003/04 m4, 2004/05 m1, 2006/07 m2,
2007/08 m3. The old site's Surrey League galleries are /photo_gallery/surrey_lg_* and the yearly /20xx/rc_20xx.htm pages.
Wayback isn't reachable from the cloud workspace; the photos were downloaded on Steve's Mac (~/Pictures/belgrave-wayback).
Not yet used: 2013/14 men m4 (Richmond Park leaders, Leo Coy) and women m1/m2 photos - those images failed to download.
Profiles: any runner named in a race-photo caption gets the photos on their profile automatically (desktop: a tile at the
right of the header; mobile: a strip beside "Compare to"). The pop-up shows which race each photo is from, with a link.

## Athletics Weekly 1962-1974 (searched 19 Oct 2026)
`athletics-weekly/winter-1962-1974.tsv`: 262 winter issue PDFs (Oct-Mar). About 40 issues from 1965-69 have no PDF on AW's site.
In this era AW called our league the "North Surrey League". Photos are mostly covers ("Cover photo by ...: caption").
Found and added: cover of 13 Mar 1965 (1964/65 m4 Morden, North and Nåjde, Ron Linstead) and 7 Nov 1970 p25
(1970/71 m1 Wimbledon leaders, Ron Linstead). Everything else the search turned up was other races (road relays,
Civil Service, county champs). Text not stored.

## Herne Hill and Thames Hare & Hounds old websites (searched 19 Oct 2026)
- Herne Hill Harriers before hernehillharriers.com (2009-): hernehillharriers.co.uk (2001-07; the domain is now a spam site)
  and hernehillharriers.org.uk (2007-09, text only). hhh.org.uk is the Hash House Harriers and nothing to do with us. The archived
  galleries only hold small (about 90px) uncaptioned thumbnails, so nothing usable.
- Thames Hare & Hounds (thameshareandhounds.org.uk, archived from 2000): 2000-2010 pages are text reports. The only league
  photo is the Feb 2011 women's team at the clubhouse, now used for women 2010/11 m4.
