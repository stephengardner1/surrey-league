# Belgravian scan — brief for reading agents

Goal: mine *The Belgravian* (Belgrave Harriers club magazine) for Surrey Cross Country League
information that slarchive.org (the Surrey League archive) is missing or holds only partially.
You are reading historical sources and recording findings. You do NOT edit the site data.

## The League
- Senior men's Surrey Cross Country League, 4 matches a season (Oct/Nov, Nov/Dec, Jan, Feb), first season 1962/63.
- In the 1960s/early 70s Belgrave often called it the **"North Surrey League"**, "N.S. League", "N. Surrey League".
  Later "Surrey League", "Surrey X-C League", "S.C.C.L.", sponsor names ("Reebok Surrey League" etc.), "Division 1/2".
- Women's Surrey League exists from the 1980s; record Belgrave women's league results too.
- Young athletes' (boys/youths/colts) league races are OUT OF SCOPE — skip them, except note photo captions only if senior.
- Other races (Surrey County Champs, Southern, National, relays) are OUT OF SCOPE. Don't confuse "Surrey County Championships"
  or "Surrey Road Relay" with the League.
- Belgrave club code in our data: BEL. Other common codes: H/W (Hercules Wimbledon), SLH (South London), WAL (Walton),
  AFD (Aldershot Farnham & District), CRO (Croydon), RAN (Ranelagh), THH (Thames H&H), KEN, HHH (Herne Hill), SUR (Surrey AC),
  C/C (Cambridge Harriers? check), TBH, etc. If unsure of a code, write the club name in full.

## Inputs
- PDFs: /home/claude/belgravian/pdf/<ID>.pdf   (IDs like B175 = issue No.175; eH07 = eHarrier No.7)
- Text layers (OCR, often garbled on pre-1990 issues): /home/claude/belgravian/txt/<ID>.txt  (pages separated by form-feed \f)
- Candidate pages per issue: /home/claude/belgravian/candidates.json  (keyword hits; a guide, NOT exhaustive —
  skim each assigned issue's whole text for cross-country / league reports too, they often appear under "Cross Country",
  "Captain's report", "Team news", season reviews, results sections, AGM reports).
- What the archive already holds: /home/claude/belgravian/existing/men-YYYY-YY.json and women-YYYY-YY.json
  (per match: meta incl. date/venue/winner/team scores, resultsHeld count, top10, and every Belgrave result held).
  Result keys: p=position, s=scoring points, n=name, c=club, t=time.
- Issue list with dates: /home/claude/belgravian/manifest.json

## Method
1. For each assigned issue, find every passage about senior League matches.
2. OCR is unreliable for names. **Whenever a name, position or time matters, look at the page image**:
   `pdftoppm -r 130 -f N -l N -png /home/claude/belgravian/pdf/<ID>.pdf /home/claude/belgravian/img/<ID>-pN`
   then Read the PNG (crop with python/PIL to zoom on a column if small). Do not guess from garbled OCR.
3. Compare against the existing extract for that season/match and record ONLY things that add or correct information:
   - **fullname**: a Belgrave (or other club) runner we hold as initials, e.g. we have "P Standing", magazine says "Phil Standing".
     Only match when initial + surname + club agree and the race/season context supports it. Give evidence quote.
   - **result**: a finishing position (and time if given) we don't hold — e.g. Belgrave runner 34th in Match 2 1973/74.
   - **correction**: a position/time/name/score in our data that the magazine contradicts.
   - **race**: race-level info for matches we barely hold (date, venue, winner, team placings/scores, finisher count, division).
   - **team**: Belgrave team position/score, division, promotion/relegation, B team results.
   - **photo**: a photograph of a NAMED senior runner where the face is reasonably clear, ideally a Surrey League race
     (other cross-country/road photos of runners who appear in the League are useful too). Note page, caption, who/where,
     and a quality rating (good / fair / poor). Extract the photo region to
     /home/claude/belgravian/photos/<ID>-p<N>-<surname>.png (render at 200dpi and crop) for good/fair ones only.
   - **note**: anything else relevant (e.g. "Belgrave did not compete in Match 3", league renamed, league tables).
4. Belgrave names: the magazine usually gives full first names in prose ("Gerry North", "Charlie Walker") and
   initials in result lists. Use the prose to identify initials. Also record full names for nicknames carefully
   (e.g. "Dick" vs "Richard": record exactly what the magazine prints, and note if both forms appear).

## Output
Append one JSON object per line to /home/claude/belgravian/findings/<your-agent-id>.jsonl with fields:
  {"type": "...", "season": "1975/76", "match": 2 or null, "issue": "B191", "page": 14,
   "club": "BEL", "held": "what our data has now (or null)", "found": "what the magazine says",
   "position": int|null, "time": "mm:ss"|null, "evidence": "short verbatim snippet you read on the page image (<=25 words)",
   "confidence": "high|medium|low", "checkedImage": true|false}
Write as you go (don't hold everything until the end). When finished, also write
/home/claude/belgravian/findings/<your-agent-id>-summary.md: issues covered, what each contained on the League,
counts by type, and any problems (unreadable pages, missing issues).
Your final reply should be that summary (short).
