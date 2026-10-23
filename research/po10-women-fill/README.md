# Women's Division 1 gaps filled from Power of 10 (23 October 2026)

Seven women's races where the archive held only part of the results:
2010/11 M1 (Richmond Park) and M3 (Ham Lands), 2011/12 M2 (Richmond Park), 2012/13 M1 (Putney Vale) and M3 (Mitcham),
2013/14 M2 (Coulsdon) and M3 (Wimbledon Common).

Power of 10 has each race only as combined Division 1 and 2 results. A finisher was added as Division 1 when
they ran for a Division 1 club in another race that season, or Power of 10 lists their first- or second-claim club
as one of that season's Division 1 clubs (Steve's rule). Runners with no club on Power of 10 were left out.

- Existing archive entries, team scores and standings were not changed.
- Names use the archive's own form where the same Power of 10 athlete appears in other archive races.
- Positions are exact where the added runners exactly fill the gap between two known archive positions;
  otherwise they carry `posEst: true` and show as ≈ on the site. Added entries carry `src: "po10"`.
- Times for 2010/11 M1 are left blank: Power of 10 rounds them up to the whole minute.
- Where a stretch had more runners than places, the weakest-evidence runner was left out (see merge.py output).

Files: `r*.txt` are the Power of 10 rows per race (race index|Div 1 position|overall position|name|club|time|basis|archive position),
`fill.txt` the final selection with archive names, `merge.py` the script that wrote them into `files/data-women.json`.
