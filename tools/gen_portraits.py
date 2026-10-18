"""Simplified geometric portraits.
Custom options: skin tone, hair style, hair colour, facial hair. Nothing else.
Generic runners: 'grey' silhouette or 'outline' — no implied skin tone."""
import os, math, re
os.makedirs("v4", exist_ok=True)

HEAD_NARROW = "M66,96 C64,58 80,40 100,40 C120,40 136,58 134,96 L131,122 C127,146 114,165 100,168 C86,165 73,146 69,122 Z"
HEAD_SQUARE = "M66,96 C64,58 80,40 100,40 C120,40 136,58 134,96 L133,140 C132,156 122,167 109,169 L91,169 C78,167 68,156 67,140 Z"
HEAD_BROADCHIN = "M66,96 C64,58 80,40 100,40 C120,40 136,58 134,96 L131,122 C128,140 122,154 115,161 Q108,167 100,167 Q92,167 85,161 C78,154 72,140 69,122 Z"  # narrow face with a broad, flattish chin (Georgie Grgec)
HEAD_WIDEPOINT = "M67,96 C64,58 80,40 100,40 C120,40 136,58 133,96 L137,124 L136.5,138 Q136,141 133.5,143.5 L112,165 Q106,170 100,170 Q94,170 88,165 L66.5,143.5 Q64,141 63.5,138 L63,124 Z"  # wide, square-cornered jaw tapering to a pointed chin (Larry Ryan)
HEAD_LONG = "M68,96 C66,58 81,40 100,40 C119,40 134,58 132,96 L129.5,124 C127,146 119,163 108,169 L92,169 C81,163 73,146 70.5,124 Z"  # long, thin, almost rectangular face (Fred Slemeck)
HEAD = "M66,96 C64,58 80,40 100,40 C120,40 136,58 134,96 L132,130 C129,152 116,168 100,170 C84,168 71,152 68,130 Z"
SQ = 'transform="translate(0,83) scale(1,0.76) translate(0,-40)"'
VEST = "M53,330 L57,246 Q59,226 61,204 C66,200 73,197 80,195.5 Q100,240 120,195.5 C127,197 134,200 139,204 Q141,226 143,246 L147,330 Z"
KIT_MAP = 'transform="matrix(6.2857 0 0 6.5 37.14 193)"'   # site's 20x20 vest icon -> this vest

# Club kits copied from the site's ClubVest icons (20x20 coordinates)
KITS = {
    "BEL": ("#7A001D", '<rect x="0" y="7" width="20" height="4" fill="#CCAD6A"/>', "#EADFC8"),
    "HOL": ("#2a4ea6", '<rect x="0" y="8" width="20" height="3" fill="#fff"/>', "#D3DCE8"),
    "HHH": ("#dc2626", "".join(f'<rect x="0" y="{y}" width="20" height="3" fill="#1a1a1a"/>' for y in (0, 6, 12, 18)), "#EDD9D3"),
    "G&G": ("#2E9A5A", '<rect x="0" y="5.5" width="4.9" height="14.5" fill="#1a1a1a"/><rect x="15.1" y="5.5" width="4.9" height="14.5" fill="#1a1a1a"/>', "#D6E6D2"),
    "KEN": ("#2a4d7a", '<path d="M11 5.5 L15 5.5 L15 7.5 C15 8.5 14 9 13 9.5 C12 9 11 8.5 11 7.5 Z" fill="#dc2626"/>', "#D3DCE6"),
    "DUL": ("#dc2626", '<rect x="0" y="7" width="20" height="1.9" fill="#2563eb"/><rect x="0" y="10.1" width="20" height="1.9" fill="#2563eb"/>', "#EDD9D3"),
    "C/C": ("#ffffff", '<rect x="0" y="10" width="20" height="10" fill="#1e3a8a"/><rect x="0" y="9" width="20" height="2" fill="#228b22"/>', "#D6DEE6"),
    "RAN": ("#1E2D5E", '<rect x="0" y="7.7" width="20" height="1.1" fill="#3B74D1"/><rect x="0" y="8.8" width="20" height="1.4" fill="#F2C14E"/><rect x="0" y="10.2" width="20" height="1.1" fill="#E39A35"/>', "#D3DCE8"),
    "STR": ("#E9B83C", '<rect x="0" y="8.2" width="20" height="0.9" fill="#1a1a1a"/><rect x="0" y="9.1" width="20" height="2.2" fill="#2E6B3A"/><rect x="0" y="11.3" width="20" height="0.9" fill="#1a1a1a"/>', "#F1E6C6"),
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
    "CRO": ("#ffffff", '<rect x="0" y="7" width="20" height="2" fill="#1f2a5c"/><rect x="0" y="10.5" width="20" height="2" fill="#1f2a5c"/>'),
    "E&E": ("#dc2626", '<rect x="0" y="8" width="20" height="3" fill="#f4c430"/>'),
    "SOC": ("#f4c430", _sides("#228b22")),
    "BOX": ("#f4c430", _sides("#dc2626")),
    "BOH": ("#87CEEB", _sides("#dc2626")),
    "AFD": ("#dc2626", '<rect x="14" y="0" width="3" height="20" fill="#fff"/><rect x="0" y="6" width="20" height="3" fill="#228b22"/>'),
    "SUR": ("#ffffff", '<rect x="0" y="7" width="20" height="1" fill="#1a1a1a"/><rect x="0" y="8" width="20" height="3" fill="#3b82f6"/><rect x="0" y="11" width="20" height="1" fill="#1a1a1a"/>'),
    "MIT": ("#2563eb", '<rect x="0" y="5" width="20" height="1.5" fill="#fff"/><rect x="0" y="8" width="20" height="3" fill="#fff"/><rect x="0" y="12.5" width="20" height="1.5" fill="#fff"/>'),
    "DMV": ("#C42F6A", '<rect x="3" y="8" width="1" height="12" fill="#BCD3EC"/><rect x="4" y="8" width="1" height="12" fill="#fff"/><rect x="16" y="8" width="1" height="12" fill="#BCD3EC"/><rect x="15" y="8" width="1" height="12" fill="#fff"/>'),  # cerise, with equal pale-blue and white side panels from below the armpit (Oct 2026, Luke Caldwell photo)
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
KITS["CRO"] = KITS["CRO"][:2] + ("#D3D7E3",)  # Croydon: white vest, so base the background on the navy stripes instead of white
SKIN = {  # base, shadow, light (tones 4-6 lifted Oct 2026 so features read on the darkest skin)
    1: ("#F3D3BE", "#E0B79F", "#F8E2D3"), 2: ("#E6BA98", "#D09D7A", "#EFCDB2"),
    3: ("#CF9B74", "#B6805B", "#DBAF8E"), 4: ("#B37C59", "#98653F", "#C5916D"),
    5: ("#8D5C40", "#72462F", "#A16F52"), 6: ("#6B4431", "#523222", "#805641"),
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
    "croppeak": '<path d="M65,100 C62,60 82,40 100,40 C118,40 138,60 135,100 L132,84 Q130,68 122,62 Q114,58 108,62 C104,65 103,70 100,70 C97,70 96,65 92,62 Q86,58 78,62 Q70,68 68,84 Z"/>',
    "croprecede": '<path d="M65,100 C62,60 82,40 100,40 C118,40 138,60 135,100 L132,84 Q131,64 125,56 Q118,48 111,54 Q105,61 100,61 Q95,61 89,54 Q82,48 75,56 Q69,64 68,84 Z"/>',
    "afro": '<path d="M65,100 C61,90 59,76 60,62 C61,38 78,22 100,21 C122,22 139,38 140,62 C141,76 139,90 135,100 L132,84 C126,72 116,66 100,65 C84,66 74,72 68,84 Z"/>',
    "crop": '<path d="M65,100 C62,60 82,40 100,40 C118,40 138,60 135,100 L132,80 L120,66 L100,62 L80,66 L68,80 Z"/>',
    "quiffrecede": '<path d="M64,100 L63,72 L72,52 L86,38 L104,29 L122,33 L134,48 L137,72 L136,100 L131,80 L128,64 L120,58 L110,63 L100,64 L90,63 L80,58 L72,64 L69,80 Z"/>',
    "quiff": '<path d="M64,100 L63,72 L72,52 L86,38 L104,29 L122,33 L134,48 L137,72 L136,100 L131,78 L126,66 L100,61 L74,68 L69,80 Z"/>',
    "curly": '<path d="M63,100 L61,70 L69,51 L83,39 L100,34 L117,39 L131,51 L139,70 L137,100 L131,80 L124,70 L100,66 L76,70 L69,80 Z"/>',
    "ponytail": '<path d="M65,104 C61,58 81,37 100,37 C121,37 139,58 135,104 L130,86 L118,70 L101,65 L82,70 L70,86 Z"/>',
    "tousled": '<path d="M63,102 L59,76 L62,58 L70,46 L79,41 L82,30 L92,33 L99,24 L107,31 L116,26 L121,35 L130,39 L137,51 L141,70 L137,102 L132,82 L124,71 L100,67 L76,71 L68,82 Z"/>',
    "shortcurls": '<path d="M65,100 L62,76 L66,60 L70,52 L76,49 L79,42 L86,41 L90,34 L97,36 L101,30 L107,35 L113,32 L118,38 L125,38 L129,46 L134,50 L138,70 L135,100 L132,84 L127,68 L120,57 L112,63 L104,62 L100,67 L95,62 L86,62 L79,57 L73,68 L68,84 Z"/>',
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
HAIR["longwavy"] = '<path d="M62,108 C56,60 78,36 100,36 C122,36 144,60 138,108 L132,92 Q128,74 113,66 L100,57 L87,66 Q72,74 68,92 Z"/>'
HAIR_BACK["longwavy"] = '<path d="M60,90 C56,52 80,34 100,34 C120,34 144,52 140,90 Q148,110 141,128 Q149,146 141,164 Q147,178 135,188 L65,188 Q53,178 59,164 Q51,146 59,128 Q52,110 60,90 Z"/>'
HAIR["longstraight"] = HAIR["longwavy"]
HAIR_BACK["longstraight"] = '<path d="M60,90 C56,52 80,34 100,34 C120,34 144,52 140,90 L143,186 L57,186 Z"/>'
HAIR["longstraight"] = HAIR["longwavy"]
HAIR_BACK["longstraight"] = '<path d="M60,90 C56,52 80,34 100,34 C120,34 144,52 140,90 L142,188 L58,188 Z"/>'
HAIR["slicktail"] = '<path d="M66,104 C62,58 81,37 100,37 C120,37 138,58 134,104 L131,86 Q129,70 117,62 Q108,62 101,67 Q94,62 85,62 Q71,70 69,86 Z"/>'
HAIR_BACK["slicktail"] = '<path d="M122,64 C138,66 146,78 146,90 Q151,98 145,106 Q150,116 141,124 Q138,130 134,128 Q137,120 133,112 Q136,102 131,94 Q130,80 122,72 Z"/>'
# man bun: hair swept straight back (topknot hairline) into a bun centred at the back of the head
HAIR["manbun"] = HAIR["topknot"].split("/>")[0] + "/>"
HAIR_BACK["manbun"] = '<ellipse cx="100" cy="39" rx="13" ry="9"/>'
HAIR["shaggyrecede"] = '<path d="M60,128 L57,116 L61,108 L56,98 L60,86 L58,74 L66,60 L72,52 L80,47 L86,38 L92,45 L98,34 L104,43 L112,36 L116,46 L124,49 L134,60 L142,74 L140,86 L144,98 L139,108 L143,116 L140,128 L134,124 L133,100 Q131,76 124,64 Q116,57 110,61 Q104,67 100,67 Q96,67 90,61 Q84,57 76,64 Q69,76 67,100 L66,124 Z"/>'
HAIR_BACK["shaggyrecede"] = '<path d="M60,90 C58,56 80,40 100,40 C120,40 142,56 140,90 L146,104 L141,114 L147,124 L140,134 L144,144 L130,140 L70,140 L56,144 L60,134 L53,124 L59,114 L54,104 Z"/>'
HAIR["longloose"] = '<path d="M60,140 C52,66 76,36 100,36 C124,36 148,66 140,140 L134,136 L133,100 Q130,80 118,70 Q108,64 97,60 Q86,70 74,78 Q68,90 67,104 L66,136 Z"/>'
HAIR_BACK["longloose"] = '<path d="M58,90 C55,52 80,34 100,34 C120,34 145,52 142,90 Q150,120 146,150 Q152,180 144,212 L56,212 Q48,180 54,150 Q50,120 58,90 Z"/>'
HAIR["cropround"] = '<path d="M65,100 C62,60 82,40 100,40 C118,40 138,60 135,100 L132,86 C131,74 126,66 116,63 C108,61 104,63 100,66 C96,63 92,61 84,63 C74,66 69,74 68,86 Z"/>'
HAIR["croprecederound"] = '<path d="M65,100 C62,60 82,40 100,40 C118,40 138,60 135,100 L132,84 C131,67 126,57 119,55 C111,54 106,60 100,60 C94,60 89,54 81,55 C74,57 69,67 68,84 Z"/>'
HAIR["tuftrecede"] = '<path d="M65,100 L62,80 L66,62 L72,50 L80,44 L84,34 L93,38 L99,28 L106,36 L114,31 L119,40 L128,44 L134,56 L138,74 L135,100 L132,84 C131,67 126,57 119,55 C111,54 106,60 100,60 C94,60 89,54 81,55 C74,57 69,67 68,84 Z"/>'
HAIR["messyfringe"] = '<path d="M63,102 L59,76 L62,58 L70,46 L79,41 L82,30 L92,33 L99,24 L107,31 L116,26 L121,35 L130,39 L137,51 L141,70 L137,102 L132,86 Q129,74 122,72 L116,79 L110,74 L102,81 L96,75 L88,80 L83,73 Q72,76 68,86 Z"/>'
HAIR["wavyback"] = '<path d="M64,108 C60,58 80,38 100,38 C121,38 140,58 136,108 L131,88 Q128,72 117,66 Q108,63 100,64 Q90,63 82,67 Q72,73 69,88 Z"/><path d="M64,96 Q56,104 60,114 Q54,122 60,132 Q56,142 64,148 L68,140 Q64,132 67,124 Q63,116 67,108 Z"/><path d="M136,96 Q144,104 140,114 Q146,122 140,132 Q144,142 136,148 L132,140 Q136,132 133,124 Q137,116 133,108 Z"/>'
HAIR_BACK["wavyback"] = '<path d="M60,90 C58,54 80,36 100,36 C120,36 142,54 140,90 Q148,104 142,118 Q150,132 140,146 Q144,158 132,160 L68,160 Q56,158 60,146 Q50,132 58,118 Q52,104 60,90 Z"/>'
HAIR["tightbun"] = HAIR["slick"]
HAIR["shaggyhorseshoe"] = '<path d="M66,104 L60,98 L62,90 L56,84 L61,78 L59,70 L66,63 L74,61 L78,67 Q72,80 71,104 Z"/><path d="M134,104 L140,98 L138,90 L144,84 L139,78 L141,70 L134,63 L126,61 L122,67 Q128,80 129,104 Z"/><path d="M88,46 Q94,41 101,43 Q108,40 113,45 Q106,44 100,46 Q94,45 88,46 Z" opacity=".55"/>'
HAIR["floppyrecede"] = '<path d="M64,100 C61,80 62,62 70,52 C78,42 90,37 100,37 C112,37 124,42 131,52 C138,62 139,80 136,100 L133,84 C132,74 129,64 123,57 Q119,63 113,62 Q107,72 92,84 Q95,74 94,64 Q86,60 78,57 C72,64 68,74 67,84 Z" opacity=".92"/><g fill="none" stroke="#000" stroke-opacity=".22" stroke-width="1.3" stroke-linecap="round"><path d="M100,44 Q104,58 96,76"/><path d="M110,46 Q110,60 102,72"/><path d="M90,46 Q86,52 82,56"/></g>'
HAIR["seventies"] = '<path d="M64,104 Q56,100 58,90 Q52,80 58,70 Q56,56 68,50 Q68,30 84,28 Q92,18 103,22 Q115,16 124,26 Q137,32 140,46 Q151,53 146,66 Q152,78 144,88 Q146,100 136,104 L133,92 C131,82 126,74 118,70 Q110,75 100,72 Q88,77 80,70 Q72,76 68,86 Z"/><g fill="none" stroke="#000" stroke-opacity=".25" stroke-width="1.4" stroke-linecap="round"><path d="M72,50 Q88,40 108,44"/><path d="M114,46 Q130,52 138,68"/></g>'
HAIR_BACK["seventies"] = '<path d="M62,82 Q52,88 55,100 Q48,110 54,120 Q48,130 56,138 Q54,148 64,150 Q72,154 78,148 L86,146 L86,130 L114,130 L114,146 L122,148 Q128,154 136,150 Q146,148 144,138 Q152,130 146,120 Q152,110 145,100 Q148,88 138,82 Z"/>'
HAIR["longflow"] = HAIR["longstraight"]
HAIR_FRONT = {"longflow": '<path d="M62,150 C60,172 60,192 58,208 C56,236 56,280 58,330 L84,330 C82,280 82,236 82,210 C80,190 78,170 76,150 Z"/><path d="M138,150 C140,172 140,192 142,208 C144,236 144,280 142,330 L116,330 C118,280 118,236 118,210 C120,190 122,170 124,150 Z"/>'}
HAIR_BACK["longflow"] = HAIR_BACK["longstraight"]
HAIR["straggly"] = '<path d="M62,104 L60,92 C57,80 58,66 62,56 L58,50 L66,48 C70,40 78,34 86,32 L84,26 L92,29 C97,26 104,25 110,27 L114,22 L117,29 C126,32 134,40 138,50 L144,52 L139,58 C142,68 142,82 139,94 L138,104 L133,88 C131,80 128,74 123,70 L126,82 L118,72 L116,80 L110,68 L104,77 L101,66 L94,75 L92,66 L84,74 L83,68 L76,72 C71,76 68,82 67,90 Z"/><g fill="none" stroke="#000" stroke-opacity=".22" stroke-width="1.3" stroke-linecap="round"><path d="M78,50 Q92,40 108,42"/><path d="M110,44 Q122,46 130,58"/><path d="M70,62 Q76,52 86,48"/></g>'
HAIR["curlyup"] = '<path d="M64,104 L63.0,80.0 Q57.6,74.0 64.1,69.5 Q60.0,62.4 67.2,59.6 Q64.8,51.8 72.3,50.8 Q71.7,42.8 79.0,43.8 Q80.1,36.0 86.9,38.9 Q89.8,31.8 95.5,36.3 Q100.0,30.3 104.5,36.3 Q110.2,31.8 113.1,38.9 Q119.9,36.0 121.0,43.8 Q128.3,42.8 127.7,50.8 Q135.2,51.8 132.8,59.6 Q140.0,62.4 135.9,69.5 Q142.4,74.0 137.0,80.0 L136,104 L131,84 Q128,72 120,66 Q112,62 106,66 Q100,62 94,66 Q88,62 80,66 Q72,72 69,84 Z"/><circle cx="94" cy="30" r="7"/><circle cx="104" cy="25" r="8"/><circle cx="112" cy="32" r="6.5"/><circle cx="101" cy="34" r="7"/>'
CURLY_WISPS = '<path d="M66,96 Q60,104 64,112 Q58,118 63,124" fill="none" stroke-width="2.2" stroke-linecap="round"/><path d="M134,96 Q140,104 136,112 Q142,118 137,124" fill="none" stroke-width="2.2" stroke-linecap="round"/>'
HAIR["halfup"] = HAIR["ponytail"] + '<path d="M93,40 C90,30 96,24 102,25 C109,25 112,32 108,40 Z"/>'
HAIR_BACK["halfup"] = '<path d="M65,90 C58,108 54,124 57,140 Q51,154 57,168 Q53,178 62,184 L138,184 Q147,178 143,168 Q149,154 143,140 C146,124 142,108 135,90 Z"/>'
HAIR["highpony"] = HAIR["ponytail"].replace('/>','/>',1) + '<path d="M88,42 C84,34 88,26 94,27 C94,20 102,17 107,22 C113,19 119,26 115,32 C120,36 116,42 112,42 Z"/>'
HAIR_BACK["highpony"] = '<path d="M96,30 C78,26 60,38 55,62 C50,86 52,112 56,134 C59,150 62,162 58,172 Q66,166 67,152 C68,136 64,116 64,96 C64,72 72,52 92,44 Z"/>'
HAIR["messyvolume"] = '<path d="M64,104 C62,94 59,88 56,84 C60,82 61,78 60,72 C58,62 60,52 66,46 Q66,34 77,36 Q78,25 90,30 Q95,19 104,27 Q114,19 119,30 Q131,27 129,38 Q139,40 140,50 C143,58 142,66 140,72 C140,78 142,84 145,88 C140,90 137,96 136,104 L132,86 C130,76 126,68 118,62 C112,60 106,62 100,61 C94,62 86,60 80,63 C74,67 70,76 68,86 Z"/><g fill="none" stroke="#000" stroke-opacity=".22" stroke-width="1.4" stroke-linecap="round"><path d="M80,52 Q92,40 106,42"/><path d="M110,40 Q122,42 130,54"/><path d="M68,62 Q72,50 82,44"/></g>'
HAIR["spiky"] = '<path d="M65,100 L63,76 L65,60 L69,52 L66,44 L75,46 L77,37 L85,41 L89,30 L95,37 L101,27 L106,36 L113,29 L115,39 L123,35 L124,45 L132,44 L131,53 L135,62 L137,76 L135,100 L132,82 L127,70 L121,64 L116,68 L110,62 L104,67 L99,61 L93,66 L87,62 L82,67 L76,64 L71,72 L68,84 Z"/>'
HAIR_BACK["tightbun"] = '<ellipse cx="136" cy="96" rx="13" ry="13"/>'
FACIAL = {
    "littletache": '<path d="M89,142 Q100,138.5 111,142 L110,145 Q100,142 90,145 Z"/>',
    "shortbeard": '<path d="M66,112 L74,124 L84,146 L116,146 L126,124 L134,112 L134,180 L66,180 Z" opacity=".6"/><path d="M86,141 L100,138 L114,141 L113,146 L100,143.5 L87,146 Z" opacity=".7"/>',
    "mostubble": '<path d="M66,112 L74,124 L84,146 L116,146 L126,124 L134,112 L134,180 L66,180 Z" opacity=".32"/><path d="M84,141 L100,137 L116,141 L117,150 L112,147 L100,144 L88,147 L83,150 Z"/>',
    "muttonchops": '<path d="M65,98 L70,98 L71,120 Q74,134 84,143 Q86,148 82,151 Q74,151 70,143 Q66,132 65,118 Z"/><path d="M135,98 L130,98 L129,120 Q126,134 116,143 Q114,148 118,151 Q126,151 130,143 Q134,132 135,118 Z"/>',
    "goatee": '<path d="M86,141 L100,138 L114,141 L113,146 L100,143.5 L87,146 Z"/><path d="M93,157 Q100,155 107,157 L105,169 Q100,171 95,169 Z"/>',
    "moustache": '<path d="M86,141 L100,138 L114,141 L113,146 L100,143.5 L87,146 Z"/>',
    "thicktache": '<path d="M100,137 C108,136 115,138 117,143 L119,151 Q116,151 114,147 C110,145 105,144.5 100,145.5 C95,144.5 90,145 86,147 Q84,151 81,151 L83,143 C85,138 92,136 100,137 Z"/>',
    "beard": '<path d="M66,112 L74,124 L84,146 L116,146 L126,124 L134,112 L134,180 L66,180 Z"/>',
    "bigbeard": '<path d="M64,106 L74,122 L84,146 L116,146 L126,122 L136,106 L136,180 L64,180 Z"/>',
    "bushybeard": '<path d="M64,106 L74,122 L84,146 L116,146 L126,122 L136,106 L136,180 L64,180 Z"/>',
    "stubble": '<path d="M66,112 L74,124 L84,146 L116,146 L126,124 L134,112 L134,180 L66,180 Z" opacity=".32"/>',
}

def _eyewhite(sk):  # an off-white, tinted towards the skin so it never glares
    return '#' + ''.join(f'{round(int(sk[i:i+2],16)*0.3+0xE8*0.7):02X}' for i in (1,3,5))

def figure(kit, mode="custom", skin=1, hair="crop", hair_colour="dark brown", facial=None, cap=None, shades=False, tattoos=False, beanie=None, mud=False, glasses=False, roots=None, stars=0, gaunt=False, greying=False, headband=None, cap_back=False, facial_colour=None, tag="f", shades_col=None, shades_up=False, scrunchie=None, crown=False, jacket=None, medal=None, temples=False, cleft=False, brow_colour=None, jacket_marks=None, define=None, frown=False, hood=None, puffy=False, creases=False, necklace=None, shades_frame="#F4F4F2", thin_brows=False, headband_thick=False, parting=False, rosy=False, glasses_col="#9A9DA3", sideburns=False, armband=False, sleeves=None, buff=None, jaw=None):
    head = HEAD_SQUARE if jaw == "square" else HEAD_NARROW if jaw == "narrow" else HEAD_BROADCHIN if jaw == "broadchin" else HEAD_WIDEPOINT if jaw == "widepoint" else HEAD_LONG if jaw == "long" else HEAD
    primary, extras, ground = KITS[kit]
    line = mode == "outline"
    if mode == "custom": sk, dk, lt = SKIN[skin]
    if mode == "custom" and define is None:  # house style: soft eye whites for all; lighter planes on the two darkest skins
        define = ('eyes', 'light') if skin >= 5 else ('eyes',)
    elif mode == "grey": sk, dk, lt = GREY
    else: sk, dk, lt = ground, ground, ground
    st = f' stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" vector-effect="non-scaling-stroke"' if line else ""
    hc = HAIR_COL.get(hair_colour, hair_colour)
    custom = mode == "custom"
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="10 20 180 252">',
         f'<defs><clipPath id="v{tag}"><path d="{VEST}"/></clipPath><clipPath id="h{tag}"><path d="{head}"/></clipPath>'
         f'<clipPath id="r{tag}"><rect x="100" y="0" width="100" height="300"/></clipPath>'
         f'<clipPath id="e{tag}"><path d="{EYE_L}"/><path d="{EYE_R}"/></clipPath>'
         f'<clipPath id="c{tag}"><rect x="0" y="92" width="200" height="300"/></clipPath></defs>',
         f'<rect width="200" height="280" fill="{ground}"/>', '<g transform="translate(0,-40)">']
    if custom and hair in HAIR_BACK:
        o.append(f'<g {SQ} fill="{hc}">{HAIR_BACK[hair]}<g clip-path="url(#r{tag})" fill="#000" opacity=".22">{HAIR_BACK[hair]}</g></g>')
    # lean body: one shape (open at the neck so outlines stay clean), neck drawn first
    if medal: o.append('<path d="M84,186 Q100,182 116,186 L121,197 L79,197 Z" fill="#1F468E"/>')
    o.append(f'<rect x="88" y="171" width="24" height="37" fill="{sk}"{st}/>')
    o.append(f'<path d="M88,193 C76,197 66,200 58,206 C46,212 40,222 39,236 L35,330 L50,330 L56,250 Q59,240 64,238 L136,238 Q141,240 144,250 L150,330 L165,330 L161,236 C160,222 154,212 142,206 C134,200 124,197 112,193" fill="{sk}"{st}/>')
    if not line:
        o.append(f'<g fill="{dk}"><path d="M112,193 C124,197 134,200 142,206 C154,212 160,222 161,236 L165,330 L150,330 L144,250 Q141,240 136,238 L120,238 Z"/>'
                 f'<path d="M58,206 C46,212 40,222 39,236 L40,246 C42,231 47,219 60,211 Z" fill="{lt}" opacity=".6"/>'
                 f'<polygon points="100,171 112,171 112,200 106,200"/>'
                 f'<path d="M88,179 L112,179 L112,189 Q100,192 88,189 Z"/></g>')
    if custom and sleeves:  # long-sleeved top under the vest (crew neck shows at the collar)
        o.append(f'<path d="M88,193 C76,197 66,200 58,206 C46,212 40,222 39,236 L35,330 L50,330 L56,250 Q59,240 64,238 L136,238 Q141,240 144,250 L150,330 L165,330 L161,236 C160,222 154,212 142,206 C134,200 124,197 112,193 Q100,197 88,193 Z" fill="{sleeves}"/>'
                 '<path d="M112,193 C124,197 134,200 142,206 C154,212 160,222 161,236 L165,330 L150,330 L144,250 Q141,240 136,238 L120,238 Z" fill="#000" opacity=".16"/>')
    if custom and buff:  # snood / buff round the neck
        o.append(f'<path d="M87,180 Q100,185 113,180 L113,199 Q100,203 87,199 Z" fill="{buff}"/><path d="M100,182 L113,180 L113,199 Q107,201 100,201 Z" fill="#000" opacity=".16"/>'
                 '<path d="M88,187 Q100,191 112,187" fill="none" stroke="#000" stroke-opacity=".18" stroke-width="1.2"/>')
    if custom and tattoos:
        t = '#3A4350'
        o.append(f'<g fill="none" stroke="{t}" stroke-width="1.3" stroke-linecap="round" opacity=".75">'
                 '<g transform="translate(8,0)"><circle cx="38" cy="238" r="4.5"/><path d="M34,252 L42,256 M33,262 L41,266"/>'
                 '<path d="M36,276 L40,270 L44,276 L40,282 Z"/><circle cx="35" cy="296" r="3"/><path d="M31,308 Q37,302 42,309"/></g>'
                 '<g transform="translate(-9,0)"><path d="M158,230 Q164,224 168,232 Q162,238 158,230 Z"/><path d="M160,248 L168,244 M161,256 L169,252"/>'
                 '<circle cx="162" cy="272" r="5"/><path d="M162,267 L162,277 M157,272 L167,272"/>'
                 '<path d="M159,292 L166,288 L166,298 Z"/><path d="M160,312 Q165,306 170,313"/></g>'
                 '<path d="M97,200 L100,197 L103,200 L100,203 Z"/></g>')
    if custom and armband:  # heart-rate armband on the upper arm (viewer's left)
        o.append('<path d="M38.1,258.5 L56,261.5 L55.4,270.5 L37.7,267.5 Z" fill="#6A7078"/><path d="M38.1,258.5 L56,261.5 L55.9,263.3 L38,260.3 Z" fill="#8A9098"/>'
                 '<rect x="40" y="260" width="7" height="7.5" rx="1.8" transform="rotate(10 43.5 264)" fill="#25282C"/>')
    # head
    if hood:  # parka hood with a fur ruff framing the face
        fur, lining = hood
        N = 30; d = []
        for i in range(N + 1):
            a0 = i * 2 * math.pi / N; am = (i - 0.5) * 2 * math.pi / N
            P = lambda r, a: f"{100 + r * math.sin(a):.1f},{100 - r * 1.1 * math.cos(a):.1f}"
            d.append(("M" if i == 0 else f"Q{P(68, am)} ") + P(61, a0))
        fur_path = " ".join(d) + " Z"
        hg_pre = (f'<path d="{fur_path}" fill="{fur}"/>'
                  f'<path d="{fur_path}" fill="#000" opacity=".18" clip-path="url(#r{tag})"/>'
                  f'<ellipse cx="100" cy="106" rx="50" ry="60" fill="{lining}"/>')
    else:
        hg_pre = ''
    hg = [hg_pre + f'<g fill="{sk}"{st}><path d="M72,100 L56,104 L58,124 L74,132 Z"/><path d="M128,100 L144,104 L142,124 L126,132 Z"/>'
          + ('' if line else f'<path d="M128,100 L144,104 L142,124 L126,132 Z" fill="{dk}"/>') +
          f'<path d="{head}"/></g>']  # ears tuck under the face, so narrow faces don't show a gap (Oct 2026)
    if not line:
        hg.append(f'<g clip-path="url(#h{tag})"><polygon points="112,40 140,40 140,180 100,180 100,170 118,150 124,118 120,92" fill="{dk}"/>'
                  f'<polygon points="60,40 100,40 90,68 60,82" fill="{lt}" opacity=".7"/></g>')
    if custom:
        ink = "#1E1714"
        brow = hc if hair_colour not in ("grey", "blonde", "ginger", "bleached") else {"grey": "#8C8A86", "blonde": "#9A7A45", "ginger": "#A65A2A", "bleached": "#6B4A2E"}[hair_colour]
        if hair in ("buzz","buzzrecede") or hair is None: brow = "#3A2C24" if skin <= 3 else "#1E1714"
        if brow_colour: brow = brow_colour
        hg += [(f'<g fill="{brow}"><polygon points="74,102 94,95 94,100 75,107"/><polygon points="106,95 126,102 125,107 106,100"/></g><path d="M98,92 L98,99 M102,92 L102,99" stroke="{dk}" stroke-width="1.2" opacity=".7"/>' if frown == "worried" else f'<g fill="{brow}"><polygon points="74,95 94,101 94,106 75,100"/><polygon points="106,101 126,95 125,100 106,106"/></g>' if frown else f'<g fill="{brow}"><polygon points="74,100 94,97 95,102 75,105"/><polygon points="105,97 126,100 125,105 105,102"/></g>' if not thin_brows else f'<g fill="{brow}"><polygon points="75,101.5 94,98.5 94.5,100.6 75.5,103.2"/><polygon points="106,98.5 125,101.5 124.5,103.2 105.5,100.6"/></g>'),
               (f'<g fill="{_eyewhite(sk)}"><path d="{EYE_L}"/><path d="{EYE_R}"/></g>' if define and 'eyes' in define else '') +
               f'<g clip-path="url(#e{tag})" fill="{ink}"><circle cx="85" cy="111.5" r="3.8"/><circle cx="115" cy="111.5" r="3.8"/></g>'
               f'<g fill="none" stroke="{ink}" stroke-width="1.8" stroke-linecap="round"><path d="M76,112 Q85,105 94,112"/><path d="M106,112 Q115,105 124,112"/></g>',
               f'<polygon points="100,108 105,136 96,136" fill="{dk}"/>',
               f'<path d="M89,151 L100,148 L111,151 Q100,158 89,151 Z" fill="{dk}"/>']
        if creases:  # light lines from the nose down past the mouth (age)
            hg.append(f'<path d="M91,131 Q83,141 86,155 M109,131 Q117,141 114,155" stroke="{dk}" stroke-width="1.6" fill="none" stroke-linecap="round" opacity=".75"/>')
        if cleft:  # cleft ('bum') chin
            hg.append(f'<path d="M100,158 Q98.5,163 100,168" stroke="{dk}" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
        if define and 'light' in define:  # soft lighter planes so features read on very dark skin
            hl = '#' + ''.join(f'{round(int(lt[i:i+2],16)*0.6+255*0.4):02X}' for i in (1,3,5))
            hg.append(f'<g fill="{hl}" clip-path="url(#h{tag})"><path d="M97,106 L103,106 L101.5,130 L98.5,130 Z" opacity=".35"/>'
                      f'<path d="M70,116 Q80,112 90,118 L84,132 Q76,128 71,124 Z" opacity=".16"/>'
                      f'<path d="M93,155 Q100,158.5 107,155 Q100,161 93,155 Z" opacity=".4"/></g>')
        if gaunt:  # hollow cheeks under the cheekbones
            hg.append(f'<g clip-path="url(#h{tag})"><g fill="{dk}" opacity=".65"><path d="M74,118 Q86,121 90,139 Q84,131 75,122 Z"/><path d="M126,118 Q114,121 110,139 Q116,131 125,122 Z"/></g><g fill="{lt}" opacity=".6"><path d="M73,115 Q84,115 90,120 Q82,117 73,117 Z"/><path d="M127,115 Q116,115 110,120 Q118,117 127,117 Z"/></g></g>')
        if facial:
            fc = HAIR_COL.get(facial_colour, facial_colour) if facial_colour else hc
            if facial in ("moustache", "goatee", "littletache", "thicktache"):
                hg.append(f'<g fill="{fc}">{FACIAL[facial]}</g>')
            else:
                hg.append(f'<g clip-path="url(#h{tag})" fill="{fc}">{FACIAL[facial]}</g>')
                if facial == "beard":
                    hg.append(f'<path d="M90,149 L110,149 L108,154 L92,154 Z" fill="{dk}"/>')
                if facial == "bigbeard":  # big full beard with moustache: sideburns run up into the hair, hugs a thin face, thickest at the chin
                    hg.append(f'<path d="M66,92 L71,94 L72,116 Q76,132 85,141 L115,141 Q124,132 128,116 L129,94 L134,92 L135,116 L135,132 Q134,152 126,166 Q118,179 108,184 L104,187 L100,185 L96,187 L92,184 Q82,179 74,166 Q66,152 65,132 L65,116 Z" fill="{fc}"/>'
                              f'<path d="M91,150 Q100,147 109,150 L107,155 Q100,157 93,155 Z" fill="{dk}"/>')
                if facial == "bushybeard":  # full, bushy beard that spills past the jawline
                    hg.append(f'<path d="M64,118 L60,140 Q66,168 84,180 Q100,188 116,180 Q134,168 140,140 L136,118 L128,128 L118,146 L82,146 L72,128 Z" fill="{fc}"/>'
                              f'<path d="M88,149 L112,149 L109,155 L91,155 Z" fill="{dk}"/>')
        if hair in HAIR:
            hg.append(f'<g fill="{hc}"' + (f' clip-path="url(#c{tag})"' if (cap or beanie) else '') + (' opacity=".6"' if hair in ("buzz","buzzrecede") else '') + f'>{HAIR[hair]}<g clip-path="url(#r{tag})" fill="#000" opacity=".22">{HAIR[hair]}</g></g>')
            if greying is True:
                hg.append(f'<clipPath id="hg{tag}">{HAIR[hair]}</clipPath><g clip-path="url(#hg{tag})" fill="none" stroke="#CFCAC2" stroke-width="1.8" stroke-linecap="round" opacity=".9"><path d="M60.4,78.2 q3.4,-4.1 6.8,0"/><path d="M64.8,90.0 q3.1,-3.7 6.2,0"/><path d="M58.6,100.0 q3.1,-3.8 6.3,0"/><path d="M70.4,68.4 q2.8,-3.4 5.6,0"/><path d="M131.2,79.2 q3.2,-3.8 6.4,0"/><path d="M126.7,91.9 q3.5,-4.2 6.9,0"/><path d="M135.0,100.5 q2.7,-3.2 5.3,0"/><path d="M123.5,70.1 q2.6,-3.1 5.1,0"/><path d="M66.2,57.0 q2.5,-3.0 5.1,0"/><path d="M126.5,57.8 q3.3,-4.0 6.7,0"/><path d="M81.1,44.6 q3.0,-3.6 6.0,0"/><path d="M113.9,43.8 q2.8,-3.3 5.6,0"/><path d="M98.7,38.0 q3.3,-4.0 6.7,0"/><path d="M90.1,51.3 q2.7,-3.3 5.5,0"/><path d="M103.9,50.3 q3.3,-3.9 6.5,0"/></g>')
            if greying == "sides":  # flat grey on the sides below the crown, geometric two-tone
                hg.append(f'<clipPath id="hs{tag}">{HAIR[hair]}</clipPath><g clip-path="url(#hs{tag})"><path d="M40,72 L76,62 L80,120 L40,120 Z" fill="#B9B3AA"/><path d="M160,72 L124,62 L120,120 L160,120 Z" fill="#A49E96"/></g>')
            if temples:  # grey at the temples
                hg.append(f'<clipPath id="ht{tag}">{HAIR[hair]}</clipPath><g clip-path="url(#ht{tag})" fill="#9C948A" opacity=".8"><path d="M56,80 L73,77 L72,106 L56,106 Z"/><path d="M144,80 L127,77 L128,106 L144,106 Z"/></g>')
            if headband:  # thin sports headband across the hairline
                hg.append(f'<path d="M62,83 Q100,61 138,83 L138,96 Q100,74 62,96 Z" fill="{headband}"/><path d="M62,83 Q100,61 138,83 L138,85 Q100,63 62,85 Z" fill="#fff" opacity=".12"/>' if headband_thick else f'<path d="M63,86 Q100,64 137,86 L137,91 Q100,70 63,91 Z" fill="{headband}"/>')
            if roots and hair == "curtains":
                hg.append(f'<clipPath id="hr{tag}">{HAIR["curtains"]}</clipPath><path clip-path="url(#hr{tag})" d="M56,84 C52,50 76,28 100,28 C124,28 148,50 144,84 C132,58 116,48 104,52 L101,60 L99,60 L96,52 C84,48 68,58 56,84 Z" fill="{HAIR_COL.get(roots, roots)}"/>')
            if hair in ("ponytail", "halfup", "longflow") or (hair == "tightbun" and parting):
                hg.append(f'<path d="M100,40 L101,65" stroke="{dk}" stroke-width="1.5"/>')
            if hair == "curlyup":  # loose curls escaping at the temples
                hg.append(f'<g stroke="{hc}">{CURLY_WISPS}</g>')
            if rosy:  # flushed cheeks (halved Oct 2026)
                hg.append(f'<g fill="#E0505A" opacity=".1" clip-path="url(#h{tag})"><ellipse cx="80" cy="130" rx="12" ry="8.5"/><ellipse cx="120" cy="130" rx="12" ry="8.5"/></g>')
            if sideburns:  # long 70s sideburns down the cheeks
                hg.append(f'<g fill="{hc}"><path d="M64,92 L73,94 L74,114 L81,124 L82,134 L69,146 Q66,138 65,126 Z"/><path d="M136,92 L127,94 L126,114 L119,124 L118,134 L131,146 Q134,138 135,126 Z"/></g>')
            if hair == "highpony":  # hair tie where the bunch is gathered on top
                hg.append('<path d="M89,40 Q100,44 111,40 L110,44.5 Q100,48.5 90,44.5 Z" fill="#000" fill-opacity=".35"/>')
    if custom and glasses:
        gw = "4.2" if glasses == "square" else "2.2" if glasses_col != "#9A9DA3" else "1.6"
        lens = '<circle cx="85" cy="111" r="10"/><circle cx="115" cy="111" r="10"/>' if glasses == "round" else ('<rect x="73" y="102" width="24" height="17" rx="1.5"/><rect x="103" y="102" width="24" height="17" rx="1.5"/>' if glasses == "square" else '<rect x="74" y="103" width="22" height="17" rx="5"/><rect x="104" y="103" width="22" height="17" rx="5"/>')
        hg.append(f'<g fill="#FFFFFF" fill-opacity=".18" stroke="{glasses_col}" stroke-width="{gw}">{lens}</g>'
                  f'<path d="M96,109 Q100,106 104,109 M74,108 L66,106 M126,108 L134,106" fill="none" stroke="{glasses_col}" stroke-width="{gw}"/>')
    if custom and shades:
        hg.append('<path d="M66,104 Q100,98 134,104 L131,121 Q118,128 104,120 L100,116 L96,120 Q82,128 69,121 Z" fill="' + (shades_col or "#2B3039") + '"/>'
                  '<path d="M72,108 Q84,105 94,108 L92,112 Q82,110 73,112 Z" fill="#8FA3B8" opacity=".55"/>'
                  '<path d="M106,108 Q116,105 128,108 L127,112 Q117,110 107,112 Z" fill="#8FA3B8" opacity=".35"/>'
                  '<path d="M63,101 Q100,94 137,101 L136,106 Q100,99 64,106 Z" fill="' + shades_frame + '"/>')
    if custom and shades_up:
        hg.append('<path d="M66,70 Q100,58 134,70 L132,82 Q118,86 104,80 L100,77 L96,80 Q82,86 68,82 Z" fill="#2B3039"/>'
                  '<path d="M64,68 Q100,55 136,68 L135,72 Q100,60 65,72 Z" fill="#F4F4F2" opacity=".8"/>')
    if custom and scrunchie:
        if hair == "topknot":  # ruffled band around the base of the bun
            hg.append(f'<path d="M89,41 q2,-5 4,0 q2,-5 4,0 q2,-5 4,0 q2,-5 4,0 q2,-5 4,0 q2,-5 4,0 L113,45 q-2,5 -4,0 q-2,5 -4,0 q-2,5 -4,0 q-2,5 -4,0 q-2,5 -4,0 q-2,5 -4,0 Z" fill="{scrunchie}"/>'
                      f'<path d="M89,43 L113,43" stroke="#000" stroke-opacity=".18" stroke-width="1"/>')
    if custom and scrunchie and hair == "lowbun":  # band where the low bun meets the head
        hg.append(f'<path d="M145,97 q4,1.5 0,3 q4,1.5 0,3 q4,1.5 0,3 q4,1.5 0,3 L151,109 q-4,-1.5 0,-3 q-4,-1.5 0,-3 q-4,-1.5 0,-3 q-4,-1.5 0,-3 Z" fill="{scrunchie}"/>')
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
    if jacket:  # club manager's quarter-zip top instead of a racing vest
        jc, jd, crest = jacket[:3]
        sh1, sh2 = jacket[3] if len(jacket) > 3 else ('#7A1E2A', '#8E2633')
        body = "M88,192 C76,196 66,199 58,205 C46,211 39,221 38,236 L33,330 L167,330 L162,236 C161,221 154,211 142,205 C134,199 124,196 112,192 Z"
        if puffy:  # wider, rounder down parka behind the standard top
            o.append(f'<path d="M86,190 C70,192 50,198 36,210 C20,224 16,244 18,264 L14,330 L186,330 L182,264 C184,244 180,224 164,210 C150,198 130,192 114,190 Z" fill="{jc}"/>'
                     f'<path d="M114,190 C130,192 150,198 164,210 C180,224 184,244 182,264 L186,330 L150,330 L152,250 Q146,232 128,222 Z" fill="{jd}"/>')
        o.append(f'<path d="{body}" fill="{jc}"/>'
                 f'<path d="M112,192 C124,196 134,200 142,205 C154,211 161,221 162,236 L167,330 L138,330 L140,250 Q136,236 128,226 Z" fill="{jd}"/>'
                 f'<path d="M58,232 Q60,262 58,330 M142,232 Q140,262 142,330" stroke="#000" stroke-opacity=".25" stroke-width="1.5" fill="none"/>'
                 # shirt collar showing in the open neck, jacket collar flaps either side
                 f'<path d="M86,182 L114,182 L100,208 Z" fill="{sh1}"/><path d="M86,182 L93,192 L100,186 L107,192 L114,182 L112,178 L100,184 L88,178 Z" fill="{sh2}"/>'
                 f'<path d="M80,180 Q86,182 91,184 L100,212 L82,200 Z" fill="{jc}"/><path d="M120,180 Q114,182 109,184 L100,212 L118,200 Z" fill="{jd}"/>'
                 f'<path d="M80,180 Q86,182 91,184 L92,188 Q86,186 81,184 Z" fill="#000" opacity=".25"/>'
                 f'<path d="M100,212 L100,330" stroke="#8A8F98" stroke-width="1.6"/><rect x="97.6" y="214" width="4.8" height="9" rx="1.2" fill="#9AA0A8"/>'
                 + (f'<g transform="translate(76,236)"><circle r="10" fill="{crest[0]}"/><circle r="10" fill="none" stroke="{crest[1]}" stroke-width="1.6"/><circle r="6.2" fill="none" stroke="{crest[1]}" stroke-width=".9"/><path d="M-4,3 L-4,-2 L-2,-4 L0,-2 L2,-4 L4,-2 L4,3 Z" fill="{crest[1]}"/></g>' if crest else '')
                 )
    if jacket and puffy:  # quilted baffles
        o.append(''.join(f'<path d="M{20+k*2},{y} Q100,{y+7} {180-k*2},{y}" stroke="#000" stroke-opacity=".22" stroke-width="1.6" fill="none"/>' for k, y in ((0, 238), (1, 262), (1, 286), (1, 310)))
                 + '<path d="M40,214 Q30,240 34,268 M160,214 Q170,240 166,268" stroke="#000" stroke-opacity=".2" stroke-width="1.4" fill="none"/>')
    if jacket and jacket_marks:  # one-off extras on a coach's jacket (initials, club saltire)
        if jacket_marks.get("initials"):
            o.append(f'<text x="76" y="244" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-weight="bold" font-size="12" fill="#F2F2F0">{jacket_marks["initials"]}</text>')
        if jacket_marks.get("saltire"):
            o.append('<g transform="translate(125,236)"><rect x="-8" y="-8" width="16" height="16" fill="#E0393A"/>'
                     '<path d="M-8,-8 L8,8 M8,-8 L-8,8" stroke="#2C3036" stroke-width="2.2"/></g>')
    # kit: the site's own vest icon, scaled into this vest
    if not jacket: o.append(f'<g clip-path="url(#v{tag})"><path d="{VEST}" fill="{primary}"/><g {KIT_MAP}>{extras}</g>'
             f'<path d="M139,204 Q141,226 143,246 L147,330 L135,330 Z" fill="#000" opacity="{0 if line else .12}"/></g>')
    if necklace:  # thin chain resting on the collarbones
        o.append(f'<path d="M87,195 C87,216 113,216 113,195" fill="none" stroke="{necklace}" stroke-width="1.6" stroke-linecap="round"/>'
                 f'<path d="M87,195 C87,216 113,216 113,195" fill="none" stroke="#000" stroke-opacity=".25" stroke-width="1.6" stroke-dasharray="1.2 1.6"/>')
    if medal:  # medal on a ribbon that loops round the back of the neck
        mc = {"gold": ("#D9AA3E", "#BE9030")}[medal]
        o.append('<path d="M79,197 L88,193 L99,252 L92,252 Z" fill="#2B5BB8"/><path d="M121,197 L112,193 L101,252 L108,252 Z" fill="#234C9A"/>'
                 '<rect x="93" y="248" width="14" height="6" fill="#234C9A"/>'
                 f'<circle cx="100" cy="268" r="16" fill="{mc[0]}"/>'
                 f'<path d="M100,252 A16,16 0 0 1 100,284 Z" fill="{mc[1]}"/>')
    if stars:
        pass
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
    if custom and hair in HAIR_FRONT:  # long hair falling in front of the shoulders
        o.append(f'<g fill="{hc}">{HAIR_FRONT[hair]}</g>')
    o.append('</g></svg>')
    return "".join(o)

def save(name, svg): open(f"v4/{name}.svg", "w").write(svg)

# One-off extra: John Sanderson's curly brown poodle peeking up into the bottom-right of his card
def poodle(cx=166, cy=246, s=1.0, fur="#6E4326", dark="#55321C", light="#835333"):
    """Curly brown poodle head peeking up from the bottom edge (flat geometric, house style)."""
    P=lambda x,y:(cx+x*s,cy+y*s)
    out=[]
    def c(x,y,r,col): X,Y=P(x,y); out.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r*s:.1f}" fill="{col}"/>')
    # neck/body block running off the bottom
    X0,Y0=P(-13,8); out.append(f'<rect x="{X0:.1f}" y="{Y0:.1f}" width="{26*s:.1f}" height="{40*s:.1f}" fill="{fur}"/>')
    # ears: curly clusters hanging either side
    for side in (-1,1):
        for (x,y,r) in [(15,-2,6),(16,5,6),(15,12,5.5),(17,18,5)]:
            c(side*x,y,r,dark)
    # head: cluster of curls
    for (x,y,r) in [(0,0,13),(-8,-8,7),(0,-12,7.5),(8,-8,7),(-10,1,6),(10,1,6),(-5,-14,5),(5,-14,5)]:
        c(x,y,r,fur)
    # light catch on the topknot
    c(-3,-13,3.2,light); c(4,-9,2.6,light)
    # muzzle
    c(0,8,6.5,light)
    # eyes peeking through the fur
    c(-5,0,1.5,"#1E1714"); c(5,0,1.5,"#1E1714")
    # nose
    X,Y=P(0,5); out.append(f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{2.6*s:.1f}" ry="{2*s:.1f}" fill="#2A1A12"/>')
    return '<g class="dog">'+''.join(out)+'</g>'
def with_dog(svg, **kw): return svg.replace('</svg>', poodle(**kw)+'</svg>', 1)

# Penny Oliver and James Hancock's black cocker spaniel (same dog in both profile portraits)
def spaniel(cx=158, cy=214, s=1.2, fur="#1B1B1D", plane="#2A2A2E", sheen="#3C3C42"):
    """Black cocker spaniel peeking up from the bottom edge: long wavy ears, amber eyes, tongue out (flat geometric, house style)."""
    P=lambda x,y:(cx+x*s,cy+y*s)
    out=[]
    def c(x,y,r,col): X,Y=P(x,y); out.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r*s:.1f}" fill="{col}"/>')
    def e(x,y,rx,ry,col,rot=0): X,Y=P(x,y); out.append(f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{rx*s:.1f}" ry="{ry*s:.1f}" fill="{col}" transform="rotate({rot} {X:.1f} {Y:.1f})"/>')
    X0,Y0=P(-12,8); out.append(f'<rect x="{X0:.1f}" y="{Y0:.1f}" width="{24*s:.1f}" height="{40*s:.1f}" fill="{fur}"/>')
    # long wavy ears hanging either side
    for side in (-1,1):
        e(side*13,8,6.5,13,fur,side*-8)
        for (x,y,r) in [(14,18,4.2),(11,21,3.8),(16,14,3.6)]: c(side*x,y,r,fur)
        e(side*13,6,2.2,8,plane,side*-8)  # wave sheen down each ear
    # domed head and muzzle
    c(0,-3,12,fur)
    e(0,-11,6,3,sheen)  # sheen on the crown
    e(0,7,8,6.5,plane)  # muzzle
    # amber eyes
    for x in (-5,5): c(x,-1,2.1,"#B8792C"); c(x,-1,1.1,"#140E0A")
    # nose and tongue
    e(0,4.2,2.8,2.1,"#0C0C0D")
    e(1,12.5,2.6,3.2,"#E58A95")
    return '<g class="dog">'+''.join(out)+'</g>'
def with_spaniel(svg, **kw): return svg.replace('</svg>', spaniel(**kw)+'</svg>', 1)

# Angus Butler's dog Max: scruffy black cockapoo with a navy speckled bandana
def cockapoo(cx=154, cy=203, s=1.4, fur="#1E1C1B", plane="#2C2927", sheen="#3E3A37", band="#2E3F5C", fleck="#E8DCC4"):
    """Scruffy black cockapoo peeking up from the bottom edge: shaggy curly ears, fringe over the eyes, speckled bandana (flat geometric, house style)."""
    P=lambda x,y:(cx+x*s,cy+y*s)
    out=[]
    def c(x,y,r,col): X,Y=P(x,y); out.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r*s:.1f}" fill="{col}"/>')
    def e(x,y,rx,ry,col,rot=0): X,Y=P(x,y); out.append(f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{rx*s:.1f}" ry="{ry*s:.1f}" fill="{col}" transform="rotate({rot} {X:.1f} {Y:.1f})"/>')
    def poly(pts,col): out.append('<path d="M'+' L'.join(f'{P(x,y)[0]:.1f},{P(x,y)[1]:.1f}' for x,y in pts)+f' Z" fill="{col}"/>')
    X0,Y0=P(-13,8); out.append(f'<rect x="{X0:.1f}" y="{Y0:.1f}" width="{26*s:.1f}" height="{40*s:.1f}" fill="{fur}"/>')
    # shaggy curly ears hanging either side
    for side in (-1,1):
        for (x,y,r) in [(14,-2,5.5),(16,5,6),(15,12,5.5),(17,18,4.8),(13,21,4.2)]: c(side*x,y,r,fur)
        c(side*15,6,2.6,plane); c(side*16,15,2.2,plane)
    # shaggy head
    for (x,y,r) in [(0,0,12.5),(-8,-7,7),(0,-11,7.5),(8,-7,7),(-11,1,5.5),(11,1,5.5)]: c(x,y,r,fur)
    poly([(-13,-6),(-10,-15),(-6,-10),(-3,-18),(1,-12),(5,-17),(7,-10),(11,-14),(13,-5)],fur)
    c(-4,-12,2.6,sheen); c(5,-10,2.2,sheen)
    # muzzle, with fringe falling over the eyes
    e(0,7,8.5,6.5,plane)
    for x in (-5.5,5.5): c(x,0,1.7,"#5A3A22"); c(x,0,0.9,"#0C0A09")
    poly([(-11,-5),(-7,-1),(-4,-5),(0,-1),(4,-5),(7,-1),(11,-5),(9,-9),(-9,-9)],fur)
    e(0,4.5,2.9,2.1,"#0A0909")
    # speckled navy bandana tied at the neck
    poly([(-15,13),(15,13),(13,18),(0,30),(-13,18)],band)
    for (x,y,r) in [(-9,16,.9),(-4,19,.7),(2,16,.8),(7,19,.9),(10,15,.6),(-2,24,.8),(4,25,.6),(-6,15,.5),(0,20,.6)]: c(x,y,r,fleck)
    return '<g class="dog">'+''.join(out)+'</g>'
def with_cockapoo(svg, **kw): return svg.replace('</svg>', cockapoo(**kw)+'</svg>', 1)



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
save("millar_grey", figure("THH", "grey"))
save("lucy", figure("HHH", skin=1, hair="longloose", hair_colour="#D2B676", brow_colour="#A88C5A"))
save("alex", figure("H/W", skin=1, hair="quiff", hair_colour="mid brown"))
save("lucy_grey", figure("HHH", "grey"))
save("josh", figure("BEL", skin=1, hair="topknot", hair_colour="light brown", facial="beard"))
save("hair_topknot", figure("HOL", skin=2, hair="topknot", hair_colour="mid brown"))
save("downie", figure("BEL", skin=1, hair="quiff", hair_colour="blonde"))
save("ogden", figure("SLH", skin=1, hair="crop", hair_colour="dark brown"))
save("ogden_grey", figure("SLH", "grey"))
save("mccallum", figure("H/W", skin=1, hair="messyfringe", hair_colour="#3A2620"))
save("penney", figure("H/W", skin=1, hair="quiff", hair_colour="dark brown"))
save("dempsey", figure("THH", skin=1, hair="croppeak", hair_colour="blonde"))
save("hart", figure("BEL", skin=1, hair="tousled", hair_colour="light brown"))
save("fyfe", figure("BEL", skin=2, hair="tousled", hair_colour="dark brown", facial="stubble"))
save("hair_tousled", figure("HOL", skin=2, hair="tousled", hair_colour="mid brown"))
save("saron", figure("BEL", skin=4, hair="ponytail", hair_colour="black"))
save("owor", figure("BEL", skin=5, hair=None))
save("cap_beanie", figure("HOL", skin=2, hair="crop", hair_colour="mid brown", beanie="#5E6266"))
save("ruby", figure("H/W", skin=1, hair="ponytail", hair_colour="blonde"))
save("foster", figure("G&G", skin=1, hair="crop", hair_colour="dark brown", facial="stubble"))
save("hair_shortcurls", figure("HOL", skin=2, hair="shortcurls", hair_colour="mid brown"))
save("tennyson", figure("G&G", skin=1, hair="curlspeak", hair_colour="mid brown", greying="sides", glasses=True))
save("glasses_on", figure("HOL", skin=3, hair="crop", hair_colour="dark brown", glasses=True))
save("preston", figure("BEL", skin=3, hair="afro", hair_colour="black"))
print(len(os.listdir("v4")))
save("wolff", figure("BEL", skin=1, hair="crop", hair_colour="light brown"))
save("scott", figure("BEL", skin=2, hair="tousled", hair_colour="dark brown", facial="beard"))
save("mitchell", figure("BEL", skin=1, hair="quiff", hair_colour="ginger"))
save("evans", figure("BEL", skin=1, hair="crop", hair_colour="#A8703F"))
save("roberts", figure("HHH", skin=1, hair="messyvolume", hair_colour="#F1E7BE", brow_colour="#3A2A20", thin_brows=True, mud=True))
save("slemeck", figure("H/W", skin=1, hair="quiff", hair_colour="mid brown", facial="stubble", gaunt=True))
save("edgar", figure("BEL", skin=1, hair="buzzrecede", hair_colour="light brown", facial="moustache", shades=True))
save("sommerville", figure("BEL", skin=1, hair="tuftrecede", hair_colour="dark brown"))
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
save("panchev", figure("H/W", skin=2, hair="tousled", hair_colour="black", shades=True, armband=True))
save("royer", figure("G&G", skin=2, hair="longcurls", hair_colour="black", facial="beard"))
save("kelly", figure("BEL", skin=1, hair="quiff", hair_colour="light brown", facial="stubble"))
save("janiaud", figure("BEL", skin=3, hair="quiff", hair_colour="black", facial="stubble", crown=True))
save("renshaw", figure("THH", skin=1, hair="quiffrecede", hair_colour="#C9945A"))
save("ramm", figure("DUL", skin=1, hair="tousled", hair_colour="mid brown", facial="stubble", gaunt=True, jaw="narrow"))
save("dyer", figure("BEL", skin=1, hair="tousled", hair_colour="blonde", headband="#1C1C1E"))
save("blackwood", figure("DUL", skin=1, hair="quiff", hair_colour="light brown"))
save("nicoll", figure("H/W", skin=1, hair="bigcurls", hair_colour="ginger"))
save("ismaili", figure("THH", skin=2, hair="horseshoe", hair_colour="black", facial="goatee"))
save("hathaway", figure("HHH", skin=1, hair="crop", hair_colour="bleached", facial="moustache", facial_colour="mid brown", cap="#1C1C1E", cap_back=True))
save("day", figure("KEN", skin=1, hair="crop", hair_colour="ginger", facial="stubble", cap="#D6D8DA"))
save("coppard", figure("BEL", skin=1, hair="shortcurls", hair_colour="mid brown", facial="stubble"))
save("tanguy", figure("HHH", skin=1, hair="quiff", hair_colour="dark brown"))
save("threadgold", figure("BEL", skin=1, hair="crop", hair_colour="#C98A4E", facial="stubble"))
save("speed", figure("KEN", skin=1, hair="tousled", hair_colour="light brown"))
save("lethbridge", figure("THH", skin=1, hair="tousled", hair_colour="grey", glasses=True))
save("fox", figure("THH", skin=1, hair="straggly", hair_colour="#3A2820"))
save("woods", figure("HOL", skin=1, hair="tousled", hair_colour="light brown"))
save("ryan", figure("BEL", skin=1, hair="fringe", hair_colour="dark brown"))
save("mccolgan", figure("THH", skin=1, hair="shortcurls", hair_colour="light brown"))
save("collier", figure("KEN", skin=1, hair="tousled", hair_colour="#B07A4A", facial="stubble", facial_colour="#B5652E"))
save("green", figure("HOL", skin=1, hair="crop", hair_colour="dark brown", facial="stubble"))
save("pearce", figure("BEL", skin=1, hair="tousled", hair_colour="black"))
save("shaw", figure("HHH", skin=1, hair=None))
save("tyas", figure("BEL", skin=1, hair="tousled", hair_colour="dark brown", facial="stubble"))
save("austin", figure("HHH", skin=1, hair="slick", hair_colour="#2E211B", facial="shortbeard", facial_colour="#5A3A26", brow_colour="#3A2A20"))
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
save("john-thresher", figure("BEL", skin=1, hair="curlspeak", hair_colour="#2A1D18", glasses="square", glasses_col="#1E1E22", gaunt=True))
# Holt brothers (Herc Wimbledon, 1960s-70s)
save("bob-holt", figure("H/W", skin=1, hair="shaggyhorseshoe", hair_colour="dark brown", facial="muttonchops", gaunt=True))
save("dave-holt", figure("H/W", skin=1, hair="shaggyhorseshoe", hair_colour="dark brown", facial="muttonchops", gaunt=True, glasses="square", glasses_col="#141414"))
# women's race, Oct 2026 (race 566)
LB="#9A6E48"; SB="#B27A4E"; DB="dark brown"
W = [
 ("ruby-whyte-wilding","BEL","Ruby Whyte-Wilding",dict(skin=1,hair="plait",hair_colour=SB),"strawberry-blonde plaited hair"),
 ("sophie-tooley","HHH","Sophie Tooley",dict(skin=2,hair="ponytail",hair_colour="light brown"),"light brown ponytail"),
 ("catherine-kandie","KEN","Catherine Kandie",dict(skin=6,hair="slick",hair_colour="black"),"black hair slicked back"),
 ("olivia-stillman","HHH","Olivia Stillman",dict(skin=2,hair="ponytail",hair_colour="#2A1D18"),"near-black ponytail"),
 ("alex-gandee","BEL","Alex Gandee",dict(skin=1,hair="ponytail",hair_colour=SB),"strawberry-blonde ponytail"),
 ("billie-mcclosky","BEL","Billie McClosky",dict(skin=1,hair="ponytail",hair_colour=LB),"light brown ponytail"),
 ("lisa-bailey","STR","Lisa Bailey",dict(skin=2,hair="slick",hair_colour="blonde"),"blonde hair pulled back"),
 ("amy-clements","KEN","Amy Clements",dict(skin=1,hair="ponytail",hair_colour=DB),"dark brown ponytail"),
 ("bethanie-murray","THH","Bethanie Murray",dict(skin=1,hair="wavytie",hair_colour=DB),"dark brown flowing ponytail"),
 ("evie-warren","G&G","Evie Warren",dict(skin=1,hair="ponytail",hair_colour="#B08A55"),"dark blonde ponytail"),
 ("lucy-peters","BEL","Lucy Peters",dict(skin=1,hair="wavytie",hair_colour="blonde"),"blonde flowing ponytail"),
 ("emma-lord","H/W","Emma Lord",dict(skin=1,hair="ponytail",hair_colour="#B9955E"),"dark blonde ponytail"),
 ("alice-bridger-morales","HHH","Alice Bridger Morales",dict(skin=3,hair="wavytie",hair_colour="black"),"black curly ponytail"),
 ("emily-bradley","BEL","Emily Bradley",dict(skin=1,hair="wavyback",hair_colour="#7A4E30"),"wavy chestnut hair swept back"),
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
 ("alexandra-barbour","BEL","Alexandra Barbour",dict(skin=2,hair="tightbun",hair_colour="#2A1D18"),"straight dark hair pulled back into a tight bun"),
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
# 1967 Southern 12-stage winning team (Herc Wimbledon)
save("mike-beevor", figure("H/W", skin=1, hair="sweptback", hair_colour="dark brown"))
save("john-day", figure("H/W", skin=1, hair="fringe", hair_colour="dark brown"))
save("john-sullivan", figure("H/W", skin=1, hair="croprecede", hair_colour="mid brown", gaunt=True))
save("barry-collins", figure("H/W", skin=1, hair="sweptback", hair_colour="mid brown", facial="moustache", gaunt=True))
save("bob-rayman", figure("H/W", skin=1, hair="tousled", hair_colour="dark brown"))
save("pete-mulholland", figure("H/W", skin=1, hair="quiff", hair_colour="light brown"))
save("charlie-eastaugh", figure("H/W", skin=1, hair="crop", hair_colour="light brown", cap="#F2F1EC", jaw="square"))
save("oli-carrington", figure("H/W", skin=1, hair="tousled", hair_colour="mid brown", facial="shortbeard", facial_colour="mid brown"))
save("jonathan-cornish", figure("H/W", skin=1, hair="tousled", hair_colour="#6E5A44"))
save("gerry-north", figure("BEL", skin=1, hair="quiff", hair_colour="dark brown"))
# Alex Yee: redrawn Oct 2026, see near the end of the file
save("phil-wicks", figure("BEL", skin=1, hair="tousled", hair_colour="#5A3E2A", gaunt=True, temples=True))
save("john-gilbert", figure("KEN", skin=1, hair="fringe", hair_colour="#5C3D28", facial="stubble"))
save("chris-busaileh", figure("KEN", skin=1, hair="croppeak", hair_colour="#A85A30"))
save("jim-allchin", figure("KEN", skin=1, hair="longstraight", hair_colour="#86593A", headband="#C8323A", facial="stubble"))
save("finn-johnson", figure("H/W", skin=2, hair="quiffrecede", hair_colour="#3A2620", facial="beard"))
save("will-cockerell", figure("BEL", skin=2, hair="horseshoe", hair_colour="#D8D5CF", brow_colour="#6E655C", frown=True))
save("nick-goolab", figure("BEL", skin=3, hair="slicktail", hair_colour="#1C1714", facial="stubble", cleft=True))
save("arne-dumez", figure("BEL", skin=1, hair="quiff", hair_colour="#8E6643", facial="mostubble"))
save("geoff-jerwood", figure("HHH", skin=1, hair="shaggyrecede", hair_colour="#CFC3A6", facial="beard", brow_colour="#A8996F", jacket=("#2C3036", "#22262B", None, ("#4E5660", "#626B76")), jacket_marks={"initials": "GJ", "saltire": True}))
save("alex-lee", figure("HHH", skin=1, hair="tousled", hair_colour="#6B4A2E"))
save("benedict-whitby", figure("HHH", skin=2, hair="croppeak", hair_colour="#5E534A", temples=True))
save("falilou-kebe", figure("BEL", skin=6, hair="buzz", hair_colour="black"))
save("jack-dickson", figure("H/W", skin=1, hair="tousled", hair_colour="#9A7650"))
# parked for now (Steve 13 Oct): save("charlie-dickinson", figure("BEL", skin=1, hair=None, beanie="#2F3A2C", frown="worried", brow_colour="#C9C7C2", creases=True, hood=("#8E8474", "#2A2E26"), puffy=True, jacket=("#55604A", "#434C3A", None, ("#2F3A40", "#3B4850"))))
save("phil-swinburn", figure("HOL", skin=1, hair="quiff", hair_colour="#3A2620"))
save("rob-armstrong", figure("DUL", skin=1, hair="crop", hair_colour="#B07A4A", facial="moustache", cap="#1E1E1E"))
save("ashley-goncalves", figure("HHH", skin=2, hair="quiff", hair_colour="#1C1714", facial="shortbeard"))
save("eddie-jodrell", figure("BEL", skin=2, hair="crop", hair_colour="#2E211B"))
save("thomas-gandee", figure("BEL", skin=1, hair="quiff", hair_colour="#B9955E"))
# Wimbledon Common, Feb 2026 (race 439)
W439 = [
 ("max-milarvie","DUL","Max Milarvie",dict(skin=1,hair="tuftrecede",hair_colour="#3A2620",facial="littletache"),"slightly receding dark hair, little moustache"),
 ("alex-lennon","BEL","Alex Lennon",dict(skin=1,hair="bigcurls",hair_colour="#3A2620"),"short dark curly hair"),
 ("james-hoad","THH","James Hoad",dict(skin=1,hair="crop",hair_colour="#6B4A2E"),"short mid brown hair"),
 ("william-gardner","BEL","William Gardner",dict(skin=1,hair="croppeak",hair_colour="#9A6A44",facial="stubble"),"short gingery hair with a widow peak, stubble"),
 ("paddy-roddy","THH","Paddy Roddy",dict(skin=1,hair="sweptback",hair_colour="#2E211B",facial="beard",mud=True),"swept-back dark hair, beard, mud-splattered vest"),
 ("simon-waterhouse","BEL","Simon Waterhouse",dict(skin=1,hair="quiff",hair_colour="#5A3E2A",facial="stubble"),"swept-up brown hair, stubble"),
 ("conall-whelan","BEL","Conall Whelan",dict(skin=1,hair="tousled",hair_colour="#8E6643"),"tousled light brown hair"),
 ("simon-williams","BEL","Simon Williams",dict(skin=1,hair="quiff",hair_colour="#6B4A2E"),"swept-up mid brown hair"),
 ("christian-lee","HOL","Christian Lee",dict(skin=1,hair="quiff",hair_colour="#2E211B"),"short dark brown quiff"),
 ("sean-cordon","DUL","Sean Cordon",dict(skin=1,hair="crop",hair_colour="grey",glasses=True),"short grey hair, glasses"),
 ("michael-mccarthy","BEL","Michael McCarthy",dict(skin=1,hair="shortcurls",hair_colour="#2A1D18",facial="stubble"),"dark curly hair, stubble"),
 ("jeff-cunningham","HHH","Jeff Cunningham",dict(skin=1,hair="croppeak",hair_colour="#6B4A2E"),"short brown hair"),
 ("sam-peters","H/W","Sam Peters",dict(skin=1,hair="crop",hair_colour="#2A1D18",cap="#3A4250",cap_back=True),"backwards cap, dark hair"),
 ("ryan-hickey","HHH","Ryan Hickey",dict(skin=1,hair="crop",hair_colour="#2E211B"),"short dark brown hair"),
 ("ben-scott","BEL","Ben Scott",dict(skin=1,hair="curtains",hair_colour="#6B4A2E",tattoos=True),"floppy centre-parted brown hair, tattooed arms"),
 ("tom-gifford","BEL","Tom Gifford",dict(skin=1,hair="crop",hair_colour="#8E6643",facial="stubble"),"short light brown hair, stubble"),
]
for slug, club, name, kw, alt in W439:
    save(slug, figure(club, **kw))
W439b = [
 ("valentin-rigori","BEL","Valentin Rigori",dict(skin=1,hair="crop",hair_colour="#5A3E2A",facial="shortbeard"),"short brown hair, trimmed beard"),
 ("david-grima","H/W","David Grima",dict(skin=2,hair="sweptback",hair_colour="#2E211B",headband="#D23A2E"),"swept-back dark hair, red headband"),
 ("deron-fagan","HHH","Deron Fagan",dict(skin=6,hair=None,beanie="#3A4B5C"),"navy beanie"),
 ("lee-lintern","G&G","Lee Lintern",dict(skin=1,hair="crop",hair_colour="#4A3426",facial="beard"),"short brown hair, beard"),
 ("ian-acreman","G&G","Ian Acreman",dict(skin=1,hair="crop",hair_colour="grey"),"short grey hair"),
 ("alex-howard","THH","Alex Howard",dict(skin=1,hair="quiffrecede",hair_colour="#4E3626",gaunt=True),"short swept-back brown hair, receding at the temples"),
 ("james-hancock","BEL","James Hancock",dict(skin=1,hair="tuftrecede",hair_colour="#CFA864",rosy=True),"tufty blond hair, slight recede"),  # face finished below (eyes closer, warm brows)
 ("nick-morris","BEL","Nick Morris",dict(skin=1,hair="quiff",hair_colour="#2A1D18"),"short dark hair"),
 ("richard-sun","H/W","Richard Sun",dict(skin=2,hair="crop",hair_colour="#1C1714",shades=True),"short black hair, sunglasses"),
 ("jonathan-cocker","G&G","Jonathan Cocker",dict(skin=1,hair="crop",hair_colour="#6B4A2E",facial="moustache"),"short brown hair, moustache"),
]
for slug, club, name, kw, alt in W439b:
    save(slug, figure(club, **kw))
# women's Match 4, Wimbledon Common, Feb 2026 (race 440) plus two men from race 439
W440 = [
 ("isabel-hodder","BEL","Isabel Hodder",dict(skin=1,hair="ponytail",hair_colour="#6B4A2E"),"mid brown ponytail"),
 ("emma-howsham","G&G","Emma Howsham",dict(skin=1,hair="ponytail",hair_colour="#3A2620"),"dark brown ponytail"),
 ("eilidh-hide","BEL","Eilidh Hide",dict(skin=1,hair="ponytail",hair_colour="#C08850"),"strawberry-blonde ponytail"),
 ("karen-xiang","BEL","Karen Xiang",dict(skin=2,hair="ponytail",hair_colour="black"),"black ponytail"),
 ("claire-grima","H/W","Claire Grima",dict(skin=2,hair="wavytie",hair_colour="#8E6643"),"light brown flowing ponytail"),
 ("emma-gordon","BEL","Emma Gordon",dict(skin=1,hair="ponytail",hair_colour="blonde"),"blonde ponytail"),
 ("emily-lowery","BEL","Emily Lowery",dict(skin=1,hair="ponytail",hair_colour="#9A7650"),"light brown ponytail"),
 ("felicity-harrison","BEL","Felicity Harrison",dict(skin=1,hair="ponytail",hair_colour="#8E6643"),"light brown ponytail"),
 ("alice-martin","HOL","Alice Martin",dict(skin=1,hair="ponytail",hair_colour="#C2A06A"),"blonde ponytail"),
 ("juliet-hodder","BEL","Juliet Hodder",dict(skin=1,hair="wavytie",hair_colour="#9A7650"),"light brown flowing ponytail"),
 ("abbie-bulbulian","C/C","Abbie Bulbulian",dict(skin=1,hair="ponytail",hair_colour="#C2A06A"),"blonde ponytail"),
 ("lara-mangan","BEL","Lara Mangan",dict(skin=1,hair="wavytie",hair_colour="#6B4A2E"),"mid brown flowing ponytail"),
 ("clare-elms","KEN","Clare Elms",dict(skin=1,hair="slick",hair_colour="#6B4A2E"),"mid brown hair tied back"),
]
for slug, club, name, kw, alt in W440:
    save(slug, figure(club, **kw))
save("james-nutt", figure("HHH", skin=1, hair="quiff", hair_colour="#5A3E2A"))
save("colin-high", figure("G&G", skin=1, hair="horseshoe", hair_colour="#8E6643", facial="beard", facial_colour="#8A5A36"))
# Mitcham Common, Jan 2026 (race 433)
W433 = [
 ("gavin-eccles","BEL","Gavin Eccles",dict(skin=1,hair="shortcurls",hair_colour="#2E211B"),"short dark wavy hair"),
 ("samuel-dames","KEN","Samuel Dames",dict(skin=1,hair="quiff",hair_colour="#9A7650",facial="beard"),"swept-up light brown hair, beard"),
 ("tom-lole","BEL","Tom Lole",dict(skin=2,hair="crop",hair_colour="#2A1D18"),"short dark hair"),
 ("will-marshall","BEL","Will Marshall",dict(skin=1,hair="quiff",hair_colour="#6B4A2E"),"swept-up brown hair"),
 ("stephen-mcleod","HHH","Stephen McLeod",dict(skin=1,hair="crop",hair_colour="#2E211B",facial="beard"),"short dark hair, beard"),
 ("rory-orsborn","HHH","Rory Orsborn",dict(skin=1,hair="bigcurls",hair_colour="#2E211B"),"big dark curls"),
]
W433 += [
 ("thomas-dugre","BEL","Thomas Dugre",dict(skin=1,hair="quiff",hair_colour="#6B4A2E",facial="shortbeard"),"swept-up brown hair, trimmed beard"),
 ("arthur-peel","BEL","Arthur Peel",dict(skin=1,hair="crop",hair_colour="#6B4A2E",necklace="#CFCFCF"),"short brown hair, silver chain necklace"),
 ("angus-lamb","BEL","Angus Lamb",dict(skin=1,hair="quiff",hair_colour="#8E6643"),"swept-up light brown hair"),
 ("andrew-warburton","HHH","Andrew Warburton",dict(skin=1,hair="crop",hair_colour="#2E211B",facial="shortbeard"),"short dark hair, trimmed beard"),
 ("robert-laing","KEN","Robert Laing",dict(skin=1,hair="crop",hair_colour="#2E211B",facial="stubble"),"short dark hair, stubble"),
]
W433 += [
 ("toby-cooke","H/W","Toby Cooke",dict(skin=1,hair="croprecede",hair_colour="#6E5038"),"short receding brown hair"),
 ("harrison-hayman","SLH","Harrison Hayman",dict(skin=1,hair="tousled",hair_colour="#B8703E"),"tousled ginger hair"),
 ("edward-chuck","DUL","Edward Chuck",dict(skin=1,hair="crop",hair_colour="#2E211B",facial="stubble"),"short dark hair, stubble"),
]
W433 += [
 ("robert-sesemann","KEN","Robert Sesemann",dict(skin=1,hair="tousled",hair_colour="#5A3E2A",facial="littletache"),"tousled brown hair, little moustache"),
 ("eoin-molloy","BEL","Eoin Molloy",dict(skin=1,hair="quiff",hair_colour="#1E1714",necklace="#CFCFCF"),"thick dark swept-up hair, chain necklace"),
 ("ollie-garrod","BEL","Ollie Garrod",dict(skin=1,hair="crop",hair_colour="#8E6643",cap="#E8E6E1",glasses=True,facial="stubble"),"white cap, glasses, stubble"),
]
W433 += [
 ("matthew-houchell","G&G","Matthew Houchell",dict(skin=1,hair="crop",hair_colour="#5A3E2A",facial="stubble"),"short brown hair, stubble"),
 ("ben-clarke","KEN","Ben Clarke",dict(skin=1,hair="tousled",hair_colour="#5A3E2A",facial="littletache"),"wavy brown hair, little moustache"),
 ("benjamin-hilson","HOL","Benjamin Hilson",dict(skin=1,hair="messyfringe",hair_colour="#5A3E2A"),"messy brown fringe"),
]
W433 += [
 ("christopher-parker","THH","Christopher Parker",dict(skin=1,hair="tousled",hair_colour="#3A2620",rosy=True),"tousled dark brown hair"),
 ("monty-hudson","BEL","Monty Hudson",dict(skin=1,hair="curtains",hair_colour="#7A5A3E",necklace="#CFCFCF"),"curtained light brown hair, silver chain"),
 ("dan-wallis-gg","G&G","Dan Wallis",dict(skin=1,hair="crop",hair_colour="#2E211B",facial="stubble"),"short dark hair, stubble"),
 ("ben-pearce","HOL","Ben Pearce",dict(skin=1,hair="quiff",hair_colour="#3A2620"),"swept-up dark brown hair"),
]
W433 += [
 ("jacob-brockmann","THH","Jacob Brockmann",dict(skin=1,hair="crop",hair_colour="#6B4A2E"),"short brown hair"),
 ("alex-gutteridge","HHH","Alex Gutteridge",dict(skin=1,hair="quiff",hair_colour="#2A1D18",facial="beard"),"swept-up dark hair, full beard"),
 ("tom-davies","H/W","Tom Davies",dict(skin=2,hair="crop",hair_colour="#2A1D18",cap="#F2F1EC"),"white cap"),
 ("matt-wood","HHH","Matt Wood",dict(skin=1,hair="quiff",hair_colour="#5A3E2B"),"swept-up brown hair"),
 ("isaac-parker","KEN","Isaac Parker",dict(skin=1,hair="crop",hair_colour="#8E6643"),"short light brown hair"),
 ("tom-omahoney","HHH","Tom O'Mahoney",dict(skin=1,hair="fringe",hair_colour="#5A3E2B"),"brown fringe"),
 ("ed-brewer","G&G","Ed Brewer",dict(skin=1,hair="tousled",hair_colour="#4A3426",facial="shortbeard",facial_colour="#4A3426"),"tousled brown hair, short beard"),
 ("james-bartram","THH","James Bartram",dict(skin=1,hair="shortcurls",hair_colour="ginger"),"short ginger curls"),
 ("charlie-pickett","G&G","Charlie Pickett",dict(skin=1,hair="crop",hair_colour="#8E6643"),"short light brown hair"),
 ("harry-guttridge","C/C","Harry Guttridge",dict(skin=1,hair="quiff",hair_colour="#3A2620",necklace="#CFCFCF"),"swept-up dark hair, silver chain"),
 ("alex-harris","KEN","Alex Harris",dict(skin=1,hair="croprecede",hair_colour="#3A2620",facial="stubble",gaunt=True,creases=True),"receding dark hair, stubble"),
 ("tom-thornley","HOL","Tom Thornley",dict(skin=1,hair="sweptback",hair_colour="#8E6643"),"swept-back light brown hair"),
]
W433 += [
 ("thomas-renshaw","THH","Thomas Renshaw",dict(skin=1,hair="floppyrecede",hair_colour="#CC8E58"),"floppy, thinning strawberry-blond hair"),
 ("amittai-ben-israel","THH","Amittai Ben-Israel",dict(skin=1,hair="crop",hair_colour="#5A3E2B",gaunt=True),"short brown hair"),
]
for slug, club, name, kw, alt in W433:
    save(slug, figure(club, **kw))
# women's Match 3, Mitcham Common, Jan 2026 (race 434)
W434 = [
 ("molly-oconnor","KEN","Molly O'Connor",dict(skin=1,hair="ponytail",hair_colour="#2E211B"),"dark brown ponytail"),
 ("iona-cousland","KEN","Iona Cousland",dict(skin=1,hair="ponytail",hair_colour="#3A2620"),"dark brown hair tied back"),
 ("anika-schwarze-chintapatla","THH","Anika Schwarze-Chintapatla",dict(skin=3,hair="wavytie",hair_colour="#1C1714"),"dark wavy ponytail"),
 ("suzy-whatmough","RAN","Suzy Whatmough",dict(skin=1,hair="ponytail",hair_colour="#6B4A2E"),"brown ponytail"),
 ("kristina-popadich","BEL","Kristina Popadich",dict(skin=1,hair="wavytie",hair_colour="#2A1C17"),"long wavy near-black ponytail"),
 ("dillan-quinn","H/W","Dillan Quinn",dict(skin=2,hair="wavytie",hair_colour="#2A1D18"),"dark flowing ponytail"),
]
W434 += [
 ("sarah-riceman","BEL","Sarah Riceman",dict(skin=1,hair="slick",hair_colour="#C9A35F"),"blonde hair pulled back"),
 ("holly-pan","BEL","Holly Pan",dict(skin=2,hair="ponytail",hair_colour="#1C1714"),"black ponytail"),
]
W434 += [
 ("helena-keenan","HHH","Helena Keenan",dict(skin=1,hair="ponytail",hair_colour="#8E6643"),"light brown hair tied back"),
 ("eloise-bull","G&G","Eloise Bull",dict(skin=1,hair="ponytail",hair_colour="#5A3E2B"),"brown ponytail"),
 ("gemma-newport","BEL","Gemma Newport",dict(skin=1,hair="ponytail",hair_colour="#3A2620"),"dark brown ponytail"),
 ("sarah-palmer","STR","Sarah Palmer",dict(skin=1,hair="ponytail",hair_colour="#7A5A3E",sleeves="#1C1C1E"),"brown ponytail, black long-sleeve top"),
 ("sarah-palmer-ran","RAN","Sarah Palmer",dict(skin=1,hair="ponytail",hair_colour="#7A5A3E",sleeves="#1C1C1E"),"brown ponytail, black long-sleeve top"),
 ("elinor-skinner","KEN","Elinor Skinner",dict(skin=1,hair="ponytail",hair_colour="#5A3E2B",gaunt=True),"brown hair tied back"),
]
W434 += [
 ("sarah-holt","STR","Sarah Holt",dict(skin=1,hair="ponytail",hair_colour="#2E211B",gaunt=True),"dark hair tied back"),
 ("serena-carter","THH","Serena Carter",dict(skin=1,hair="topknot",hair_colour="#D9BE85"),"blonde top knot"),
 ("abbey-brooke","BEL","Abbey Brooke",dict(skin=1,hair="ponytail",hair_colour="#C9A35F"),"blonde ponytail"),
 ("becky-briggs","BEL","Becky Briggs",dict(skin=1,hair="ponytail",hair_colour="#E6D6AC"),"platinum blonde ponytail"),
 ("maddie-mastrolonardo","BEL","Maddie Mastrolonardo",dict(skin=1,hair="wavytie",hair_colour="#2A1D18",necklace="#C9A646"),"dark wavy ponytail, gold necklace"),
]
W434 += [
 ("jennifer-nandi","HHH","Jennifer Nandi",dict(skin=3,hair="ponytail",hair_colour="#141110",necklace="#C9A646"),"black ponytail, gold necklace"),
 ("ella-fennelly","BEL","Ella Fennelly",dict(skin=1,hair="ponytail",hair_colour="#9A7650"),"light brown ponytail"),
 ("natalie-beadle","BEL","Natalie Beadle",dict(skin=1,hair="ponytail",hair_colour="#D2B57E",necklace="#C9A646"),"blonde ponytail, gold necklace"),
 ("pamela-mchutchon","STR","Pamela McHutchon",dict(skin=1,hair="tousled",hair_colour="#DCD8D0",brow_colour="#A8A39A",necklace="#C9A646",gaunt=True,creases=True),"short white hair"),
]
W427 = [  # Beckenham Place, Nov 2025 (men)
 ("max-bloor","DUL","Max Bloor",dict(skin=1,hair="sweptback",hair_colour="#B8915E",necklace="#6E655C"),"swept strawberry-blond hair, pendant"),
 ("john-foxall","HHH","John Foxall",dict(skin=1,hair="crop",hair_colour="#2A1D18",facial="beard"),"short dark hair, full beard"),
 ("robin-boon","G&G","Robin Boon",dict(skin=1,hair="crop",hair_colour="#B8B5AF",brow_colour="#8C8780",gaunt=True,creases=True),"short grey hair"),
 ("joe-english","KEN","Joe English",dict(skin=1,hair="tousled",hair_colour="#8E6643"),"tousled light brown hair"),
 ("sebastian-anthony","G&G","Sebastian Anthony",dict(skin=1,hair="quiff",hair_colour="#2E211B",facial="stubble"),"full dark hair, stubble"),
 ("thomas-gardner","BEL","Thomas Gardner",dict(skin=1,hair="tousled",hair_colour="#6B4A2E",necklace="#CFCFCF"),"messy brown hair, silver chain"),
 ("brian-wilder","HHH","Brian Wilder",dict(skin=2,hair="crop",hair_colour="#3A3330",greying="sides",facial="stubble",facial_colour="#8C8780",gaunt=True,creases=True),"short greying hair, grey stubble"),
]
W427 += [
 ("george-jackson","HHH","George Jackson",dict(skin=1,hair="croprecede",hair_colour="#3A2620",gaunt=True),"receding dark hair"),
 ("james-roberts","BEL","James Roberts",dict(skin=1,hair="crop",hair_colour="#6B4A2E",gaunt=True),"short brown hair"),
 ("ed-gibson","DUL","Ed Gibson",dict(skin=1,hair="tousled",hair_colour="#6B4A2E"),"tousled brown hair"),
 ("jack-harrison","SLH","Jack Harrison",dict(skin=1,hair="crop",hair_colour="#7A5A3E"),"short brown hair"),
 ("matthew-varley","BEL","Matthew Varley",dict(skin=1,hair="quiff",hair_colour="#C9A35F"),"swept-up blond hair"),
 ("eddie-rolls","C/C","Eddie Rolls",dict(skin=1,hair="crop",hair_colour="#2E211B",facial="stubble"),"short dark hair, stubble"),
 ("phil-sanders","KEN","Phil Sanders",dict(skin=1,hair="crop",hair_colour="#B8B5AF",brow_colour="#8C8780",gaunt=True,creases=True),"short grey hair"),
 ("jon-phillips","DUL","Jon Phillips",dict(skin=1,hair="shortcurls",hair_colour="#5A3E2B",gaunt=True),"short wavy brown hair"),
 ("noah-fernandez","H/W","Noah Fernandez",dict(skin=2,hair="longcurls",hair_colour="#1C1714"),"long dark curls"),
 ("paul-calver","HHH","Paul Calver",dict(skin=1,hair="crop",hair_colour="#A9A7A3",facial="stubble",facial_colour="#8C8780",brow_colour="#6E655C",creases=True),"short grey hair, grey stubble"),
]
W427 += [
 ("jordan-weaver","KEN","Jordan Weaver",dict(skin=3,hair=None,facial="shortbeard",facial_colour="#6E3E24",brow_colour="#3A2620"),"shaved head, short reddish beard"),
]
W96 = [  # Belgrave 1996-97 club magazine
 ("junior-galley","BEL","Junior Galley",dict(skin=4,hair="buzz",hair_colour="#141110",facial="stubble"),"close-cropped hair"),
 ("tony-binda","BEL","Tony Binda",dict(skin=3,hair="crop",hair_colour="#141110",facial="thicktache",gaunt=True),"black hair, moustache"),
 ("phil-carstairs","BEL","Phil Carstairs",dict(skin=1,hair="croprecede",hair_colour="#B89A6A",brow_colour="#9A7A55"),"receding fair hair"),
 ("clive-gilby","BEL","Clive Gilby",dict(skin=1,hair="crop",hair_colour="#3A2620",gaunt=True),"short dark hair"),
 ("roger-alsop","HHH","Roger Alsop",dict(skin=1,hair="croprecede",hair_colour="#B5652E",brow_colour="#9A5A2E"),"receding ginger hair"),
 ("roger-alsop-bel","BEL","Roger Alsop",dict(skin=1,hair="croprecede",hair_colour="#B5652E",brow_colour="#9A5A2E"),"receding ginger hair"),
 ("gerry-adams","BEL","Gerry Adams",dict(skin=1,hair="shortcurls",hair_colour="#C08A50"),"wavy strawberry-blond hair"),
 ("mike-nouch","BEL","Mike Nouch",dict(skin=1,hair="quiffrecede",hair_colour="#2A1D18",creases=True),"receding dark hair"),
 ("darren-mead","BEL","Darren Mead",dict(skin=1,hair="crop",hair_colour="#5A3E2B"),"short brown hair"),
 ("james-estall","BEL","James Estall",dict(skin=1,hair="croprecede",hair_colour="#6B4A2E",gaunt=True,jaw="square"),"brown hair thinning on top, square jaw"),
]
for slug, club, name, kw, alt in W96:
    save(slug, figure(club, **kw))
W427 += [
 ("brandon-dewar","HHH","Brandon Dewar",dict(skin=1,hair="tousled",hair_colour="#5A3E2B",facial="stubble",facial_colour="#5A3E2B",gaunt=True),"tousled brown hair, stubble"),
]
for slug, club, name, kw, alt in W427:
    save(slug, figure(club, **kw))
for slug, club, name, kw, alt in W434:
    save(slug, figure(club, **kw))
save("jermaine-mays", figure("SLH", skin=3, hair="crop", hair_colour="black", necklace="#C9A646"))
save("gary-staines", figure("BEL", skin=1, hair="quiffrecede", hair_colour="#2A1D18"))
save("charlie-wyllie", figure("H/W", skin=1, hair="spiky", hair_colour="#E6D9AE", facial="stubble", facial_colour="#B89A6A", brow_colour="#B89A6A"))
save("george-cotton", figure("WOK", skin=1, hair="tousled", hair_colour="#6E4E33"))
save("cameron-reilly", figure("G&G", skin=1, hair="messyfringe", hair_colour="#8A6440"))
save("jack-dormer", figure("WOK", skin=1, hair="messyvolume", hair_colour="#86603E"))
save("lea-adamson", figure("BEL", skin=1, hair="wavytie", hair_colour="#5E3A26", necklace="#D4D4D4"))
save("max-heyden", figure("BEL", skin=1, hair="quiff", hair_colour="#7A5A3E"))
save("ian-crowe-wright", figure("BEL", skin=1, hair="tousled", hair_colour="#7E5E40"))
save("neil-wilson", figure("BEL", skin=1, hair="tuftrecede", hair_colour="#86664A", necklace="#CFCFCF", thin_brows=True))
save("lloyd-kempson", figure("BEL", skin=1, hair="quiff", hair_colour="#8A6A48", facial="stubble", facial_colour="#8A6A48", shades=True, shades_col="#1A1A1A", shades_frame="#2A2A2A", necklace="#C9A646"))
save("andy-coley-maud", figure("G&G", skin=1, hair="quiffrecede", hair_colour="#6B4A2E"))
save("dan-cliffe", figure("H/W", skin=2, hair="messyfringe", hair_colour="#241A16", facial="stubble", facial_colour="#2E2420"))
save("patrick-mcdougall", figure("BEL", skin=1, hair="horseshoe", hair_colour="#B8B5AF", gaunt=True, creases=True))
save("callum-stewart", figure("BEL", skin=1, hair="quiff", hair_colour="#2A1E19"))
save("jamie-parkinson", figure("THH", skin=1, hair="messyfringe", hair_colour="#3A2A22"))
save("phil-sesemann", figure("KEN", skin=2, hair="shortcurls", hair_colour="#2E211B"))
save("andy-coley-maud-cc", figure("C/C", skin=1, hair="quiffrecede", hair_colour="#6B4A2E"))
save("ralph-street", figure("RAN", skin=1, hair="tousled", hair_colour="#B57A45", headband="#1A1A1A", headband_thick=True))
save("jon-pepper", figure("RAN", skin=1, hair="messyfringe", hair_colour="#5E4230", gaunt=True))
save("kevin-quinn", figure("SLH", skin=1, hair="spiky", hair_colour="#3A2620", gaunt=True))
save("frank-tickner", figure("KEN", skin=1, hair="tousled", hair_colour="#A87A4E", facial="stubble", facial_colour="#B08A5E"))
save("paul-pollock", figure("KEN", skin=1, hair="messyvolume", hair_colour="#3A2820", gaunt=True))
save("chris-busaileh-hhh", figure("HHH", skin=1, hair="croppeak", hair_colour="#A85A30"))
save("james-mcmullan", figure("THH", skin=1, hair="quiff", hair_colour="#7A5638"))
save("ben-hurley", figure("BEL", skin=1, hair=None, facial="thicktache", facial_colour="#5A4030", brow_colour="#5A4030", frown="worried", creases=True))
save("alice-crane", figure("DMV", skin=1, hair="wavytie", hair_colour="#B8935E"))
save("martina-conner", figure("BEL", skin=1, hair="ponytail", hair_colour="#C2A06A"))
save("katie-snowden", figure("HHH", skin=1, hair="ponytail", hair_colour="#D2B27A"))
save("kate-axford", figure("BEL", skin=1, hair="highpony", hair_colour="#D9BC86", necklace="#C9A646"))
save("sarah-astin", figure("BEL", skin=1, hair="halfup", hair_colour="#3A2620", necklace="#D4D4D4"))
save("georgie-bruinvels", figure("SLH", skin=1, hair="curlyup", hair_colour="#C2602A"))
save("jared-martin", figure("THH", skin=1, hair="tousled", hair_colour="#3A2820"))
save("samantha-munday", figure("BEL", skin=1, hair="plait", hair_colour="#4A3226"))
save("holly-nixon", figure("BEL", skin=1, hair="ponytail", hair_colour="#C9A35F", necklace="#D4D4D4"))
save("sophie-harris", figure("BEL", skin=1, hair="plait", hair_colour="#6B4A32"))
save("isabel-brinsden", figure("E&E", skin=1, hair="wavytie", hair_colour="#C46A34"))
save("steph-hewitt", figure("BEL", skin=1, hair="ponytail", hair_colour="#3A2620"))
save("david-bowers", figure("BEL", skin=1, hair="buzzrecede", hair_colour="#C98A55", facial="stubble", facial_colour="#B8703E", brow_colour="#B8804E"))
save("stuart-major", figure("SLH", skin=1, hair="quiff", hair_colour="#8A6440"))
save("stuart-major-thh", figure("THH", skin=1, hair="quiff", hair_colour="#8A6440"))
save("bernie-ford", figure("AFD", skin=1, hair="seventies", hair_colour="#1E1714", facial="thicktache", facial_colour="#1E1714"))
save("dave-taylor", figure("HHH", skin=2, hair="croprecede", hair_colour="#5A3E2B", gaunt=True))
save("ben-reynolds", figure("THH", skin=1, hair="buzzrecede", hair_colour="#6B5A4A", gaunt=True))
save("tom-jervis", figure("H/W", skin=1, hair="quiff", hair_colour="#E3C98A", facial="stubble", facial_colour="#C9A060", brow_colour="#C9A060", rosy=True))
save("nick-torry", figure("KEN", skin=1, hair="croprecede", hair_colour="#6B4A2E", glasses=True, glasses_col="#1E1E22", gaunt=True))
save("john-bicourt", figure("BEL", skin=1, hair="seventies", hair_colour="#4A3022", facial="muttonchops", facial_colour="#4A3022"))
save("tony-harran", figure("HHH", skin=1, hair="tuftrecede", hair_colour="#4A3426", gaunt=True, creases=True))
save("robert-elphick", figure("KEN", skin=1, hair="tousled", hair_colour="#3A2820"))
save("david-ogden", figure("SLH", skin=1, hair="horseshoe", hair_colour="#A89880", gaunt=True, creases=True, brow_colour="#8A7A66"))
save("simon-coombes", figure("HHH", skin=1, hair="croppeak", hair_colour="#7A6A58", greying="sides", gaunt=True))
save("tom-south", figure("DUL", skin=1, hair="crop", hair_colour="#8A6E52", greying="sides", gaunt=True))
save("peter-giles", figure("H/W", skin=1, hair="slick", hair_colour="#BDB8AE", facial="goatee", facial_colour="#A8A39A", brow_colour="#8C8780", gaunt=True, creases=True, sleeves="#D8262E"))
save("peter-giles-thh", figure("THH", skin=1, hair="slick", hair_colour="#BDB8AE", facial="goatee", facial_colour="#A8A39A", brow_colour="#8C8780", gaunt=True, creases=True, sleeves="#D8262E"))
save("mike-farmery", figure("THH", skin=1, hair="horseshoe", hair_colour="#6E6254", glasses=True, brow_colour="#6E6254", gaunt=True, creases=True))
save("kassa-tadesse", figure("BEL", skin=5, hair="buzzrecede", hair_colour="black", gaunt=True))
save("paul-freary", figure("BEL", skin=1, hair="wavyback", hair_colour="#A88656", headband="#1A1A1A", shades=True, shades_col="#5A2A26", shades_frame="#2A2A2A", facial="stubble", facial_colour="#8A6A48", necklace="#D4D4D4", gaunt=True))
save("stephen-sharp", figure("BEL", skin=2, hair="buzzrecede", hair_colour="#6E5A40", gaunt=True, necklace="#1A1A1A"))
save("mark-miles", figure("BEL", skin=1, hair="tousled", hair_colour="#7E6040"))
save("kevin-nash", figure("BEL", skin=1, hair="bob", hair_colour="#D8BC7C", brow_colour="#A88A58"))
save("tim-watson", figure("BEL", skin=1, hair="croppeak", hair_colour="#8E6E4A", gaunt=True))
# 2005 National 12-stage winners + 1988 Wimbledon Common
save("chris-moss", figure("BEL", skin=1, hair="tousled", hair_colour="#7E5E40"))
save("richard-ward", figure("BEL", skin=1, hair="buzz", hair_colour="#8E6E4A"))
save("david-anderson", figure("BEL", skin=1, hair="crop", hair_colour="#2E211B"))
save("spencer-barden", figure("BEL", skin=1, hair="buzzrecede", hair_colour="#6B4A2E"))
save("jonathon-blackledge", figure("BEL", skin=1, hair="croppeak", hair_colour="#3A2620"))
save("peter-clarke", figure("H/W", skin=1, hair="crop", hair_colour="#5E4430", parting=True, gaunt=True))
save("mark-sinclair", figure("BEL", skin=1, hair="messyfringe", hair_colour="#241A15", gaunt=True))
save("jean-paul-wright", figure("BEL", skin=1, hair="quiff", hair_colour="#3A2620"))
save("mike-hayes", figure("BEL", skin=1, hair="tuftrecede", hair_colour="#B89A6A", gaunt=True))
save("marcello-bizio", figure("BEL", skin=2, hair="crop", hair_colour="black"))
save("ollie-foote", figure("BEL", skin=1, hair="crop", hair_colour="#6B4A2E"))
save("malachi-byansi", figure("BEL", skin=5, hair=None, gaunt=True))
save("russell-dessaix-chin", figure("BEL", skin=3, hair="longcurls", hair_colour="#1E1714", headband="#F2F2F0", headband_thick=True, gaunt=True))
save("james-kelly", figure("BEL", skin=1, hair="crop", hair_colour="#3A2A20", gaunt=True))
save("alan-black", figure("BEL", skin=1, hair="sweptback", hair_colour="#5A4030", gaunt=True))
# 1979 Surrey youths road relay winners
save("david-north", figure("BEL", skin=1, hair="messyvolume", hair_colour="#2E211B"))
save("mark-waller", figure("BEL", skin=1, hair="shortcurls", hair_colour="#2E211B", glasses=True))
save("john-gladwin", figure("BEL", skin=1, hair="fringe", hair_colour="#6B4A2E"))
# 1965 Belgrave club 10, Wimbledon Common
save("chris-keavey", figure("BEL", skin=1, hair="sweptback", hair_colour="#2A1E18"))
save("john-moore", figure("BEL", skin=1, hair="quiff", hair_colour="#241A15", facial="moustache", facial_colour="#241A15"))
save("john-bromley", figure("BEL", skin=1, hair="croprecede", hair_colour="#9A8A74", gaunt=True, creases=True))
save("don-maclean", figure("BEL", skin=1, hair="shortcurls", hair_colour="#2E211B"))
save("chris-greenwood", figure("KEN", skin=1, hair=None, facial="shortbeard", facial_colour="#4A3E36", brow_colour="#3A2E26", gaunt=True))
save("dame-dibaba", figure("KEN", skin=4, hair="shortcurls", hair_colour="black", facial="shortbeard", facial_colour="#1C1714", gaunt=True))
save("nick-acfield", figure("KEN", skin=1, hair="shortcurls", hair_colour="#7A5A3A", glasses="round", glasses_col="#3A2E26"))
save("olly-buck", figure("KEN", skin=1, hair="messyfringe", hair_colour="#3A2A20", mud=True))
save("max-nicholls", figure("KEN", skin=2, hair="messyvolume", hair_colour="#2E211B"))
save("nic-lukies", figure("BEL", skin=1, hair="wavyback", hair_colour="#B5602E", facial="moustache", facial_colour="#A0542A", brow_colour="#A0542A"))
save("jon-pepper-slh", figure("SLH", skin=1, hair="messyfringe", hair_colour="#5E4230", gaunt=True))
save("lewis-lloyd", figure("HHH", skin=1, hair="buzz", hair_colour="#D8BE8A", brow_colour="#C4A876", gaunt=True))
save("vic-maughan", figure("HHH", skin=3, hair="buzzrecede", hair_colour="#4A423C", gaunt=True, creases=True))
save("lucy-macalister", figure("THH", skin=1, hair="ponytail", hair_colour="#6B4A2E", shades=True, shades_col="#2A2E3A", shades_frame="#D0507A", gaunt=True))
save("julia-bleasdale", figure("THH", skin=1, hair="ponytail", hair_colour="#A8875A", gaunt=True))  # 2012 Olympian, scraped-back dark blonde ponytail
save("elizabeth-apsley", figure("THH", skin=1, hair="long", hair_colour="#D8BC86"))  # long straight fair hair swept back
save("dorchie-cockerell", figure("THH", skin=1, hair="longstraight", hair_colour="#5A4030"))  # nee Lee; long straight brown hair
save("chrissie-wellington", figure("BEL", skin=2, hair="longcurls", hair_colour="#C9A060"))  # 4x Ironman world champion; long blonde curls
save("alex-bruce-littlewood", figure("H/W", skin=1, hair="quiff", hair_colour="#7A5232"))  # short light-brown hair pushed up
save("simon-rayner", figure("BOX", skin=2, hair="buzzrecede", hair_colour="#6B5A4A", gaunt=True, shades=True, shades_col="#5A2A3A", shades_frame="#2A2A2A"))  # latest SL club Boxers (1995-97); cropped receding hair, sports shades
save("simon-rayner-hw", figure("H/W", skin=2, hair="buzzrecede", hair_colour="#6B5A4A", gaunt=True, shades=True, shades_col="#5A2A3A", shades_frame="#2A2A2A"))  # Hercules Wimbledon years, 1989-95
save("luke-caldwell", figure("DMV", skin=1, hair="messyvolume", hair_colour="#2E2018", facial="stubble", facial_colour="#3A2A20", gaunt=True))  # dark messy hair, stubble, lean
save("alice-braham", figure("THH", skin=2, hair="wavytie", hair_colour="#BC965F", gaunt=True))  # sun-streaked wavy blonde tied back, lean, tanned
save("john-foss", figure("SLH", skin=1, hair="croprecede", hair_colour="#CFC9BE", brow_colour="#9A948A", gaunt=True, creases=True))
save("david-symons", figure("THH", skin=1, hair="croppeak", hair_colour="#4A3628", gaunt=True, creases=True))
save("steve-smythe", figure("DUL", skin=2, hair="croprecede", hair_colour="#3A2E26", shades=True, shades_col="#1E2228", shades_frame="#2A2A2A", gaunt=True))
save("steve-smythe-hhh", figure("HHH", skin=2, hair="croprecede", hair_colour="#3A2E26", shades=True, shades_col="#1E2228", shades_frame="#2A2A2A", gaunt=True))
save("clare-pauzers", figure("HHH", skin=1, hair="wavyback", hair_colour="#7A3A24", thin_brows=True, gaunt=True))
save("james-murray", figure("KEN", skin=1, hair="sweptback", hair_colour="#3A2820", facial="mostubble", facial_colour="#3A2820"))
save("phil-woodford-smith", figure("KEN", skin=1, hair="slick", hair_colour="#241A15", facial="shortbeard", facial_colour="#1C1410"))
save("james-ewing", figure("KEN", skin=3, hair="crop", hair_colour="#241A15", gaunt=True))
save("cameron-dockerill", figure("KEN", skin=1, hair="quiff", hair_colour="#3A2820"))
save("simon-wurr", figure("THH", skin=1, hair="tuftrecede", hair_colour="#2E211B", greying="sides", gaunt=True))
save("mike-cummings", figure("HHH", skin=1, hair="buzz", hair_colour="#C8B8A4", gaunt=True))
save("tom-conlon", figure("HHH", skin=1, hair="croppeak", hair_colour="#3A2E26", greying="sides", gaunt=True, creases=True))
save("molly-smith", figure("HHH", skin=1, hair="lowbun", hair_colour="#7A5638", scrunchie="#C8202A", thin_brows=True, necklace="#E8E2D8"))
save("arlo-ludewick", figure("HHH", skin=1, hair="tousled", hair_colour="#7A5236"))



# Belgravian archive photos, batch 1 (Oct 2026): 1960s-70s Belgrave runners from The Belgravian.
# Hair colour inferred from black-and-white photos (tone only) - revise if anyone remembers otherwise.
save("adrian-major", figure("BEL", skin=1, hair="shortcurls", hair_colour="dark brown", gaunt=True))
save("bill-kerr", figure("BEL", skin=1, hair="quiff", hair_colour="dark brown", gaunt=True, jaw="narrow"))
save("brian-gorman", figure("BEL", skin=1, hair="messyvolume", hair_colour="#2A1E18"))
save("charlie-dabbs", figure("BEL", skin=1, hair="quiff", hair_colour="#241A15", glasses="square", glasses_col="#1E1E1E"))
save("charlie-manning", figure("BEL", skin=1, hair="quiffrecede", hair_colour="mid brown", gaunt=True, creases=True))
save("john-davies", figure("BEL", skin=1, hair="messyvolume", hair_colour="#1F1612", gaunt=True))
save("pat-newell", figure("BEL", skin=1, hair="croprecede", hair_colour="light brown", rosy=True))

# Belgravian archive photos, batch 2 (Oct 2026). Hair colour inferred from black-and-white photos.
save("tony-fairclough", figure("BEL", skin=1, hair="tousled", hair_colour="dark brown", gaunt=True))
save("trevor-hart", figure("BEL", skin=1, hair="shortcurls", hair_colour="dark brown", jaw="square"))
save("ron-linstead", figure("BEL", skin=1, hair="quiff", hair_colour="#241A15", gaunt=True, jaw="narrow"))
save("john-baker", figure("BEL", skin=1, hair="horseshoe", hair_colour="#BBA98C", brow_colour="#9A8A70", gaunt=True, creases=True))
save("simon-holmes", figure("BEL", skin=1, hair="seventies", hair_colour="dark brown"))
save("mike-kortenray", figure("H/W", skin=1, hair="shaggyrecede", hair_colour="light brown", facial="beard", facial_colour="#8E6643"))
save("geoff-biscoe", figure("MIT", skin=1, hair="quiff", hair_colour="dark brown"))
save("john-lee", figure("CRO", skin=1, hair="long", hair_colour="#241A15", gaunt=True))

# Belgravian archive photos, batch 3 (Oct 2026). B/w photos except the Chastons (colour).
save("andy-north", figure("BEL", skin=1, hair="messyvolume", hair_colour="#B8955A", brow_colour="#8E6E45"))
save("charlie-dickinson", figure("BEL", skin=1, hair="quiffrecede", hair_colour="#3A2A20", gaunt=True, creases=True))
save("dave-beaver", figure("BEL", skin=1, hair="messyvolume", hair_colour="#241A15", gaunt=True))
save("john-mather", figure("BEL", skin=1, hair="croprecede", hair_colour="light brown", rosy=True))
save("jon-hobbs", figure("BEL", skin=1, hair="quiff", hair_colour="#241A15"))
save("justin-chaston", figure("BEL", skin=2, hair="messyvolume", hair_colour="#3A2A20", gaunt=True))  # Steve: a bit more hair
save("matt-chaston", figure("BEL", skin=1, hair="messyvolume", hair_colour="#7A4528", rosy=True))
save("mark-anderson", figure("BEL", skin=1, hair="croprecederound", hair_colour="dark brown", jaw="square"))  # Steve chose option 4

# Belgravian archive photos, batch 4 (Oct 2026). B/w photos except Kimaiyo and Dent (colour).
save("martin-lake", figure("BEL", skin=1, hair="quiff", hair_colour="dark brown", jaw="square"))
save("martin-lewington", figure("BEL", skin=1, hair="quiffrecede", hair_colour="#2E211B", gaunt=True))
save("pete-gardner", figure("BEL", skin=1, hair="quiff", hair_colour="#2E211B", gaunt=True))
save("ray-foley", figure("BEL", skin=1, hair="croprecede", hair_colour="light brown", rosy=True))
save("richard-langley", figure("BEL", skin=1, hair="messyvolume", hair_colour="#241A15", facial="shortbeard", facial_colour="#241A15"))
save("don-faircloth", figure("CRO", skin=1, hair="croprecede", hair_colour="#2E211B", gaunt=True))
save("john-kimaiyo", figure("BEL", skin=6, hair="buzz", hair_colour="black", gaunt=True))
save("martin-dent", figure("BEL", skin=1, hair="buzz", hair_colour="light brown"))

# Belgravian archive photos, batch 5 (Oct 2026): Belgrave women, colour photos from Alan Mead's galleries and The Belgravian.
save("catherine-bryson", figure("BEL", skin=1, hair="messyvolume", hair_colour="#E6D29A", brow_colour="#B89A62", rosy=True))
save("gabby-collison", figure("BEL", skin=1, hair="lowbun", hair_colour="#241A15", gaunt=True))
save("jodie-favell", figure("BEL", skin=1, hair="topknot", hair_colour="#D9BC78", brow_colour="#A88C5A", rosy=True))
save("louise-cooper", figure("BEL", skin=1, hair="ponytail", hair_colour="#B8955A", brow_colour="#8E6E45", gaunt=True))
save("sarah-murphy", figure("BEL", skin=1, hair="ponytail", hair_colour="#2E211B"))
save("tilly-heaton", figure("C/C", skin=1, hair="ponytail", hair_colour="#241A15", gaunt=True))
save("tilly-heaton-bel", figure("BEL", skin=1, hair="ponytail", hair_colour="#241A15", gaunt=True))
save("vicky-clarke", figure("BEL", skin=1, hair="ponytail", hair_colour="#9A6A3A", brow_colour="#7A5236"))

# Belgravian archive photos, batch 6 (Oct 2026): redraws from colour photos in Alan Mead's galleries
# (later saves replace the earlier versions of these portraits above).
save("david-anderson", figure("BEL", skin=1, hair="spiky", hair_colour="#2E211B", jaw="square"))
save("james-kelly", figure("BEL", skin=1, hair="tuftrecede", hair_colour="#3A2A20", gaunt=True))
save("john-gladwin", figure("BEL", skin=1, hair="spiky", hair_colour="#8E6643", brow_colour="#6B4A2E"))
save("kevin-nash", figure("BEL", skin=1, hair="curtains", hair_colour="#D8BC7C", brow_colour="#A88A58", gaunt=True))
save("mark-miles", figure("BEL", skin=1, hair="messyfringe", hair_colour="#7E6040", jaw="square"))
save("ollie-foote", figure("BEL", skin=1, hair="messyvolume", hair_colour="#2E211B", gaunt=True))
save("spencer-barden", figure("BEL", skin=1, hair="quiffrecede", hair_colour="#9A8A78", brow_colour="#6E5E4C", gaunt=True))
save("will-cockerell", figure("BEL", skin=1, hair="horseshoe", hair_colour="#4A3A2E", gaunt=True))

# Belgravian archive photos, batch 7 (Oct 2026): 1960s Belgrave, black-and-white photos (hair colour inferred).
save("gerry-north", figure("BEL", skin=1, hair="messyvolume", hair_colour="#2E211B", jaw="square", creases=True))
save("geoff-north", figure("BEL", skin=1, hair="quiff", hair_colour="#2E211B"))
save("laurie-ohara", figure("BEL", skin=1, hair="messyvolume", hair_colour="#A88458", brow_colour="#7A5E3E"))
save("chris-steer", figure("BEL", skin=1, hair="messyvolume", hair_colour="dark brown", jaw="square"))
save("barry-sawyer", figure("BEL", skin=1, hair="croprecede", hair_colour="dark brown"))
save("charlie-walker", figure("BEL", skin=1, hair="quiff", hair_colour="#2E211B", jaw="narrow"))
save("john-dear", figure("BEL", skin=1, hair="messyvolume", hair_colour="#241A15", glasses="square", glasses_col="#1E1E1E"))
save("michael-baker", figure("BEL", skin=1, hair="tousled", hair_colour="#2E211B"))

# Belgravian archive photos, batch 8 (Oct 2026): 1970s, black-and-white photos (hair colour inferred).
save("pat-oconnor", figure("BEL", skin=1, hair="messyvolume", hair_colour="#2E211B", gaunt=True))
save("colin-pearson", figure("BEL", skin=1, hair="quiff", hair_colour="#241A15", jaw="square"))
save("jim-rimmer", figure("BEL", skin=1, hair="quiffrecede", hair_colour="#2E211B", gaunt=True, jaw="narrow"))
save("john-stow", figure("BEL", skin=1, hair="messyvolume", hair_colour="#241A15", gaunt=True))
save("fred-paget", figure("BEL", skin=1, hair="quiffrecede", hair_colour="#241A15", gaunt=True))
save("bill-weller", figure("BEL", skin=1, hair="crop", hair_colour="light brown", facial="moustache", facial_colour="#6B4A2E", gaunt=True))
save("bill-weller-wal", figure("WAL", skin=1, hair="crop", hair_colour="light brown", facial="moustache", facial_colour="#6B4A2E", gaunt=True))
save("doug-maughan", figure("BEL", skin=1, hair="crop", hair_colour="mid brown"))
save("john-roberts", figure("SLH", skin=1, hair="quiffrecede", hair_colour="#2E211B", gaunt=True))

# Belgravian archive photos, batch 9 (Oct 2026): black-and-white photos (hair colour inferred).
save("norman-stairs", figure("BEL", skin=1, hair="quiffrecede", hair_colour="mid brown", gaunt=True))
save("jack-hampshire", figure("BEL", skin=1, hair="quiff", hair_colour="#241A15", glasses="square", glasses_col="#1E1E1E", gaunt=True))
save("ranjit-bhatia", figure("BEL", skin=4, hair="crop", hair_colour="black", facial="littletache", gaunt=True))
save("graham-macky", figure("BEL", skin=1, hair="seventies", hair_colour="dark brown", facial="beard"))
save("frank-ward", figure("BEL", skin=1, hair="messyvolume", hair_colour="#241A15", facial="thicktache"))
save("kevin-sturman", figure("BEL", skin=1, hair="messyvolume", hair_colour="#B8955A", brow_colour="#8E6E45", jaw="square"))
save("stuart-paton", figure("BEL", skin=1, hair="sweptback", hair_colour="#2E211B", gaunt=True))
save("andy-paton", figure("BEL", skin=1, hair="quiffrecede", hair_colour="#2E211B", gaunt=True))

# Jaw shapes (Steve, Oct 2026): three options - "round" (the default HEAD), "square" and "narrow".
# Belgravian archive / Alan Mead gallery photos, batch 10 (Oct 2026): mostly colour photos.
save("adam-leane", figure("BEL", skin=1, hair="crop", hair_colour="#3A2620", jaw="round"))
save("alan-mead", figure("BEL", skin=1, hair=None, facial="stubble", facial_colour="#B9B3AA", glasses=True, jaw="round", creases=True))
save("charles-herrington", figure("BEL", skin=1, hair="crop", hair_colour="#3A2620", cap="#F2F1EC", jaw="round"))
save("clive-shippen", figure("BEL", skin=1, hair="floppyrecede", hair_colour="#3A2A20", gaunt=True, jaw="narrow"))
save("neil-speaight", figure("BEL", skin=1, hair="messyfringe", hair_colour="#3A2620", jaw="square"))
save("knut-hegvold", figure("H/W", skin=1, hair="spiky", hair_colour="#4A3428", gaunt=True, jaw="narrow"))
save("knut-hegvold-bel", figure("BEL", skin=1, hair="spiky", hair_colour="#4A3428", gaunt=True, jaw="narrow"))
save("clive-gilby", figure("BEL", skin=1, hair="croppeak", hair_colour="#3A2620", gaunt=True, jaw="narrow"))
# Gary Staines: main portrait in his most recent club (South London Harriers, 2000-02); Belgrave version for his earlier years
save("gary-staines", figure("SLH", skin=1, hair="messyvolume", hair_colour="#241A15", gaunt=True, jaw="narrow"))
save("gary-staines-bel", figure("BEL", skin=1, hair="messyvolume", hair_colour="#241A15", gaunt=True, jaw="narrow"))

# Belgravian archive / Alan Mead gallery photos, batch 11 (Oct 2026). B/w except Hayes and Ashe (colour).
save("bob-smith", figure("BEL", skin=1, hair="messyvolume", hair_colour="#2E211B", jaw="round"))
save("catherine-eastham", figure("BEL", skin=1, hair="lowbun", hair_colour="#B8955A", brow_colour="#8E6E45", jaw="round"))
save("don-anderson", figure("BEL", skin=1, hair="quiff", hair_colour="#2E211B", jaw="round"))
save("karen-fenner", figure("W/W", skin=1, hair="tightbun", hair_colour="#3A2620", jaw="round"))
save("marco-mazzotta", figure("BEL", skin=1, hair="quiff", hair_colour="#241A15", gaunt=True, jaw="narrow"))
save("mike-hayes", figure("BEL", skin=1, hair="shaggyrecede", hair_colour="#B89A6A", brow_colour="#8E7550", gaunt=True, jaw="narrow"))
save("richard-ashe", figure("BEL", skin=1, hair="spiky", hair_colour="#241A15", jaw="square"))
save("yacin-yusuf", figure("BEL", skin=6, hair="buzz", hair_colour="black", gaunt=True, jaw="narrow"))

# Jon Solly (Herne Hill Harriers), photo from Steve, Oct 2026: short textured dark brown hair, short sides, prominent ears, longish face
save("jon-solly", figure("HHH", skin=1, hair="shortcurls", hair_colour="dark brown", jaw="narrow"))

# Batch 12 (Oct 2026): Hercules Wimbledon history pages, The Belgravian and Alan Mead's galleries.
# Black-and-white photos: hair colour inferred from tone (dark -> dark brown).
B12 = [
 ("mike-fuller", "H/W", dict(skin=1, hair="longcurls", hair_colour="dark brown", facial="thicktache")),  # redraw from 1975 colour photo
 ("rory-mcmahon", "H/W", dict(skin=1, hair="crop", hair_colour="#D9B56E", facial="stubble", facial_colour="#B8935A")),
 ("gina-galbraith", "H/W", dict(skin=1, hair="ponytail", hair_colour="#6B4A32")),
 ("lisa-thomas", "VAC", dict(skin=1, hair="ponytail", hair_colour="#9C5B3A")),  # most recent club VAC 2026/27
 ("lisa-thomas-hw", "H/W", dict(skin=1, hair="ponytail", hair_colour="#9C5B3A")),
 ("ray-odonoghue", "HHH", dict(skin=1, hair="quiffrecede", hair_colour="dark brown", jaw="narrow", creases=True)),  # b/w guess
 ("dave-beard", "H/W", dict(skin=1, hair="croprecede", hair_colour="dark brown", gaunt=True, jaw="narrow")),  # b/w guess
 ("pete-carton", "BEL", dict(skin=1, hair="shaggyrecede", hair_colour="dark brown")),  # b/w guess
 ("dick-piotrowski", "BEL", dict(skin=1, hair="tousled", hair_colour="dark brown")),  # b/w guess
 ("chris-moss", "BEL", dict(skin=1, hair="messyfringe", hair_colour="#9A7550", jaw="square")),  # redraw from colour photo
]
for slug, kit, kw in B12:
    save(slug, figure(kit, **kw))

# Batch 13 (Oct 2026): top Surrey League athletes from the Kent AC, Thames Hare & Hounds and Herne Hill club websites.
B13 = [
 ("teresa-murphy", "KEN", dict(skin=1, hair="ponytail", hair_colour="#E3C77F", headband="#F2D21B")),
 ("isabel-bradley", "KEN", dict(skin=1, hair="ponytail", hair_colour="#4A3020")),
 ("peter-lighting", "KEN", dict(skin=1, hair="crop", hair_colour="#9C7A55", shades=True, jaw="narrow")),
 ("joe-hartley", "KEN", dict(skin=1, hair="tousled", hair_colour="#8A6440", jaw="narrow")),
 ("neil-phillips", "KEN", dict(skin=1, hair="crop", hair_colour="ginger", facial="stubble", facial_colour="#C47A3A", jaw="narrow")),
 ("sarah-hanley", "KEN", dict(skin=1, hair="ponytail", hair_colour="#6E4A30")),
 ("ben-harding", "KEN", dict(skin=1, hair="crop", hair_colour="#3A2A20", jaw="narrow")),
 ("jonathan-tipper", "KEN", dict(skin=1, hair="tousled", hair_colour="#4A3424", facial="stubble", jaw="narrow", creases=True)),
 ("victoria-buck", "KEN", dict(skin=1, hair="ponytail", hair_colour="#6B4A33")),
 ("alexa-parker", "KEN", dict(skin=1, hair="lowbun", hair_colour="#7A5A3C")),
 ("caoimhe-nic-fhogartaigh", "KEN", dict(skin=1, hair="bob", hair_colour="#E2C98A")),
 ("jerry-watson", "THH", dict(skin=1, hair="crop", hair_colour="#E6E4DE", facial="beard", facial_colour="#E6E4DE", glasses=True, creases=True)),  # drawn from 2026 photos (white hair)
 ("martin-shore", "THH", dict(skin=1, hair="crop", hair_colour="#8A7055", greying="sides")),
 ("ian-harkness", "THH", dict(skin=1, hair="croprecede", hair_colour="#B08E5E", facial="shortbeard", facial_colour="#B9B3A8", greying="sides", creases=True)),
 ("james-mcmullan", "THH", dict(skin=1, hair="quiff", hair_colour="#4A3424", facial="stubble")),  # redraw from Runner's World photo
 ("ruby-woolfe", "THH", dict(skin=1, hair="highpony", hair_colour="#5A3E2A")),
 ("victoria-barthelmess", "THH", dict(skin=1, hair="ponytail", hair_colour="#9A7448")),
 ("lauren-major", "THH", dict(skin=1, hair="ponytail", hair_colour="#A68458")),
 ("elizabeth-stavreski", "THH", dict(skin=2, hair="ponytail", hair_colour="#2A1E18")),
 ("natalie-seymour", "THH", dict(skin=1, hair="ponytail", hair_colour="#D9BC7E")),
 ("katy-hedgethorne", "THH", dict(skin=1, hair="bob", hair_colour="#A0522D")),
 ("gordon-pearce", "THH", dict(skin=1, hair="spiky", hair_colour="#3A2A20")),
 ("nick-altmann", "THH", dict(skin=1, hair=None, facial="stubble", facial_colour="#7A6A5A")),
 ("rebekah-edgar", "THH", dict(skin=1, hair="ponytail", hair_colour="#6B4A33")),
 ("keith-newton", "HHH", dict(skin=1, hair="tousled", hair_colour="#8A6440")),
 ("ben-paviour", "HHH", dict(skin=1, hair="floppyrecede", hair_colour="#7A5A3C", facial="stubble")),
 ("sarah-grover", "HHH", dict(skin=1, hair="ponytail", hair_colour="#8A6440")),
 ("julia-wedmore", "HHH", dict(skin=1, hair="ponytail", hair_colour="#A07E54")),
 ("grace-leyland", "HHH", dict(skin=1, hair="ponytail", hair_colour="#2E2018")),
 ("fiona-de-mauny", "HHH", dict(skin=1, hair="ponytail", hair_colour="#8A6440", jaw="narrow")),
 ("chloe-tighe", "HHH", dict(skin=1, hair="topknot", hair_colour="#5A3E2A")),
 ("cathy-ansell", "HHH", dict(skin=1, hair="ponytail", hair_colour="#3A2A20")),
 ("stacey-ward", "HHH", dict(skin=1, hair="ponytail", hair_colour="#D4B47A")),
 ("natasha-lodge", "HHH", dict(skin=1, hair="ponytail", hair_colour="#A0603A")),
 ("ella-newton", "HHH", dict(skin=1, hair="longloose", hair_colour="#C8A46E")),
]
for slug, kit, kw in B13:
    save(slug, figure(kit, **kw))

# Batch 14 (Oct 2026): Aldershot greats, photos from the Athletics Weekly archive. B/w photos: hair colour inferred from tone (mid-brown preferred).
B14 = [
 ("mick-woods", "AFD", dict(skin=1, hair="tousled", hair_colour="#5A4030", greying="sides")),  # from 2014 colour photo
 ("eddie-herridge", "AFD", dict(skin=1, hair="crop", hair_colour="#2E2018", jaw="narrow")),
 ("richard-partridge", "AFD", dict(skin=1, hair="croprecederound", hair_colour="#8A6A48")),
 ("bob-lunnon", "AFD", dict(skin=1, hair="tousled", hair_colour="#7A5A3C", facial="moustache")),
 ("robin-hudson", "AFD", dict(skin=1, hair="shortcurls", hair_colour="#2E2018")),
 ("john-kendall", "AFD", dict(skin=1, hair="fringe", hair_colour="#8A6A48", jaw="narrow")),
]
for slug, kit, kw in B14:
    save(slug, figure(kit, **kw))

# Batch 15 (Oct 2026): Athletics Weekly 24 Mar 1984 (final Surrey League race 1983/84, photo Bill Laws) and AW 2001 feature (Mike Boyle).
# B/w photos: hair colour inferred from tone (dark -> dark brown).
B15 = [
 ("paul-magner", "E&E", dict(skin=1, hair="tousled", hair_colour="#3A2A20", jaw="narrow")),
 ("gary-ribbons", "BOX", dict(skin=1, hair="messyvolume", hair_colour="#3A2A20")),  # most recent club Boxhill Racers (1987-2002)
 ("gary-ribbons-ee", "E&E", dict(skin=1, hair="messyvolume", hair_colour="#3A2A20")),
 ("dave-glassborow", "HHH", dict(skin=1, hair="shortcurls", hair_colour="#3A2A20", jaw="narrow")),
 ("mike-boyle", "HHH", dict(skin=1, hair="horseshoe", hair_colour="#3A2A20", jaw="narrow")),  # from 2001 colour photos
]
for slug, kit, kw in B15:
    save(slug, figure(kit, **kw))

# Tim Eglen (Aldershot, Farnham & District), photo from Steve, Oct 2026: short sandy-brown hair greying at the sides, lean lined face, clean-shaven
save("tim-eglen", figure("AFD", skin=1, hair="crop", hair_colour="#9C8566", greying="sides", jaw="narrow"))

# Tim Eglen redraw: no greying (Steve, Oct 2026)
save("tim-eglen", figure("AFD", skin=1, hair="crop", hair_colour="#9C8566", jaw="narrow"))

# Nick Bester (Holland Sports; earlier Herne Hill 2018/19), photo from Steve, Oct 2026: brown hair, short sides, swept-up quiff, lean face, clean-shaven
save("nick-bester", figure("HOL", skin=1, hair="quiff", hair_colour="#7A5A3C", jaw="narrow"))
save("nick-bester-hhh", figure("HHH", skin=1, hair="quiff", hair_colour="#7A5A3C", jaw="narrow"))

# Nick Bester redraw: thicker chin (Steve, Oct 2026)
save("nick-bester", figure("HOL", skin=1, hair="quiff", hair_colour="#7A5A3C", jaw="square"))
save("nick-bester-hhh", figure("HHH", skin=1, hair="quiff", hair_colour="#7A5A3C", jaw="square"))

# New facial style "boxgoatee" (Oct 2026, for Rob Norville): moustache joined to a full chin beard that runs along the jaw, cheeks clear
FACIAL["boxgoatee"] = ('<path d="M86,141 L100,138 L114,141 L116,146 L100,143.5 L84,146 Z"/>'
                       '<path d="M84,146 L88,153 L112,153 L116,146 L121,158 Q118,175 100,182 Q82,175 79,158 Z"/>')
# Rob Norville (Belgrave), belgraveharriers.com photo, Oct 2026: short tight dark curls, boxgoatee
save("robert-norville", figure("BEL", skin=5, hair="shortcurls", hair_colour="#1E1612", facial="boxgoatee", facial_colour="#1E1612"))

# ---- Chin dimple (Oct 2026): a softer, smaller mark than cleft=True (bum chin) ----
import re as _re_d
def dimple(svg, up=False):
    """Add a small chin dimple under the mouth (use for a slight chin dent; cleft=True is the full bum chin). up=True draws it as ^ instead of v."""
    m = _re_d.search(r'<path d="M89,151 L100,148 L111,151 Q100,158 89,151 Z" fill="(#[0-9A-Fa-f]{6})"/>', svg)
    if not m: return svg
    mark = (f'<path d="{'M98,163.2 Q100,160.8 102,163.2' if up else 'M98,163.5 Q100,166 102,163.5'}" stroke="{m.group(1)}" stroke-width="1.7" fill="none" '
            f'stroke-linecap="round" opacity=".8"/>')
    return svg[:m.end()] + mark + svg[m.end():]

# ---- Batch 19 (Oct 2026): shortlist Draws, part 1 ----
save("abdulla-elsadig", figure("BEL", skin=6, hair="buzz", hair_colour="black"))
save("aimee-hargreaves", figure("HHH", skin=1, hair="ponytail", hair_colour="mid brown", shades=True, shades_col="#3B5BD6"))
save("aisling-ahern", figure("KEN", skin=1, hair="ponytail", hair_colour="light brown"))
save("alex-brecker", figure("BEL", skin=3, hair="crop", hair_colour="#E6E2DA", brow_colour="#2E211B", jaw="narrow"))
save("alex-brown", figure("HHH", skin=1, hair="ponytail", hair_colour="blonde"))
save("alex-marginean", figure("HHH", skin=1, hair="longwavy", hair_colour="light brown"))
save("alex-miller", figure("BEL", skin=1, hair="buzzrecede", hair_colour="light brown", gaunt=True, jaw="narrow"))
save("alex-mills", figure("BEL", skin=1, hair="messyfringe", hair_colour="mid brown", jaw="narrow"))
save("alex-robinson", figure("H/W", skin=1, hair="quiff", hair_colour="mid brown", facial="stubble", facial_colour="#6B4A2E", jaw="square"))
save("alice-reed", figure("BEL", skin=1, hair="ponytail", hair_colour="dark brown"))
save("alison-purnell", figure("H/W", skin=1, hair="shaggyrecede", hair_colour="light brown", headband="#2C55A8", headband_thick=True, creases=True))
save("andrew-cumine", figure("BEL", skin=1, hair="messyvolume", hair_colour="dark brown", jaw="square"))
save("andrius-jaksevicius", figure("BEL", skin=1, hair="crop", hair_colour="mid brown", gaunt=True, jaw="narrow"))
save("anna-garnier", figure("THH", skin=1, hair="bob", hair_colour="light brown", creases=True))
save("anna-sharp", figure("BEL", skin=1, hair="ponytail", hair_colour="mid brown", jaw="narrow"))
save("anne-hegvold", figure("H/W", skin=1, hair="longstraight", hair_colour="mid brown", jaw="narrow"))
save("annmarie-seymour", figure("H/W", skin=1, hair="bob", hair_colour="blonde"))
save("ben-ireland", figure("BEL", skin=1, hair="crop", hair_colour="dark brown", cap="#2B3E66", facial="littletache", facial_colour="#3A2620"))
save("ben-revill", dimple(figure("H/W", skin=1, hair="messyfringe", hair_colour="light brown", creases=True)))
save("ben-toomer", figure("H/W", skin=1, hair="crop", hair_colour="dark brown", glasses=True, glasses_col="#222222", gaunt=True, jaw="narrow"))
save("bethany-brown", figure("BEL", skin=1, hair="ponytail", hair_colour="blonde"))
save("bradley-courtney-pinn", figure("BEL", skin=1, hair="quiff", hair_colour="dark brown", jaw="square"))
save("camilla-barden", figure("BEL", skin=1, hair="ponytail", hair_colour="dark brown", jaw="narrow"))
save("carl-delaney", dimple(figure("HHH", skin=1, hair="quiffrecede", hair_colour="dark brown", jaw="narrow")))
save("carolyne-baxter", figure("G&G", skin=1, hair="ponytail", hair_colour="mid brown", jaw="narrow"))
save("charlie-rogers", figure("BEL", skin=2, hair="quiff", hair_colour="black", facial="stubble", facial_colour="#1E1612", jaw="square", cleft=True))
save("charlie-sandison", figure("H/W", skin=1, hair="spiky", hair_colour="light brown", shades=True, shades_col="#2E8B57"))
save("chloe-beckett", figure("THH", skin=1, hair="ponytail", hair_colour="mid brown", headband="#2A2A2A", jaw="narrow"))
save("chris-warren", figure("BEL", skin=1, hair="messyvolume", hair_colour="black", facial="moustache", facial_colour="#1E1612"))
save("craig-ruddy", figure("BEL", skin=1, hair="crop", hair_colour="dark brown", facial="shortbeard", facial_colour="#2E211B", jaw="square"))
save("dan-wallis", figure("BEL", skin=1, hair="messyfringe", hair_colour="mid brown", jaw="square"))
save("david-walsh", figure("BEL", skin=1, hair="crop", hair_colour="dark brown", jaw="square", cleft=True))
save("david-williams", figure("G&G", skin=1, hair="crop", hair_colour="grey", jaw="square", creases=True))
save("dimos-evangelidis", figure("H/W", skin=2, hair="croprecede", hair_colour="dark brown", gaunt=True, jaw="narrow", creases=True))
save("dominic-kiralyfi", figure("H/W", skin=1, hair="messyfringe", hair_colour="light brown", shades_up=True, shades=True, shades_col="#C9A227", jaw="square"))
save("dylan-mitchard", figure("BEL", skin=1, hair="quiff", hair_colour="light brown", jaw="narrow"))
save("ed-catmur", figure("THH", skin=1, hair="croprecede", hair_colour="dark brown", glasses=True, glasses_col="#3A3A3A", facial="stubble", facial_colour="#3A2620"))
save("ella-may-hards", figure("BEL", skin=1, hair="ponytail", hair_colour="blonde", jaw="narrow"))
save("emily-barrett", figure("BEL", skin=1, hair="ponytail", hair_colour="mid brown", jaw="narrow"))
save("emily-robbins", figure("BEL", skin=1, hair="ponytail", hair_colour="blonde"))
save("estle-viljoen", figure("H/W", skin=2, hair="tightbun", hair_colour="#5A4636", creases=True))
save("felicity-cole", figure("BEL", skin=1, hair="longstraight", hair_colour="#B9B3AA", jaw="narrow"))
save("fi-maddocks", figure("BEL", skin=1, hair="longstraight", hair_colour="ginger", jaw="narrow"))
save("garret-lee", figure("BEL", skin=2, hair="quiff", hair_colour="black", jaw="square"))
save("george-loxton", figure("BEL", skin=1, hair="crop", hair_colour="mid brown", jaw="narrow"))
save("george-mallett", figure("H/W", skin=1, hair="crop", hair_colour="blonde"))
save("georgia-curry", figure("BEL", skin=2, hair="tightbun", hair_colour="dark brown", jaw="narrow"))
save("georgie-fenn", figure("BEL", skin=1, hair="ponytail", hair_colour="mid brown"))
save("grace-richardson", figure("BEL", skin=1, hair="ponytail", hair_colour="mid brown", jaw="narrow"))
save("hannah-edwards", figure("HHH", skin=1, hair="ponytail", hair_colour="light brown"))
save("heather-statham", figure("THH", skin=1, hair="ponytail", hair_colour="light brown"))
save("hector-revill", figure("H/W", skin=1, hair="curly", hair_colour="light brown", glasses=True, glasses_col="#1E1E1E"))
save("helena-corbin", figure("HHH", skin=2, hair="tightbun", hair_colour="black", jaw="narrow"))
save("henry-silverstein", figure("H/W", skin=1, hair="messyvolume", hair_colour="dark brown", jaw="narrow"))
save("imogen-mackie", figure("BEL", skin=1, hair="ponytail", hair_colour="auburn", headband="#1E1E1E", headband_thick=True, jaw="narrow"))
save("imogen-wolsey", figure("BEL", skin=1, hair="ponytail", hair_colour="blonde"))
save("james-fox", figure("BEL", skin=1, hair="crop", hair_colour="light brown", gaunt=True, jaw="narrow"))
save("james-harvey", figure("G&G", skin=1, hair="messyfringe", hair_colour="mid brown", jaw="narrow"))
save("james-wootton", figure("BEL", skin=1, hair="crop", hair_colour="light brown", jaw="narrow"))
save("jess-reed", figure("BEL", skin=1, hair="halfup", hair_colour="blonde"))
save("jess-saunders", figure("BEL", skin=1, hair="ponytail", hair_colour="blonde", jaw="narrow"))
save("jess-winfield", figure("HHH", skin=1, hair="ponytail", hair_colour="light brown", glasses=True, glasses_col="#3A2A20"))
save("jessica-davies", figure("THH", skin=1, hair="slicktail", hair_colour="dark brown", rosy=True))
save("jessica-lowe", figure("BEL", skin=2, hair="ponytail", hair_colour="black", headband="#1E1E1E", headband_thick=True, jaw="narrow"))
save("jonny-neville", figure("BEL", skin=1, hair="crop", hair_colour="light brown", facial="stubble", facial_colour="#B07A45"))
save("josephine-rhodes", figure("BEL", skin=1, hair="ponytail", hair_colour="mid brown"))
save("jurgita-levertaviciute", figure("BEL", skin=1, hair="ponytail", hair_colour="dark brown", headband="#ECE8E2", headband_thick=True))
save("justin-reid", figure("H/W", skin=1, hair="crop", hair_colour="grey", facial="stubble", facial_colour="#9A958E", creases=True, jaw="square"))
save("justine-lynch", figure("BEL", skin=1, hair="ponytail", hair_colour="light brown", headband="#1E1E1E", headband_thick=True))
save("katie-ellen-french", figure("BEL", skin=1, hair="ponytail", hair_colour="dark brown", jaw="narrow"))
save("laura-goodson", figure("BEL", skin=1, hair="ponytail", hair_colour="blonde"))
save("lizzie-goldie-scot", figure("BEL", skin=1, hair="ponytail", hair_colour="dark brown", jaw="narrow"))
save("lydia-gallyer-barnett", figure("BEL", skin=1, hair="ponytail", hair_colour="#C9935A", jaw="narrow"))
save("maddy-whitman", figure("BEL", skin=1, hair="longwavy", hair_colour="light brown"))
save("mary-setyabule", figure("HHH", skin=1, hair="tightbun", hair_colour="dark brown", glasses=True, glasses_col="#C0506A", creases=True))
save("matilde-lomba", figure("H/W", skin=2, hair="longstraight", hair_colour="dark brown", shades=True, shades_col="#1E1E1E", shades_frame="#1E1E1E", jaw="narrow"))
save("matt-jones", figure("THH", skin=1, hair="crop", hair_colour="mid brown", creases=True, jaw="square"))
save("mhairi-hall", figure("BEL", skin=1, hair="ponytail", hair_colour="dark brown", jaw="narrow"))
save("mohammed-ismail", figure("HHH", skin=5, hair="buzzrecede", hair_colour="black", facial="shortbeard", facial_colour="#1A1412", jaw="narrow"))
save("monika-gajek", figure("HHH", skin=1, hair="longwavy", hair_colour="light brown"))
save("naomi-lenane", figure("BEL", skin=1, hair="ponytail", hair_colour="dark brown", jaw="narrow"))
save("nathan-visick", figure("BEL", skin=1, hair="crop", hair_colour="mid brown", jaw="narrow"))
save("niamh-thompson", figure("H/W", skin=1, hair="ponytail", hair_colour="light brown"))
save("nick-buckle", figure("BEL", skin=1, hair="messyfringe", hair_colour="light brown", jaw="square"))
save("nick-bundle", figure("BEL", skin=1, hair="messyvolume", hair_colour="dark brown", gaunt=True, jaw="narrow"))
save("oliver-carrington", figure("H/W", skin=1, hair="crop", hair_colour="dark brown", jaw="narrow"))
save("olivia-papaioannou", figure("BEL", skin=1, hair="ponytail", hair_colour="dark brown", jaw="narrow"))
save("orna-mcginley", figure("BEL", skin=1, hair="ponytail", hair_colour="dark brown", jaw="narrow"))
save("patricia-walker", figure("BEL", skin=1, hair="ponytail", hair_colour="blonde"))
save("patrizia-gnoato", figure("HHH", skin=1, hair="longstraight", hair_colour="dark brown", jaw="narrow"))
save("paul-cheetham", figure("THH", skin=1, hair="crop", hair_colour="grey", cap="#22335A", facial="stubble", facial_colour="#9A958E", gaunt=True, jaw="narrow", creases=True))
save("ron-clark", figure("HHH", skin=1, hair="quiff", hair_colour="dark brown", jaw="square"))
save("bob-harrison", figure("HHH", skin=1, hair="buzzrecede", hair_colour="grey", shades=True, shades_col="#3A3A3A", gaunt=True, jaw="narrow", creases=True))
save("rachel-brown", figure("BEL", skin=1, hair="tightbun", hair_colour="dark brown", jaw="narrow"))
save("rebecca-barrow", figure("HHH", skin=2, hair="bigcurls", hair_colour="#8A5A32", headband="#ECE8E2"))
save("reece-edwards", figure("BEL", skin=1, hair="croprecede", hair_colour="light brown", facial="moustache", facial_colour="#8E6E45"))
save("rhys-boorman", figure("H/W", skin=1, hair="crop", hair_colour="light brown", cap="#3A3C40"))
save("richard-henderson", figure("HHH", skin=1, hair="messyvolume", hair_colour="light brown", jaw="narrow"))
save("rob-tuer", figure("H/W", skin=1, hair="crop", hair_colour="black", jaw="square"))
save("ross-christie", figure("BEL", skin=1, hair="quiff", hair_colour="mid brown", facial="shortbeard", facial_colour="#6B4A2E"))
save("ryan-mccallister", dimple(figure("H/W", skin=1, hair="messyfringe", hair_colour="light brown", jaw="square")))
save("sam-charlton", figure("BEL", skin=1, hair="crop", hair_colour="dark brown", jaw="narrow"))
save("sam-whiting", figure("HHH", skin=1, hair="spiky", hair_colour="#CBBB9C", brow_colour="#8E6E45"))
save("sarah-dewhirst", figure("BEL", skin=1, hair="ponytail", hair_colour="mid brown", jaw="narrow"))
save("simon-baines", figure("THH", skin=1, hair="crop", hair_colour="#C99A62", brow_colour="#A0784A", jaw="square"))
save("simon-wade", figure("H/W", skin=1, hair="crop", hair_colour="dark brown", creases=True, jaw="narrow"))
save("sophie-cowper", figure("BEL", skin=1, hair="tightbun", hair_colour="blonde"))
save("sophie-hicks", figure("BEL", skin=1, hair="ponytail", hair_colour="blonde"))
save("steph-mccall", figure("HHH", skin=1, hair="ponytail", hair_colour="light brown"))
save("steph-mitchell", figure("HHH", skin=1, hair="ponytail", hair_colour="auburn"))
save("steve-jones", figure("BEL", skin=1, hair="quiff", hair_colour="dark brown", facial="stubble", facial_colour="#2E211B"))
save("suzanne-swaine", figure("HHH", skin=1, hair="ponytail", hair_colour="dark brown", jaw="narrow"))
save("terry-booth", figure("G&G", skin=1, hair="buzzrecede", hair_colour="grey", gaunt=True, creases=True, jaw="narrow"))
save("toby-fletcher", figure("BEL", skin=1, hair="messyvolume", hair_colour="mid brown", jaw="square"))
save("tom-cheetham", figure("H/W", skin=1, hair="horseshoe", hair_colour="#B9A88E", gaunt=True, creases=True, jaw="narrow"))
save("tommy-taylor", figure("BEL", skin=1, hair="quiff", hair_colour="dark brown", jaw="narrow"))
save("vikki-filsell", figure("THH", skin=1, hair="bob", hair_colour="mid brown", creases=True))
save("will-lewis", figure("H/W", skin=1, hair="quiff", hair_colour="mid brown", facial="mostubble", facial_colour="#5A3E28"))
save("will-scott", figure("THH", skin=1, hair="crop", hair_colour="light brown", glasses=True, glasses_col="#1E1E1E", facial="stubble", facial_colour="#6B4A2E", jaw="narrow"))
save("will-stockley", figure("BEL", skin=1, hair="messyvolume", hair_colour="dark brown"))
save("zoe-macdonald", figure("BEL", skin=1, hair="ponytail", hair_colour="mid brown", jaw="narrow"))

# same runners in their other clubs' vests (the athlete page shows the latest club)
save("simon-wade-hhh", figure("HHH", skin=1, hair="crop", hair_colour="dark brown", creases=True, jaw="narrow"))
save("anna-garnier-hw", figure("H/W", skin=1, hair="bob", hair_colour="light brown", creases=True))
save("heather-statham-cc", figure("C/C", skin=1, hair="ponytail", hair_colour="light brown"))
save("steph-mccall-cc", figure("C/C", skin=1, hair="ponytail", hair_colour="light brown"))
save("steph-mccall-slh", figure("SLH", skin=1, hair="ponytail", hair_colour="light brown"))

# Ed Mallett redraw (Oct 2026): Steve says very blonde hair
save("mallett", figure("H/W", skin=1, hair="crop", hair_colour="#E6D29A", brow_colour="#A88A55", facial="stubble", facial_colour="#C9AE78"))

# George Mallett redraw (Oct 2026): swept-up quiff, very pale blond, as in the club photos
save("george-mallett", figure("H/W", skin=1, hair="quiff", hair_colour="#E6D29A", brow_colour="#A88A55"))

# Mallett swap (Oct 2026): Steve says George has dark hair, so the blond runner in the H/W photos is Ed
# ("George Mallet (top)" in the caption is the dark-haired runner behind)
save("mallett", figure("H/W", skin=1, hair="quiff", hair_colour="#E6D29A", brow_colour="#A88A55"))
save("george-mallett", figure("H/W", skin=1, hair="quiff", hair_colour="#2E211B", jaw="narrow"))

# ---- Eye shapes and spacing (Oct 2026). Steve approved: wide, narrow, hooded, downturned, upturned; spacing on test ----
import re as _re_e
_EL0 = "M76,112 Q85,105 94,112 Q85,117 76,112 Z"; _ER0 = "M106,112 Q115,105 124,112 Q115,117 106,112 Z"
_LL0 = "M76,112 Q85,105 94,112"; _LR0 = "M106,112 Q115,105 124,112"
EYE_SHAPES = {  # name: (left eye, right eye, left lid line, right lid line)
    "wide": ("M76,112 Q85,102 94,112 Q85,119.5 76,112 Z", "M106,112 Q115,102 124,112 Q115,119.5 106,112 Z", "M76,112 Q85,102 94,112", "M106,112 Q115,102 124,112"),
    "narrow": ("M76,112 Q85,108 94,112 Q85,114.5 76,112 Z", "M106,112 Q115,108 124,112 Q115,114.5 106,112 Z", "M76,112 Q85,108 94,112", "M106,112 Q115,108 124,112"),
    "hooded": ("M76,112 Q85,108.5 94,112 Q85,117 76,112 Z", "M106,112 Q115,108.5 124,112 Q115,117 106,112 Z", "M75,111 Q85,107.5 95,112 M76,107.5 Q85,103.5 94,107", "M105,112 Q115,107.5 125,111 M106,107 Q115,103.5 124,107.5"),
    "smallhooded": ("M78.5,112 Q85,109.5 91.5,112 Q85,115.5 78.5,112 Z", "M108.5,112 Q115,109.5 121.5,112 Q115,115.5 108.5,112 Z", "M78,111.5 Q85,108.5 92,112 M78.5,108 Q85,105.5 91.5,107.5", "M108,112 Q115,108.5 122,111.5 M108.5,107.5 Q115,105.5 121.5,108"),
    "small": ("M78.5,112 Q85,109.5 91.5,112 Q85,115.5 78.5,112 Z", "M108.5,112 Q115,109.5 121.5,112 Q115,115.5 108.5,112 Z", "M78,111.5 Q85,108.5 92,112", "M108,112 Q115,108.5 122,111.5"),
    "almond": ("M75,110.5 Q85,104 94.5,111.8 Q85,116.8 75,110.5 Z", "M105.5,111.8 Q115,104 125,110.5 Q115,116.8 105.5,111.8 Z", "M75,110.5 Q85,104 94.5,111.8", "M105.5,111.8 Q115,104 125,110.5"),
    "downturned": ("M75,115 Q85,105 94,112 Q85,118 75,115 Z", "M106,112 Q115,105 125,115 Q115,118 106,112 Z", "M75,115 Q85,105 94,112", "M106,112 Q115,105 125,115"),
    "upturned": ("M75,109 Q85,104 94,112 Q85,116 75,109 Z", "M106,112 Q115,104 125,109 Q115,116 106,112 Z", "M75,109 Q85,104 94,112", "M106,112 Q115,104 125,109"),
}
def _shift_x(d, dx):
    return _re_e.sub(r'(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)', lambda m: f"{float(m.group(1))+dx:g},{m.group(2)}", d)
def eyes(svg, shape=None, spacing=0):
    """Change eye shape (EYE_SHAPES key) and/or spacing (+ = further apart, - = closer; each eye moves this many units)."""
    el, er, ll, lr = EYE_SHAPES[shape] if shape else (_EL0, _ER0, _LL0, _LR0)
    el, ll = _shift_x(el, -spacing), _shift_x(ll, -spacing)
    er, lr = _shift_x(er, spacing), _shift_x(lr, spacing)
    svg = svg.replace(f'd="{_EL0}"', f'd="{el}"').replace(f'd="{_ER0}"', f'd="{er}"')
    svg = svg.replace(f'd="{_LL0}"', f'd="{ll}"').replace(f'd="{_LR0}"', f'd="{lr}"')
    svg = svg.replace('<circle cx="85" cy="111.5"', f'<circle cx="{85-spacing:g}" cy="111.5"').replace('<circle cx="115" cy="111.5"', f'<circle cx="{115+spacing:g}" cy="111.5"')
    # hooded: draw the hood crease as its own, finer line (the lash line keeps the normal weight)
    if " M" in ll:
        (lash_l, crease_l), (lash_r, crease_r) = ll.split(" M", 1), lr.split(" M", 1)
        m = _re_e.search(r'<g fill="none" stroke="(#[0-9A-Fa-f]{6})" stroke-width="1\.8" stroke-linecap="round"><path d="' + _re_e.escape(ll) + r'"/><path d="' + _re_e.escape(lr) + r'"/></g>', svg)
        if m:
            col = m.group(1)
            svg = (svg[:m.start()] + f'<g fill="none" stroke="{col}" stroke-width="1.8" stroke-linecap="round"><path d="{lash_l}"/><path d="{lash_r}"/></g>'
                   + f'<g fill="none" stroke="{col}" stroke-width="{HOOD_W}" stroke-linecap="round"><path d="M{crease_l}"/><path d="M{crease_r}"/></g>' + svg[m.end():])
    return svg
HOOD_W = 1.0  # hood crease line weight

# ---- Batch 20 (Oct 2026): shortlist Draws, Kent AC and Herne Hill club-archive photos ----
save("adele-prince", figure("KEN", skin=1, hair="bob", hair_colour="#5A3A28", jaw="narrow"))
save("alex-morales", figure("KEN", skin=2, hair="quiff", hair_colour="#241A15", jaw="square"))
save("alexander-marks", figure("HHH", skin=1, hair="crop", hair_colour="#B07A45", facial="stubble", facial_colour="#B07A45"))
save("alison-thomson", figure("KEN", skin=1, hair="ponytail", hair_colour="dark brown", jaw="narrow"))
save("andrea-barber", figure("KEN", skin=1, hair="longstraight", hair_colour="blonde"))
save("andrew-perfect", figure("HHH", skin=1, hair="quiff", hair_colour="grey", gaunt=True, jaw="narrow", creases=True))
save("andrew-simms", figure("HHH", skin=1, hair="croprecede", hair_colour="light brown", facial="stubble", facial_colour="#9A8468", creases=True))
save("annabel-hobday", figure("HHH", skin=1, hair="tightbun", hair_colour="light brown"))
save("annabelle-hadlow", figure("KEN", skin=1, hair="slick", hair_colour="#8A7A68", creases=True, gaunt=True))
save("ben-millar", figure("HHH", skin=1, hair="buzzrecede", hair_colour="light brown", jaw="square", creases=True))
save("che-compton", figure("KEN", skin=1, hair="crop", hair_colour="grey", creases=True, jaw="square"))
save("duncan-rimmer", figure("HHH", skin=1, hair="messyfringe", hair_colour="#9A6A3A", jaw="square"))
save("eliza-grant", figure("KEN", skin=1, hair="bob", hair_colour="dark brown"))
save("ellie-brown", figure("KEN", skin=1, hair="messyvolume", hair_colour="grey", creases=True))
save("genevieve-blanch", figure("KEN", skin=1, hair="ponytail", hair_colour="light brown", jaw="narrow"))
save("glen-keegan", figure("HHH", skin=1, hair=None, jaw="square", frown=True))
save("jake-simmonds", figure("KEN", skin=1, hair="messyfringe", hair_colour="dark brown", glasses=True, glasses_col="#1E1E1E", facial="stubble", facial_colour="#3A2620"))
save("james-bowler", figure("KEN", skin=1, hair="crop", hair_colour="light brown"))
save("james-ward", figure("HHH", skin=1, hair="crop", hair_colour="dark brown", jaw="square", creases=True))
save("jennifer-smith", figure("KEN", skin=1, hair="ponytail", hair_colour="light brown", jaw="narrow"))
save("jonathan-ratcliffe", figure("HHH", skin=1, hair="croprecede", hair_colour="dark brown", jaw="narrow"))
save("jules-gevers", figure("KEN", skin=1, hair="croprecede", hair_colour="mid brown", jaw="narrow", creases=True))
save("karina-box", figure("KEN", skin=1, hair="ponytail", hair_colour="dark brown", shades=True, shades_col="#3A1E22", shades_frame="#3A1E22"))
save("kate-williams", figure("KEN", skin=1, hair="messyfringe", hair_colour="grey", creases=True))
save("kathy-sharpe", figure("KEN", skin=1, hair="ponytail", hair_colour="dark brown"))
save("kieran-white", figure("H/W", skin=1, hair="crop", hair_colour="dark brown", jaw="narrow"))
save("laura-miles", figure("HHH", skin=1, hair="ponytail", hair_colour="mid brown"))
save("lawrence-avery", figure("KEN", skin=1, hair="messyvolume", hair_colour="#9A6A3A", jaw="square"))
save("lily-newton", figure("HHH", skin=1, hair="longstraight", hair_colour="blonde"))
save("lydia-blackmore", figure("KEN", skin=1, hair="ponytail", hair_colour="light brown"))
save("marcelo-fortes", figure("HHH", skin=2, hair="buzzrecede", hair_colour="#2E211B", facial="shortbeard", facial_colour="#2E211B"))
save("matthew-thomas", figure("KEN", skin=1, hair="messyvolume", hair_colour="#1E1612", shades=True, shades_col="#C0392B"))
save("nicky-hayes", figure("KEN", skin=1, hair="messyfringe", hair_colour="grey", glasses=True, glasses_col="#3A3A3A", creases=True))
save("nicola-cartlidge", figure("KEN", skin=1, hair="ponytail", hair_colour="mid brown", gaunt=True, jaw="narrow"))
save("raj-paranandi", figure("HHH", skin=3, hair="quiff", hair_colour="black"))
save("richard-giles", figure("KEN", skin=1, hair="crop", hair_colour="dark brown", facial="shortbeard", facial_colour="#2E211B"))
save("robert-peacock", figure("HHH", skin=1, hair="quiffrecede", hair_colour="mid brown", jaw="narrow"))
save("rowan-crichton", figure("KEN", skin=1, hair="messyfringe", hair_colour="dark brown", jaw="square"))
save("sally-urquhart", figure("KEN", skin=1, hair="ponytail", hair_colour="light brown", jaw="narrow"))
save("samuel-wilcock", figure("KEN", skin=1, hair="crop", hair_colour="dark brown", cap="#1E2A44", jaw="square", creases=True))
save("sarah-young", figure("KEN", skin=1, hair="bob", hair_colour="blonde", creases=True))
save("stuart-beaney", figure("KEN", skin=1, hair="crop", hair_colour="mid brown", facial="beard", facial_colour="#5A3E28", glasses=True, glasses_col="#1E1E1E"))
save("suze-spalding", figure("KEN", skin=1, hair="ponytail", hair_colour="dark brown", gaunt=True, jaw="narrow"))
save("tim-alexander", figure("KEN", skin=1, hair=None, jaw="square"))
save("tim-lawrence", figure("KEN", skin=1, hair="crop", hair_colour="dark brown", jaw="narrow"))
save("valdis-pauzers", figure("HHH", skin=1, hair="messyvolume", hair_colour="grey", gaunt=True, creases=True, jaw="narrow"))
save("vic-cartwright", figure("KEN", skin=1, hair="messyfringe", hair_colour="dark brown", glasses=True, glasses_col="#3A3A3A"))
save("zuzana-nemeckova", figure("KEN", skin=1, hair="slicktail", hair_colour="#2E211B", jaw="narrow"))

# Mallett, final (Oct 2026): Steve sent a photo of both - George (bib 159) blond quiff, Ed (bib 160) dark brown hair and short beard
save("george-mallett", figure("H/W", skin=1, hair="quiff", hair_colour="#E6D29A", brow_colour="#A88A55"))
save("mallett", figure("H/W", skin=1, hair="quiff", hair_colour="#5A3E2B", facial="shortbeard", facial_colour="#3A2A20", jaw="narrow"))

# Huw Lobb (THH), Oct 2026: Steve sent Man v Horse 2004 and Helsinki 2005 photos. Short receding brown hair, lean narrow face
save("huw-lobb", figure("THH", skin=1, hair="croppeak", hair_colour="#6B4A2E", gaunt=True, jaw="narrow"))

# Huw Lobb redraw (Oct 2026): Steve - mouth lines rather than cheekbones; high but straight hairline
HAIR["crophigh"] = '<path d="M65,100 C62,60 82,40 100,40 C118,40 138,60 135,100 L132,84 C131,66 127,58.5 120,57 Q100,55.5 80,57 C73,58.5 69,66 68,84 Z"/>'
save("huw-lobb", figure("THH", skin=1, hair="crophigh", hair_colour="#6B4A2E", creases=True, jaw="narrow"))

# Wayne Oxborough (THH), Oct 2026: The Belgravian, March 1998, photo (h) "Jim Estall (66) tracks Wayne Oxborough". Dark hair, dark stubble, lean
save("wayne-oxborough", figure("THH", skin=1, hair="messyfringe", hair_colour="#2E211B", facial="stubble", facial_colour="#2E211B", gaunt=True, jaw="narrow"))

# Simon Fairbrother (BOX), Oct 2026: from AAA Champs 1994 / KP Games 1995 photos (reference only). Sandy swept-back hair, broad jaw
save("simon-fairbrother", figure("BOX", skin=1, hair="spiky", hair_colour="#C08A50", brow_colour="#8E6E45", jaw="square"))

# Roger Hackney (AFD), Oct 2026: UPPA/Photoshot 1982 steeplechase photo (reference only, b&w). Thick wavy swept hair, clean-shaven, square jaw
save("roger-hackney", figure("AFD", skin=1, hair="messyvolume", hair_colour="#7E6040", jaw="square"))

# ---- Site export -------------------------------------------------------------
# Every live portrait, written to site/<slug>.svg under the exact file name the
# site uses (files/portraits/athletes/). Most portraits are saved under their
# site slug already; older ones were saved under short working names, mapped here.
SITE_NAMES = {
 "aaron-wilson": "awilson",
 "adrien-royer": "royer",
 "alex-janiaud": "janiaud",
 "alex-milne": "alex",
 "andrew-green": "green",
 "andrew-penney": "penney",
 "andy-fyfe": "fyfe",
 "andy-weir": "weir",
 "anisse-ismaili": "ismaili",
 "barnaby-day": "day",
 "ben-racle": "racle",
 "caleb-hathaway": "hathaway",
 "chris-threadgold": "threadgold",
 "conall-mcnally": "mcnally",
 "dan-pettitt": "pettitt",
 "daniel-shaw": "shaw",
 "daniel-wolff": "wolff",
 "dylan-evans": "evans",
 "ed-mallett": "mallett",
 "eoin-brady": "brady",
 "ethan-mccolgan": "mccolgan",
 "findlay-dyer": "dyer",
 "fintan-pearce": "pearce",
 "fred-slemeck": "slemeck",
 "freddie-hessian": "freddie",
 "george-gathercole": "gathercole",
 "george-ogden": "ogden",
 "henry-hart": "conall-whelan",
 "hugo-hewitt": "hewitt",
 "ian-ellwood": "ellwood",
 "indy-barnes": "barnes",
 "isaac-lutaya": "lutaya",
 "jack-brotchie": "brotchie",
 "jack-hobden": "hobden",
 "jack-kavanagh": "jack",
 "jack-millar": "millar",
 "jack-ramm": "ramm",
 "jack-woods": "woods",
 "james-blackwood": "blackwood",
 "james-preston": "preston",
 "james-stockings": "stockings",
 "jamie-crowe": "jamie",
 "jeremy-dempsey": "dempsey",
 "john-hutchins": "hutchins",
 "john-lethbridge": "lethbridge",
 "john-sanderson": "sanderson",
 "john-sanderson-dog": "sanderson_dog",
 "jonathan-collier": "collier",
 "jonny-scott": "scott",
 "josh-mitchell": "mitchell",
 "josh-snow": "downie",
 "josh-trigwell": "josh",
 "kieran-barnes": "kbarnes",
 "kitty-shepherd-cross": "kitty",
 "larry-ryan": "ryan",
 "liam-burthem": "burthem",
 "lucy-jones": "lucy",
 "mack-downie": "downie",
 "margaret-coogan": "coogan",
 "mark-tennyson": "tennyson",
 "mathew-speed": "joe-english",
 "matthew-edgar": "edgar",
 "morgan-roberts": "roberts",
 "neil-chisholm": "chisholm",
 "nick-lightfoot": "lightfoot",
 "oliver-fox": "fox",
 "oliver-reynolds": "reynolds",
 "oliver-young": "young",
 "owen-hind": "hind",
 "pancho-panchev": "panchev",
 "paskar-owor": "owor",
 "rian-mccawley": "mccawley",
 "richard-mcdowell": "mcdowell",
 "richard-ollington": "ollington",
 "rob-kelly": "kelly",
 "ronan-tanguy": "tanguy",
 "rowan-board": "board",
 "ruby-carter": "ruby",
 "sam-bramwell": "sam",
 "sam-gebreselassie": "samg",
 "sam-sommerville": "sommerville",
 "sam-tyas": "young",
 "saron-haileselase": "saron",
 "simon-coppard": "coppard",
 "sonny-nicoll": "nicoll",
 "stuart-mccallum": "mccallum",
 "suzie-harvey": "suzie",
 "tom-austin": "austin",
 "tom-foster": "foster",
 "zach-nolan": "nolan"
}
def export_site(site_dir="/home/claude/surrey-league/files/portraits/athletes", out="site"):
    """Copy every generated portrait that the site uses into out/, named as on the site."""
    import shutil
    os.makedirs(out, exist_ok=True)
    live = {f[:-4] for f in os.listdir(site_dir) if f.endswith(".svg")} if os.path.isdir(site_dir) else set()
    # also every slug registered on the site (add('slug',...) in index.html), so new portraits export too
    idx = os.path.join(os.path.dirname(os.path.dirname(site_dir)), "index.html")
    if os.path.exists(idx):
        import re as _re
        live |= set(_re.findall(r"add\('([a-z0-9-]+)',", open(idx).read()))
    for slug in sorted(live | set(SITE_NAMES)):
        src = f"v4/{SITE_NAMES.get(slug, slug)}.svg"
        if os.path.exists(src):
            shutil.copy(src, f"{out}/{slug}.svg")
# ---- Brow tilt (Oct 2026): lift the inner ends for a warm, open look; follow eye spacing ----
import re as _re_b
def brows(svg, lift=0, spacing=0, drop=0):
    """lift > 0 raises the inner ends of both brows (warm/upturned); spacing matches eyes() (- = closer); drop > 0 lowers both brows (eyes set right under them)."""
    m = _re_b.search(r'<g fill="(#[0-9A-Fa-f]{3,6})"><polygon points="([^"]+)"/><polygon points="([^"]+)"/></g>', svg)
    if not m: return svg
    def pts(s): return [tuple(float(v) for v in p.split(",")) for p in s.split()]
    def fmt(ps): return " ".join(f"{x:g},{y:g}" for x, y in ps)
    L, R = pts(m.group(2)), pts(m.group(3))
    lx = max(x for x, _ in L); rx = min(x for x, _ in R)
    L = [(x - spacing, y + drop - (lift if x >= lx - 2 else 0)) for x, y in L]
    R = [(x + spacing, y + drop - (lift if x <= rx + 2 else 0)) for x, y in R]
    new = f'<g fill="{m.group(1)}"><polygon points="{fmt(L)}"/><polygon points="{fmt(R)}"/></g>'
    return svg[:m.start()] + new + svg[m.end():]

# James Hancock, redrawn Oct 2026: tufty receding blond hair, round jaw, eyes set closer, warm upturned brows
_HANCOCK_KW = next(t[3] for v in list(globals().values()) if isinstance(v, list) and v and isinstance(v[0], tuple) and len(v[0]) == 5 for t in v if t[0] == "james-hancock")
HANCOCK_FACE = lambda svg: brows(eyes(svg, None, -2), 2.5, -2)
save("james-hancock", HANCOCK_FACE(figure("BEL", **_HANCOCK_KW)))

# John Sanderson, redrawn Oct 2026: hooded eyes, square jaw, light stubble, current dark quiff
save("sanderson", eyes(figure("G&G", skin=1, hair="quiff", hair_colour="dark brown", facial="stubble", facial_colour="#8A6A50", jaw="square"), "hooded"))
# profile-page-only version: his dog sits inside the athlete-page crop; the site animates it popping up at the end of the blink loop
save("sanderson_dog", with_dog(eyes(figure("G&G", skin=1, hair="quiff", hair_colour="dark brown", facial="stubble", facial_colour="#8A6A50", jaw="square"), "hooded"), cx=158, cy=214, s=1.2))

# Richard Ollington, redrawn Oct 2026: short dark curls, light stubble, rounded jaw, warm upturned eyes
save("ollington", eyes(figure("THH", skin=2, hair="shortcurls", hair_colour="#241A15", facial="stubble", facial_colour="#4A3A30"), "upturned"))
# profile-page-only dog versions for Penny Oliver and James Hancock (their shared spaniel), built from their batch settings
def _batch_kw(slug):
    for v in list(globals().values()):
        if isinstance(v, list) and v and isinstance(v[0], tuple) and len(v[0]) == 5:
            for t in v:
                if t[0] == slug: return t[1], t[3]
for _slug in ("penny-oliver", "james-hancock"):
    _club, _kw = _batch_kw(_slug)
    _fig = figure(_club, **_kw)
    if _slug == "james-hancock": _fig = HANCOCK_FACE(_fig)
    save(f"{_slug}-dog", with_spaniel(_fig, cx=154, cy=203, s=1.4))
SITE_NAMES["penny-oliver-dog"] = "penny-oliver-dog"
SITE_NAMES["james-hancock-dog"] = "james-hancock-dog"
# Lionel Mann, redrawn Oct 2026: shaggy receding hair greying at the sides, bushy beard, downturned eyes
save("lionel-mann", eyes(figure("BEL", skin=1, hair="shaggyrecede", hair_colour="dark brown", facial="bushybeard", greying="sides"), "downturned"))
# Steve Gardner, redrawn Oct 2026: neat mid-brown quiff, light stubble, eyes slightly closer, rosy, dark half-zip
save("steve-gardner", eyes(figure("BEL", skin=1, hair="quiff", hair_colour="#5E4430", facial="stubble", facial_colour="#7A5E48", rosy=True, jacket=("#2E3238", "#23262B", None)), None, -1))
# Angus Butler, redrawn Oct 2026: hair swept back into a bun at the back, big full beard and moustache hugging a thin face,
# small wide-set lightly hooded eyes right under the brows; his dog Max (black cockapoo) pops up on his profile page
ANGUS = lambda: brows(eyes(figure("HHH", skin=1, hair="manbun", hair_colour="#3B2A1F", facial="bigbeard", facial_colour="#3B2A1F", jaw="narrow"), "smallhooded", 3), 0, 3, 4).replace('r="3.8"', 'r="3.2"')
save("angus-butler", ANGUS())
save("angus-butler-dog", with_cockapoo(ANGUS(), cy=188))
SITE_NAMES["angus-butler-dog"] = "angus-butler-dog"
# Tish Jones (BEL), Oct 2026: wavy light-brown ponytail, narrow lean face, flushed cheeks (no visor, no shades)
save("tish-jones", figure("BEL", skin=1, hair="wavytie", hair_colour="#9A7048", jaw="narrow", gaunt=True, rosy=True))
# ---- Brow, earring and light-mud helpers (Oct 2026, first used for Mimi Corden-Lloyd) ----
import re as _rm
def archbrows(svg, col=None, lift=0):
    """Fuller, softly arched brows set low over the eyes (replaces the default brow pair)."""
    m=_rm.search(r'<g fill="(#[0-9A-Fa-f]{3,6})"><polygon points="74,100 94,97 95,102 75,105"/><polygon points="105,97 126,100 125,105 105,102"/></g>', svg)
    if not m: return svg
    c=col or m.group(1)
    L=f"95,99.8 88,{98.3-lift} 80,99.6 72.5,104.6 80,102.4 88,102.1 95,103.9"
    R=f"105,99.8 112,{98.3-lift} 120,99.6 127.5,104.6 120,102.4 112,102.1 105,103.9"
    return svg[:m.start()]+f'<g fill="{c}"><polygon points="{L}"/><polygon points="{R}"/></g>'+svg[m.end():]
def earrings(svg, col="#C9A646", pearl=False):
    """Small gold huggie hoops on both ear lobes (optional pearl drop)."""
    e=f'<g fill="none" stroke="{col}" stroke-width="1.5"><circle cx="61" cy="111" r="2.6"/><circle cx="139" cy="111" r="2.6"/></g>'
    if pearl: e+='<g fill="#F2EEE6"><circle cx="61" cy="116.4" r="1.9"/><circle cx="139" cy="116.4" r="1.9"/></g>'
    return svg.replace('</svg>', e+'</svg>', 1)
def skinmud(svg, seed=7):
    """Light cross-country mud: a few flecks and streaks on the arms and the vest (none on the face or neck)."""
    import random
    r=random.Random(seed); o=[]
    for (x0,x1,y0,y1,n) in [(34,60,206,330,9),(140,166,206,330,9),(74,126,216,330,12)]:
        for _ in range(n):
            x=r.uniform(x0,x1); y=r.uniform(y0,y1); rx=r.uniform(.6,1.8); o.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{rx*r.uniform(.7,1.3):.1f}"/>')
    o.append('<path d="M46,214 q3,6 2,13 q-3,-6 -2,-13 Z"/><path d="M153,222 q-2,7 0,14 q2,-8 0,-14 Z"/>')
    return svg.replace('</svg>', '<g fill="#5E4330" opacity=".7">'+''.join(o)+'</g></svg>', 1)
# Mimi Corden-Lloyd, redrawn Oct 2026: narrow face, dark slicked-back hair with centre parting in a bun, brows tapering to the temples,
# gold hoops through the earlobes with pearl drops, gold chain, a little cross-country mud on the arms
save("mimi-corden-lloyd", skinmud(earrings(archbrows(figure("BEL", skin=2, hair="tightbun", hair_colour="#241A15", necklace="#C9A646", parting=True, jaw="narrow")), pearl=True)))
# Tight curls (Oct 2026, first used for Sam Bramwell): a close crop edged with small round curls, with a few curl marks on top
import math as _mt
HAIR["tightcurls"] = HAIR["cropround"] + "".join(f'<circle cx="{100+35*_mt.cos(_mt.radians(195-i*15)):.1f}" cy="{72-34*_mt.sin(_mt.radians(195-i*15)):.1f}" r="5.6"/>' for i in range(15)) + "".join(f'<circle cx="{x}" cy="{y}" r="5"/>' for x, y in [(86,50),(100,46),(114,50),(78,62),(122,62),(92,58),(108,58)])
def curl_marks(svg): return svg.replace('</svg>', ''.join(f'<path d="M{x-3},{y+1} q3,-4 6,0" fill="none" stroke="#000" stroke-opacity=".18" stroke-width="1.2"/>' for x, y in [(84,48),(98,44),(112,48),(76,60),(124,60),(90,56),(106,55)]) + '</svg>', 1)
# Sam Bramwell, redrawn Oct 2026: tight strawberry-blond curls, squarer jaw, chin dimple, small eyes with light brows sitting low on them (no hood), flushed
save("sam", curl_marks(dimple(brows(eyes(figure("HHH", skin=1, hair="tightcurls", hair_colour="#D29655", brow_colour="#B98352", rosy=True, jaw="square", thin_brows=True), "small"), 0, 0, 6)).replace('r="3.8"', 'r="3.2"')))
# Jack Millar, redrawn Oct 2026: dark short curls, narrow face, bum chin, small slightly close-set eyes with thin brows sitting low, flushed, mud spatter on his vest
save("millar", brows(eyes(figure("THH", skin=1, hair="shortcurls", hair_colour="#2E211B", rosy=True, jaw="narrow", cleft=True, thin_brows=True, mud=True), "small", -1.5), 0, -1.5, 4).replace('r="3.8"', 'r="3.2"'))
# Paul Sanderson (G&G, John's dad), Oct 2026: tousled grey hair, round dark glasses, smile lines, ruddy, square jaw; also ran for Woking in the 1980s
PAUL_KW = dict(skin=1, hair="tousled", hair_colour="#C9C5BE", brow_colour="#8C857C", glasses="round", glasses_col="#3A3D42", creases=True, rosy=True, jaw="square")
save("paul-sanderson", figure("G&G", **PAUL_KW))
save("paul-sanderson-wok", figure("WOK", **PAUL_KW))
# Georgie Grgec, redrawn Oct 2026: narrow face with a broad chin and a slight ^ dimple, almond eyes set close under softly arched brows
# that taper to the temples, dark wavy ponytail, light tan, small gold hoops
save("georgie-grgec", earrings(brows(archbrows(eyes(dimple(figure("HHH", skin=2, hair="wavytie", hair_colour="#3A2A22", jaw="broadchin"), up=True), "almond")), 0, 0, 2)))
# Jack Kavanagh, redrawn Oct 2026: strawberry-blond quiff, light ginger stubble, narrow face, light brows, flushed
save("jack", figure("HOL", skin=1, hair="quiff", hair_colour="#C08A55", brow_colour="#A87A4E", rosy=True, jaw="narrow", thin_brows=True, facial="stubble", facial_colour="#C9A07A"))
# Mel Wilkins (BEL), Oct 2026: light-brown ponytail, narrow face, light brows, fine silver chain
save("mel-wilkins", figure("BEL", skin=1, hair="ponytail", hair_colour="#6E5038", brow_colour="#7E6248", jaw="narrow", thin_brows=True, necklace="#CFCFCF"))
# Zoe Doyle (BEL), Oct 2026: dark-blonde ponytail, narrow face with defined cheekbones, almond eyes, fine gold chain
save("zoe-doyle", eyes(figure("BEL", skin=1, hair="ponytail", hair_colour="#C9A86E", brow_colour="#8E7048", jaw="narrow", gaunt=True, necklace="#C9A646"), "almond"))
# Thick long plait and rounded brows (Oct 2026, first used for Amelia Pettitt)
import re as _rb
HAIR["thickplait"] = HAIR["ponytail"]
HAIR_BACK["thickplait"] = "".join(f'<ellipse cx="{137+i*1.8:.1f}" cy="{86+i*13}" rx="{10.5-i*0.45:.1f}" ry="9.5"/>' for i in range(9)) + '<path d="M148,190 L160,212 L140,212 Z"/>'
def roundbrows(svg):
    """Softly rounded, arched brows (replaces the brow pair)."""
    m = _rb.search(r'<g fill="(#[0-9A-Fa-f]{3,6})"><polygon points="[^"]+"/><polygon points="[^"]+"/></g>', svg)
    if not m: return svg
    L = "74.5,105 77.5,101 83,98.6 89,98.6 94.5,101.4 94.2,103.6 89,101.6 83.2,101.6 78.2,103.6 75.6,106.6"
    R = " ".join(f"{200-float(p.split(',')[0]):g},{p.split(',')[1]}" for p in L.split())
    return svg[:m.start()] + f'<g fill="{m.group(1)}"><polygon points="{L}"/><polygon points="{R}"/></g>' + svg[m.end():]
# Amelia Pettitt (KEN), Oct 2026: dark-blonde hair in a thick long plait, narrow face, almond eyes, rounded light brows, flushed
save("amelia-pettitt", roundbrows(eyes(figure("KEN", skin=1, hair="thickplait", hair_colour="#B89565", brow_colour="#9A7A52", jaw="narrow", thin_brows=True, rosy=True), "almond")))
# Ellen Weir (THH), Oct 2026: brown plaited ponytail, darker brows, rosy, fine gold chain, small gold hoops
save("ellen-weir", earrings(figure("THH", skin=1, hair="plait", hair_colour="#6B4A32", brow_colour="#4E3626", rosy=True, necklace="#C9A646")))
# Sam Haughian (BOH), Oct 2026: dark tousled hair, squarer jaw with a small chin dimple, lean cheeks, dark stubble,
# strong straight brows sitting low on slightly downturned eyes, silver chain
save("sam-haughian", dimple(brows(eyes(figure("BOH", skin=2, hair="tousled", hair_colour="#2A1E18", brow_colour="#221812", facial="stubble", facial_colour="#3A2C24", necklace="#D4D4D4", jaw="square", gaunt=True), "downturned"), 0, 0, 4)))
# Ross Braden (KEN), Oct 2026: dark brown floppy hair receding at the temples, narrow lean face, flushed,
# strong dark brows over lightly hooded eyes, clean-shaven
save("ross-braden", brows(eyes(figure("KEN", skin=1, hair="floppyrecede", hair_colour="#3A2A20", brow_colour="#2E211A", rosy=True, jaw="narrow", gaunt=True), "hooded"), 0, 0, 3))
# ---- Thin arched brows and a lopsided mouth (Oct 2026, first used for Alex Yee) ----
def thinarchbrows(svg):
    """Thin arched brows, set lower at the inner ends than the outer (replaces the brow pair, keeping its height)."""
    m = _rb.search(r'<g fill="(#[0-9A-Fa-f]{3,6})"><polygon points="[0-9.]+,[0-9.]+ [0-9.]+,([0-9.]+) [^"]+"/><polygon points="[^"]+"/></g>', svg)
    if not m: return svg
    dy = float(m.group(2)) - 100
    L = [(73.5,101.2),(80,99.4),(87,100.2),(94.5,102.6),(94.5,104.8),(87,102.5),(80,101.7),(74.2,102.5)]
    f = lambda pts: " ".join(f"{x:g},{y+dy:g}" for x, y in pts)
    return svg[:m.start()] + f'<g fill="{m.group(1)}"><polygon points="{f(L)}"/><polygon points="{f([(200-x, y) for x, y in L])}"/></g>' + svg[m.end():]
def lopsided(svg, side="left"):
    """A slightly wider mouth lifted at one corner (left = the viewer's left)."""
    a = "M86.5,148 L100,147.6 L113.5,151.2 Q100,157.8 86.5,148 Z" if side == "left" else "M86.5,151.2 L100,147.6 L113.5,148 Q100,157.8 86.5,151.2 Z"
    return svg.replace('<path d="M89,151 L100,148 L111,151 Q100,158 89,151 Z"', f'<path d="{a}"', 1)
# Alex Yee (KEN, Olympic triathlon champion), redrawn Oct 2026: swept-up dark quiff with faded sides, narrow face with high cheekbones,
# narrow eyes under thin arched brows that dip at the inner ends, mouth lifted on one side, gold medal
save("alex-yee", lopsided(thinarchbrows(brows(eyes(figure("KEN", skin=2, hair="quiff", temples=True, hair_colour="#3E2A1F", brow_colour="#2A1D16", medal="gold", jaw="narrow", gaunt=True), "narrow"), 0, 0, 3)), "left"))
# ---- Flat fringe, big sideways quiff and a full goatee (Oct 2026, Sam Charlton / Larry Ryan / Ben Coughlan) ----
HAIR["flatfringe"] = '<path d="M66,100 C62,58 80,38 100,38 C120,38 138,58 134,100 L132.5,84 Q131,79 126,77.5 L116,77.5 L114,73.5 L112,77.5 L99,77.5 L97,73 L95,77.5 L86,77.5 L84,74 L82,77.5 L74,77.5 Q69,79 67.5,84 Z"/>'
HAIR["sidepart"] = '<path d="M63,102 C59,64 68,46 80,39 C88,24 112,17 130,25 C143,31 147,44 141,56 C143,70 140,86 136,102 L133,85 C131,73 124,65 112,63 C100,61 90,63 81,60 C74,66 69,76 67,89 Z"/><path d="M81,60 Q79,50 82,41" fill="none" stroke="#000" stroke-opacity=".32" stroke-width="1.6" stroke-linecap="round"/><g fill="none" stroke="#000" stroke-opacity=".17" stroke-width="1.3" stroke-linecap="round"><path d="M88,44 Q110,28 134,36"/><path d="M90,54 Q114,41 138,49"/></g>'
FACIAL["fullgoatee"] = '<path fill-rule="evenodd" d="M85.5,141 L100,138 L114.5,141 L112.5,151 L109.5,162 L106,169.5 Q100,171.5 94,169.5 L90.5,162 L87.5,151 Z M91.5,146.5 L108.5,146.5 L106.5,157.5 Q100,160.5 93.5,157.5 Z"/>'
# Sam Charlton (BEL), redrawn Oct 2026: dark brown hair, very short sides and a short fringe cut flat across the forehead, pointy chin, full goatee
save("sam-charlton", brows(figure("BEL", skin=1, hair="flatfringe", hair_colour="#3A2A20", brow_colour="#2A1D16", facial="fullgoatee", facial_colour="#3A2A20", jaw="narrow"), 0, 0, 1))
# Larry Ryan (BEL), redrawn Oct 2026: big mid-brown quiff swept sideways with the parting on the other side, thick arched brows,
# eyes slightly far apart, wide square-cornered jaw to a pointed chin, smile lines from nose to mouth, silver chain
save("ryan", archbrows(eyes(figure("BEL", skin=1, hair="sidepart", hair_colour="#5A4030", brow_colour="#4A3426", jaw="widepoint", creases=True, necklace="#D4D4D4"), None, 2)))
# Ben Coughlan (BEL), Oct 2026: short dark auburn curls, long thin face with a strong chin, high cheekbones, thin warm brows, open eyes
save("ben-coughlan", curl_marks(brows(eyes(figure("BEL", skin=1, hair="tightcurls", hair_colour="#5E3322", brow_colour="#4A2A1C", thin_brows=True, jaw="broadchin", gaunt=True), None, 1), 1.5, 1)))
# ---- Thick swept hair, single hoop, cheek dimples, wide smile (Oct 2026, first used for Eoin Molloy) ----
HAIR["thickswept"] = '<path d="M64,100 C59,62 70,40 88,32 C104,25 127,27 139,41 C147,52 145,70 138,85 L136,100 L133,87 C131,77 126,71 120,69 L117,75 L112,67 C104,66 96,68 90,72 L86,66 C80,70 74,75 70,83 L67,91 Z"/><g fill="none" stroke="#000" stroke-opacity=".2" stroke-width="1.3" stroke-linecap="round"><path d="M80,48 Q102,34 128,40"/><path d="M78,60 Q102,46 134,54"/><path d="M96,64 Q114,56 132,66"/></g>'
def hoop(svg, col="#CFCFCF", side="right"):
    """One small hoop earring through the lobe (right = the viewer's right)."""
    cx = 139 if side == "right" else 61
    return svg.replace('</svg>', f'<circle cx="{cx}" cy="111" r="2.6" fill="none" stroke="{col}" stroke-width="1.5"/></svg>', 1)
def widesmile(svg):
    """A wider, open smile."""
    return svg.replace('<path d="M89,151 L100,148 L111,151 Q100,158 89,151 Z"', '<path d="M85.5,149.5 L100,147.5 L114.5,149.5 Q100,160 85.5,149.5 Z"', 1)
def cheekdimples(svg, col="#000"):
    """Little smile dimples just outside the corners of the mouth (call after widesmile, or on the standard mouth)."""
    d = '<g fill="none" stroke="' + col + '" stroke-opacity=".18" stroke-width="1.4" stroke-linecap="round"><path d="M82,145.5 Q80,150 82,155"/><path d="M118,145.5 Q120,150 118,155"/></g>'
    m = re.search(r'<path d="M8[5-9][^"]*Q100,1[56]\d[^"]*Z" fill="[^"]*"/>', svg)
    return svg[:m.end()] + d + svg[m.end():] if m else svg
# Eoin Molloy (BEL), redrawn Oct 2026: thick dark brown hair swept up and across, black headband, squarer jaw, almond eyes under
# straight dark brows, rosy cheeks, wide smile with cheek dimples, fine silver chain, small silver hoop in one ear
save("eoin-molloy", hoop(cheekdimples(widesmile(brows(eyes(figure("BEL", skin=1, hair="thickswept", hair_colour="#3B2A20", brow_colour="#2A1D16", headband="#1A1A1A", necklace="#CFCFCF", rosy=True, jaw="square"), "almond"), 0, 0, 3)))))
# Tom Higgs (SLH), Oct 2026: short tufty strawberry-blond hair receding at the corners, trimmed ginger beard on a long face,
# light ginger brows, small pale eyes, thin dark rectangular glasses, flushed
save("tom-higgs", brows(eyes(figure("SLH", skin=1, hair="tuftrecede", hair_colour="#C99A62", brow_colour="#B48552", facial="shortbeard", facial_colour="#B8733E", glasses=True, glasses_col="#2E3136", jaw="narrow", rosy=True), "small"), 0, 0, 2).replace('r="3.8"', 'r="3.2"'))
# ---- Hair slides, tapering brows and an abstract mouth-size control (Oct 2026, first used for Emma Gordon) ----
import re as _rq
def hairclips(svg, col="#B8BCC2"):
    """Two small metal hair slides, one each side of the parting."""
    return svg.replace('</svg>', f'<g fill="{col}" transform="translate(0,-40)"><rect x="-1.4" y="-6" width="2.8" height="12" rx="1.2" transform="translate(79,107) rotate(28)"/><rect x="-1.4" y="-6" width="2.8" height="12" rx="1.2" transform="translate(122,105) rotate(-28)"/></g></svg>', 1)
def taperbrows(svg, rise=1.6):
    """Brows with thick inner heads that rise gently outwards, then taper to a thin tail that dips slightly (keeps the brow height)."""
    m = _rq.search(r'<g fill="(#[0-9A-Fa-f]{3,6})"><polygon points="[0-9.]+,[0-9.]+ [0-9.]+,([0-9.]+) [^"]+"/><polygon points="[^"]+"/></g>', svg)
    if not m: return svg
    dy = float(m.group(2)) - 100
    L = [(95,99.6),(88,98.6-rise*.5),(81,98.2-rise),(76.2,99.4-rise*.6),(72.6,102.8),(76.5,102.4-rise*.3),(81,102.6-rise*.6),(88,103.4-rise*.3),(95.2,104.8)]
    f = lambda pts: " ".join(f"{x:g},{y+dy:g}" for x, y in pts)
    return svg[:m.start()] + f'<g fill="{m.group(1)}"><polygon points="{f(L)}"/><polygon points="{f([(200-x, y) for x, y in L])}"/></g>' + svg[m.end():]
def mouth(svg, width=1.0, full=1.0):
    """House-style mouth (one flat shape, skin-toned), resized only: width scales it sideways, full deepens the lower lip."""
    m = _rq.search(r'<path d="M89,151 L100,148 L111,151 Q100,158 89,151 Z" fill="([^"]*)"/>', svg)
    if not m: return svg
    x0, x1 = 100 - 11 * width, 100 + 11 * width
    d = f"M{x0:g},151 L100,148 L{x1:g},151 Q100,{151 + 7 * full:g} {x0:g},151 Z"
    return svg[:m.start()] + f'<path d="{d}" fill="{m.group(1)}"/>' + svg[m.end():]
# Emma Gordon (BEL), redrawn Oct 2026: soft rounded jaw, small eyes set a little wide, mid-brown brows sitting low with thick heads
# tapering to the temples, dark-blonde hair sleeked back from a centre parting with silver slides into a ponytail, small gold hoops,
# a slightly wider, fuller mouth, flushed
save("emma-gordon", mouth(taperbrows(hairclips(earrings(brows(eyes(figure("BEL", skin=1, hair="ponytail", hair_colour="#9A7B58", brow_colour="#6B4E3A", rosy=True), "small", 1.5), 0, 1.5, 4).replace('r="3.8"', 'r="3.2"')))), 1.1, 1.3))
# ---- Two-tone balding fuzz, heavy-topped glasses, thin sideburns (Oct 2026, first used for Ollie Garrod) ----
import re as _rg
HAIR["fuzzbald"] = ('<path opacity=".9" d="M65,102 C62,58 82,39 100,39 C118,39 138,58 135,102 L131,102 C131,86 129.5,74 126,66 C120,52 110,42 100,42 C90,42 80,52 74,66 C70.5,74 69,86 69,102 Z"/>'
    '<path opacity=".45" d="M87,44.5 Q100,40.5 113,44.5 Q109,55.5 100,56.5 Q91,55.5 87,44.5 Z"/>')  # very short sides continuing finely over a bald top, joined to a lighter island at the front of the crown
def _after_lids(svg, extra):
    """Insert extra shapes right after the eyelid lines, so they share the eyes' coordinates (the face is squashed vertically)."""
    m = _rg.search(r'<g fill="none" stroke="#[0-9A-Fa-f]{6}" stroke-width="1.8" stroke-linecap="round"><path d="M[67][^"]*"/>(?:(?!</g>).)*</g>', svg)
    return svg[:m.end()] + extra + svg[m.end():] if m else svg
def browglasses(svg, col="#2E2622"):
    """Soft rectangular glasses, wider than tall, with a heavy top rim and fine lower rims."""
    lens = lambda x: f'<path d="M{x},101 L{x+28},101 L{x+27},118 Q{x+26.5},123 {x+21},123 L{x+6},123 Q{x+1},123 {x+0.5},118 Z"/>'
    return _after_lids(svg, f'<g fill="none" stroke="{col}" stroke-width="1.1" stroke-linejoin="round">{lens(68.5)}{lens(103.5)}</g>'
        f'<g fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round"><path d="M68.5,101.5 L96.5,101.5"/><path d="M103.5,101.5 L131.5,101.5"/><path d="M96.5,102.5 Q100,100.5 103.5,102.5" stroke-width="2"/>'
        f'<path d="M68.5,102 L62.5,101" stroke-width="2"/><path d="M131.5,102 L137.5,101" stroke-width="2"/></g>')
def thinsideburns(svg, col):
    """Thin, short sideburns in front of the ears."""
    return _after_lids(svg, f'<g fill="{col}"><path d="M64.6,90 L68,90 L68.4,110 L66,110 Z"/><path d="M135.4,90 L132,90 L131.6,110 L134,110 Z"/></g>')
# Ollie Garrod (BEL), redrawn Oct 2026: very short light ginger-brown hair, balding with a small island at the front of the crown,
# heavy-topped rectangular glasses, thin sideburns, ginger moustache and chin beard around the mouth only, thin light brows, long narrow face
save("ollie-garrod", thinsideburns(browglasses(eyes(figure("BEL", skin=1, hair="fuzzbald", hair_colour="#A87A55", brow_colour="#9C7250", thin_brows=True, jaw="narrow", rosy=True, facial="fullgoatee", facial_colour="#B07A50"), None)), "#A87A55"))
# ---- Very close crop, abstract nose width (Oct 2026, first used for Paskar Owor) ----
HAIR["closebald"] = HAIR["fuzzbald"].split("/>")[0] + "/>"   # very close crop: a fine rim over an almost bald top joining short sides
def nose(svg, width=1.0, length=1.0):
    """House-style triangle nose, resized only (no nostrils or shading): width scales the base, length moves the tip down."""
    w = 4.5 * width; y = 108 + 28 * length
    return svg.replace('points="100,108 105,136 96,136"', f'points="100,108 {100+w:g},{y:g} {100-w:g},{y:g}"', 1)
# Paskar Owor (BEL), redrawn Oct 2026: very close crop, almost bald on top, round head, very dark skin, eyes set a little wide under
# thin rounded brows sitting low, smile lines from nose to mouth, broad nose
save("owor", nose(roundbrows(brows(eyes(figure("BEL", skin=6, hair="closebald", hair_colour="#1A1412", brow_colour="#0E0B0A", creases=True), None, 1.5), 0, 1.5, 4)), 2.2))
# Ethan McColgan (THH), redrawn Oct 2026: thick wavy golden-brown hair swept up with volume, long narrow face, small deep-set eyes
# under thin light-brown brows sitting low, high cheekbones, long narrow nose, flushed
save("mccolgan", nose(brows(eyes(figure("THH", skin=1, hair="messyvolume", hair_colour="#8E6A44", brow_colour="#7A5A3C", thin_brows=True, jaw="narrow", gaunt=True, rosy=True), "small"), 0, 0, 4).replace('r="3.8"', 'r="3.2"'), 0.9, 1.1))
# ---- Long face, short tufty side-swept hair, eye bags (Oct 2026, first used for Fred Slemeck) ----
HAIR["tuftsweep"] = ('<path d="M134,98 C138,76 137,58 129,47 L131,38 L120,40 L116,30 L106,34 L98,24 L90,31 L78,27 L76,37 L64,39 L68,48 L58,56 L64,62 C62,74 63,86 66,98 L68,86 C70,76 74,70 82,68 L88,74 L94,66 L102,72 L108,66 L115,72 Q125,74 130,82 L133,90 Z"/>'
    '<g fill="none" stroke="#000" stroke-opacity=".2" stroke-width="1.3" stroke-linecap="round"><path d="M120,62 Q100,46 70,46"/><path d="M112,52 Q95,38 76,36"/></g>')  # short, tufty hair lifting off the forehead and sweeping to one side, short sides
def eyebags(svg, col="#000"):
    """A faint hint of a bag just under each eye."""
    return _after_lids(svg, f'<g fill="none" stroke="{col}" stroke-opacity=".16" stroke-width="1.2" stroke-linecap="round"><path d="M77,117.2 Q83.5,120 90,117.2"/><path d="M110,117.2 Q116.5,120 123,117.2"/></g>')
# Fred Slemeck (H/W), redrawn Oct 2026: long, thin, almost rectangular face; short tufty mid-brown hair lifting off the forehead and
# sweeping right to left; brows close to the eyes, tilting up towards the middle; smallish open eyes with a hint of bags; long nose;
# wide smile with smile lines; light stubble
save("slemeck", eyebags(nose(widesmile(taperbrows(brows(eyes(figure("H/W", skin=1, hair="tuftsweep", hair_colour="#7E5E40", brow_colour="#6E5440", facial="stubble", facial_colour="#8A6A52", jaw="long", creases=True), "small"), 0, 0, 6), -1.6)), 0.9, 1.1)))
# ---- Thick hair from a side parting going two ways (Oct 2026, first used for Gary Staines) ----
HAIR["pompback"] = ('<path d="M66,96 C63,84 61,76 62,68 Q55,58 63,49 Q70,40 82,37 C96,23 124,21 136,35 C144,46 141,66 135,96 L132,84 C130,74 124,66 118,64 Q108,60 98,62 Q90,62 84,63 Q76,66 71,74 L68,86 Z"/>'
    '<path d="M82.5,63 Q81,51 82.5,38" fill="none" stroke="#fff" stroke-opacity=".3" stroke-width="1.5" stroke-linecap="round"/>'
    '<g fill="none" stroke="#fff" stroke-opacity=".13" stroke-width="1.4" stroke-linecap="round"><path d="M81,46 Q70,46 62,55"/><path d="M81,55 Q71,57 65,66"/>'
    '<path d="M88,57 Q100,39 128,35"/><path d="M95,62 Q110,47 134,45"/><path d="M107,63 Q121,55 135,58"/></g>')  # thick hair from a side parting: a little goes down one side, the rest sweeps up and back across the head (Gary Staines)
# Gary Staines, redrawn Oct 2026: thick near-black hair from a side parting (some shoots out to one side, the rest sweeps up and back),
# long face with a strong square jaw, deep-set eyes under heavy, low, knitted brows, long nose, deep nose-to-mouth lines, lean cheeks.
# Main version in South London Harriers kit (his last Surrey League club), plus his Belgrave years.
GARY = lambda kit: nose(taperbrows(brows(eyes(figure(kit, skin=1, hair="pompback", hair_colour="#231A16", brow_colour="#1E1714", creases=True, gaunt=True, jaw="square"), None, -0.5), 0, -0.5, 3.5), 1.8), 1.0, 1.15)
save("gary-staines", GARY("SLH"))
save("gary-staines-bel", GARY("BEL"))
HAIR["quiffslim"] = '<path d="M66.5,100 L66.3,85 L67,75 L68.8,66 L71.4,58.5 L74.8,52 L79,46.5 L86,38 L104,29 L122,33 L129.5,43.5 L131.6,55 L132.8,65 L133.5,75 L133.7,85 L133.5,100 L130,80 L125,67 L100,61 L75,68 L70,80 Z"/>'  # short quiff hugging a long, narrow head: no gap at the temples (Dylan Evans)
# ---- Angled brows and high cheekbones (Oct 2026, first used for Dylan Evans) ----
def angledbrows(svg, peak=1.4):
    """Straight, solid brows with thick inner heads that run level, then angle down at the outer third to a short tail (keeps the brow height)."""
    m = _rq.search(r'<g fill="(#[0-9A-Fa-f]{3,6})"><polygon points="[0-9.]+,[0-9.]+ [0-9.]+,([0-9.]+) [^"]+"/><polygon points="[^"]+"/></g>', svg)
    if not m: return svg
    dy = float(m.group(2)) - 100
    L = [(95,99.4),(86,98.8),(80,98.4-peak),(75.5,100.2),(72.4,103.4),(76,102.6),(80.4,101.6-peak*.6),(86,102.4),(95.2,104.4)]
    f = lambda pts: " ".join(f"{x:g},{y+dy:g}" for x, y in pts)
    return svg[:m.start()] + f'<g fill="{m.group(1)}"><polygon points="{f(L)}"/><polygon points="{f([(200-x, y) for x, y in L])}"/></g>' + svg[m.end():]
def cheekbones(svg, skin=1, tag="f", depth=1.0):
    """High, prominent cheekbones: a sharp-edged hollow under each cheekbone, angling from below the ear towards the mouth corner,
    with a fine light edge along the bone (use instead of gaunt=True)."""
    sk, dk, lt = SKIN[skin]
    return _after_lids(svg, f'<g clip-path="url(#h{tag})"><g fill="{dk}" opacity="{.7*depth:.2f}"><path d="M66,125 L84,123.5 Q87,124 87.5,127 L90,143 Q81,131 66,131 Z"/><path d="M134,125 L116,123.5 Q113,124 112.5,127 L110,143 Q119,131 134,131 Z"/></g>'
        f'<g fill="{lt}" opacity=".55"><path d="M66,121.5 L84,121 Q87,121.5 87.5,124 Q85,123 84,123.5 L66,125 Z"/><path d="M134,121.5 L116,121 Q113,121.5 112.5,124 Q115,123 116,123.5 L134,125 Z"/></g></g>')
# Dylan Evans (BEL), redrawn Oct 2026: short light-brown quiff fitted to a long narrow head (full hairline, no recede),
# prominent high cheekbones, solid straight brows angling down at the outer ends, long straight nose
save("evans", cheekbones(nose(angledbrows(brows(eyes(figure("BEL", skin=1, hair="quiffslim", hair_colour="#8A5E3A", brow_colour="#7A5236", jaw="long")), 0, 0, 2)), 0.9, 1.15)))
# ---- Bushy sides with a thinning floppy top, deep-set eyes, long strong chin (Oct 2026, first used for Alex Howard) ----
HAIR["floppythin"] = ('<path fill-rule="evenodd" d="M64,106 L58,102 L60,95 L56,88 L59,80 L57,72 L62,64 L66,56 C68,46 80,35 100,34 C120,34 132,46 134,56 L138,64 L143,72 L141,80 L144,88 L140,95 L142,102 L136,106 L133,90 C132,78 130,68 126,62 Q123,54 116,52 Q110,56 103,61 Q95,66 86,66.5 Q91,62 91.5,57 Q86,52.5 80,54 Q75,58 73,64 C70,70 68,80 67,90 Z'
    ' M92,48 Q101,47 109,51 Q101,49.5 92,50 Z M99,43 Q107,42.5 113,46 Q106,45 99,44.6 Z"/>')  # bushy ragged sides over the ears, thinning floppy top with a deep temple recede and scalp showing through (Alex Howard)
def sockets(svg, skin=1, tag="f", depth=1.0):
    """Deep-set eyes: soft shadow in each eye socket between the brow and the upper lid."""
    sk, dk, lt = SKIN[skin]
    return _after_lids(svg, f'<g clip-path="url(#h{tag})" fill="#4A2E22" opacity="{.16*depth:.2f}"><path d="M74,106 Q85,100 96,104 Q97,108 94.5,110 Q85,104.5 76,111 Q73.5,109 74,106 Z"/><path d="M126,106 Q115,100 104,104 Q103,108 105.5,110 Q115,104.5 124,111 Q126.5,109 126,106 Z"/></g>')
HEAD_LONGCHIN = "M68,96 C66,58 81,40 100,40 C119,40 134,58 132,96 L130,124 L128.5,149 Q127.5,159 120.5,167.5 Q112.5,176 100,176 Q87.5,176 79.5,167.5 Q72.5,159 71.5,149 L70,124 Z"  # long face, squarish jaw and a long, strong, broad chin (Alex Howard)
def longchin(svg):
    """Swap the broad-chin head (jaw="broadchin") for a longer face with a longer, stronger chin."""
    return svg.replace(HEAD_BROADCHIN, HEAD_LONGCHIN)
def chindef(svg, skin=1, tag="f"):
    """Definition under the mouth: a soft shadow in the dip between lower lip and chin."""
    sk, dk, lt = SKIN[skin]
    return _after_lids(svg, f'<path d="M92.5,161 Q100,158.6 107.5,161 Q100,164.6 92.5,161 Z" fill="{dk}"/>')
# Alex Howard (THH), redrawn Oct 2026: very dark hair, bushy ragged sides over the ears, thinning floppy top with a deep temple recede,
# long face with a squarish jaw and long strong chin, definition under the mouth, full curved brows over deep-set eyes, high cheekbones, long nose
save("alex-howard", chindef(longchin(cheekbones(sockets(nose(archbrows(eyes(figure("THH", skin=1, hair="floppythin", hair_colour="#2A1D17", brow_colour="#1E1612", jaw="broadchin"), None, -0.5)), 1.0, 1.25), depth=1.4), depth=1.3))))
HAIR["quifflow"] = '<path d="M64,100 L63,72 L72,52 L86,38 L104,29 L122,33 L134,48 L137,72 L136,100 L131.5,84 L129.5,73 L122,68 L111,71 L100,71.5 L89,71 L78,68 L70.5,73 L68.5,84 Z"/>'  # short textured quiff with only a slight recede and a lower forehead (Tom Foster)
# Tom Foster (G&G), redrawn Oct 2026: short dark textured quiff with a slight recede and greying sides, long lean face, high cheekbones,
# short dark stubble, heavy straight brows set low over deep-set eyes, long straight nose
save("foster", cheekbones(sockets(nose(angledbrows(brows(eyes(figure("G&G", skin=1, hair="quifflow", hair_colour="#2A2220", brow_colour="#221A16", facial="stubble", facial_colour="#2E2724", greying="sides", jaw="long"), None, 0), 0, 0, 4), 1.2), 0.95, 1.2), depth=1.2), depth=1.0))
# ---- Spiky top with tight sides, hair poking out behind the ears, warm shading for bleached hair (Oct 2026, first used for Morgan Roberts) ----
HAIR["spikyup"] = '<path d="M64.5,101 L61,92 L60.5,80 L58,70 L62,63 L58.5,53 L68,50 L69,39 L79,41 L83,30 L93,35 L101,24 L108,33 L118,27 L121,38 L131,36 L131,47 L141.5,53 L138,63 L142,70 L139.5,80 L139,92 L135.5,101 L132.5,90 C132,84 131,80 129,77 Q126,69 118,67 L110,69 L100,66.5 L90,69 L82,67 Q74,69 71,77 C69,80 68,84 67.5,90 Z"/>'  # messy spiky top swept up, sides kept tight above the ears (Morgan Roberts)
FACIAL["goateestubble"] = '<path fill-rule="evenodd" opacity=".2" d="M84,141 L100,137.5 L116,141 L114,152 L111,163 L107,171 Q100,173.5 93,171 L89,163 L86,152 Z M91,146.5 L109,146.5 L107,157.5 Q100,160.5 93,157.5 Z"/>'  # stubble round the mouth and on the chin only (Morgan Roberts)
def napeflicks(svg, col):
    """Hair poking out low at the back of the head, below and behind the ears (drawn behind the head and ears)."""
    g = '<g transform="translate(0,83) scale(1,0.76) translate(0,-40)">'
    f = (f'<g fill="{col}"><path d="M72,104 L64,112 L60,128 L54,146 L62,140 L63,152 L69,140 L73,146 L74,128 Z"/>'
         f'<path d="M128,104 L136,112 L140,128 L146,146 L138,140 L137,152 L131,140 L127,146 L126,128 Z"/></g>'
         f'<g clip-path="url(#rf)" fill="#000" opacity=".22"><path d="M128,104 L136,112 L140,128 L146,146 L138,140 L137,152 L131,140 L127,146 L126,128 Z"/></g>')
    i = svg.find(g)
    return svg[:i+len(g)] + f + svg[i+len(g):] if i >= 0 else svg
def warmshade(svg, col="#8A5A2A", op=".3"):
    """Shade the far side of light (blond/bleached) hair with a warm brown instead of grey, so it doesn't turn khaki."""
    return svg.replace('fill="#000" opacity=".22">', f'fill="{col}" opacity="{op}">')
# Morgan Roberts (HHH), redrawn Oct 2026: bleached messy hair swept up into spikes, tight above the ears and poking out low behind them,
# long pale face, dark straight brows set low over small deep-set eyes, defined cheekbones, long nose, fine silver chain
save("roberts", warmshade(napeflicks(cheekbones(sockets(nose(angledbrows(brows(eyes(figure("HHH", skin=1, hair="spikyup", hair_colour="#F3DA9C", brow_colour="#4A3628", necklace="#D4D4D4", jaw="long"), "small", 0.5), 0, 0.5, 4), 0.6), 1.05, 1.2), depth=1.6), depth=1.3), "#F3DA9C")))
# ---- Even brow thickening (Oct 2026, first used for Dom Nolan) ----
import re as _rt
def thickbrows(svg, w=0.9):
    """Thicken the current brow pair evenly (outlines the brow shapes in their own colour)."""
    return _rt.sub(r'<g fill="(#[0-9A-Fa-f]{3,6})"><polygon', lambda m: f'<g fill="{m.group(1)}" stroke="{m.group(1)}" stroke-width="{w}" stroke-linejoin="round"><polygon', svg, count=1)
# Dom Nolan (CRO), Oct 2026: thick black hair swept up and across with volume on top, long narrow face, high cheekbones,
# small hooded almond-set eyes under slightly thick straight dark brows, light olive skin
save("dom-nolan", thickbrows(cheekbones(nose(angledbrows(brows(eyes(figure("CRO", skin=2, hair="thickswept", hair_colour="#1A1412", brow_colour="#15100E", jaw="narrow"), "smallhooded", 0.5), 0, 0.5, 3), 0.8), 1.0, 1.15), skin=2, depth=1.0), 0.8))
# Martin Duff (AFD, 1986-92), Oct 2026: bald on top with short sandy-grey sides, ruddy, thin wire-rimmed glasses, square jaw,
# hooded eyes looking down, large nose, lines from nose to mouth
save("martin-duff", nose(brows(eyes(figure("AFD", skin=1, hair="horseshoe", hair_colour="#B59C82", brow_colour="#A08670", glasses=True, glasses_col="#A9A49A", rosy=True, creases=True, jaw="square"), "hooded"), 0, 0, 2), 1.15, 1.2))
# Grenville Tuck (H/W from 1989), Oct 2026, from Athletics Weekly 28 Oct 1978 p5 (AAA 6-stage relay, Cambridge & Coleridge vest in the photo):
# thick dark wavy seventies hair over the ears, full moustache, long lean face, high cheekbones, heavy low brows over deep-set eyes.
# Grenville only: not for his twin Graham Tuck or any "G Tuck" result.
save("grenville-tuck", cheekbones(sockets(nose(angledbrows(brows(eyes(figure("H/W", skin=1, hair="seventies", hair_colour="#2A1D17", brow_colour="#1E1612", facial="thicktache", facial_colour="#2A1D17", jaw="long"), None, 0), 0, 0, 4), 0.8), 1.0, 1.25), depth=1.2), depth=0.9))
# ---- Slim, wide-set cheek hollows and a lower chin crease (Oct 2026, first used for Owen Hind) ----
def cheekhollows(svg, skin=1, tag="f", inset=4.0, depth=1.0, dy=0.0):
    """Like cheekbones(), but the hollows are slimmer and set further apart: their inner edges move out towards the ears by `inset`; dy moves them down the face."""
    sk, dk, lt = SKIN[skin]; i = inset; d = dy
    L = f"M66,{125+d} L{84-i},{123.5+d} Q{87-i},{124+d} {87.5-i},{127+d} L{90-i},{143+d} Q{81-i*.6},{131+d} 66,{131+d} Z"
    R = f"M134,{125+d} L{116+i},{123.5+d} Q{113+i},{124+d} {112.5+i},{127+d} L{110+i},{143+d} Q{119+i*.6},{131+d} 134,{131+d} Z"
    Lh = f"M66,{121.5+d} L{84-i},{121+d} Q{87-i},{121.5+d} {87.5-i},{124+d} Q{85-i},{123+d} {84-i},{123.5+d} L66,{125+d} Z"
    Rh = f"M134,{121.5+d} L{116+i},{121+d} Q{113+i},{121.5+d} {112.5+i},{124+d} Q{115+i},{123+d} {116+i},{123.5+d} L134,{125+d} Z"
    return _after_lids(svg, f'<g clip-path="url(#h{tag})"><g fill="{dk}" opacity="{.7*depth:.2f}"><path d="{L}"/><path d="{R}"/></g><g fill="{lt}" opacity=".55"><path d="{Lh}"/><path d="{Rh}"/></g></g>')
def chincrease(svg, skin=1, tag="f", y=164, lit=True, w=1.0):
    """A soft crease across the chin, about halfway down from the mouth (use with a long chin); lit=True lights the chin pad below it, as if from above; w widens both."""
    sk, dk, lt = SKIN[skin]; a = lambda dx: f"{100+dx*w:g}"
    pad = f'<path d="M{a(-7)},{y+1.2} Q100,{y-1} {a(7)},{y+1.2} Q{a(6.5)},{y+7} 100,{y+8.2} Q{a(-6.5)},{y+7} {a(-7)},{y+1.2} Z" fill="{lt}" opacity=".75"/>' if lit else ''
    return _after_lids(svg, f'<g clip-path="url(#h{tag})">{pad}<path d="M{a(-7.5)},{y} Q100,{y-2.6} {a(7.5)},{y} Q100,{y+3.4} {a(-7.5)},{y} Z" fill="{dk}"/></g>')
HAIR["tuftfit"] = HAIR["tuftrecede"].replace("M65,100 L62,80 L66,62", "M66.8,104 L64.6,80 L67,62").replace("L134,56 L138,74 L135,100 L132,84", "L133,56 L135.6,74 L133.4,104 L131.6,86").replace("68,84 Z", "68.4,86 Z")  # tuftrecede hugging the head, sides running down to the ears: no gap at the temples (Owen Hind)
# Owen Hind (KEN), redrawn Oct 2026: dark brown tufty hair with a slight recede, oblong face with a long strong chin and a crease
# halfway down it (chin lit below, both widened), slim wide-set cheek hollows low by the base of the nose, small eyes slightly close together tucked right under heavy straight brows
save("hind", chincrease(longchin(cheekhollows(sockets(nose(angledbrows(brows(eyes(figure("KEN", skin=1, hair="tuftfit", hair_colour="#3A2820", brow_colour="#2A1D16", jaw="broadchin"), "small", -1.5), 0, -1.5, 6.5), 1.0), 0.95, 1.2), depth=1.3), inset=4, dy=9)), y=163.5, lit=True, w=1.45))
# ---- Triangular head with a long flat chin (Oct 2026, first used for Jared Martin) ----
HEAD_TRI = "M65,96 C63,58 80,40 100,40 C120,40 137,58 135,96 L131.5,122 C128,140 119,157 110,169.5 L108,173 L92,173 L90,169.5 C81,157 72,140 68.5,122 Z"  # broad temples tapering straight to a long, narrow, flat chin
def trihead(svg):
    """Swap the default round head (jaw=None) for the triangular head with a long flat chin."""
    return svg.replace(HEAD, HEAD_TRI)
def softbrows(svg, thick=3.4, rise=0.0):
    """Medium-weight brows in one soft, even curve, a little fuller at the inner end (a kind, open look); keeps the brow height. rise lifts the inner ends."""
    m = _rq.search(r'<g fill="(#[0-9A-Fa-f]{3,6})"( [^>]*)?><polygon points="[0-9.]+,[0-9.]+ [0-9.]+,([0-9.]+) [^"]+"/><polygon points="[^"]+"/></g>', svg)
    if not m: return svg
    dy = float(m.group(3)) - 100
    t = thick
    top = [(73.8,103.6),(77,101.2),(81,99.8),(85.5,99.4),(90,100.1-rise*.5),(94.8,101.6-rise)]
    bot = [(95,101.6-rise+t*1.05),(90,100.1-rise*.5+t),(85.5,99.4+t),(81,99.8+t*.9),(77,101.2+t*.7),(74.2,103.9+t*.25)]
    L = top+bot
    f = lambda pts: " ".join(f"{x:g},{y+dy:g}" for x, y in pts)
    return svg[:m.start()] + f'<g fill="{m.group(1)}"><polygon points="{f(L)}"/><polygon points="{f([(200-x, y) for x, y in L])}"/></g>' + svg[m.end():]
# Jared Martin (THH), redrawn Oct 2026: short dark brown crop, triangular head with broad temples and a long flat chin,
# small hooded eyes under soft curved medium brows, long nose, clean cheeks
save("jared-martin", trihead(nose(softbrows(brows(eyes(figure("THH", skin=1, hair="crop", hair_colour="#3A2820", brow_colour="#2E211A"), "smallhooded", 0), 0, 0, 3), 3.4, 0), 0.95, 1.15)))
# ---- Low centre-parted sweep (Oct 2026, first used for Indy Barnes) ----
HAIR["lowpart"] = ('<path d="M65.5,100 C62,60 82,39 100,39 C118,39 138,60 134.5,100 L132,99 Q131.5,90 128.5,84.5 L126,87 Q122,79.5 113,76.5 Q106,74.5 100,73 Q94,74.5 87,76.5 Q78,79.5 74,87 L71.5,84.5 Q68.5,90 68,99 Z"/>'
    '<path d="M100,73.5 L100,47" fill="none" stroke="#000" stroke-opacity=".3" stroke-width="1.5" stroke-linecap="round"/>'
    '<g fill="none" stroke="#000" stroke-opacity=".16" stroke-width="1.2" stroke-linecap="round"><path d="M97,54 Q83,58 74,74"/><path d="M103,54 Q117,58 126,74"/></g>')  # medium top parted in the middle and swept out and down to the temples: low hairline, short forehead
# Indy Barnes (THH), redrawn Oct 2026: mid-brown hair parted in the middle and swept out and down to the temples (low hairline,
# short forehead), short sides, young smooth face with a slightly narrow chin, light flush, hooded eyes, medium-thin soft brows, dark long sleeves
save("barnes", nose(softbrows(brows(eyes(figure("THH", hair="lowpart", jaw="narrow", skin=1, hair_colour="#6A4A32", brow_colour="#4A3222", sleeves="#1E2A33", rosy=True), "hooded", 0), 0, 0, 1), 2.8, 0.3), 0.9, 1.1))
# ---- A gentle inward-up eye tilt: halfway between the default eye and 'downturned' (Oct 2026, Richard Ollington) ----
import re as _rtilt
def _blend(a, b, t):
    na = [float(x) for x in _rtilt.findall(r'-?\d+\.?\d*', a)]; nb = iter(float(x) for x in _rtilt.findall(r'-?\d+\.?\d*', b)); it = iter(na)
    return _rtilt.sub(r'-?\d+\.?\d*', lambda m: f"{(lambda x, y: x + (y - x) * t)(next(it), next(nb)):g}", a)
EYE_SHAPES["softdown"] = tuple(_blend(a, b, .5) for a, b in zip((_EL0, _ER0, _LL0, _LR0), EYE_SHAPES["downturned"]))
# Richard Ollington (THH): eyes lift gently towards the middle (was "upturned", which tilted them down inwards)
save("ollington", eyes(figure("THH", skin=2, hair="shortcurls", hair_colour="#241A15", facial="stubble", facial_colour="#4A3A30"), "softdown"))
# Keith Newton (HHH), redrawn Oct 2026: spiky mid-brown hair, long face with a narrow chin, wide smile with smile lines and dimples,
# narrowed eyes under warm brows, long nose
save("keith-newton", cheekdimples(widesmile(nose(brows(eyes(figure("HHH", skin=1, hair="spiky", hair_colour="#6E4E36", brow_colour="#4E3626", creases=True, jaw="narrow"), "narrow", 0), 0.8, 0, 2), 1.0, 1.2))))
# ---- Slicked-back centre parting variants (Oct 2026, first used for Isabel Hodder) ----
# ---- Slicked-back hair with a sharp centre parting (Oct 2026, first used for Isobel Hodder) ----
_PART = ('<path d="M100,63 L100,40" fill="none" stroke="#000" stroke-opacity=".32" stroke-width="1.5" stroke-linecap="round"/>'
         '<g fill="none" stroke="#fff" stroke-opacity=".16" stroke-width="1.2" stroke-linecap="round"><path d="M96,46 Q82,50 72,66"/><path d="M104,46 Q118,50 128,66"/><path d="M95,54 Q84,58 76,72"/><path d="M105,54 Q116,58 124,72"/></g>')
for _k, _src in (("slickpart", "slicktail"), ("slickbun", "lowbun"), ("slicktop", "tightbun")):
    HAIR[_k] = HAIR[_src] + _PART
    if _src in HAIR_BACK: HAIR_BACK[_k] = HAIR_BACK[_src]
import re as _rh
def shortlonghead(k):
    """HEAD_LONGCHIN with everything below the cheekbones squashed up by k (k<1 = shorter face, same strong chin)."""
    return _rh.sub(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', lambda m: f"{m.group(1)},{(96+(float(m.group(2))-96)*k) if float(m.group(2))>96 else float(m.group(2)):g}", HEAD_LONGCHIN)
# Isabel Hodder (BEL; the league spells her Isobel), redrawn Oct 2026: mid-brown hair slicked back from a sharp centre parting into a tight bun,
# strong jaw and chin (a little shorter than the long-chin head) with definition under the mouth, gently arched brows, small silver hoops, light flush
save("isabel-hodder", earrings(widesmile(chindef(nose(softbrows(brows(eyes(figure("BEL", skin=1, hair="slicktop", hair_colour="#5A3E2A", brow_colour="#4A3222", rosy=True, jaw="broadchin"), "almond", 0), 0, 0, 2), 3.0, 0.6), 0.9, 1.15).replace(HEAD_BROADCHIN, shortlonghead(.9)))), col="#CFCFCF"))

# ---- Scraped back at the front, hanging down behind (Oct 2026, first used for Juliet Hodder) ----
HAIR["slickdown"] = HAIR["slick"]
HAIR_BACK["slickdown"] = '<path d="M65,90 C63,52 80,36 100,36 C120,36 137,52 135,90 L133,150 Q131,172 126,190 L74,190 Q69,172 67,150 Z"/>'
def narrowchin(head, f, y0=128):
    """Pull the lower face in towards the centre line (f<1 = narrower chin), easing in from y0 down to the chin."""
    return _rh.sub(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', lambda m: (lambda x, y: f"{(100+(x-100)*(1-(1-f)*min(1,(y-y0)/40))) if y > y0 else x:g},{y:g}")(float(m.group(1)), float(m.group(2))), head)
# Juliet Hodder (BEL), redrawn Oct 2026: Isabel's sister and much like her, with a longer, much narrower chin; darker blonde hair scraped back
# at the front and hanging down behind; gently arched brows, small silver hoops, fine silver chain, light flush
save("juliet-hodder", earrings(widesmile(chindef(nose(softbrows(brows(eyes(figure("BEL", skin=1, hair="slickdown", hair_colour="#9A7650", brow_colour="#5A4030", rosy=True, necklace="#D4D4D4", jaw="broadchin"), "almond", 0), 0, 0, 2), 3.0, 0.6), 0.9, 1.15).replace(HEAD_BROADCHIN, narrowchin(shortlonghead(1.0), 0.68)))), col="#CFCFCF"))

# Nikki Haines (BEL, 1994-2000), Oct 2026, from a Belgravian London Marathon photo (black and white, hair colour inferred):
# thick dark hair with wavy volume swept up on top, lean narrow face with defined cheekbones, slightly downturned eyes a little close-set,
# thin raised brows (a concentrating look)
save("nikki-haines", cheekbones(nose(softbrows(brows(eyes(figure("BEL", skin=1, hair="messyvolume", hair_colour="#3A2A20", brow_colour="#2E211A", jaw="narrow"), "downturned", -1.5), 1.2, -1.5, 2), 2.4, 1.2), 0.95, 1.15), depth=.7))

# Paul Evans (BEL; Olympic marathoner, Chicago Marathon winner 1996), Oct 2026: tousled dark-blond hair swept up, long lean face,
# long face with a broad square chin, high cheekbones, long nose, smallish eyes under light brows, weathered flush
save("paul-evans", cheekbones(nose(brows(eyes(figure("BEL", skin=1, hair="tousled", hair_colour="#D2B070", brow_colour="#B09060", jaw="broadchin", rosy=True), "small", 0), 0, 0, 2), 0.95, 1.25), depth=.8).replace(HEAD_BROADCHIN, shortlonghead(.92)))

export_site()
