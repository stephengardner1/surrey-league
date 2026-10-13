"""Simplified geometric portraits.
Custom options: skin tone, hair style, hair colour, facial hair. Nothing else.
Generic runners: 'grey' silhouette or 'outline' — no implied skin tone."""
import os
os.makedirs("v4", exist_ok=True)

HEAD = "M66,96 C64,58 80,40 100,40 C120,40 136,58 134,96 L132,130 C129,152 116,168 100,170 C84,168 71,152 68,130 Z"
SQ = 'transform="translate(0,83) scale(1,0.76) translate(0,-40)"'
VEST = "M53,330 L57,246 Q59,226 61,204 C66,200 73,197 80,195.5 Q100,240 120,195.5 C127,197 134,200 139,204 Q141,226 143,246 L147,330 Z"
KIT_MAP = 'transform="matrix(6.2857 0 0 6.5 37.14 193)"'   # site's 20x20 vest icon -> this vest

# Club kits copied from the site's ClubVest icons (20x20 coordinates)
KITS = {
    "BEL": ("#7A001D", '<rect x="0" y="7" width="20" height="4" fill="#CCAD6A"/>', "#EADFC8"),
    "HOL": ("#2a4ea6", '<rect x="0" y="8" width="20" height="3" fill="#fff"/>', "#D3DCE8"),
    "HHH": ("#dc2626", "".join(f'<rect x="0" y="{y}" width="20" height="3" fill="#1a1a1a"/>' for y in (0, 6, 12, 18)), "#EDD9D3"),
    "G&G": ("#228b22", "", "#D6E6D2"),
    "KEN": ("#2a4d7a", '<path d="M13 5 L15 5.5 L15 7.5 C15 8.5 14 9 13 9.5 C12 9 11 8.5 11 7.5 L11 5.5 Z" fill="#dc2626"/>', "#D3DCE6"),
    "DUL": ("#dc2626", '<rect x="0" y="7" width="20" height="1.9" fill="#2563eb"/><rect x="0" y="10.1" width="20" height="1.9" fill="#2563eb"/>', "#EDD9D3"),
    "C/C": ("#ffffff", '<rect x="0" y="10" width="20" height="10" fill="#1e3a8a"/><rect x="0" y="9" width="20" height="2" fill="#228b22"/>', "#D6DEE6"),
    "RAN": ("#1e3a8a", '<rect x="0" y="8" width="20" height="3" fill="#f4c430"/>', "#D3DCE8"),
    "STR": ("#E9B83C", '<rect x="0" y="8.2" width="20" height="0.9" fill="#1a1a1a"/><rect x="0" y="9.1" width="20" height="2.2" fill="#2E6B3A"/><rect x="0" y="11.3" width="20" height="0.9" fill="#1a1a1a"/><circle cx="14" cy="4.6" r="1.4" fill="#1a1a1a"/><circle cx="14" cy="4.6" r="0.6" fill="#E9B83C"/>', "#F1E6C6"),
    "WOK": ("#ff6600", '<rect x="0" y="8" width="20" height="3" fill="#32CD32"/>', "#F2DFCF"),
    "FUL": ("#ffffff", "".join(f'<rect x="0" y="{y}" width="20" height="3" fill="#1a1a1a"/>' for y in (0, 6, 12, 18)), "#DFE2E6"),
    "FOT": ("#000000", '<rect x="0" y="0" width="20" height="6" fill="#fff"/><rect x="0" y="6" width="20" height="4" fill="#f4c430"/>', "#E6E3D6"),
    "W/W": ("#1a1a1a", '<rect x="0" y="8" width="20" height="4" fill="#dc2626"/>', "#E6DCDC"),
    "REI": ("#dc2626", '<polygon points="0,0 1.8,0 20,18.2 20,20 18.2,20 0,1.8" fill="#87CEEB"/>', "#EDD9D3"),

    "SLH": ("#ffffff", '<rect x="13" y="0" width="4" height="20" fill="#800020"/>', "#E6DCDE"),
    "THH": ("#ffffff", '<g stroke="#1a1a1a" stroke-width="1.1" stroke-linecap="butt"><line x1="6.5" y1="4" x2="13.5" y2="12"/><line x1="13.5" y1="4" x2="6.5" y2="12"/></g>', "#DCE2E6"),
    "H/W": ("#f4c430", '<polygon points="0,3.2 0,5.8 20,20.5 20,17.9" fill="#c41e3a"/>', "#F1E6C6"),
}
def _tint(h, f=0.78, base=(0xE4,0xE6,0xEA)):
    h=h.lstrip('#'); r,g,b=(int(h[i:i+2],16) for i in (0,2,4))
    return "#%02X%02X%02X" % tuple(round(c*(1-f)+bb*f) for c,bb in zip((r,g,b),base))
def _sides(c): return f'<rect x="3" y="0" width="3" height="20" fill="{c}"/><rect x="14" y="0" width="3" height="20" fill="{c}"/>'
_MORE = {
    "HER": ("#1e3a8a", '<rect x="0" y="8" width="20" height="3" fill="#dc2626"/>'),
    "WAL": ("#1a1a1a", '<rect x="0" y="6" width="20" height="2" fill="#f4c430"/><rect x="0" y="8" width="20" height="2" fill="#dc2626"/><rect x="0" y="10" width="20" height="2" fill="#f4c430"/>'),
    "CRO": ("#ffffff", '<rect x="0" y="5" width="20" height="2" fill="#1a1a1a"/><rect x="0" y="12" width="20" height="2" fill="#1a1a1a"/>'),
    "E&E": ("#dc2626", '<rect x="0" y="8" width="20" height="3" fill="#f4c430"/>'),
    "SOC": ("#f4c430", _sides("#228b22")),
    "BOX": ("#f4c430", _sides("#dc2626")),
    "BOH": ("#87CEEB", _sides("#dc2626")),
    "AFD": ("#dc2626", '<rect x="14" y="0" width="3" height="20" fill="#fff"/><rect x="0" y="6" width="20" height="3" fill="#228b22"/>'),
    "SUR": ("#ffffff", '<rect x="0" y="7" width="20" height="1" fill="#1a1a1a"/><rect x="0" y="8" width="20" height="3" fill="#3b82f6"/><rect x="0" y="11" width="20" height="1" fill="#1a1a1a"/>'),
    "MIT": ("#2563eb", '<rect x="0" y="5" width="20" height="1.5" fill="#fff"/><rect x="0" y="8" width="20" height="3" fill="#fff"/><rect x="0" y="12.5" width="20" height="1.5" fill="#fff"/>'),
    "DMV": ("#A52A2A", _sides("#fff")),
    "W4H": ("#f4c430", '<rect x="0" y="8" width="20" height="4" fill="#00CED1"/>'),
    "K&P": ("#1E90FF", '<polygon points="8,0 20,0 20,20 0,20 0,8" fill="#1a1a1a"/><polygon points="0,0 8,0 20,12 20,20 12,20 0,8" fill="#fff"/>'),
    "S&D": ("#1e3a8a", '<rect x="0" y="8" width="20" height="3" fill="#f4c430"/>'),
    "SEL": ("#dc2626", '<rect x="0" y="6" width="20" height="3" fill="#fff"/><rect x="0" y="11" width="20" height="3" fill="#fff"/>'),
    "DWN": ("#228b22", '<rect x="0" y="8" width="20" height="3" fill="#fff"/>'),
    "LCR": ("#1e3a8a", _sides("#f4c430")),
    "ADV": ("#000000", '<text x="10" y="14" text-anchor="middle" fill="#dc2626" font-size="11" font-weight="bold" font-family="Helvetica, Arial, sans-serif">A</text>'),
    "MPA": ("#ffffff", '<polygon points="0,6 6,0 10,0 0,10" fill="#1e3a8a"/><polygon points="0,10 10,0 14,0 0,14" fill="#f4c430"/><polygon points="0,14 14,0 18,0 0,18" fill="#1e3a8a"/>'),
    "262": ("#2563eb", '<polygon points="4,0 9,0 20,11 20,16" fill="#fff"/><polygon points="0,4 0,9 11,20 16,20" fill="#fff"/><polygon points="8,0 12,0 20,8 20,12" fill="#dc2626"/><polygon points="0,8 0,12 8,20 12,20" fill="#dc2626"/>'),
    "OME": ("#dc2626", "".join(f'<rect x="{x}" y="0" width="2" height="20" fill="#fff"/>' for x in (3,7,11,15))),
    "BAC": ("#f5f5dc", '<path d="M4 9 Q10 7 16 9 L15 11 Q10 9.5 5 11 Z" fill="#dc2626"/><path d="M15 10 L16 9 L17 10 L16 12 Z" fill="#1e3a8a"/>'),
    "VAC": ("#ffffff", '<rect x="0" y="8" width="20" height="3" fill="#1a1a1a"/>'),
}
for _k,(_p,_pat) in _MORE.items(): KITS[_k]=(_p,_pat,_tint(_p))
SKIN = {  # base, shadow, light
    1: ("#F3D3BE", "#E0B79F", "#F8E2D3"), 2: ("#E6BA98", "#D09D7A", "#EFCDB2"),
    3: ("#CF9B74", "#B6805B", "#DBAF8E"), 4: ("#A9714E", "#8E5A3B", "#BB8663"),
    5: ("#7A4B33", "#5E3826", "#8E5C41"), 6: ("#4E2F22", "#3B2219", "#62402F"),
}
HAIR_COL = {"black": "#1C1714", "dark brown": "#3A2620", "mid brown": "#6B4A2E", "light brown": "#8E6643",
            "blonde": "#C9A35F", "auburn": "#9A4A26", "ginger": "#C8743A", "grey": "#A9A7A3", "bleached": "#E3C46A"}
GREY = ("#BFC3C9", "#AAAFB6", "#CDD1D6")
INK = "#24272D"

EYE_L = "M76,112 Q85,105 94,112 Q85,117 76,112 Z"
EYE_R = "M106,112 Q115,105 124,112 Q115,117 106,112 Z"
HAIR = {  # in head coordinates
    "buzzrecede": '<path d="M66,96 C64,58 80,40 100,40 C120,40 136,58 134,96 L131,80 Q130,66 124,58 Q118,50 112,50 Q106,52 104,58 Q100,62 96,58 Q94,52 88,50 Q82,50 76,58 Q70,66 69,80 Z"/>',
    "buzz": '<path d="M66,96 C64,58 80,40 100,40 C120,40 136,58 134,96 L130,74 L116,59 L100,56 L84,59 L70,74 Z"/>',
    "bigcurls": '<path d="M64,104 L57.7,84.4 Q43.0,80.3 55.0,71.2 Q42.5,62.8 56.9,58.0 Q47.8,46.0 63.1,45.9 Q58.4,31.7 73.1,36.3 Q73.2,21.2 85.8,30.1 Q90.8,15.7 100.0,28.0 Q109.2,15.7 114.2,30.1 Q126.8,21.2 126.9,36.3 Q141.6,31.7 136.9,45.9 Q152.2,46.0 143.1,58.0 Q157.5,62.8 145.0,71.2 Q157.0,80.3 142.3,84.4 L136,104 L134,88 Q131,72 122,64 Q112,70 104,63 Q96,70 86,64 Q74,68 69,76 Q66,82 66,88 Z"/>',
    "curlspeak": '<path d="M62,114 L59.6,83.0 Q46.8,78.5 57.0,70.0 Q46.8,61.5 59.6,57.0 Q53.2,45.5 67.1,45.6 Q65.3,32.5 78.5,37.1 Q81.5,24.0 92.5,32.6 Q100.0,21.0 107.5,32.6 Q118.5,24.0 121.5,37.1 Q134.7,32.5 132.9,45.6 Q146.8,45.5 140.4,57.0 Q153.2,61.5 143.0,70.0 Q153.2,78.5 140.4,83.0 L138,114 L134,98 Q132,78 123,66 Q114,60 107,65 L100,74 L93,65 Q86,60 77,66 Q68,78 66,98 Z"/>',
    "horseshoe": '<path d="M64,102 C62,84 63,74 69,66 L74,70 Q70,84 70,102 Z"/><path d="M136,102 C138,84 137,74 131,66 L126,70 Q130,84 130,102 Z"/>',
    "sweptback": '<path d="M58,118 Q50,92 56,70 C60,46 78,30 98,32 Q108,26 118,32 C136,38 148,60 144,92 Q146,108 142,118 Q137,122 134,116 L133,96 C131,80 126,66 114,60 Q104,56 96,58 Q82,62 74,74 Q69,84 68,98 L67,116 Q62,122 58,118 Z"/><g fill="none" stroke="#000" stroke-opacity=".28" stroke-width="1.6" stroke-linecap="round"><path d="M78,66 Q94,46 122,44"/><path d="M90,58 Q108,42 132,52"/><path d="M118,60 Q132,62 138,80"/></g>',
    "fringe": '<path d="M65,100 C60,54 80,32 101,33 C122,32 140,54 135,100 L132,86 Q129,72 120,70 L106,76 Q92,80 80,73 Q71,76 68,86 Z"/><g fill="none" stroke="#000" stroke-opacity=".25" stroke-width="1.4" stroke-linecap="round"><path d="M84,58 Q98,66 104,74"/><path d="M98,52 Q112,60 118,70"/></g>',
    "curtains": '<path d="M60,108 C54,62 76,32 100,32 C124,32 146,62 140,108 L136,104 C135,94 132,86 126,80 C116,72 107,70 102,58 L98,58 C93,70 84,72 74,80 C68,86 65,94 64,104 Z"/>',
    "croppeak": '<path d="M65,100 C62,60 82,40 100,40 C118,40 138,60 135,100 L132,84 Q130,68 122,62 Q114,58 108,64 L100,72 L92,64 Q86,58 78,62 Q70,68 68,84 Z"/>',
    "croprecede": '<path d="M65,100 C62,60 82,40 100,40 C118,40 138,60 135,100 L132,84 Q131,64 125,56 Q118,48 111,54 Q105,61 100,61 Q95,61 89,54 Q82,48 75,56 Q69,64 68,84 Z"/>',
    "afro": '<path d="M65,100 C61,90 59,76 60,62 C61,38 78,22 100,21 C122,22 139,38 140,62 C141,76 139,90 135,100 L132,84 C126,72 116,66 100,65 C84,66 74,72 68,84 Z"/>',
    "crop": '<path d="M65,100 C62,60 82,40 100,40 C118,40 138,60 135,100 L132,80 L120,66 L100,62 L80,66 L68,80 Z"/>',
    "quiffrecede": '<path d="M64,100 L63,72 L72,52 L86,38 L104,29 L122,33 L134,48 L137,72 L136,100 L131,80 L128,64 L120,58 L110,63 L100,64 L90,63 L80,58 L72,64 L69,80 Z"/>',
    "quiff": '<path d="M64,100 L63,72 L72,52 L86,38 L104,29 L122,33 L134,48 L137,72 L136,100 L131,78 L126,66 L100,61 L74,68 L69,80 Z"/>',
    "curly": '<path d="M63,100 L61,70 L69,51 L83,39 L100,34 L117,39 L131,51 L139,70 L137,100 L131,80 L124,70 L100,66 L76,70 L69,80 Z"/>',
    "ponytail": '<path d="M65,104 C61,58 81,37 100,37 C121,37 139,58 135,104 L130,86 L118,70 L101,65 L82,70 L70,86 Z"/>',
    "tousled": '<path d="M63,102 L59,76 L62,58 L70,46 L79,41 L82,30 L92,33 L99,24 L107,31 L116,26 L121,35 L130,39 L137,51 L141,70 L137,102 L132,82 L124,71 L100,67 L76,71 L68,82 Z"/>',
    "shortcurls": '<path d="M65,100 L62,76 L66,60 L70,52 L76,49 L79,42 L86,41 L90,34 L97,36 L101,30 L107,35 L113,32 L118,38 L125,38 L129,46 L134,50 L138,70 L135,100 L132,84 L127,68 L120,57 L112,63 L104,62 L100,78 L95,62 L86,62 L79,57 L73,68 L68,84 Z"/>',
    "topknot": '<path d="M65,104 C61,58 81,37 100,37 C121,37 139,58 135,104 L131,84 L118,68 L100,64 L82,68 L69,84 Z"/><ellipse cx="101" cy="32" rx="12" ry="10"/><path d="M93,44 L109,44 L106,38 L96,38 Z"/>',
    "long": '<path d="M64,104 C62,56 82,40 100,40 C118,40 138,56 136,104 L128,78 L104,70 L70,84 Z"/>',
}
HAIR_BACK = {
    "ponytail": '<path d="M120,62 C140,64 152,82 152,106 C152,132 146,156 134,178 Q131,184 129,180 C136,158 138,136 135,114 C133,96 130,84 120,72 Z"/>',
    "long": '<path d="M62,92 C58,52 80,34 100,34 C122,34 142,52 138,92 L142,200 L120,204 L80,204 L58,200 Z"/>',
}
# long curly hair: curly crown at the front, scalloped curls falling behind the shoulders
HAIR["longcurls"] = HAIR["bigcurls"]
HAIR_BACK["longcurls"] = '<path d="M58,90 C54,52 78,30 100,30 C122,30 146,52 142,90 Q150,104 144,118 Q152,132 146,146 Q154,160 146,174 Q152,188 142,200 L120,204 L80,204 L58,200 Q48,188 54,174 Q46,160 54,146 Q48,132 56,118 Q50,104 58,90 Z"/>'
# women's styles
HAIR["slick"] = '<path d="M66,104 C62,58 81,37 100,37 C120,37 138,58 134,104 L131,86 L119,68 L101,62 L82,68 L69,86 Z"/>'
HAIR["plait"] = HAIR["ponytail"]
HAIR_BACK["plait"] = "".join(f'<ellipse cx="{136+i*1.6:.1f}" cy="{84+i*12}" rx="{8-i*0.35:.1f}" ry="8"/>' for i in range(9)) + '<path d="M146,186 L156,206 L140,206 Z"/>'
HAIR["lowbun"] = HAIR["ponytail"]
HAIR_BACK["lowbun"] = '<ellipse cx="138" cy="108" rx="15" ry="15"/>'
HAIR["bob"] = '<path d="M60,140 C52,70 74,36 102,36 C130,36 150,70 140,140 L132,142 L132,96 Q126,74 112,68 Q96,80 74,78 Q68,90 68,100 L68,142 Z"/>'
HAIR_BACK["bob"] = '<path d="M58,90 C56,52 80,34 100,34 C122,34 144,52 142,90 L144,150 L56,150 Z"/>'
HAIR["wavytie"] = '<path d="M64,104 C60,57 80,37 100,37 C122,37 140,57 136,104 L131,86 Q132,74 124,70 L118,74 L110,66 L100,70 L90,65 L82,72 L76,68 Q68,76 69,86 Z"/>'
HAIR_BACK["wavytie"] = '<path d="M120,62 C138,62 150,74 150,88 Q158,100 150,112 Q158,126 149,138 Q154,152 143,162 Q144,174 132,182 Q129,184 129,180 Q136,168 134,154 Q138,140 134,126 Q137,112 132,100 Q130,84 120,72 Z"/>'
FACIAL = {
    "mostubble": '<path d="M66,112 L74,124 L84,146 L116,146 L126,124 L134,112 L134,180 L66,180 Z" opacity=".32"/><path d="M84,141 L100,137 L116,141 L117,150 L112,147 L100,144 L88,147 L83,150 Z"/>',
    "muttonchops": '<path d="M64,92 L75,96 L78,128 Q80,142 76,150 L70,146 Q66,132 64,118 Z"/><path d="M136,92 L125,96 L122,128 Q120,142 124,150 L130,146 Q134,132 136,118 Z"/>',
    "goatee": '<path d="M86,141 L100,138 L114,141 L113,146 L100,143.5 L87,146 Z"/><path d="M93,157 Q100,155 107,157 L105,169 Q100,171 95,169 Z"/>',
    "moustache": '<path d="M86,141 L100,138 L114,141 L113,146 L100,143.5 L87,146 Z"/>',
    "beard": '<path d="M66,112 L74,124 L84,146 L116,146 L126,124 L134,112 L134,180 L66,180 Z"/>',
    "stubble": '<path d="M66,112 L74,124 L84,146 L116,146 L126,124 L134,112 L134,180 L66,180 Z" opacity=".32"/>',
}

def figure(kit, mode="custom", skin=1, hair="crop", hair_colour="dark brown", facial=None, cap=None, shades=False, tattoos=False, beanie=None, mud=False, glasses=False, roots=None, stars=0, gaunt=False, greying=False, headband=None, cap_back=False, facial_colour=None, tag="f", shades_col=None, shades_up=False, scrunchie=None, crown=False):
    primary, extras, ground = KITS[kit]
    line = mode == "outline"
    if mode == "custom": sk, dk, lt = SKIN[skin]
    elif mode == "grey": sk, dk, lt = GREY
    else: sk, dk, lt = ground, ground, ground
    st = f' stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" vector-effect="non-scaling-stroke"' if line else ""
    hc = HAIR_COL.get(hair_colour, hair_colour)
    custom = mode == "custom"
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="10 20 180 252">',
         f'<defs><clipPath id="v{tag}"><path d="{VEST}"/></clipPath><clipPath id="h{tag}"><path d="{HEAD}"/></clipPath>'
         f'<clipPath id="r{tag}"><rect x="100" y="0" width="100" height="300"/></clipPath>'
         f'<clipPath id="e{tag}"><path d="{EYE_L}"/><path d="{EYE_R}"/></clipPath>'
         f'<clipPath id="c{tag}"><rect x="0" y="92" width="200" height="300"/></clipPath></defs>',
         f'<rect width="200" height="280" fill="{ground}"/>', '<g transform="translate(0,-40)">']
    if custom and hair in HAIR_BACK:
        o.append(f'<g {SQ} fill="{hc}">{HAIR_BACK[hair]}<g clip-path="url(#r{tag})" fill="#000" opacity=".22">{HAIR_BACK[hair]}</g></g>')
    # lean body: one shape (open at the neck so outlines stay clean), neck drawn first
    o.append(f'<rect x="88" y="171" width="24" height="37" fill="{sk}"{st}/>')
    o.append(f'<path d="M88,193 C76,197 66,200 58,206 C46,212 40,222 39,236 L35,330 L50,330 L56,250 Q59,240 64,238 L136,238 Q141,240 144,250 L150,330 L165,330 L161,236 C160,222 154,212 142,206 C134,200 124,197 112,193" fill="{sk}"{st}/>')
    if not line:
        o.append(f'<g fill="{dk}"><path d="M112,193 C124,197 134,200 142,206 C154,212 160,222 161,236 L165,330 L150,330 L144,250 Q141,240 136,238 L120,238 Z"/>'
                 f'<path d="M58,206 C46,212 40,222 39,236 L40,246 C42,231 47,219 60,211 Z" fill="{lt}" opacity=".6"/>'
                 f'<polygon points="100,171 112,171 112,200 106,200"/>'
                 f'<path d="M88,179 L112,179 L112,189 Q100,192 88,189 Z"/></g>')
    if custom and tattoos:
        t = '#3A4350'
        o.append(f'<g fill="none" stroke="{t}" stroke-width="1.3" stroke-linecap="round" opacity=".75">'
                 '<g transform="translate(8,0)"><circle cx="38" cy="238" r="4.5"/><path d="M34,252 L42,256 M33,262 L41,266"/>'
                 '<path d="M36,276 L40,270 L44,276 L40,282 Z"/><circle cx="35" cy="296" r="3"/><path d="M31,308 Q37,302 42,309"/></g>'
                 '<g transform="translate(-9,0)"><path d="M158,230 Q164,224 168,232 Q162,238 158,230 Z"/><path d="M160,248 L168,244 M161,256 L169,252"/>'
                 '<circle cx="162" cy="272" r="5"/><path d="M162,267 L162,277 M157,272 L167,272"/>'
                 '<path d="M159,292 L166,288 L166,298 Z"/><path d="M160,312 Q165,306 170,313"/></g>'
                 '<path d="M97,200 L100,197 L103,200 L100,203 Z"/></g>')
    # head
    hg = [f'<g fill="{sk}"{st}><path d="M66,100 L56,104 L58,124 L68,130 Z"/><path d="M134,100 L144,104 L142,124 L132,130 Z"/>'
          f'<path d="{HEAD}"/></g>']
    if not line:
        hg.append(f'<path d="M134,100 L144,104 L142,124 L132,130 Z" fill="{dk}"/>'
                  f'<g clip-path="url(#h{tag})"><polygon points="112,40 140,40 140,180 100,180 100,170 118,150 124,118 120,92" fill="{dk}"/>'
                  f'<polygon points="60,40 100,40 90,68 60,82" fill="{lt}" opacity=".7"/></g>')
    if custom:
        ink = "#1E1714"
        brow = hc if hair_colour not in ("grey", "blonde", "ginger", "bleached") else {"grey": "#8C8A86", "blonde": "#9A7A45", "ginger": "#A65A2A", "bleached": "#6B4A2E"}[hair_colour]
        if hair in ("buzz","buzzrecede") or hair is None: brow = "#3A2C24" if skin <= 3 else "#1E1714"
        hg += [f'<g fill="{brow}"><polygon points="74,100 94,97 95,102 75,105"/><polygon points="105,97 126,100 125,105 105,102"/></g>',
               f'<g clip-path="url(#e{tag})" fill="{ink}"><circle cx="85" cy="111.5" r="3.8"/><circle cx="115" cy="111.5" r="3.8"/></g>'
               f'<g fill="none" stroke="{ink}" stroke-width="1.8" stroke-linecap="round"><path d="M76,112 Q85,105 94,112"/><path d="M106,112 Q115,105 124,112"/></g>',
               f'<polygon points="100,108 105,136 96,136" fill="{dk}"/>',
               f'<path d="M89,151 L100,148 L111,151 Q100,158 89,151 Z" fill="{dk}"/>']
        if gaunt:  # hollow cheeks under the cheekbones
            hg.append(f'<g fill="{dk}" opacity=".65"><path d="M74,118 Q86,121 90,139 Q84,131 75,122 Z"/><path d="M126,118 Q114,121 110,139 Q116,131 125,122 Z"/></g><g fill="{lt}" opacity=".6"><path d="M73,115 Q84,115 90,120 Q82,117 73,117 Z"/><path d="M127,115 Q116,115 110,120 Q118,117 127,117 Z"/></g>')
        if facial:
            fc = HAIR_COL.get(facial_colour, facial_colour) if facial_colour else hc
            if facial in ("moustache", "goatee"):
                hg.append(f'<g fill="{fc}">{FACIAL[facial]}</g>')
            else:
                hg.append(f'<g clip-path="url(#h{tag})" fill="{fc}">{FACIAL[facial]}</g>')
                if facial == "beard":
                    hg.append(f'<path d="M90,149 L110,149 L108,154 L92,154 Z" fill="{dk}"/>')
        if hair in HAIR:
            hg.append(f'<g fill="{hc}"' + (f' clip-path="url(#c{tag})"' if (cap or beanie) else '') + (' opacity=".6"' if hair in ("buzz","buzzrecede") else '') + f'>{HAIR[hair]}<g clip-path="url(#r{tag})" fill="#000" opacity=".22">{HAIR[hair]}</g></g>')
            if greying:
                hg.append(f'<clipPath id="hg{tag}">{HAIR[hair]}</clipPath><g clip-path="url(#hg{tag})" fill="none" stroke="#CFCAC2" stroke-width="1.8" stroke-linecap="round" opacity=".9"><path d="M60.4,78.2 q3.4,-4.1 6.8,0"/><path d="M64.8,90.0 q3.1,-3.7 6.2,0"/><path d="M58.6,100.0 q3.1,-3.8 6.3,0"/><path d="M70.4,68.4 q2.8,-3.4 5.6,0"/><path d="M131.2,79.2 q3.2,-3.8 6.4,0"/><path d="M126.7,91.9 q3.5,-4.2 6.9,0"/><path d="M135.0,100.5 q2.7,-3.2 5.3,0"/><path d="M123.5,70.1 q2.6,-3.1 5.1,0"/><path d="M66.2,57.0 q2.5,-3.0 5.1,0"/><path d="M126.5,57.8 q3.3,-4.0 6.7,0"/><path d="M81.1,44.6 q3.0,-3.6 6.0,0"/><path d="M113.9,43.8 q2.8,-3.3 5.6,0"/><path d="M98.7,38.0 q3.3,-4.0 6.7,0"/><path d="M90.1,51.3 q2.7,-3.3 5.5,0"/><path d="M103.9,50.3 q3.3,-3.9 6.5,0"/></g>')
            if headband:  # thin sports headband across the hairline
                hg.append(f'<path d="M63,86 Q100,64 137,86 L137,91 Q100,70 63,91 Z" fill="{headband}"/>')
            if roots and hair == "curtains":
                hg.append(f'<clipPath id="hr{tag}">{HAIR["curtains"]}</clipPath><path clip-path="url(#hr{tag})" d="M56,84 C52,50 76,28 100,28 C124,28 148,50 144,84 C132,58 116,48 104,52 L101,60 L99,60 L96,52 C84,48 68,58 56,84 Z" fill="{HAIR_COL.get(roots, roots)}"/>')
            if hair == "ponytail":
                hg.append(f'<path d="M100,40 L101,65" stroke="{dk}" stroke-width="1.5"/>')
    if custom and glasses:
        hg.append('<g fill="#FFFFFF" fill-opacity=".18" stroke="#9A9DA3" stroke-width="1.6"><rect x="74" y="103" width="22" height="17" rx="5"/><rect x="104" y="103" width="22" height="17" rx="5"/></g>'
                  '<path d="M96,109 Q100,106 104,109 M74,108 L66,106 M126,108 L134,106" fill="none" stroke="#9A9DA3" stroke-width="1.6"/>')
    if custom and shades:
        hg.append('<path d="M66,104 Q100,98 134,104 L131,121 Q118,128 104,120 L100,116 L96,120 Q82,128 69,121 Z" fill="' + (shades_col or "#2B3039") + '"/>'
                  '<path d="M72,108 Q84,105 94,108 L92,112 Q82,110 73,112 Z" fill="#8FA3B8" opacity=".55"/>'
                  '<path d="M106,108 Q116,105 128,108 L127,112 Q117,110 107,112 Z" fill="#8FA3B8" opacity=".35"/>'
                  '<path d="M63,101 Q100,94 137,101 L136,106 Q100,99 64,106 Z" fill="#F4F4F2"/>')
    if custom and shades_up:
        hg.append('<path d="M66,70 Q100,58 134,70 L132,82 Q118,86 104,80 L100,77 L96,80 Q82,86 68,82 Z" fill="#2B3039"/>'
                  '<path d="M64,68 Q100,55 136,68 L135,72 Q100,60 65,72 Z" fill="#F4F4F2" opacity=".8"/>')
    if custom and scrunchie:
        hg.append(f'<ellipse cx="128" cy="74" rx="6" ry="8" fill="{scrunchie}"/>')
    if custom and beanie:
        hg.append(f'<g fill="{beanie}"><path d="M62,98 C60,52 80,30 100,30 C120,30 140,52 138,98 Z"/></g>'
                  f'<g clip-path="url(#r{tag})" fill="#000" opacity=".15"><path d="M62,98 C60,52 80,30 100,30 C120,30 140,52 138,98 Z"/></g>'
                  f'<path d="M61,84 Q100,77 139,84 L139,100 Q100,93 61,100 Z" fill="{beanie}"/>'
                  f'<path d="M61,84 Q100,77 139,84 L139,100 Q100,93 61,100 Z" fill="#000" opacity=".18"/>'
                  '<g stroke="#000" stroke-opacity=".22" stroke-width="1.6">' +
                  "".join(f'<line x1="{x}" y1="{83 - abs(x-100)*0.1 + 1}" x2="{x}" y2="{98 - abs(x-100)*0.1}"/>' for x in range(66, 136, 6)) +
                  '</g>')
    if custom and cap and cap_back:  # cap worn backwards: crown only, strap opening at the front
        hg.append(f'<g fill="{cap}"><path d="M62,94 C60,54 80,36 100,36 C120,36 140,54 138,94 Q100,82 62,94 Z"/></g>'
                  f'<path d="M93,88 Q100,78 107,88 Q100,86 93,88 Z" fill="{hc}"/>'
                  + (f'<path d="M64,94 ' + ''.join('q4,8 8,0 ' for _ in range(9)) + f'Q100,83 64,94 Z" fill="{hc}"/>' if hair and hair not in ("buzz", "buzzrecede") else '')
                  + 
                  f'<g clip-path="url(#r{tag})" fill="#000" opacity=".12"><path d="M62,94 C60,54 80,36 100,36 C120,36 140,54 138,94 Z"/></g>')
    elif custom and cap:
        hg.append(f'<g fill="{cap}"><path d="M63,98 C61,58 80,38 100,38 C120,38 139,58 137,98 Z"/>'
                  f'<path d="M56,97 Q100,82 144,97 Q146,105 138,110 Q100,99 62,110 Q54,105 56,97 Z"/></g>'
                  f'<path d="M56,97 Q100,82 144,97 Q144,100 142,101 Q100,88 58,101 Q56,100 56,97 Z" fill="#fff" opacity=".35"/>'
                  f'<g clip-path="url(#r{tag})" fill="#000" opacity=".12"><path d="M63,98 C61,58 80,38 100,38 C120,38 139,58 137,98 Z"/></g>'
                  f'<path d="M62,110 Q100,99 138,110 L136,114 Q100,104 64,114 Z" fill="#000" opacity=".28"/>')
    if custom and crown:  # little gold crown perched at a jaunty angle
        hg.append('<g transform="translate(0,5) rotate(-8 100 30)"><path d="M84,36 L82,16 L92,26 L100,12 L108,26 L118,16 L116,36 Z" fill="#E2B23A" stroke="#B8862A" stroke-width="1.2" stroke-linejoin="round"/>'
                  '<rect x="84" y="31" width="32" height="5" fill="#C9962E"/><circle cx="82" cy="15" r="2.4" fill="#E2B23A"/><circle cx="100" cy="11" r="2.6" fill="#E2B23A"/><circle cx="118" cy="15" r="2.4" fill="#E2B23A"/>'
                  '<circle cx="100" cy="27" r="2.6" fill="#C41E3A"/><circle cx="91" cy="31" r="1.6" fill="#2563EB"/><circle cx="109" cy="31" r="1.6" fill="#2563EB"/></g>')
    o.append(f'<g {SQ}>' + "".join(hg) + '</g>')
    # kit: the site's own vest icon, scaled into this vest
    o.append(f'<g clip-path="url(#v{tag})"><path d="{VEST}" fill="{primary}"/><g {KIT_MAP}>{extras}</g>'
             f'<path d="M139,204 Q141,226 143,246 L147,330 L135,330 Z" fill="#000" opacity="{0 if line else .12}"/></g>')
    if stars:
        import math
        stars_gold = "#CCAD6A"
        w = 6.6 * stars + 3; x0, y0 = 62, 225.5
        g = [f'<rect x="{x0}" y="{y0}" width="{w:.1f}" height="10" rx="1" fill="{primary}" stroke="{stars_gold}" stroke-width="1"/>']
        for i in range(stars):
            cx, cy, R = x0 + 4.8 + 6.6 * i, y0 + 5.2, 2.7
            pts = " ".join(f"{cx + (R if k % 2 == 0 else R * .42) * math.sin(k * math.pi / 5):.2f},{cy - (R if k % 2 == 0 else R * .42) * math.cos(k * math.pi / 5):.2f}" for k in range(10))
            g.append(f'<polygon points="{pts}" fill="{stars_gold}"/>')
        o.append(f'<g clip-path="url(#v{tag})">' + "".join(g) + '</g>')
    if mud:
        import random
        r = random.Random(1060)
        dots = []
        for _ in range(38):
            x = r.uniform(58, 142); y = r.triangular(212, 330, 300)
            rx = r.uniform(0.7, 2.6); ry = rx * r.uniform(0.7, 1.3)
            dots.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}"/>')
        dots.append('<path d="M70,296 q6,-3 12,1 q-5,4 -12,-1 Z"/><path d="M118,268 q4,-2 7,2 q-4,2 -7,-2 Z"/>')
        o.append(f'<g clip-path="url(#v{tag})" fill="#6B4A2E" opacity=".75">' + "".join(dots) + '</g>')
    if line:
        o.append(f'<path d="{VEST}" fill="none"{st}/>')
    o.append('</g></svg>')
    return "".join(o)

def save(name, svg): open(f"v4/{name}.svg", "w").write(svg)

# generic runners
for k in KITS:
    slug = k.replace("/", "")
    save(f"grey_{slug}", figure(k, "grey"))
    save(f"outline_{slug}", figure(k, "outline"))
# options sheet (Holland kit throughout)
for s in SKIN: save(f"skin_{s}", figure("HOL", skin=s, hair="crop", hair_colour="dark brown"))
for i, h in enumerate(["none", "buzz", "crop", "quiff", "curly", "ponytail", "long"]):
    save(f"hair_{h}", figure("HOL", skin=2, hair=h, hair_colour="mid brown"))
for f in ["none", "stubble", "moustache", "beard"]:
    save(f"facial_{f}", figure("HOL", skin=3, hair="crop", hair_colour="dark brown", facial=None if f == "none" else f))
for c in HAIR_COL: save(f"col_{c.replace(' ', '-')}", figure("HOL", skin=2, hair="quiff", hair_colour=c))
# winners
save("kitty_grey", figure("BEL", "grey")); save("jack_grey", figure("HOL", "grey"))
save("kitty", figure("BEL", skin=2, hair="ponytail", hair_colour="dark brown"))
save("jack", figure("HOL", skin=1, hair="quiff", hair_colour="light brown"))
save("sam", figure("HHH", skin=1, hair="curly", hair_colour="ginger"))
save("suzie", figure("G&G", skin=1, hair="ponytail", hair_colour="auburn"))
save("sam_grey", figure("HHH", "grey")); save("suzie_grey", figure("G&G", "grey"))
save("col_ginger", figure("HOL", skin=2, hair="quiff", hair_colour="ginger"))
save("freddie", figure("H/W", skin=1, hair="crop", hair_colour="light brown", facial="stubble", cap="#F2F1EC"))
save("freddie_grey", figure("H/W", "grey"))
save("cap_none", figure("HOL", skin=2, hair="crop", hair_colour="mid brown"))
save("cap_cap", figure("HOL", skin=2, hair="crop", hair_colour="mid brown", cap="#F2F1EC"))
save("jamie", figure("H/W", skin=1, hair="crop", hair_colour="dark brown", facial="moustache"))
save("samg", figure("BEL", skin=4, hair="buzz", hair_colour="black", facial="beard", shades=True))
save("shades_none", figure("HOL", skin=3, hair="crop", hair_colour="dark brown"))
save("shades_on", figure("HOL", skin=3, hair="crop", hair_colour="dark brown", shades=True))
save("brotchie", figure("HHH", skin=1, hair="buzzrecede", hair_colour="light brown", facial="stubble", tattoos=True))
save("tat_none", figure("HOL", skin=2, hair="crop", hair_colour="mid brown"))
save("tat_on", figure("HOL", skin=2, hair="crop", hair_colour="mid brown", tattoos=True))
save("millar", figure("THH", skin=1, hair="shortcurls", hair_colour="mid brown", mud=True))
save("millar_grey", figure("THH", "grey"))
save("lucy", figure("HHH", skin=1, hair="ponytail", hair_colour="blonde"))
save("alex", figure("H/W", skin=1, hair="quiff", hair_colour="mid brown"))
save("lucy_grey", figure("HHH", "grey"))
save("josh", figure("BEL", skin=1, hair="topknot", hair_colour="light brown", facial="beard"))
save("hair_topknot", figure("HOL", skin=2, hair="topknot", hair_colour="mid brown"))
save("downie", figure("BEL", skin=1, hair="quiff", hair_colour="blonde"))
save("ogden", figure("SLH", skin=1, hair="crop", hair_colour="dark brown"))
save("ogden_grey", figure("SLH", "grey"))
save("mccallum", figure("H/W", skin=1, hair="crop", hair_colour="black"))
save("penney", figure("H/W", skin=1, hair="quiff", hair_colour="dark brown"))
save("dempsey", figure("THH", skin=1, hair="croppeak", hair_colour="blonde"))
save("hart", figure("BEL", skin=1, hair="tousled", hair_colour="light brown"))
save("sanderson", figure("G&G", skin=2, hair="quiff", hair_colour="dark brown", facial="stubble"))
save("fyfe", figure("BEL", skin=2, hair="tousled", hair_colour="dark brown"))
save("hair_tousled", figure("HOL", skin=2, hair="tousled", hair_colour="mid brown"))
save("saron", figure("BEL", skin=4, hair="ponytail", hair_colour="black"))
save("owor", figure("BEL", skin=6, hair="buzz", hair_colour="black", beanie="#5E6266"))
save("cap_beanie", figure("HOL", skin=2, hair="crop", hair_colour="mid brown", beanie="#5E6266"))
save("ruby", figure("H/W", skin=1, hair="ponytail", hair_colour="blonde"))
save("foster", figure("G&G", skin=1, hair="crop", hair_colour="dark brown", facial="stubble"))
save("hair_shortcurls", figure("HOL", skin=2, hair="shortcurls", hair_colour="mid brown"))
save("tennyson", figure("G&G", skin=1, hair="curlspeak", hair_colour="mid brown", greying=True, glasses=True))
save("glasses_on", figure("HOL", skin=3, hair="crop", hair_colour="dark brown", glasses=True))
save("ollington", figure("THH", skin=2, hair="crop", hair_colour="dark brown", facial="beard"))
save("preston", figure("BEL", skin=3, hair="afro", hair_colour="black"))
print(len(os.listdir("v4")))
save("wolff", figure("BEL", skin=1, hair="crop", hair_colour="light brown"))
save("scott", figure("BEL", skin=2, hair="tousled", hair_colour="dark brown", facial="beard"))
save("mitchell", figure("BEL", skin=1, hair="quiff", hair_colour="ginger"))
save("evans", figure("BEL", skin=1, hair="crop", hair_colour="#A8703F"))
save("roberts", figure("HHH", skin=1, hair="curtains", hair_colour="bleached", roots="mid brown", mud=True))
save("slemeck", figure("H/W", skin=1, hair="quiff", hair_colour="mid brown", facial="beard", gaunt=True))
save("edgar", figure("BEL", skin=1, hair="buzzrecede", hair_colour="light brown", facial="moustache", shades=True))
save("sommerville", figure("BEL", skin=1, hair="croprecede", hair_colour="dark brown"))
save("mcdowell", figure("H/W", skin=1, hair=None))
save("coogan", figure("HHH", skin=1, hair="ponytail", hair_colour="blonde"))
save("hind", figure("KEN", skin=1, hair="quiffrecede", hair_colour="dark brown"))
save("martin", figure("THH", skin=1, hair="crop", hair_colour="dark brown"))
save("hind", figure("KEN", skin=1, hair="quiffrecede", hair_colour="dark brown"))
save("barnes", figure("THH", skin=1, hair="crop", hair_colour="dark brown"))
save("mcnally", figure("BEL", skin=1, hair="crop", hair_colour="ginger", facial="beard", stars=4))
save("board", figure("HHH", skin=1, hair="bigcurls", hair_colour="black"))
save("weir", figure("THH", skin=1, hair="croprecede", hair_colour="dark brown"))
save("chisholm", figure("THH", skin=1, hair="croppeak", hair_colour="dark brown"))
save("panchev", figure("H/W", skin=2, hair="tousled", hair_colour="black", shades=True))
save("royer", figure("G&G", skin=2, hair="longcurls", hair_colour="black", facial="beard"))
save("kelly", figure("BEL", skin=1, hair="quiff", hair_colour="light brown", facial="stubble"))
save("janiaud", figure("BEL", skin=3, hair="quiff", hair_colour="black", facial="stubble", crown=True))
save("renshaw", figure("THH", skin=1, hair="quiffrecede", hair_colour="#C9945A"))
save("ramm", figure("DUL", skin=1, hair="tousled", hair_colour="mid brown", facial="stubble"))
save("dyer", figure("BEL", skin=1, hair="tousled", hair_colour="blonde", headband="#1C1C1E"))
save("blackwood", figure("DUL", skin=1, hair="quiff", hair_colour="light brown"))
save("nicoll", figure("H/W", skin=1, hair="bigcurls", hair_colour="ginger"))
save("ismaili", figure("THH", skin=2, hair="horseshoe", hair_colour="black", facial="goatee"))
save("hathaway", figure("HHH", skin=1, hair="crop", hair_colour="bleached", facial="moustache", facial_colour="mid brown", cap="#1C1C1E", cap_back=True))
save("day", figure("KEN", skin=1, hair="crop", hair_colour="ginger", facial="stubble", cap="#1F3550"))
save("coppard", figure("BEL", skin=1, hair="shortcurls", hair_colour="mid brown", facial="stubble"))
save("tanguy", figure("HHH", skin=1, hair="quiff", hair_colour="dark brown"))
save("threadgold", figure("BEL", skin=1, hair="crop", hair_colour="#C98A4E", facial="stubble"))
save("speed", figure("KEN", skin=1, hair="tousled", hair_colour="light brown"))
save("lethbridge", figure("THH", skin=1, hair="tousled", hair_colour="grey", glasses=True))
save("fox", figure("THH", skin=1, hair="quiff", hair_colour="dark brown"))
save("woods", figure("HOL", skin=1, hair="tousled", hair_colour="light brown"))
save("ryan", figure("BEL", skin=1, hair="fringe", hair_colour="dark brown"))
save("mccolgan", figure("THH", skin=1, hair="shortcurls", hair_colour="light brown"))
save("collier", figure("KEN", skin=1, hair="crop", hair_colour="#B07A4A", facial="stubble", facial_colour="#B5652E"))
save("green", figure("HOL", skin=1, hair="crop", hair_colour="dark brown", facial="stubble"))
save("pearce", figure("BEL", skin=1, hair="tousled", hair_colour="black"))
save("shaw", figure("HHH", skin=1, hair=None))
save("tyas", figure("BEL", skin=1, hair="tousled", hair_colour="dark brown", facial="stubble"))
save("austin", figure("HHH", skin=2, hair="crop", hair_colour="mid brown", facial="beard", cap="#A7A9A6"))
save("ellwood", figure("KEN", skin=1, hair="tousled", hair_colour="mid brown"))
save("mccawley", figure("BEL", skin=2, hair="sweptback", hair_colour="dark brown"))
save("kbarnes", figure("HOL", skin=1, hair="shortcurls", hair_colour="mid brown", facial="moustache"))
save("mallett", figure("H/W", skin=1, hair="crop", hair_colour="mid brown", facial="stubble"))
save("hutchins", figure("WOK", skin=1, hair="crop", hair_colour="#B07A4A"))
save("gathercole", figure("THH", skin=1, hair="quiff", hair_colour="mid brown"))
save("lightfoot", figure("G&G", skin=1, hair="topknot", hair_colour="light brown", glasses=True))
save("brady", figure("H/W", skin=1, hair="croprecede", hair_colour="ginger"))
save("stockings", figure("H/W", skin=1, hair="shortcurls", hair_colour="mid brown", facial="beard"))
save("hobden", figure("H/W", skin=1, hair="shortcurls", hair_colour="ginger", cap="#1C1C1E", cap_back=True))
save("hewitt", figure("HOL", skin=1, hair="tousled", hair_colour="#B89668"))
save("nolan", figure("BEL", skin=1, hair="crop", hair_colour="mid brown", facial="moustache"))
save("lutaya", figure("H/W", skin=6, hair="buzz", hair_colour="black"))
save("young", figure("BEL", skin=1, hair="tousled", hair_colour="dark brown", facial="stubble"))
save("racle", figure("KEN", skin=1, hair="croprecede", hair_colour="mid brown", facial="beard"))
save("snow", figure("BEL", skin=1, hair="quiff", hair_colour="blonde"))
save("reynolds", figure("BEL", skin=1, hair="buzz", hair_colour="mid brown"))
save("awilson", figure("DUL", skin=1, hair="quiff", hair_colour="#C98A4E", facial="beard", facial_colour="#B5652E"))
save("burthem", figure("HHH", skin=1, hair="tousled", hair_colour="dark brown", facial="beard"))
save("pettitt", figure("KEN", skin=1, hair="croprecede", hair_colour="mid brown", facial="beard", shades=True))
# Holt brothers (Herc Wimbledon, 1960s-70s)
save("bob-holt", figure("H/W", skin=1, hair="croprecede", hair_colour="dark brown", facial="muttonchops", gaunt=True))
save("dave-holt", figure("H/W", skin=1, hair="quiffrecede", hair_colour="dark brown", facial="muttonchops", gaunt=True))
# women's race, Oct 2026 (race 566)
LB="#9A6E48"; SB="#B27A4E"; DB="dark brown"
W = [
 ("ruby-whyte-wilding","BEL","Ruby Whyte-Wilding",dict(skin=1,hair="plait",hair_colour=SB),"strawberry-blonde plaited hair"),
 ("sophie-tooley","HHH","Sophie Tooley",dict(skin=2,hair="ponytail",hair_colour="light brown"),"light brown ponytail"),
 ("catherine-kandie","KEN","Catherine Kandie",dict(skin=6,hair="slick",hair_colour="black"),"black hair slicked back"),
 ("olivia-stillman","HHH","Olivia Stillman",dict(skin=2,hair="ponytail",hair_colour="#2A1D18"),"near-black ponytail"),
 ("alex-gandee","BEL","Alex Gandee",dict(skin=1,hair="ponytail",hair_colour=SB),"strawberry-blonde ponytail"),
 ("billie-mcclosky","BEL","Billie McClosky",dict(skin=1,hair="ponytail",hair_colour=LB),"light brown ponytail"),
 ("lisa-bailey","STR","Lisa Bailey",dict(skin=2,hair="slick",hair_colour="blonde",scrunchie="#F4C430"),"blonde hair pulled back with a yellow clip"),
 ("amy-clements","KEN","Amy Clements",dict(skin=1,hair="ponytail",hair_colour=DB),"dark brown ponytail"),
 ("bethanie-murray","THH","Bethanie Murray",dict(skin=1,hair="wavytie",hair_colour=DB),"dark brown flowing ponytail"),
 ("evie-warren","G&G","Evie Warren",dict(skin=1,hair="ponytail",hair_colour="#B08A55"),"dark blonde ponytail"),
 ("lucy-peters","BEL","Lucy Peters",dict(skin=1,hair="wavytie",hair_colour="blonde"),"blonde flowing ponytail"),
 ("emma-lord","H/W","Emma Lord",dict(skin=1,hair="ponytail",hair_colour="#B9955E"),"dark blonde ponytail"),
 ("alice-bridger-morales","HHH","Alice Bridger Morales",dict(skin=3,hair="wavytie",hair_colour="black"),"black curly ponytail"),
 ("emily-bradley","BEL","Emily Bradley",dict(skin=1,hair="lowbun",hair_colour=DB),"dark brown hair tied up"),
 ("isabelle-pickett","G&G","Isabelle Pickett",dict(skin=1,hair="ponytail",hair_colour="ginger"),"ginger ponytail"),
 ("felicity-hayward","THH","Felicity Hayward",dict(skin=2,hair="wavytie",hair_colour=DB),"dark brown ponytail"),
 ("gabriel-reynolds","HHH","Gabriel Reynolds",dict(skin=2,hair="ponytail",hair_colour="#8A6A45"),"light brown ponytail"),
 ("lara-bromilow","KEN","Lara Bromilow",dict(skin=2,hair="lowbun",hair_colour="black"),"black hair tied low"),
 ("megan-gildea","HHH","Megan Gildea",dict(skin=1,hair="topknot",hair_colour="blonde",scrunchie="#D9466A"),"blonde bun with pink scrunchie"),
 ("maeve-kenny","SLH","Maeve Kenny",dict(skin=1,hair="lowbun",hair_colour=DB),"dark brown hair tied back"),
 ("emilie-arnoux","BEL","Emilie Arnoux",dict(skin=3,hair="slick",hair_colour="blonde",shades=True,shades_col="#E0661E"),"blonde hair slicked back, orange sunglasses"),
 ("katie-good","KEN","Katie Good",dict(skin=2,hair="ponytail",hair_colour=DB),"dark brown ponytail"),
 ("ellie-freeden","KEN","Ellie Freeden",dict(skin=1,hair="ponytail",hair_colour="#2A1D18"),"near-black ponytail"),
 ("alice-smith","SLH","Alice Smith",dict(skin=2,hair="tousled",hair_colour="grey",glasses=True),"short grey hair, glasses"),
 ("florence-wiggins","THH","Florence Wiggins",dict(skin=1,hair="topknot",hair_colour="mid brown"),"mid brown top knot"),
 ("alexandra-barbour","BEL","Alexandra Barbour",dict(skin=2,hair="wavytie",hair_colour=DB),"dark brown ponytail"),
 ("ella-king-powrie","BEL","Ella King Powrie",dict(skin=1,hair="ponytail",hair_colour="blonde"),"blonde ponytail"),
 ("betsy-griffiths","RAN","Betsy Griffiths",dict(skin=1,hair="plait",hair_colour="mid brown",shades=True,shades_col="#1F5F8B"),"mid brown plait, blue sunglasses"),
 ("nicola-douglas","STR","Nicola Douglas",dict(skin=2,hair="bob",hair_colour="blonde"),"short blonde bob"),
 ("georgie-furze","WOK","Georgie Furze",dict(skin=2,hair="wavytie",hair_colour=LB),"light brown flowing ponytail"),
 ("emma-rowland","BEL","Emma Rowland",dict(skin=3,hair="ponytail",hair_colour="black",shades_up=True),"black ponytail, sunglasses on her head"),
 ("charlotte-griffiths","BEL","Charlotte Griffiths",dict(skin=1,hair="topknot",hair_colour="mid brown"),"mid brown bun"),
 ("mary-james","SLH","Mary James",dict(skin=3,hair="topknot",hair_colour=DB),"dark brown curly bun"),
 ("penny-oliver","BEL","Penny Oliver",dict(skin=1,hair="wavytie",hair_colour=LB),"light brown wavy ponytail"),
 ("ava-mcandie","H/W","Ava McAndie",dict(skin=1,hair="ponytail",hair_colour=LB),"light brown ponytail"),
 ("bethan-goddard","BEL","Bethan Goddard",dict(skin=1,hair="plait",hair_colour="mid brown"),"mid brown plait"),
 ("nikki-sturzaker","HHH","Nikki Sturzaker",dict(skin=3,hair="wavytie",hair_colour=DB,gaunt=True),"dark brown curly ponytail"),
 ("hannah-english","HHH","Hannah English",dict(skin=1,hair="wavytie",hair_colour="#2A1D18"),"near-black curly ponytail"),
 ("clara-pettit","H/W","Clara Pettit",dict(skin=1,hair="ponytail",hair_colour="#9E7B50"),"light brown ponytail"),
]
for slug, club, name, kw, alt in W:
    save(slug, figure(club, **kw))
save("mike-fuller", figure("H/W", skin=1, hair="longcurls", hair_colour="dark brown", facial="mostubble"))
save("gerry-north", figure("BEL", skin=1, hair="quiff", hair_colour="dark brown"))
