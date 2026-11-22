# Builds files/frame/index.html: the Surrey League page for the kitchen Frame (1080x1920 portrait).
# Run: python3 tools/frame/build.py   (needs Node and fontTools). Rebuilt by the "Frame page" workflow when results change.
import json, collections, datetime, re, os, html as H
import spot
FILES = spot.FILES; OUT = FILES + 'frame/'
S = FILES
src = spot.SITE
esc = lambda t: H.escape(str(t), quote=True)
os.makedirs(OUT + 'vests', exist_ok=True); os.makedirs(OUT + 'busts', exist_ok=True)
SEASON = sorted(json.load(open(S + 'data.json'))['seasonsData'])[-1]
N = {k: v.replace('&', '&amp;') for k, v in spot.INFO['names'].items()}
VESTS = {}
def u(k):
    if k == 'trophy': return '/trophy.svg?v=2'
    if k == 'titling': return '/fonts/CastoroBelgraveTitlingLight-Regular.woff2'
    VESTS.setdefault(k, None)
    return '/frame/vests/' + re.sub(r'[^A-Za-z0-9]', '', k) + '.svg'
def bust(name, club):
    # the site's list bust: the portrait with its background rectangle stripped
    p = spot.PORTRAITS.get(name.lower())
    if not p: return f'<img src="{u(club)}" alt="" style="width: 40px; height: 40px; display: block; margin: 0 8px 14px">'
    t = open(spot.PORT + p['file'] + '.svg').read()
    open(OUT + 'busts/' + p['file'] + '.svg', 'w').write(re.sub(r'<rect width="200" height="280"[^>]*/>', '', t, count=1))
    return f'<img src="/frame/busts/{p["file"]}.svg" alt="" style="width: 40px; height: 56px; display: block">'
INK='#1d211d';MUT='#686e66';INK2='#4c514a';RULE='#dfe2dd';LINK='#1b649e'
SANS="'Public Sans', system-ui, sans-serif";MONO="'IBM Plex Mono', ui-monospace, monospace";DISP="'Castoro Belgrave Titling', Georgia, serif"
def g(r,*ks):
    for k in ks:
        if k in r: return r[k]
def load(f,rel):
    d=json.load(open(S+f)); st=d['seasonsData'][SEASON]['standings']
    for x in st: x['t']=sum(x.get(k) or 0 for k in ('m1','m2','m3','m4'))
    st=sorted(st,key=lambda x:x['t'])
    rs=sorted([r for r in d['races'] if r['season']==SEASON and r.get('results')],key=lambda r:r['match'])
    return d,st,rs,rel
HEAD=f"font-family: {SANS}; font-size: 15px; font-weight: 500; letter-spacing: 0.025em; text-transform: uppercase; color: {MUT}"
G100='#f3f4f2';G300='#c9ccc7';G700='#3c403a'
def table(st,rel,title):
    hc=lambda t,w:f'<div style="width: {w}px; text-align: right">{t}</div>'
    h=f'<div style="display: flex; align-items: center; gap: 6px; height: 30px; box-sizing: border-box; border-bottom: 1px solid {RULE}; {HEAD}"><div style="flex-grow: 1">{title}&#39;s Div 1</div>{hc("Tot",56)}{hc("M1",42)}{hc("M2",42)}{hc("M3",42)}{hc("M4",42)}</div>\n'
    n=len(st)
    for i,x in enumerate(st):
        c=x['club']
        bb=f'2px dotted {G300}' if i==n-1-rel else f'1px solid {G100}'
        pw='font-weight: 700; color: '+INK if i==0 else 'color: '+INK2
        tw=f'font-weight: 700; color: {LINK}' if i==0 else f'font-weight: 600; color: {INK}'
        ms=''.join(f'<div style="width: 42px; text-align: right; font-family: {MONO}; font-size: 17px; color: {INK2}">{x.get(k) or "-"}</div>' for k in ('m1','m2','m3','m4'))
        h+=f'<div style="display: flex; align-items: center; gap: 6px; height: 40px; box-sizing: border-box; border-bottom: {bb}"><div style="width: 26px; font-family: {SANS}; font-size: 19px; {pw}">{i+1}</div><img src="{u(c)}" alt="{N[c]}" style="width: 22px; height: 22px; display: block"><div style="flex-grow: 1; min-width: 0; padding-left: 4px; white-space: nowrap; font-family: {SANS}; font-size: 19px; font-weight: {600 if i==0 else 400}; color: {INK}">{c.replace("&","&amp;")}</div><div style="width: 56px; text-align: right; font-family: {MONO}; font-size: 19px; {tw}">{x["t"]}</div>{ms}</div>\n'
    return h
def col(title,st,rs,rel,note,extra=''):
    a,b=st[0],st[1]; gap=b['t']-a['t']; race=rs[-1]
    return f'''<div style="width: 468px; display: flex; flex-direction: column">
<div style="display: flex; flex-direction: column">
{table(st,rel,title)}</div>
{extra}</div>
'''
dm,sm,rm,_=load('data.json',2); dw,sw,rw,_=load('data-women.json',3)
def cup(rs,label):
    pos=collections.defaultdict(dict)
    for r in rs:
        for x in r['results']:
            sc=g(x,'s','pts')
            if sc: pos[(g(x,'n','name'),g(x,'c','club'))][r['match']]=sc
    best3=label!='Mitchell Cup'  # women: best 3 of 4; men: every race counts
    need=min(3,len(rs)) if best3 else len(rs)
    ind=sorted([(sum(sorted(v.values())[:3]) if best3 else sum(v.values()),k,v) for k,v in pos.items() if len(v)>=need])[:5]
    tot=[t for t,_,_ in ind]
    ex=f'<div style="margin-top: 20px; display: flex; flex-direction: column"><div style="display: flex; align-items: center; gap: 6px; height: 30px; box-sizing: border-box; border-bottom: 1px solid {RULE}; {HEAD}"><div style="flex-grow: 1">{label}</div><div style="width: 60px; text-align: right">Tot</div><div style="width: 44px"></div><div style="width: 44px"></div></div>\n'
    for i,(t,(n,c),v) in enumerate(ind):
        nm=n.split(' (')[0]; rank=tot.index(t)+1; rk=f'={rank}' if tot.count(t)>1 else str(i+1)
        ps=''.join(f'<div style="width: 44px; text-align: right; font-family: {MONO}; font-size: 15px; color: {MUT}">{v[k]}</div>' for k in sorted(v))
        ex+=f'<div style="display: flex; align-items: center; gap: 6px; height: 52px; box-sizing: border-box; border-bottom: 1px solid {G100}"><div style="width: 34px; font-family: {SANS}; font-size: 19px; color: {MUT}">{rk}</div><div style="align-self: flex-end; flex-shrink: 0; width: 40px; height: 50px; margin-bottom: 1px; margin-left: -4px; overflow: hidden">{bust(nm,c)}</div><div style="flex-grow: 1; padding-left: 4px; white-space: nowrap; font-family: {SANS}; font-size: 19px; color: {G700}">{nm}</div><div style="width: 60px; text-align: right; font-family: {MONO}; font-size: 19px; font-weight: 500; color: {INK}">{t}</div>{ps}</div>\n'
    return ex+'</div>\n'
ex=cup(rm,'Mitchell Cup'); exw=cup(rw,'Individual')
_i=src.index('const VENUE_SHORT='); VS=json.loads(src[src.index('{',_i):src.index('};',_i)+1].replace("'",'"'))
FT=json.load(open(S+'fixture-times.json'))
def fixtures():
    mm=dm['seasonsData'][SEASON]['matches']; wm=dw['seasonsData'][SEASON]['matches']
    L=f'font-family: {SANS}; font-size: 18px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: {MUT}'
    h=f'<div style="display: flex; flex-direction: column"><div style="display: flex; align-items: center; gap: 8px; height: 30px; box-sizing: border-box; border-bottom: 1px solid {RULE}; {HEAD}"><div style="width: 266px">Matches</div><div style="width: 240px">Men</div><div style="width: 74px">Team</div><div style="width: 1px; align-self: stretch; margin: 0 10px; background: {G300}"></div><div style="width: 240px">Women</div><div style="width: 74px">Team</div></div>\n'
    nxt=True
    for m,w in zip(mm,wm):
        assert m['date']==w['date'] and m['venue']==w['venue']
        dt=datetime.date.fromisoformat(m['date']); ds=f'{dt.day} {dt.strftime("%b")}'
        up=not m.get('winner')
        vc=MUT if up else INK
        row=f'<div style="display: flex; align-items: center; gap: 8px; height: 36px; box-sizing: border-box; border-bottom: 1px solid {G100}; font-family: {SANS}; font-size: 18px; color: {INK}"><div style="width: 76px; font-family: {MONO}; font-size: 16px; color: {MUT}">{ds}</div><div style="width: 182px; white-space: nowrap; color: {vc}">{VS.get(m["venue"],m["venue"])}</div>'
        if False:
            pass
        else:
            for x in (m,w):
                if x is w: row+=f'<div style="width: 1px; align-self: stretch; margin: 0 10px; background: {G300}"></div>'
                if up:
                    ft=FT.get(SEASON,{}).get(str(m['num']) if 'num' in m else '',{})
                    hm=ft.get('women' if x is w else 'men') if ft.get('date')==m['date'] else None
                    st=(lambda h,mi:f"{h%12 or 12}{':'+str(mi).zfill(2) if mi else ''}{'am' if h<12 else 'pm'}")(*map(int,hm.split(':'))) if hm else '-'
                    row+=f'<div style="width: 240px; font-family: {SANS}; color: {INK2 if hm else MUT}">{st}</div><div style="width: 74px"></div>'
                else: row+=f'<div style="width: 240px; display: flex; align-items: center; gap: 8px; white-space: nowrap"><img src="{u(x["winnerClub"])}" alt="{N[x["winnerClub"]]}" style="width: 18px; height: 18px; display: block"><div>{x["winner"].split(" ",1)[-1]}</div></div><div style="width: 74px; display: flex; align-items: center; gap: 6px"><img src="{u(x["teamWinner"])}" alt="{N[x["teamWinner"]]}" style="width: 18px; height: 18px; display: block"><div style="font-weight: 600">{x["teamWinner"].replace("&","&amp;")}</div></div>'
        h+=row+'</div>\n'
    return h+'</div>\n'
fixtures=fixtures()
SPOT=spot.build((u,N,SANS,MONO,DISP,INK,INK2,MUT,RULE,'#f3f4f2',u('trophy')))
PHJ=json.load(open(os.path.join(spot.HERE,'photos.json')))
# heights: everything on the page is a fixed size, so the photo slots take whatever the columns leave over
ROW,THEAD,CUP=40,30,20+30+52*5
COLH=1840-80-18-16-(spot.CARD_H+36)-16-(30+36*len(dm['seasonsData'][SEASON]['matches']))
def pos(ph,H,W=468):
    # crop so the eyes sit a third of the way down the slot (or so the top of the frame stays in, where 'top' is set)
    import struct
    sh=W*ph.get('ratio',1.5)
    want=ph['eye']*sh-H/3
    if 'top' in ph: want=min(want,ph['top']*sh)
    return f"{max(0,min(100,100*want/max(sh-H,1))):.1f}%"
def photo(group,table_rows):
    H=COLH-(THEAD+ROW*table_rows)-CUP-20-8-52
    PH=PHJ[group]
    imgs=''.join(f'<img class="photo-{group}" src="{ph["src"]}" alt="{esc(ph["alt"])}" style="position: absolute; left: 0; top: 0; width: 468px; height: {H}px; display: block; object-fit: cover; object-position: 50% {pos(ph,H)}; transition: opacity 1s ease; opacity: {1 if k==0 else 0}">' for k,ph in enumerate(PH))
    print('photo',group,H)
    return (f'<div style="margin-top: 20px; display: flex; flex-direction: column; gap: 8px"><div style="position: relative; width: 468px; height: {H}px; border-radius: 8px; overflow: hidden; background: #f3f4f2">{imgs}'
            f'<div style="position: absolute; inset: 0; background: linear-gradient(to top left, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0) 40%)"></div>'
            f'<div style="position: absolute; right: 12px; bottom: 9px; font-family: {SANS}; font-size: 15px; line-height: 20px; color: rgba(255,255,255,0.8)"><span id="credit-{group}">\U0001F4F7 {esc(PH[0].get("credit",""))}</span></div></div>'
            f'<div style="height: 52px; font-family: {SANS}; font-size: 18px; line-height: 25px; color: {INK2}"><span id="caption-{group}">{esc(PH[0]["caption"])}</span></div></div>\n')
men=col('Men',sm,rm,2,'',photo('men',len(sm))+ex)
women=col('Women',sw,rw,3,'',photo('women',len(sw))+exw)
NAMES=[n for n,_,_,_ in spot.SHORTLIST]
html=open(os.path.join(spot.HERE,'page.html')).read()
html=(html.replace('@@MEN@@',men).replace('@@WOMEN@@',women).replace('@@SPOT@@',SPOT).replace('@@FIXTURES@@',fixtures)
      .replace('@@SEASON@@',SEASON).replace('@@CSS@@',spot.BLINK_CSS+'\n'+spot.INTRO_CSS+'\n'+spot.DOG_CSS)
      .replace('@@PHOTOS@@',json.dumps({g:[[p['caption'],p.get('credit','')] for p in PHJ[g]] for g in ('men','women')})).replace('@@COLH@@',str(COLH))
      .replace('@@SPOTS@@',str(len(NAMES))).replace('@@TROPHY@@',u('trophy')).replace('@@TITLING@@',u('titling')))
assert '@@' not in html
open(OUT+'index.html','w').write(html)
vs=json.loads(__import__('subprocess').check_output(['node',os.path.join(spot.HERE,'vestall.js'),S+'index.html',json.dumps(sorted(VESTS))]))
for k,v in vs.items(): open(OUT+'vests/'+re.sub(r'[^A-Za-z0-9]','',k)+'.svg','w').write(v)
print('frame page', len(html), 'bytes;', len(NAMES), 'spotlight athletes;', len(VESTS), 'vests;', SEASON)
