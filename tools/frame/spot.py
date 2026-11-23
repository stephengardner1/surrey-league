# Athlete spotlight for the Frame page: poster card on the left, finish stats and race graph on the right.
# Built from the site's own data and code (files/index.html), so it follows the site's rules.
import json, re, math, os, subprocess, collections
from fontTools.ttLib import TTFont
HERE = os.path.dirname(os.path.abspath(__file__))
FILES = os.path.join(HERE, '..', '..', 'files') + '/'
SITE = open(FILES + 'index.html').read()
CARD_H = 219  # spotlight card height; the band adds 36px of padding
DM, DW = FILES + 'data.json', FILES + 'data-women.json'

FONT = TTFont(FILES + 'fonts/CastoroBelgraveTitlingLight-Regular.woff')
CMAP = FONT.getBestCmap(); HMTX = FONT['hmtx']; UPM = FONT['head'].unitsPerEm
def text_w(s, size):
    return sum(HMTX[CMAP[ord(ch)]][0] for ch in s if ord(ch) in CMAP) * size / UPM

import subprocess
def _club_info():
    i = SITE.index('CHART_CLUB_COLORS={'); j = SITE.index('};', i)
    pairs = {k: (a, b) for k, a, b in re.findall(r"'([^']+)':\['(#[0-9a-fA-F]{3,6})','(#[0-9a-fA-F]{3,6})'\]", SITE[i:j])}
    ground = json.loads(re.search(r'PORTRAIT_GROUND=(\{[^}]*\})', SITE).group(1))
    names = dict(re.findall(r"'([A-Z0-9&/]{2,4})':\{name:'([^']*)'", SITE))
    return {'chartpairs': pairs, 'ground': ground, 'names': names}
INFO = _club_info()
PORTRAITS = json.load(open(FILES + 'portraits/portraits.json'))
def _rank():
    # every portrait runner with their individual titles and league titles, counted the way the site counts them
    files = {}
    for k, v in PORTRAITS.items(): files.setdefault(v['file'], (k, v['club']))
    res = []
    for path, women in [(DM, False), (DW, True)]:
        d = json.load(open(path)); sd = d['seasonsData']; latest = sorted(sd)[-1]
        hist = collections.defaultdict(list)
        for r in d['races']:
            for x in r.get('results') or []:
                n = x.get('n') or x.get('name')
                if n: hist[n].append((r['season'], x.get('c') or x.get('club'), bool(x.get('s') or x.get('pts'))))
        for a in d.get('athletes', []):
            for hr in a.get('historicalRaces') or []: hist[a['name']].append((hr['season'], hr['club'], False))
        ind = collections.Counter()
        for se, v in sd.items():
            if se != latest and v.get('individualRankings'): ind[v['individualRankings'][0]['name']] += 1
        for se, ws in (d.get('mitchellCupWinners') or {}).items():
            if se != latest and not sd.get(se, {}).get('individualRankings'):
                for w in ws: ind[w['name']] += 1
        low = {n.lower(): n for n in hist}
        for f, (k, club) in files.items():
            disp = low.get(k)
            if not disp: continue
            seasons = collections.defaultdict(set)
            for se, c, sc in hist[disp]:
                if sc: seasons[se].add(c)
            titles = [se for se, cl in seasons.items() if se != latest and sd.get(se, {}).get('standings') and sd[se]['standings'][0]['club'] in cl]
            res.append((len(titles) + ind[disp], disp, club, f, 'W' if women else 'M', ind[disp], len(titles), len(hist[disp])))
    return sorted(res, reverse=True)
RANK = _rank()
DOGS = {'angus-butler', 'james-hancock', 'john-sanderson', 'penny-oliver'}
def _pick():
    by = {r[3]: r for r in RANK}
    core = ['steve-gardner', 'jack-kavanagh', 'lucy-jones', 'neil-chisholm', 'sam-bramwell']
    dogs = sorted(DOGS)
    men = [r[3] for r in RANK if r[4] == 'M' and (r[5] >= 2 or r[6] >= 7)]
    women = [r[3] for r in RANK if r[4] == 'W' and r[5] + r[6] >= 3]
    order, seen = [], set()
    # interleave so the rotation mixes eras, men and women, and the dogs
    pools = [core, men, women, dogs]
    while any(pools):
        for p in pools:
            while p:
                f = p.pop(0)
                if f not in seen and f in by: seen.add(f); order.append(f); break
    return [(by[f][1], by[f][2], DW if by[f][4] == 'W' else DM, f) for f in order]
SHORTLIST = _pick()
_v = json.loads(subprocess.check_output(['node', os.path.join(HERE, 'vestall.js'), FILES + 'index.html', json.dumps(sorted({c for _, c, _, _ in SHORTLIST}))]))
def chart_colour(club):
    p = INFO['chartpairs'].get(club)
    if p: return p[1] if p[0].lower() in ('#fff', '#ffff00', '#ffd700') else p[0]
    fills = re.findall(r'fill="(#[0-9a-fA-F]{3,6})"', _v.get(club) or '')
    return next((f for f in fills if 1.05 / (L(rgb(f)) + .05) >= 2.2), '#1b649e')
PORT = FILES + 'portraits/athletes/'

def rgb(c):
    c = c.replace('#', '')
    if len(c) == 3: c = ''.join(v + v for v in c)
    n = int(c, 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
def hexc(v): return '#' + ''.join('%02x' % max(0, min(255, round(x))) for x in v)
def L(c):
    f = lambda x: (x / 255) / 12.92 if x / 255 <= 0.03928 else (((x / 255) + 0.055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])
ACCENT = {'BEL': '#BC9F64', 'CRO': '#98A1CA'}
MINBY = {'H/W': 1.5, 'BOX': 1.5, 'STR': 1.5, 'CRO': 1.5}
def poster_ink(bg, vest, club):
    # port of the site's posterInk
    b = rgb(bg); v = rgb(vest) if vest else None
    lum = (0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]) / 255 if v else 1
    if club in ACCENT: base = rgb(ACCENT[club])
    elif v and lum < 0.8: base = [x * 0.55 + v[i] * 0.45 for i, x in enumerate(b)]
    else: base = [x * 0.72 for x in b]
    lb = L(b)
    cr = lambda c: (max(L(c), lb) + .05) / (min(L(c), lb) + .05)
    MIN = MINBY.get(club, 2)
    out = base
    if cr(out) < MIN:
        import colorsys
        h, l0, s = colorsys.rgb_to_hls(*[x / 255 for x in base])
        l = l0
        while l > 0.05 and cr(out) < MIN:
            out = [x * 255 for x in colorsys.hls_to_rgb(h, l, s)]; l -= 0.005
    return hexc(out)

BLINK_CSS='.bk{transform-box:view-box;transform-origin:100px 112.5px;animation:bk 4s .3s infinite}.bc{opacity:0;animation:bc 4s .3s infinite}.pp{animation:pp 4s .3s infinite cubic-bezier(.45,0,.25,1)}@keyframes bk{0%,4.5%,100%{transform:scaleY(1)}1.8%,2.7%{transform:scaleY(0)}}@keyframes bc{0%,1.3%,3.3%,100%{opacity:0}1.8%,2.7%{opacity:1}}@keyframes pp{0%,24%{transform:translateX(0)}31%,68%{transform:translateX(3.6px)}76%,100%{transform:translateX(0)}}'
INTRO_CSS='@keyframes slStick{0%{clip-path:inset(-30% 100% -30% -2%);translate:0 -3px;rotate:-1.2deg}75%{translate:0 0;rotate:0deg}100%{clip-path:inset(-30% -4% -30% -2%);translate:0 0;rotate:0deg}}@keyframes slRise{0%{opacity:0;translate:0 9px}100%{opacity:1;translate:0 0}}@keyframes slFade{0%{opacity:0}100%{opacity:1}}@media (prefers-reduced-motion:reduce){.sl-intro *{animation:none!important}}'
def blinker(t):
    # port of the site's makeBlinker / blinkEyes (with glance)
    t=t.replace('viewBox="10 20 180 252"','viewBox="-15 -8 230 330"')
    t=re.sub(r'<rect width="200" height="280"[^>]*/>','',t,count=1)
    t=re.sub(r'<g (fill="#[0-9A-Fa-f]{6}")><path d="(M[67]\d(?:\.\d+)?,1\d\d(?:\.\d+)? Q)',r'<g class="bk" \1><path d="\2',t,count=1)
    t=re.sub(r'<g clip-path="url\(#ef\)"([^>]*)>((?:(?!</g>).)*)</g>',lambda m:'<g class="bk" clip-path="url(#ef)"'+m.group(1)+'>'+m.group(2).replace('<circle ','<circle class="pp" ')+'</g>',t)
    def lash(m):
        c,lp,rest=m.group(1),m.group(2),m.group(3)
        xl=float(re.match(r'M(\d+(?:\.\d+)?)',lp).group(1)); mr=re.search(r'd="M(\d+(?:\.\d+)?)',rest); xr=float(mr.group(1)) if mr else xl+30
        Lp=lambda x:f'M{x:g},112.5 Q{x+9:g},116.5 {x+18:g},112.5'
        return (f'<g class="bk" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"><path d="{lp}"/>{rest}</g>'
                f'<g class="bc" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"><path d="{Lp(xl)}"/><path d="{Lp(xr)}"/></g>')
    t=re.sub(r'<g fill="none" stroke="(#[0-9A-Fa-f]{6})" stroke-width="1.8" stroke-linecap="round"><path d="(M[67][^"]*)"/>((?:(?!</g>).)*)</g>',lash,t,count=1)
    t=re.sub(r'<(\w+)((?:\s[^<>]*?)?)\s*/>',r'<\1\2></\1>',t)  # explicit closing tags for the template
    return t

def ordinal(n): return '%d%s' % (n, 'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))

def history(name, path):
    d = json.load(open(path)); h = []
    for r in d['races']:
        for x in r.get('results') or []:
            if (x.get('n') or x.get('name')) == name:
                p = x.get('p', x.get('pos'))
                if isinstance(p, int): h.append((r['season'], r['match'], p))
    have = {(se, m) for se, m, _ in h}
    for a in d.get('athletes', []):
        if a['name'] == name:
            for hr in a.get('historicalRaces') or []:
                if isinstance(hr.get('pos'), int) and (hr['season'], hr['match']) not in have: h.append((hr['season'], hr['match'], hr['pos']))
    return sorted(h)

# titles won off the course, confirmed by Steve: team manager for Belgrave's 2025/26 men's title
EXTRA_TITLES = {'Steve Gardner': ['2026']}
def a_scores(name, path):
    d = json.load(open(path)); n = 0
    for r in d['races']:
        for x in r.get('results') or []:
            if (x.get('n') or x.get('name')) == name and (x.get('s') or x.get('pts')): n += 1
    return n

def honours(name, path):
    d = json.load(open(path)); sd = d['seasonsData']; latest = sorted(sd)[-1]
    women = path == DW; seasons = {}
    for r in d['races']:
        for x in r.get('results') or []:
            if (x.get('n') or x.get('name')) == name and (x.get('s') or x.get('pts')):
                seasons.setdefault(r['season'], set()).add(x.get('c') or x.get('club'))
    yr = lambda s: s.split('/')[1]
    titles = sorted(yr(se) for se, cl in seasons.items() if se != latest and sd.get(se, {}).get('standings') and sd[se]['standings'][0]['club'] in cl)
    ind = sorted(yr(se) for se, v in sd.items() if se != latest and v.get('individualRankings') and v['individualRankings'][0]['name'] == name)
    ind = sorted(set(ind) | {yr(se) for se, ws in (d.get('mitchellCupWinners') or {}).items() if se != latest and not sd.get(se, {}).get('individualRankings') and any(w['name'] == name for w in ws)})
    titles = sorted(set(titles) | set(EXTRA_TITLES.get(name, [])))
    out = []
    if ind: out.append(('Individual champion' if women else 'Mitchell Cup', '\U0001F3C5', ind))
    if titles: out.append(('League Winner', 'TROPHY', titles))
    return out

def light_skin(svg):
    """True when the portrait's face colour (its most used warm fill) is light."""
    import collections, colorsys
    best = None
    for h, k in collections.Counter(re.findall(r'fill="(#[0-9A-Fa-f]{6})"', svg)).most_common():
        r, g, b = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]
        H, Lh, S = colorsys.rgb_to_hls(r, g, b)
        if r > g > b and H < 0.12 and S > 0.12 and 0.15 < Lh < 0.92: best = (r, g, b); break
    return bool(best) and L([x * 255 for x in best]) > 0.3

def dark_ground(col, club):
    """The club's kit colour (or its portrait ground, if the kit has no hue), dark and greyed down."""
    import colorsys
    for c in (INFO['chartpairs'].get(club) or ())[:1] + (col,):
        H, _, S = colorsys.rgb_to_hls(*[x / 255 for x in rgb(c)])
        if S > 0.15: break
    return hexc([x * 255 for x in colorsys.hls_to_rgb(H, 0.25, 0.2)])

def spotlight(name, club, path, file, ctx):
    u, N, SANS, MONO, DISP, INK, INK2, MUT, RULE, G100, TROPHY = ctx
    dog = file in DOGS
    svg = open(PORT + file + ('-dog' if dog else '') + '.svg').read()
    bg = re.search(r'<rect width="200" height="280" fill="(#[0-9A-Fa-f]{3,6})"', svg).group(1)
    vest = re.search(r'<path d="M53,330[^"]*" fill="(#[0-9A-Fa-f]{6})"', svg)
    ink = poster_ink(bg, vest.group(1) if vest else None, club)
    h = history(name, path); pos = [p for _, _, p in h]
    races, wins = len(pos), sum(p == 1 for p in pos)
    top3, top10, best = sum(p <= 3 for p in pos), sum(p <= 10 for p in pos), min(pos)
    seasons = sorted(set(s for s, _, _ in h))
    # poster card, scaled from the site's 150px card
    W = 240; s = 180 / 150; H = CARD_H
    sur = name.split(' ')[-1].upper()
    fs = min(52, 40 * (150 - 14) / text_w(sur, 40))
    c = 7 * math.sqrt(2) * s
    back = hexc([x / 2 + 127.5 for x in rgb(bg)])
    def ink_for(col, bgc, mn):
        cc = rgb(col); lb = L(rgb(bgc)); i = 0
        while i < 40 and (lb + .05) / (L(cc) + .05) < mn: cc = [x * 0.92 for x in cc]; i += 1
        return hexc(cc)
    pill_ink = ink_for(ink, '#FFFFFF', 4.5)
    PF = 10.5  # pill text, scaled up from the site's 5.4px so it reads on the Frame
    pills = ''
    for l, e, ys in honours(name, path):
        yrs = ' '.join('\u2019' + y[-2:] for y in ys)
        full = f'{l} X {yrs}'
        tally = len(full) * PF * 0.74 + PF * 1.6 > W - 7 * s - 6 * s
        mark = (f'<img src="{TROPHY}" alt="" style="display: inline-block; height: 1.25em; width: auto; vertical-align: -0.25em; margin: 0 0.05em">'
                if e == 'TROPHY' else e)
        pills += (f'<span style="background: rgba(255,255,255,.94); border-radius: 99px; padding: {PF*0.48+PF*.06:.1f}px {PF*0.78:.1f}px {PF*0.48-PF*.06:.1f}px; '
                  f'display: inline-flex; align-items: center; font-family: {SANS}; font-weight: 700; font-size: {PF}px; line-height: 1; letter-spacing: .03em; '
                  f'text-transform: uppercase; white-space: pre; color: {pill_ink}">{(str(len(ys)) + chr(215) + ' ' + l + ' ' + mark) if tally else (l + ' ' + mark + ' ' + yrs)}</span>')
    pillbox = (f'<div style="position: absolute; left: {7*s:.1f}px; right: {6*s:.1f}px; bottom: {7*s:.1f}px; z-index: 2; display: flex; flex-wrap: wrap-reverse; '
               f'gap: {3*s:.1f}px; animation: slFade .45s ease-out .85s both">{pills}</div>') if pills else ''
    art = blinker(svg).replace('<svg ', f'<svg width="{W}" height="{W*330/230:.1f}" aria-hidden="true" style="display: block" ', 1)
    # every card's drawing sits in the same page, so give its ids a prefix of its own (clip paths would otherwise clash)
    pre = re.sub(r'[^a-z0-9]', '', file) + '-'
    ids = set(re.findall(r'id="([^"]+)"', art))
    for i in ids:
        art = art.replace(f'id="{i}"', f'id="{pre}{i}"').replace(f'url(#{i})', f'url(#{pre}{i})').replace(f'href="#{i}"', f'href="#{pre}{i}"')
    card = (f'<div class="sl-intro{" dogcard" if dog else ""}" style="position: relative; width: {W}px; height: {H}px; flex-shrink: 0">'
            f'<div style="position: absolute; inset: 0; border-radius: {12*s:.0f}px; overflow: hidden; background: {bg}; '
            f'clip-path: polygon(0 0, 100% 0, 100% {H-c:.1f}px, {W-c:.1f}px 100%, 0 100%)">'
            f'<div role="img" aria-label="Portrait of {name}" style="position: absolute; left: 0; top: -36px; width: {W}px; animation: slRise .6s cubic-bezier(.2,.8,.3,1) .5s both">{art}</div>'
            f'{pillbox}</div>'
            f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true" style="position: absolute; left: 0; top: 0">'
            f'<polygon points="{W-c:.1f},{H} {W},{H-c:.1f} {W-c:.1f},{H-c:.1f}" fill="{back}" stroke="{back}" stroke-width="1.5" stroke-linejoin="round"></polygon></svg></div>')
    # stats, in the order of the site's athlete stats
    stats = [(races, 'Races'), (wins, 'Wins'), (top3, 'Top 3'), (top10, 'Top 10'), (ordinal(best), 'Best')]
    stats = [(v, l) for v, l in stats if v != 0]  # leave out a count with nothing in it
    if len(stats) < 5:  # a thin row: add how often they scored for the A team (the site's "A Scores")
        a = a_scores(name, path)
        if a: stats.insert(1, (a, 'Scores'))
    st = ''.join(f'<div style="width: 78px; display: flex; flex-direction: column; align-items: center; gap: 4px; white-space: nowrap; animation: slFade .3s ease-out {.55+.13*k:.2f}s both">'
                 f'<div style="font-family: {DISP}; font-weight: 600; font-size: 32px; line-height: 34px; color: {INK}">{v}</div>'
                 f'<div style="font-family: {SANS}; font-size: 14px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: {MUT}">{l}</div></div>'
                 for k, (v, l) in enumerate(stats))
    # race graph: earliest left; y runs from best (top) to worst (bottom), as on the site
    GW, GH, pad = 716, 90, 9
    ptop = 36  # headroom for the best-finish label
    mn, mx = min(pos), max(pos)
    gx = lambda i: pad + (i / max(len(pos) - 1, 1)) * (GW - 2 * pad)
    gy = lambda p: ptop + ((p - mn) / ((mx - mn) or 1)) * (GH - ptop - pad)
    line = chart_colour(club)
    marks = ''
    for i, p in enumerate(pos):
        x, y = gx(i), gy(p)
        if p == best:
            pts = []
            for j in range(5):
                a = math.radians(j * 72 - 90); b = math.radians(j * 72 + 36 - 90)
                pts += [f'{x+7*math.cos(a):.1f},{y+7*math.sin(a):.1f}', f'{x+2.8*math.cos(b):.1f},{y+2.8*math.sin(b):.1f}']
            marks += f'<polygon points="{" ".join(pts)}" fill="#f59e0b" stroke="#d97706" stroke-width="1"></polygon>'
        else:
            marks += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{line}"></circle>'
    i0 = pos.index(best); x0, y0 = gx(i0), gy(best)
    lab = ordinal(best); lw = len(lab) * 9.5 + 14; lh = 22
    # the best finish is always the top of the scale, so the label goes above it, clear of the line
    lx = max(0, min(GW - lw, x0 - lw / 2))
    ly = y0 - 10 - lh
    marks += (f'<rect x="{lx:.1f}" y="{ly:.1f}" width="{lw:.1f}" height="{lh}" rx="4" fill="#1f2937"></rect>'
              f'<text x="{lx+lw/2:.1f}" y="{ly+15.5:.1f}" text-anchor="middle" fill="#ffffff" style="font-family: {SANS}; font-size: 15px; font-weight: 600">{lab}</text>')
    poly = ' '.join(f'{gx(i):.1f},{gy(p):.1f}' for i, p in enumerate(pos))
    graph = (f'<svg width="{GW}" height="{GH}" viewBox="0 0 {GW} {GH}" role="img" aria-label="Finishing position in each race" style="display: block">'
             f'<polyline points="{poly}" fill="none" stroke="{line}" stroke-width="2" stroke-linejoin="round"></polyline>{marks}</svg>')
    span = seasons[0] if len(seasons) == 1 else f'{seasons[0]} to {seasons[-1]}'
    axis = (f'<div style="display: flex; justify-content: space-between; font-family: {SANS}; font-size: 17px; color: {MUT}">'
            f'<div>{seasons[0]}</div><div>{seasons[-1]}</div></div>') if len(seasons) > 1 else ''
    avail = 716 - 16 - 78 * len(stats)
    nfs = min(32, 32 * avail / max(text_w(name.upper(), 32), 1))
    right = (f'<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 10px">'
             f'<div style="display: flex; align-items: flex-start; gap: 16px">'
             f'<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 8px">'
             ''
             f'<div style="font-family: {DISP}; font-weight: 300; font-size: {nfs:.1f}px; line-height: 40px; text-transform: uppercase; letter-spacing: -0.01em; color: {INK}; white-space: nowrap">{name}</div>'
             f'<div style="display: flex; align-items: center; gap: 8px; font-family: {SANS}; font-size: 18px; color: {INK2}; white-space: nowrap">'
             f'{INFO["names"].get(club, club).replace("&", "&amp;")}</div></div>'
             f'<div style="display: flex">{st}</div></div>'
             f'<div style="border-top: 1px solid {G100}; padding-top: 8px; display: flex; flex-direction: column; gap: 2px">{graph}{axis}</div></div>')
    print('spotlight', name, club, bg, ink, races, wins, top3, top10, best, seasons[0], seasons[-1], 'fs', round(fs, 1))
    G = INFO['ground'].get(club, '#E6EAE4')
    tint = hexc([x / 2 + 127.5 for x in rgb(G)])
    return f'<div style="margin: 0 -48px; padding: 18px 48px; background: {tint}; display: flex; gap: 28px; height: {H}px">{card}{right}</div>'

DOG_CSS = '.dog{transform:translateY(107.5px);animation:dog 4s .3s infinite}@keyframes dog{0%,72%{transform:translateY(107.5px);animation-timing-function:cubic-bezier(.2,1.6,.4,1)}78%,90%{transform:translateY(35.5px);animation-timing-function:cubic-bezier(.6,0,.9,.5)}95%,100%{transform:translateY(107.5px)}}.dogcard .pp{transform-box:view-box;animation:roll 4s .3s infinite}@keyframes roll{0%,79%,93%,100%{transform:translate(0,0)}80.5%{transform:translate(-1.6px,-2.4px)}82%,89.5%{transform:translate(0,-3.6px)}91%{transform:translate(1.4px,-2.2px)}}@media (prefers-reduced-motion:reduce){.dog,.dogcard .pp{animation:none}}'
def build(ctx):
    return ''.join(f'<div class="spot" data-spot="{i}" style="display: none">{spotlight(n, c, p, f, ctx)}</div>'
                   for i, (n, c, p, f) in enumerate(SHORTLIST))
