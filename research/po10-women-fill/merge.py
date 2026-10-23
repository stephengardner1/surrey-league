"""Fill gaps in seven women's Division 1 races (2010/11 to 2013/14) from Power of 10.

Power of 10 has these races only as combined Division 1 and 2 results. A finisher is
treated as Division 1 when: they are already in the archive for the race; or they ran for
a Division 1 club in another race that season; or Power of 10 lists their first- or
second-claim club as one of that season's Division 1 clubs (Steve's rule, 23 Oct 2026).
Existing archive entries, team scores and standings are never changed.
Positions are exact where the runners between two known archive positions fill the gap
exactly; otherwise they are marked posEst (best estimate, a few Division 1 runners missing).
Usage: python3 merge.py <rev-dir> [--write]
"""
import json, sys, os, unicodedata, re
REV = sys.argv[1]; WRITE = '--write' in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'files/data-women.json')
RACES = [('2010/11',1),('2010/11',3),('2011/12',2),('2012/13',1),('2012/13',3),('2013/14',2),('2013/14',3)]
ROUNDED = {0}  # Power of 10 times for 2010/11 match 1 are rounded up to whole minutes
po = {i:{} for i in range(7)}
for f in ['r0.txt','r2.txt','r3.txt','r4.txt','r5.txt','r6.txt']:
    for l in open(os.path.join(REV,f)).read().rstrip('\n').split('\n'):
        p = l.split('|')
        if p[1] == 'U': continue
        po[int(p[0])][int(p[2])] = dict(name=re.sub(r'\s+',' ',p[3]).strip(), time=p[5].strip())
fill = {i:[] for i in range(7)}
for l in open(os.path.join(REV,'fill.txt')).read().rstrip('\n').split('\n'):
    i,cp,arch,b,club,nm = l.split('|')
    fill[int(i)].append(dict(cp=int(cp), arch=int(arch) if arch else None, basis=b, club=club, name=nm or None))
def norm(n): return unicodedata.normalize('NFKD',n).encode('ascii','ignore').decode().lower().replace('.','').strip()
def isbad(n): return not n or re.match(r'^(unknown|anonymous|an other)\b', n.lower())
d = json.load(open(P)); report = []
for i,(s,m) in enumerate(RACES):
    race = next(r for r in d['races'] if r['season']==s and r['match']==m)
    res = race['results']; held = {norm(x['name']):x for x in res}
    used = set(); occupied = {x['pos'] for x in res if isinstance(x.get('pos'),int)}
    rows = sorted(fill[i], key=lambda x:x['cp'])
    anchors = []  # (cp, pos)
    new = []
    for r in rows:
        if r['basis']=='A':
            if r['arch']: anchors.append((r['cp'], r['arch']))
            continue
        nm = r['name'] if r['name'] and not isbad(r['name']) else po[i][r['cp']]['name']
        if isbad(nm): continue
        h = held.get(norm(nm))
        if h is not None:  # already held under this name (e.g. matched by archive name): use as anchor
            if isinstance(h.get('pos'),int) and h['pos']>0: anchors.append((r['cp'], h['pos']))
            continue
        new.append(dict(cp=r['cp'], basis=r['basis'], name=nm, club=r['club'], time='' if i in ROUNDED else po[i][r['cp']]['time']))
    anchors.sort()
    fin = race.get('finishers')
    exact = est = 0
    # segments between anchors (plus open tail)
    bounds = anchors + [(10**6, (fin+1) if fin else None)]
    prev = (0, 0)
    for cp_b, pos_b in bounds:
        seg = [x for x in new if prev[0] < x['cp'] < cp_b]
        hi = pos_b if pos_b else prev[1] + len(seg) + 1 + 10**4
        avail = [p for p in range(prev[1]+1, hi) if p not in occupied]
        ok = pos_b is not None and len(avail) == len(seg)
        if pos_b is not None and len(seg) > len(avail):
            # too many runners for the places: drop the weakest evidence (club match only) first, from the back
            extra = len(seg) - len(avail)
            for x in sorted(seg, key=lambda x:(x['basis']=='S', -x['cp'])):
                if extra == 0: break
                x['drop'] = True; extra -= 1
            report.append(f'{s} m{m}: before {pos_b}, left out ' + ', '.join(x['name'] for x in seg if x.get('drop')))
            seg = [x for x in seg if not x.get('drop')]
            ok = False
        for k,x in enumerate(seg):
            x['pos'] = avail[k] if k < len(avail) else None
            x['est'] = not ok
        prev = (cp_b, pos_b if pos_b else prev[1])
    add = [x for x in new if x.get('pos') and not x.get('drop')]
    for x in add:
        e = {'pos':x['pos'],'name':x['name'],'club':x['club']}
        if x['time']: e['time'] = x['time']
        if x['est']: e['posEst'] = True
        e['src'] = 'po10'
        res.append(e); occupied.add(x['pos'])
        exact += not x['est']; est += x['est']
    res.sort(key=lambda x:(x['pos'] if isinstance(x.get('pos'),int) else 9999))
    if add:
        race['po10Fill'] = {'added': len(add), 'exact': exact, 'source': 'Power of 10 combined Division 1 and 2 results; Division 1 runners picked by club'}
    report.append(f'{s} m{m}: held {len(res)-len(add)}, added {len(add)} ({exact} exact positions, {est} estimated), finishers {fin}, now {len(res)}, dropped {len(new)-len(add)}')
print('\n'.join(report))
if WRITE: open(P,'w').write(json.dumps(d,ensure_ascii=False,separators=(',',':'))); print('written')
