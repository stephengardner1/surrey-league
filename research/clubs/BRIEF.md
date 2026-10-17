# Club archive trawl: brief for reading agents

Goal: mine a club's own publications for Surrey Cross Country League information that slarchive.org
(the Surrey League archive) is missing or holds only partially, plus face photos of named League runners.
You read sources and record findings. You do NOT edit the site, the repo, or any data file.

## The League (scope)
- Surrey Cross Country League, senior men (from 1962/63) and senior women (from the 1980s). Usually 4 matches a season (Oct–Feb).
- **Division 1 only.** Division 2/3/4 results are OUT OF SCOPE (record at most a one-line "note" that the club was in Div 2 that season, or was promoted/relegated).
- Young athletes' league races, County Champs, Southern, National, relays, road races: OUT OF SCOPE for results.
  (Photos of named runners from those events ARE useful if the runner also ran in Div 1 of the League.)
- Club codes in our data: KEN Kent AC, THH Thames Hare & Hounds, HHH Herne Hill Harriers, BEL Belgrave, H/W Hercules Wimbledon,
  SLH South London Harriers, RAN Ranelagh, AFD Aldershot Farnham & District, G&G Guildford & Godalming, CRO Croydon,
  C/C Clapham Chasers, DUL Dulwich Runners, WOK Woking, E&E Epsom & Ewell, REI Reigate Priory, STR Stragglers, HOL Holland Sports.
  If unsure, write the club name in full.

## What the archive already holds
/home/claude/archives/existing/<CLUB>-<men|women>-<YYYY-YY>.json — one per season where we hold that club's runners.
Each is a list of matches: meta (season, match, date, venue, winner, teamScores...), resultsHeld (count), top10,
and `club` = every result we hold for that club (p=position, s=scoring points, n=name, c=club, t=time).
Seasons with no file = we hold no results for that club that season (or it wasn't in Div 1).

## Method
1. Find every passage about senior Division 1 League matches: race reports, season reviews, captain's/AGM reports, results lists, photo captions.
2. If text extraction is unreliable (scans), look at the page image before recording a name, position or time:
   `pdftoppm -r 130 -f N -l N -png file.pdf out` then Read the PNG (crop with PIL to zoom). Don't guess.
3. Compare with the existing extract. Record ONLY things that add or correct information:
   - **fullname**: a runner we hold as initials or a short/variant name, the source gives the full name (initial + surname + club + season must agree).
   - **spelling**: our name is misspelt (machine-read from handwritten results; trust the club source more).
   - **result**: a Div 1 finishing position/time we don't hold.
   - **correction**: a position/time/score in our data the source contradicts (flag only — we never change standings or team scores).
   - **race**: race-level info for matches we barely hold (date, venue, winner, team placings/scores, finisher count).
   - **team**: club team position/score, promotion/relegation, title wins.
   - **photo**: a photo of a NAMED senior runner with a reasonably clear face. Crop it (render ~200dpi) to
     /home/claude/archives/<source>/photos/<slug-of-name>-<n>.jpg (good/fair only) and record name, club, year,
     event, caption, quality (good/fair/poor), colour or b/w, and short appearance notes (hair colour/style, facial hair, glasses).
   - **note**: anything else relevant (e.g. club joined Div 1 in year X, league renamed).
4. Record exactly what the source prints for names (nicknames vs formal names: note both if both appear).

## Output
Append one JSON object per line to /home/claude/archives/<source>/findings.jsonl:
  {"type": "...", "season": "2014/15", "match": 2 or null, "sex": "men|women", "source": "short id", "url": "...", "page": int|null,
   "club": "KEN", "held": "what our data has now (or null)", "found": "what the source says",
   "position": int|null, "time": "mm:ss"|null, "evidence": "short verbatim snippet (<=25 words)",
   "confidence": "high|medium|low", "checkedImage": true|false}
Photos: also one line per photo in /home/claude/archives/<source>/photos.jsonl:
  {"name","club","year","event","caption","quality","colour":true|false,"appearance","file","url","page"}
Write as you go. When finished, write /home/claude/archives/<source>/summary.md: what you covered, counts by type,
best finds, and problems (unreachable files, unreadable pages). Your final reply = that summary (short).
Keep downloaded files under /home/claude/archives/<source>/raw/. Be polite to the sites: no parallel hammering, small pauses between downloads.
