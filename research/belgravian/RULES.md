# Turning Belgravian findings into a change list — rules (from Steve)

You convert free-text findings into precise, machine-applicable operations against the LIVE data:
- Men:   /home/claude/surrey-league/files/data.json        races[] {season, match, date, venue, finishers, teamScores, ...,
         results[] {p=position, s=scoring pts, n=name, c=club code, t=time, x/b/guest/... other flags}}
- Women: /home/claude/surrey-league/files/data-women.json  races[] {season, match, date, venue, finishers, ...,
         results[] {pos, name, club, time, pts, scoringPos, ...}}
Read the data with python (`python3 -I`), never edit it. Findings: /home/claude/belgravian/findings/*.jsonl (fields: type, season,
match, issue, page, club, held, found, position, time, evidence, confidence, checkedImage). Page images can be re-checked:
`pdftoppm -r 130 -f N -l N -png /home/claude/belgravian/pdf/<ISSUE>.pdf <your work dir>/x` then Read the PNG.

## Steve's rules (non-negotiable)
1. **Never change league standings**: team scores, team positions, season tables/totals, champions, promotion/relegation,
   and the finishing POSITIONS (p / pos) and scoring points (s / pts) of results we already hold. These come from the
   canonical printed League records. Disagreements go to `flag` ops (only MAJOR ones — e.g. a whole match duplicated, scores
   attached to the wrong clubs, a run of positions shifted by one, a held name being a completely different person;
   skip trivial ±1 / printing-scale differences).
2. **Names: trust The Belgravian over our data.** Our historical names were machine-read from photos of handwritten results,
   so garbles are common. Apply: initials → full first name; misspellings; a garbled name at a held position replaced by
   the name the magazine prints at that same position for the same club (e.g. held "D Hampshire" → magazine "D. Mainstone").
   Keep the magazine's own form of the first name (Gerry not Gerald unless that's what's printed in race context). If the
   magazine only gives initial+surname, fix the surname but keep the initial. Don't apply low-confidence identifications;
   medium only if the evidence clearly links initial+surname+club+era (e.g. a team list with the full name in that season).
3. **Add missing detail that makes sense**: times for held results (only where t is missing — if a held time differs,
   that's a flag only if major); exact dates (as "27th October 1962" style, matching existing full-date strings);
   venue only where held venue is vague/abbreviated and the magazine is specific and consistent — otherwise flag;
   finisher counts where held is null/0; extra finishers at positions we DON'T hold (Belgrave non-scorers etc.), only if the
   magazine gives an actual overall finishing position. Results with times but no overall position: do NOT add (list them
   in a `note` op instead).
4. Women's results: add Belgrave women's results at positions the women's file doesn't already hold for that match; if the
   match itself doesn't exist in the women's file, don't invent a race — emit `newrace` (see below) for Steve to decide.
5. Division II (or other non-Division-1) races: do NOT merge into the Division 1 races. Emit them as `div2` ops grouped
   per race (all fields), for Steve to decide whether the site should hold a second division.
6. Matches where the held data is entirely missing beyond a winner (e.g. 1973/74, 1977/78 Div1 if any, 1976/77 M2/M3,
   1974/75 M1/M2/M4, 1975/76 M4, 1978/79 M4): ADD results the magazine gives with overall positions (rule 3), plus date,
   finishers. Do not touch team scores/standings even if they're missing — put magazine team scores in a `note`.
7. Every op carries source: {"issue","page","evidence"} copied from the finding(s) it comes from.

## Output: one JSON object per line to /home/claude/belgravian/ops/<your-id>.jsonl
{"op":"rename",  "file":"men|women","season","match","pos":int,"club","from":"held name exactly","to":"new name","why":"initials→full|misread|spelling","confidence","source":{...}}
{"op":"time",    "file","season","match","pos","name":"held name","time":"mm:ss","source"}
{"op":"add",     "file","season","match","pos","name","club","time":null|"mm:ss","source"}        # only positions not held
{"op":"racemeta","file","season","match","field":"date|venue|finishers","from":held,"to":new,"source"}
{"op":"flag",    "file","season","match","what":"short plain-English description of the major discrepancy","held","magazine","source"}
{"op":"div2",    "file","season","match","division":"II","date","venue","winner","finishers","results":[{pos,name,club,time}],"teamScores":[...],"source"}
{"op":"newrace", "file","season","match","date","venue","results":[...],"source"}
{"op":"note",    "season","match","text","source"}
Validate each rename/time/add against the live data before writing it (held name must exist at that pos+club; add pos must be free).
If two findings conflict, prefer the one with checkedImage and higher confidence; if still unclear, emit a flag not a rename.
Finish with /home/claude/belgravian/ops/<your-id>-summary.md (counts per op, anything you skipped and why) and a short reply.
