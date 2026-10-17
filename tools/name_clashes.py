"""Find suspect first names in pre-2013/14 men's results (the photo-transcribed era).

Older AI transcription sometimes turned an initial ("M Sharp") into an invented first name
("Maurice Sharp"). This lists club + surname + initial groups where two or more first names
appear that are NOT simple nickname pairs (Andy/Andrew), with how often each form appears.
A rare full name beside a common initial is the classic sign of an invented name.

Usage: python3 tools/name_clashes.py [--all] [--club BEL] [--surname Sharp]
"""
import json, re, sys, collections, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NICK = [s.split() for s in """andy andrew drew|dave david|mike michael mick micky mickey|matt matthew|steve stephen steven
will william bill billy|jim james jimmy jamie|john jon jonathan johnny jack|phil philip phillip|pete peter
rob robert bob bobby robbie|rich richard dick rick ricky|tom thomas tommy|tony anthony|chris christopher
nick nicholas nic|al alan allan alastair alistair alaster alasdair alister|glen glenn|ian iain|ken kenneth kenny
tim timothy|dan daniel danny|sam samuel|ben benjamin|joe joseph|ed edward eddie ted|charlie charles|fred frederick
ron ronald|don donald|jeff geoff geoffrey jeffrey|gerry gerald gerard|les leslie|ray raymond|terry terence
pat patrick paddy padraic|greg gregory|alex alexander sandy|stu stuart stewart|nat nathan nathaniel|josh joshua
olly oli oliver ollie|harry henry|mark marc|doug douglas|vic victor|reg reginald|len leonard|bert albert herbert
norm norman|graham graeme|jez jeremy|si simon|gary garry gaz|kev kevin|ade adrian|col colin|barry baz
del derek|stan stanley|fran francis frank|mo marcus""".replace('\n', '|').split('|')]


def same(a, b):
    a, b = a.lower(), b.lower()
    return a == b or any(a in s and b in s for s in NICK)


args = sys.argv[1:]
opt = lambda k: args[args.index(k) + 1].lower() if k in args else None
club_f, sur_f = opt('--club'), opt('--surname')
d = json.load(open(os.path.join(ROOT, 'files/data.json')))
G = collections.defaultdict(lambda: collections.defaultdict(list))
for r in d['races']:
    if r['season'] >= '2013/14':
        continue  # surreyleague.org results are authoritative from 2013/14
    for x in r['results'] or []:
        p = re.sub(r'\s*\(\d\)$', '', x['n'].strip()).split()
        if len(p) < 2:
            continue
        G[(x['c'], p[-1], p[0][0].upper())][p[0].strip('.')].append(f"{r['season']} m{r['match']}")

rows = []
for (club, sur, ini), forms in G.items():
    if club_f and club.lower() != club_f or sur_f and sur.lower() != sur_f:
        continue
    groups = []
    for f in (f for f in forms if len(f) > 1):
        for g in groups:
            if same(g[0], f):
                g.append(f); break
        else:
            groups.append([f])
    if len(groups) >= 2 or '--all' in args:
        rows.append((sum(map(len, forms.values())), club, sur, ini, forms))
rows.sort(reverse=True)
print(len(rows), 'groups to look at\n')
for total, club, sur, ini, forms in rows:
    print(f'{club} {sur} ({ini}.)  ' + ',  '.join(
        f'{f} x{len(v)} [{v[0].split()[0]}–{v[-1].split()[0]}]' for f, v in sorted(forms.items(), key=lambda kv: -len(kv[1]))))
