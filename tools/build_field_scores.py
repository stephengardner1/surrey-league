"""Build files/field-scores.json from files/field-depth.json.

Gives every Division 1 race in the analysis two scores from 0 to 100,
each the share of same-sex races it beats:
  stacked - quality at the front: average era-adjusted WA points of the best 10,
            the 10th-best runner's points, UK 5K top-100 count, National top-100 count
  deep    - quality through the field: average era-adjusted points of the best 100,
            the 100th-best runner's points, UK 5K top-1,000 count
Run: python3 tools/build_field_scores.py
"""
import json, os, statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, 'files/field-depth.json')))
P = [1300 - i * 10 for i in range(91)]
RT = d['rt']


def kth(c, k):
    """Points of the k-th best finisher (to the nearest 10)."""
    for x, n in zip(P, c):
        if n >= k:
            return x
    return 390


def avg_top(c, k):
    return st.mean(kth(c, j) for j in range(1, k + 1))


def pct(vals):
    s = sorted(v for v in vals if v is not None)
    m = len(s) - 1
    return [None if v is None else (100 * sum(w < v for w in s) + 50 * (sum(w == v for w in s) - 1)) / m for v in vals]


def blend(cols, i):
    v = [c[i] for c in cols if c[i] is not None]
    return sum(v) / len(v)


def place(scores, i):
    return 1 + sum(s > scores[i] for s in scores)


out = {'updated': d.get('updated'), 'races': {}}
for g, div in (('M', 'men'), ('W', 'women')):
    R = [r for r in d['races'] if r['g'] == g]
    # The 2026 National (Sedgefield) had a small field, so it isn't a fair check for 2026/27
    nat = [None if r['s'] == '2026/27' or not r.get('x') else r['x'][1] for r in R]
    S = [pct([avg_top(r['a'], 10) for r in R]), pct([kth(r['a'], 10) for r in R]),
         pct([r['r'][RT.index(100)] for r in R]), pct(nat)]
    D = [pct([avg_top(r['a'], 100) for r in R]), pct([kth(r['a'], 100) for r in R]),
         pct([r['r'][RT.index(1000)] for r in R])]
    sc = [blend(S, i) for i in range(len(R))]
    dc = [blend(D, i) for i in range(len(R))]
    for i, r in enumerate(R):
        out['races'][f"{div}|{r['s']}|{r['m']}"] = {
            'g': g, 'k': r['g'] + r['s'] + '-' + str(r['m']), 'of': len(R), 'n': r['n'],
            'st': round(sc[i]), 'stP': place(sc, i), 'dp': round(dc[i]), 'dpP': place(dc, i),
            'a10': round(avg_top(r['a'], 10)), 'k100': kth(r['a'], 100),
            'uk100': r['r'][RT.index(100)], 'uk1000': r['r'][RT.index(1000)],
            'nat': nat[i], 'p': r.get('p', 0),
            'from': min(x['s'] for x in R),
        }
json.dump(out, open(os.path.join(ROOT, 'files/field-scores.json'), 'w'), separators=(',', ':'))
print(len(out['races']), 'races')
