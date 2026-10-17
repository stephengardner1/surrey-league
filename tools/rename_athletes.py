"""Apply Steve's approved athlete name changes, logged in tools/name_changes.json.

Each entry: {"sex": "men"|"women", "club": "BEL", "from": ["P Buckley"], "to": "Padraic Buckley",
             "seasons": ["1986/87","1999/00"] or null, "evidence": "...", "approved": "..."}
Optional "races": [["1997/98", 1, 56], ...] limits a change to those exact results (season, match, position),
for when two real people share one raw name in a season.

Renames the raw result names (club-scoped, optionally season-scoped) AND the stored summary
sections (seasonsData, achievements, athletes ...). Positions, times and scores are untouched.
Safe to re-run: names already changed are simply not found again.

Usage:  python3 tools/rename_athletes.py --dry     (report only)
        python3 tools/rename_athletes.py           (write)   then: python3 tools/build_og.py
"""
import json, re, sys, collections, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FILES = {'men': 'files/data.json', 'women': 'files/data-women.json'}
DRY = '--dry' in sys.argv
LOG = json.load(open(os.path.join(ROOT, 'tools/name_changes.json')))


def in_range(rng, season, span=None):
    if not rng:
        return True
    if season:
        return rng[0] <= season <= rng[1]
    if span:  # achievements carry "1990/91-1994/95" style spans
        a, b = (span.split('-') + [span])[:2]
        if len(b) < 7:
            b = a
        return not (b < rng[0] or a > rng[1])
    return False


def race_ok(r, season, match, pos):
    """Entries with "races": [[season, match, pos], ...] rename only those exact results (and the
    race winner line when pos is 1). Used when two real people share a raw name in one season."""
    if not r.get('races'):
        return True
    return match is not None and pos is not None and [season, match, str(pos)] in [[a, b, str(c)] for a, b, c in r['races']]


def walk(o, rows, hits, season=None, match=None):
    if isinstance(o, dict):
        if isinstance(o.get('season'), str):
            season = o['season']
        if isinstance(o.get('match'), int) and 'results' in o:
            match = o['match']
        for nk, ck in (('n', 'c'), ('name', 'club'), ('winner', 'winnerClub')):
            if nk in o and ck in o:
                pos = 1 if nk == 'winner' else o.get('p', o.get('pos'))
                for r in rows:
                    if o[ck] == r['club'] and o[nk] in r['from'] and in_range(r['seasons'], season, o.get('span')) \
                            and race_ok(r, season, match, pos):
                        hits[(r['club'], o[nk], r['to'])] += 1
                        if not DRY:
                            o[nk] = r['to']
                        break
        for k, v in o.items():
            walk(v, rows, hits, k if re.fullmatch(r'\d{4}/\d{2}', k) else season, match)
    elif isinstance(o, list):
        for v in o:
            walk(v, rows, hits, season, match)


for sex, fn in FILES.items():
    path = os.path.join(ROOT, fn)
    raw = open(path).read()
    d = json.loads(raw)
    assert json.dumps(d, separators=(',', ':'), ensure_ascii=False) == raw, fn + ' would not round-trip'
    hits = collections.Counter()
    walk(d, [r for r in LOG if r['sex'] == sex], hits)
    print(fn, sum(hits.values()), 'names changed' + (' (dry run)' if DRY else ''))
    for (club, old, new), n in hits.most_common():
        print(f'   {club:5} {old} -> {new}  x{n}')
    if not DRY and hits:
        open(path, 'w').write(json.dumps(d, separators=(',', ':'), ensure_ascii=False))
