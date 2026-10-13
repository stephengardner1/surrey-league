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
for file, club, names in re.findall(r"add\('([a-z0-9\-]+)','([^']+)',((?:'[^']*',?)+)\)", html):
    for n in re.findall(r"'([^']*)'", names):
        m[n.lower()] = {'file': file, 'club': club}
json.dump(m, open(os.path.join(P, 'portraits.json'), 'w'), separators=(',', ':'))
print(len(m), 'names;', len(os.listdir(os.path.join(P, 'og', 'athletes'))), 'athlete images;', len(os.listdir(os.path.join(P, 'og', 'clubs'))), 'club images')
