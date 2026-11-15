#!/usr/bin/env python3
"""Keep race-photo captions in step with official result corrections.

Finishing places in captions are written as {pos:Name|fallback} and filled in
live by the site, so a correction that moves runners up or down needs nothing here.

This script handles the other kind of correction: a bib number given to the wrong
person. Each photo records who wore which visible bib (bibs:{328:'Molly Smith'}).
After a correction has been applied to the data files and the official snapshot,
run it for that race. For every recorded bib it looks up the bib's official
finishing place, takes the runner now at that place in our data (which already has
Steve's name corrections), and if that is a different person it swaps the old name
for the new one in that photo's caption, place tokens, links and bib record.

Usage:
  python3 tools/sync_photo_captions.py --division men --season 2026/27 --match 2 \
      --feed tools/official-snapshots/match196-senior-men.json [--dry-run]

Prints one line per change, and warnings for anything that needs a human eye
(a bib no longer in the results, or a name swap where the club wording in the
caption may now be wrong). Prints nothing when every caption is still right.
"""
import argparse, json, re, sys

INDEX = 'files/index.html'


def slug(n):
    return re.sub(r'[^a-z0-9-]', '', re.sub(r'\s+', '-', (n or '').lower()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--division', choices=['men', 'women'], required=True)
    ap.add_argument('--season', required=True)
    ap.add_argument('--match', type=int, required=True)
    ap.add_argument('--feed', required=True, help='official feed entry for the race (snapshot file)')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    data = json.load(open('files/data-women.json' if a.division == 'women' else 'files/data.json'))
    race = next((r for r in data['races'] if r['season'] == a.season and r['match'] == a.match), None)
    if not race:
        sys.exit(f'No {a.division} race {a.season} match {a.match} in the data')
    by_pos = {(x.get('p') or x.get('pos')): (x.get('n') or x.get('name')) for x in race['results']}
    feed = json.load(open(a.feed))
    bib_rank = {str(p['bib']): p['rank'] for p in feed.get('positions', []) if p.get('bib') is not None}
    same = {}  # alias slug -> canonical slug, so Steve's spellings count as the same person
    for canon, al in (data.get('athleteAliases') or {}).items():
        for x in al + [canon]:
            same[slug(x)] = slug(canon)

    def person(n):
        return same.get(slug(n), slug(n))

    s = open(INDEX, encoding='utf-8').read()
    key = ("w|" if a.division == 'women' else '') + f"{a.season}|{a.match}"
    start = s.find(f"  '{key}':[")
    if start < 0:
        return  # no photos for this race
    end = s.find("\n  '", start + 1)
    block = s[start:end]
    new_block = block
    changes, warnings = [], []
    for obj in re.findall(r"\{src:'photos/races/[^']+'.*?bibs:\{[^}]*\}[^{]*?\}", block, re.S):
        src = re.search(r"src:'([^']+)'", obj).group(1)
        bibs = dict(re.findall(r"(\d+):'((?:[^'\\]|\\.)*)'", re.search(r"bibs:\{([^}]*)\}", obj).group(1)))
        o = obj
        for bib, old in bibs.items():
            rank = bib_rank.get(bib)
            if rank is None:
                warnings.append(f"{src}: bib {bib} ({old}) is no longer in the official results - check the caption by hand")
                continue
            new = by_pos.get(rank)
            if not new or new == 'Unknown' or person(new) == person(old):
                continue
            o = o.replace(old, new)
            old_last, new_last = old.split()[-1], new.split()[-1]
            if old_last != new_last:  # surname-only mentions, e.g. "Jones finished ..."
                o = re.sub(r"(?<![A-Za-z'\-])" + re.escape(old_last) + r"(?![A-Za-z\-])", new_last, o)
            changes.append(f"{src}: bib {bib} is now {new} (was {old})")
            warnings.append(f"{src}: check the club wording around {new}'s name is still right")
        new_block = new_block.replace(obj, o)
    for c in changes:
        print('CHANGED', c)
    for w in warnings:
        print('CHECK', w)
    if changes and not a.dry_run:
        open(INDEX, 'w', encoding='utf-8').write(s[:start] + new_block + s[end:])


if __name__ == '__main__':
    main()
