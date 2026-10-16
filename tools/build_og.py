"""Builds the link-preview images and lookup used by _worker.js.
Run from the repo root after adding or changing portraits:  python3 tools/build_og.py"""
import os, re, json, cairosvg
ROOT = os.path.join(os.path.dirname(__file__), '..', 'files')
P = os.path.join(ROOT, 'portraits')
def square(svg):
    # show the site crop (head down past the club band) on a square, widening the background
    svg = svg.replace('viewBox="10 20 180 252"', 'viewBox="-6 20 212 212"', 1)
    return re.sub(r'<rect width="200" height="280"', '<rect x="-40" width="280" height="280"', svg, count=1)
for kind in ('athletes', 'clubs'):
    os.makedirs(os.path.join(P, 'og', kind), exist_ok=True)
    for f in sorted(os.listdir(os.path.join(P, kind))):
        if not f.endswith('.svg'): continue
        svg = open(os.path.join(P, kind, f)).read()
        cairosvg.svg2png(bytestring=square(svg).encode(), write_to=os.path.join(P, 'og', kind, f[:-4] + '.png'), output_width=600, output_height=600)
# superstar lookup, read straight from the add(...) lines in index.html so there is one source of truth
html = open(os.path.join(ROOT, 'index.html')).read()
m = {}
for file, club, names in re.findall(r"add\('([a-z0-9\-]+)','([^']+)',((?:(?:'[^']*'|\"[^\"]*\"),?)+)\)", html):
    for n in [a or b for a, b in re.findall(r"'([^']*)'|\"([^\"]*)\"", names)]:
        m.setdefault(n.lower(), {'file': file, 'club': club})  # first add() for a name is the main portrait; later ones are other-club versions
json.dump(m, open(os.path.join(P, 'portraits.json'), 'w'), separators=(',', ':'))
print(len(m), 'names;', len(os.listdir(os.path.join(P, 'og', 'athletes'))), 'athlete images;', len(os.listdir(os.path.join(P, 'og', 'clubs'))), 'club images')

# cache-busting version for the site's portrait image URLs: a short hash of every portrait file
import hashlib
hsh = hashlib.md5()
for kind in ('athletes', 'clubs'):
    for f in sorted(os.listdir(os.path.join(P, kind))):
        if f.endswith('.svg'): hsh.update(f.encode()); hsh.update(open(os.path.join(P, kind, f), 'rb').read())
v = hsh.hexdigest()[:8]
html = open(os.path.join(ROOT, 'index.html')).read()
html2 = re.sub(r"const PORTRAIT_V='[^']*';", f"const PORTRAIT_V='{v}';", html, count=1)
if html2 != html: open(os.path.join(ROOT, 'index.html'), 'w').write(html2)
print('portrait version', v)

# which portraits are women (for the loading carousel's man/woman alternation), from the results files
from collections import Counter
def names_in(path, key):
    d = json.load(open(os.path.join(ROOT, path))); c = Counter()
    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get(key), str): c[o[key].lower()] += 1
            for k, v in o.items():
                if k in ('athleteAliases', 'nameAliases') and isinstance(v, dict):
                    for a, b in v.items():
                        c[a.lower()] += 1
                        for x in (b if isinstance(b, list) else [b]):
                            if isinstance(x, str): c[x.lower()] += 1
                else: walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(d); return c
men, women = names_in('data.json', 'n'), names_in('data-women.json', 'name')
files = {}
for file, club, names in re.findall(r"add\('([a-z0-9\-]+)','([^']+)',((?:(?:'[^']*'|\"[^\"]*\"),?)+)\)", html):
    ns = [(a or b).lower() for a, b in re.findall(r"'([^']*)'|\"([^\"]*)\"", names)]
    w, mm = sum(women[n] for n in ns), sum(men[n] for n in ns)
    files.setdefault(file, [0, 0]); files[file][0] += w; files[file][1] += mm
wf = sorted(f for f, (w, mm) in files.items() if w > mm)
mf = sorted(f for f, (w, mm) in files.items() if mm >= w and mm > 0)
html = open(os.path.join(ROOT, 'index.html')).read()
line = "const PORTRAIT_WOMEN='" + ','.join(wf) + "';const PORTRAIT_MEN='" + ','.join(mf) + "';"
if 'const PORTRAIT_WOMEN=' in html:
    html2 = re.sub(r"const PORTRAIT_WOMEN='[^']*';const PORTRAIT_MEN='[^']*';", line, html, count=1)
else:
    html2 = html.replace(f"const PORTRAIT_V='{v}';", f"const PORTRAIT_V='{v}';" + line, 1)
if html2 != html: open(os.path.join(ROOT, 'index.html'), 'w').write(html2)
print(len(wf), 'women,', len(mf), 'men portraits;', len(files) - len(wf) - len(mf), 'unplaced')

# results pages: the highest-placed finisher in each race who has a portrait, so the loader can show them when a race link is opened
import json as _json
def _aliases(src):
    out = {}
    for name in ('BUILTIN_ALIASES', 'OVERRIDE_ALIASES'):
        m = re.search(name + r"=\{(.*?)\};", src, re.S)
        if m:
            for a, b in re.findall(r"'((?:[^'\\]|\\.)*)':'((?:[^'\\]|\\.)*)'", m.group(1)):
                out[a.replace("\\'", "'").lower()] = b.replace("\\'", "'")
    return out
html = open(os.path.join(ROOT, 'index.html')).read()
AL = _aliases(html)
PM = {}
for file, club, names in re.findall(r"add\('([a-z0-9\-]+)','([^']+)',((?:(?:'[^']*'|\"[^\"]*\"),?)+)\)", html):
    for n in [a or b for a, b in re.findall(r"'([^']*)'|\"([^\"]*)\"", names)]:
        k = n.lower()
        if k in PM and PM[k][1] != club: PM[k + '@' + club] = (file, club)
        elif k not in PM: PM[k] = (file, club)
def _pfile(name, club):
    for k in dict.fromkeys([name.lower(), AL.get(name.lower(), name).lower()]):
        a = PM.get(k)
        if a and a[1] == club: return a[0]
        b = PM.get(k + '@' + club)
        if b: return b[0]
    return None
tops = {}
for path, pre, nk, ck, pk in (('data.json', 'm', 'n', 'c', 'p'), ('data-women.json', 'w', 'name', 'club', 'pos')):
    for r in _json.load(open(os.path.join(ROOT, path)))['races']:
        code = (r.get('season') or '').replace('/', '')[-4:] + '-' + str(r.get('match'))
        def _pos(x):
            try: return int(str(x.get(pk)).strip())
            except Exception: return 9999
        for x in sorted(r.get('results') or [], key=_pos):
            f = _pfile(x.get(nk) or '', x.get(ck) or '')
            if f: tops[pre + '/' + code] = f; break
_json.dump(tops, open(os.path.join(P, 'race-tops.json'), 'w'), separators=(',', ':'), sort_keys=True)
print(len(tops), 'races with a portrait finisher')

# club GOAT ranks for the link-preview description
import subprocess, sys
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_goat_ranks.py')], check=False)
