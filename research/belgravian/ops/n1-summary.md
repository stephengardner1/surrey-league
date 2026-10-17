# n1 summary: findings a01–a03 (1962/63 to 1968/69, men only)

**Output:** `/home/claude/belgravian/ops/n1.jsonl`, 344 ops. The generator script is `work/n1/gen.py`.

| Op | Count |
|---|---|
| time | 159 |
| rename | 69 |
| add | 53 |
| racemeta | 31 |
| flag | 14 |
| note | 18 |
| div2 / newrace | 0 |

**Checks:** every rename, time and add was checked against the live data.json and none failed.
- Each rename's held name is at that position and club.
- Each time only fills a missing `t`.
- Each add goes to a free position.

**Other files:** none of these findings touch women's results or Division 2. Per Steve's decision, no div2 ops were emitted.

## Main flags (for Steve)
- **1967/68 Match 3 is a copy of Match 2.** Apart from Thresher in 1st, the held runners in 3rd to 49th repeat Match 2.
  - This match is really Race 4 (Richmond Park, 24 Feb 1968). The flag holds the true result.
  - The data was not restructured. Only the date, finisher count and Thresher's time were set.
- **1967/68 Match 1.** Five Belgrave runners are held under other clubs with garbled names: positions 66, 143, 146, 147 and 155. They are flagged, not renamed, because the club differs.
  - Separately, the held time at 141 (27:03) should read 37:03.
- **Team scores attached to the wrong clubs or copied from another match:**
  - 1964/65 M2 (Surrey and Walton swapped).
  - 1964/65 M4 (Walton should be 506).
  - 1965/66 M2 (HHH 390, Surrey 515).
  - 1965/66 M4 (order of H/W, Croydon, Walton and Surrey).
  - 1968/69 M2 (Mitcham, HHH, Walton and Ranelagh copied from Match 3).
- **1966/67 M1:** Belgrave names at scoring positions 32 to 53 look out of order. This is inferred from time order, so it is flagged only, with no renames and no times at those positions.
- **1966/67 M4:** the magazine has Holt 1st and North 2nd, against our dead heat.
- **1962/63 M4:** Roath and Strange are swapped in 2nd and 3rd.
- **1964/65 M3:** the held Belgrave list mixes actual and scoring positions.
- **1968/69 M1:** many held times are wrong, notably 119 (should be 37:30) and 120 (should be 38:17).
- **1968/69 M4:** Belgrave's ten add up to 129, not 135.

## Position-basis decisions
- **Lists given as actual finishing places** were used for adds:
  - 1963/64 M2 (we held only the winner).
  - 1964/65 M3 Stairs (56th).
  - 1966/67 M3.
  - 1967/68 M1 and M2.
  - 1968/69 M2 to M4.
- **1965/66 M4, Belgrave positions 49 to 71:** added. Our held positions there equal the scoring positions and the H/W team line includes 70, so the basis looks consistent. This is noted.
- **Not added (times only, no overall place)**, listed in notes instead:
  - 1963/64 M1: 40 runners.
  - 1965/66 M1: 40 runners.
  - 1966/67 M1: 27 runners.
- **Caiger's 14th in 1964/65 M4** is a scoring position, so it went in a note rather than an add.

## Skipped and why
- The fullname for Gerry North ("Gerald" in a caption or profile) was skipped. Rule 2 says to use the race-context form.
- "G. Dance" (1966/67 M3, 1967/68 Race 4) was left alone, as it is probably a typo for Bill Dance.
- Bradley (1962/63 M2 20th) was renamed "J Bradley", keeping the initial the list prints. The prose suggests Pat, but that conflicts with the "J".
- 1965/66 M2 73rd: renamed "R Brown" (medium confidence). The list prints "Brown (R)".
- 1964/65 M4 winner: renamed "Bengt Najde", based on a medium-confidence finding without an image check, and Najde is the magazine's spelling. Review this one.
- "Don McLean" appears as "Maclean" everywhere in the magazine. It is renamed only at the two positions a finding covered, and a note suggests an alias for the rest.
- 1969/70 M1 date (25 Oct 1969): this comes only from a fixture list, so it went in a note and no change was made.
- Photo findings are out of scope.
- No 1962/63 to 1963/64 venue changes were made. 1965/66 M4 and 1966/67 M4 venue "Croydon" became "Lloyd Park", which is consistent with the existing venueAliases. 1968/69 M2 was changed the same way.
