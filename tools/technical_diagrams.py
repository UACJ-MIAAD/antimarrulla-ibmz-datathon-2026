"""Hand-laid technical SVG views. Shapes and connectors carry architectural meaning.

Visual system: dark canvas that matches the public site, elevated cards with soft shadows,
tinted icon badges, pill labels, rounded connectors and a subtle dot grid.
"""
from html import escape as esc
import textwrap

BG0 = '#0a1324'     # canvas
BG1 = '#122039'     # card
BG2 = '#18294a'     # raised / header
GRID = '#1b2b49'
LINE = '#2b3f63'
INK = '#eef4fd'
MUTED = '#a3b5d1'
BLUE = '#6ea8ff'
TEAL = '#3fd6b4'
VIOLET = '#b8a2ff'
AMBER = '#ffb65c'
RED = '#ff7088'
COLORS = {'blue': BLUE, 'teal': TEAL, 'violet': VIOLET, 'amber': AMBER, 'red': RED, 'ink': INK}
KEY_OF = {v: k for k, v in COLORS.items()}

ICONS = {
    'person': '<circle cx="16" cy="8" r="4"/><path d="M7 27v-4a9 9 0 0 1 18 0v4M16 18v10"/>',
    'browser': '<rect x="2" y="4" width="28" height="23" rx="3"/><path d="M2 11h28M7 8h1m3 0h1m3 0h1M11 17l-4 4 4 4m10-8 4 4-4 4"/>',
    'hospital': '<path d="M5 29V9h22v20M2 29h28M11 9V3h10v6M16 5v3m-2-1h4M12 29v-7h8v7M10 14h2m8 0h2m-12 4h2m8 0h2"/>',
    'server': '<rect x="4" y="3" width="24" height="8" rx="2"/><rect x="4" y="13" width="24" height="8" rx="2"/><rect x="4" y="23" width="24" height="6" rx="2"/><path d="M8 7h1m4 0h10M8 17h1m4 0h10M8 26h1"/>',
    'container': '<path d="M3 9l13-6 13 6v15l-13 6-13-6zM3 9l13 6 13-6M16 15v15M9 6l14 6"/>',
    'key': '<circle cx="10" cy="11" r="7"/><path d="M15 16l13 13m-4-4 4-4m-9-1 4-4"/>',
    'lock': '<rect x="5" y="14" width="22" height="15" rx="3"/><path d="M10 14V9a6 6 0 0 1 12 0v5M16 20v4"/>',
    'shield': '<path d="M16 2l12 5v9c0 7-12 14-12 14S4 23 4 16V7zM10 15l4 4 8-9"/>',
    'model': '<circle cx="6" cy="7" r="3"/><circle cx="6" cy="25" r="3"/><circle cx="17" cy="16" r="4"/><circle cx="27" cy="7" r="3"/><circle cx="27" cy="25" r="3"/><path d="M9 9l5 5M9 23l5-5m7-4 4-5m-4 9 4 5"/>',
    'chart': '<path d="M4 3v25h26M8 22l7-8 6 3 8-12"/><path d="M23 5h6v6"/>',
    'file': '<path d="M7 2h13l7 7v21H7zM20 2v8h7M11 16h12m-12 5h12m-12 5h8"/>',
    'database': '<ellipse cx="16" cy="7" rx="12" ry="5"/><path d="M4 7v19c0 7 24 7 24 0V7M4 16c0 7 24 7 24 0"/>',
    'check': '<circle cx="16" cy="16" r="13"/><path d="M9 16l5 5 10-12"/>',
    'package': '<path d="M3 9l13-6 13 6v16l-13 5-13-5zM3 9l13 6 13-6M16 15v15M10 6l13 6v7"/>',
    'split': '<path d="M3 16h9m0 0V5h15m-15 11h15m-15 0v11h15M23 2l4 3-4 3m0 5 4 3-4 3m0 5 4 3-4 3"/>',
}


def _key(color):
    return KEY_OF.get(color, 'blue')


class Canvas:
    def __init__(self, title, subtitle, h=820):
        self.h = h
        defs = []
        for k, v in COLORS.items():
            defs.append(f'<marker id="a-{k}" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M1 1.5L11 6 1 10.5 3.6 6z" fill="{v}"/></marker>')
            defs.append(f'<linearGradient id="t-{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{v}" stop-opacity=".16"/><stop offset=".55" stop-color="{v}" stop-opacity=".05"/><stop offset="1" stop-color="{v}" stop-opacity=".02"/></linearGradient>')
            defs.append(f'<linearGradient id="e-{k}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{v}" stop-opacity=".95"/><stop offset="1" stop-color="{v}" stop-opacity=".55"/></linearGradient>')
        defs.append('<filter id="sh" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000814" flood-opacity=".55"/></filter>')
        defs.append('<filter id="sh-s" x="-20%" y="-30%" width="140%" height="180%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#000814" flood-opacity=".5"/></filter>')
        defs.append(f'<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1.2" cy="1.2" r="1.2" fill="{GRID}"/></pattern>')
        defs.append('<radialGradient id="glow" cx="12%" cy="0%" r="75%"><stop offset="0" stop-color="#2a5bb8" stop-opacity=".35"/><stop offset="1" stop-color="#2a5bb8" stop-opacity="0"/></radialGradient>')
        defs.append('<radialGradient id="glow2" cx="100%" cy="100%" r="60%"><stop offset="0" stop-color="#1f8f7c" stop-opacity=".18"/><stop offset="1" stop-color="#1f8f7c" stop-opacity="0"/></radialGradient>')
        defs.append(f'<linearGradient id="accent" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{TEAL}"/></linearGradient>')
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {h}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{esc(title)}</title><desc id="desc">{esc(subtitle)}</desc>',
            '<defs>' + ''.join(defs) + '</defs>',
            '<style>text{font-family:Inter,"SF Pro Text",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;letter-spacing:-.005em} .mono{font-family:"JetBrains Mono",ui-monospace,SFMono-Regular,Consolas,monospace;letter-spacing:0} .caps{letter-spacing:.09em}</style>',
            f'<rect width="1200" height="{h}" rx="18" fill="{BG0}"/>',
            f'<rect width="1200" height="{h}" rx="18" fill="url(#grid)" opacity=".9"/>',
            f'<rect width="1200" height="{h}" rx="18" fill="url(#glow)"/>',
            f'<rect width="1200" height="{h}" rx="18" fill="url(#glow2)"/>',
            f'<rect x=".5" y=".5" width="1199" height="{h-1}" rx="18" fill="none" stroke="#22365a"/>']
        self.raw('<rect x="32" y="22" width="5" height="50" rx="2.5" fill="url(#accent)"/>')
        self.text(50, 44, title, 25, INK, weight=750)
        self.text(50, 68, subtitle, 14.5, MUTED)
        self.raw(f'<path d="M32 88H1168" stroke="{LINE}" stroke-width="1"/>')

    def raw(self, s): self.parts.append(s)

    def text(self, x, y, text, size=17, color=INK, anchor='start', weight=400, mono=False, caps=False):
        cls = ' class="mono"' if mono else (' class="caps"' if caps else '')
        self.raw(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}"{cls}>{esc(str(text))}</text>')

    def lines(self, x, y, text, width=260, size=16, color=MUTED, anchor='start'):
        strings = text if isinstance(text, list) else textwrap.wrap(text, max(12, int(width/(size*.54))))
        for i,t in enumerate(strings): self.text(x,y+i*(size+6),t,size,color,anchor)

    def line(self,x1,y1,x2,y2,color=LINE,dash=False):
        self.raw(f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width="1.6" fill="none" stroke-linecap="round"'+(' stroke-dasharray="5 6"' if dash else '')+'/>')

    def icon(self, name, x, y, color=BLUE, size=32):
        self.raw(f'<g transform="translate({x} {y}) scale({size/32})" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')

    def badge(self, name, cx, cy, color, r=19):
        """Tinted circular badge holding a line icon."""
        self.raw(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" fill-opacity=".14" stroke="{color}" stroke-opacity=".55" stroke-width="1.2"/>')
        s = r*1.15
        self.icon(name, cx-s/2, cy-s/2, color, s)

    def group(self,x,y,w,h,title,sub='',color=BLUE):
        k=_key(color)
        self.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{color}" fill-opacity=".045" stroke="{color}" stroke-opacity=".42" stroke-width="1.4" stroke-dasharray="7 6"/>')
        tw=sum(9.6 if ch.isupper() else 8.2 if ch.isalnum() else 6.0 for ch in title)+30
        self.raw(f'<rect x="{x+14}" y="{y+12}" width="{tw}" height="24" rx="12" fill="{color}" fill-opacity=".16" stroke="{color}" stroke-opacity=".45"/>')
        self.text(x+27,y+28.5,title,12,color,weight=750,caps=True)
        if sub:self.text(x+18,y+54,sub,13,MUTED)

    def _card(self,x,y,w,h,color,radius=12):
        k=_key(color)
        self.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{BG1}" filter="url(#sh)"/>')
        self.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="url(#t-{k})" stroke="{color}" stroke-opacity=".6" stroke-width="1.4"/>')
        if radius < h/2 - 1:
            self.raw(f'<path d="M{x+radius} {y+1.2}H{x+w-radius}" stroke="url(#e-{k})" stroke-width="2.6" stroke-linecap="round"/>')

    def node(self,x,y,w,h,title,detail='',icon='container',color=BLUE,kind='process'):
        k=_key(color)
        self.raw('<g class="node">')
        if kind=='file':
            self.raw(f'<path d="M{x} {y+10}Q{x} {y} {x+10} {y}H{x+w-24}L{x+w} {y+24}V{y+h-10}Q{x+w} {y+h} {x+w-10} {y+h}H{x+10}Q{x} {y+h} {x} {y+h-10}Z" fill="{BG1}" filter="url(#sh)"/>')
            self.raw(f'<path d="M{x} {y+10}Q{x} {y} {x+10} {y}H{x+w-24}L{x+w} {y+24}V{y+h-10}Q{x+w} {y+h} {x+w-10} {y+h}H{x+10}Q{x} {y+h} {x} {y+h-10}Z" fill="url(#t-{k})" stroke="{color}" stroke-opacity=".6" stroke-width="1.4"/>')
            self.raw(f'<path d="M{x+w-24} {y}V{y+16}Q{x+w-24} {y+24} {x+w-16} {y+24}H{x+w}Z" fill="{color}" fill-opacity=".28" stroke="{color}" stroke-opacity=".6" stroke-width="1.2" stroke-linejoin="round"/>')
        elif kind=='io':
            self.raw(f'<path d="M{x+18} {y}H{x+w}L{x+w-18} {y+h}H{x}Z" fill="{BG1}" filter="url(#sh)"/>')
            self.raw(f'<path d="M{x+18} {y}H{x+w}L{x+w-18} {y+h}H{x}Z" fill="url(#t-{k})" stroke="{color}" stroke-opacity=".6" stroke-width="1.4" stroke-linejoin="round"/>')
        else:
            self._card(x,y,w,h,color,h/2 if kind=='terminal' else 12)
        if icon:
            self.badge(icon,x+34 if kind!='terminal' else x+h/2+4,y+33 if h>70 else y+h/2,color,18 if h>70 else 16)
        tx=x+62 if icon else x+20
        if kind=='terminal' and icon: tx=x+h/2+30
        ty=y+38 if h>70 else y+h/2+6
        self.text(tx,ty,title,18,INK,weight=680)
        if detail:self.lines(x+20 if kind!='io' else x+30,y+68,detail,w-40,14.5)
        self.raw('</g>')

    def db(self,x,y,w,h,title,detail='',color=VIOLET):
        k=_key(color)
        self.raw('<g class="node">')
        body=f'M{x} {y+18}V{y+h-18}C{x} {y+h+6} {x+w} {y+h+6} {x+w} {y+h-18}V{y+18}'
        self.raw(f'<path d="{body}" fill="{BG1}" filter="url(#sh)"/>')
        self.raw(f'<path d="{body}" fill="url(#t-{k})" stroke="{color}" stroke-opacity=".65" stroke-width="1.4"/>')
        self.raw(f'<path d="M{x} {y+34}C{x} {y+58} {x+w} {y+58} {x+w} {y+34}" fill="none" stroke="{color}" stroke-opacity=".22" stroke-width="1.2"/>')
        self.raw(f'<ellipse cx="{x+w/2}" cy="{y+18}" rx="{w/2}" ry="18" fill="{BG2}"/><ellipse cx="{x+w/2}" cy="{y+18}" rx="{w/2}" ry="18" fill="{color}" fill-opacity=".22" stroke="{color}" stroke-opacity=".75" stroke-width="1.4"/>')
        self.text(x+w/2,y+60,title,17.5,INK,'middle',700)
        if detail:self.lines(x+w/2,y+84,detail,w-26,13.5,anchor='middle')
        self.raw('</g>')

    def cloud(self,x,y,w,h,title,detail=''):
        self.raw('<g class="node">')
        d=f'M{x+w*.2} {y+h}C{x-w*.06} {y+h} {x-w*.02} {y+h*.4} {x+w*.22} {y+h*.4}C{x+w*.2} {y-h*.05} {x+w*.7} {y-h*.05} {x+w*.72} {y+h*.3}C{x+w*1.06} {y+h*.12} {x+w*1.12} {y+h} {x+w*.82} {y+h}Z'
        self.raw(f'<path d="{d}" fill="{BG1}" filter="url(#sh)"/><path d="{d}" fill="url(#t-amber)" stroke="{AMBER}" stroke-opacity=".75" stroke-width="1.4"/>')
        self.text(x+w/2,y+h*.56,title,17.5,INK,'middle',700)
        self.text(x+w/2,y+h*.8,detail,13.5,AMBER,'middle',500)
        self.raw('</g>')

    def decision(self,cx,cy,w,h,title,detail=''):
        self.raw('<g class="node">')
        d=f'M{cx} {cy-h/2}L{cx+w/2} {cy} {cx} {cy+h/2} {cx-w/2} {cy}Z'
        self.raw(f'<path d="{d}" fill="{BG1}" filter="url(#sh)" stroke-linejoin="round"/><path d="{d}" fill="url(#t-blue)" stroke="{BLUE}" stroke-opacity=".75" stroke-width="1.5" stroke-linejoin="round"/>')
        self.text(cx,cy-2,title,16.5,INK,'middle',700)
        if detail:self.text(cx,cy+21,detail,13.5,MUTED,'middle')
        self.raw('</g>')

    def edge(self,points,label='',color='blue',dash=False,lx=None,ly=None):
        r=12
        d=f'M{points[0][0]} {points[0][1]}'
        for i in range(1,len(points)-1):
            (x0,y0),(x1,y1),(x2,y2)=points[i-1],points[i],points[i+1]
            l1=max(abs(x1-x0),abs(y1-y0)); l2=max(abs(x2-x1),abs(y2-y1))
            rr=min(r,l1/2,l2/2)
            ax=x1-(rr if x1>x0 else -rr if x1<x0 else 0); ay=y1-(rr if y1>y0 else -rr if y1<y0 else 0)
            bx=x1+(rr if x2>x1 else -rr if x2<x1 else 0); by=y1+(rr if y2>y1 else -rr if y2<y1 else 0)
            d+=f' L{ax} {ay} Q{x1} {y1} {bx} {by}'
        d+=f' L{points[-1][0]} {points[-1][1]}'
        col=COLORS[color]
        self.raw(f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity=".18" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
        self.raw(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#a-{color})"'+(' stroke-dasharray="7 6"' if dash else '')+'/>')
        if label:
            if lx is None:lx=(points[0][0]+points[-1][0])/2
            if ly is None:ly=(points[0][1]+points[-1][1])/2-10
            self.label(lx,ly,label,col)

    def label(self,x,y,text,color=BLUE):
        w=len(text)*7.1+22
        self.raw(f'<rect x="{x-w/2}" y="{y-15.5}" width="{w}" height="23" rx="11.5" fill="#0d1a31" stroke="{color}" stroke-opacity=".55" filter="url(#sh-s)"/>')
        self.text(x,y+0.5,text,12.5,color,'middle',620)

    def note(self,x,y,w,text,color=AMBER):
        size=13.5
        strings=textwrap.wrap(text, max(12, int((w-34)/(size*.54))))
        h=len(strings)*(size+6)+18
        self.raw(f'<rect x="{x}" y="{y-4}" width="{w}" height="{h}" rx="10" fill="{color}" fill-opacity=".08" stroke="{color}" stroke-opacity=".35"/>')
        self.raw(f'<rect x="{x}" y="{y-4}" width="4" height="{h}" rx="2" fill="{color}"/>')
        for i,t in enumerate(strings): self.text(x+18,y+16+i*(size+6),t,size,color,weight=500)

    def foot(self,text):
        self.raw(f'<circle cx="38" cy="{self.h-27}" r="3" fill="{TEAL}"/>')
        self.text(50,self.h-22,text,13,MUTED)

    def finish(self):return '\n'.join(self.parts+['</svg>'])+'\n'


def system():
    c=Canvas('Container architecture / privacy boundaries','C4-style container view · arrows name the data crossing each boundary',780)
    c.group(280,150,860,530,'APPROVED MVP · TWO CONTAINERS ON ONE HOST','Logical key isolation; the host administrator remains trusted.',BLUE)
    c.cloud(38,116,200,106,'Public website','Netlify · static only')
    c.node(34,310,185,116,'Team browser',['Synthetic input','Risk + contributions'],'browser',TEAL)
    c.icon('person',107,460,INK,38);c.text(126,520,'Operator',16,INK,'middle');c.line(126,464,126,426,TEAL)
    c.node(320,300,275,138,'Hospital',['Frontend + API','Validate · encrypt · decrypt','Paillier private key in memory'],'hospital',TEAL)
    c.node(810,300,285,138,'Risk service',['Public model + integer weights','Homomorphic linear scoring','No Paillier private key'],'server',BLUE)
    c.db(330,520,255,112,'Encrypted vault',['AES-256-GCM payload','Persistent Docker volume'])
    c.node(820,530,260,92,'Model artifact','Versioned weights W and B','model',VIOLET,kind='file')
    c.edge([(135,310),(135,222)],'HTTPS',color='amber',lx=185,ly=272)
    c.edge([(219,367),(320,367)],'SSH tunnel',color='teal',lx=270,ly=350)
    c.edge([(595,333),(810,333)],'19 ciphertexts + public key',lx=700,ly=318)
    c.edge([(810,398),(595,398)],'Encrypted score Enc(z)',lx=700,ly=420)
    c.edge([(457,438),(457,520)],'Save encrypted result',color='violet',lx=575,ly=482)
    c.edge([(950,530),(950,438)],'Load W, B',color='violet',dash=True,lx=1010,ly=485)
    c.note(320,706,790,'Public site has no route to the Hospital API. Plaintext feature values and the decrypted result stay in Hospital.',TEAL)
    return c.finish()


def deployment():
    c=Canvas('Deployment topology / ports and mounts','Deployment specification · final provider and English VM evidence remain separate',810)
    c.group(432,116,720,654,'TARGET VM · IBM LINUXONE / UBUNTU 24.04','Same-host Docker network · host administrator is trusted')
    c.group(463,204,658,222,'DOCKER NETWORK · internal','No service port published to the host',TEAL)
    c.cloud(45,125,270,110,'Netlify','Static pitch / map / forecast')
    c.node(46,350,282,126,'Operator laptop',['Browser via local tunnel','VM: 127.0.0.1:8080'],'browser',TEAL)
    c.node(493,282,255,112,'Hospital container',['Serves port 8080','Paillier key: memory'],'hospital',TEAL)
    c.node(832,282,255,112,'Risk container',['Internal port 8443','TLS identity only'],'server',BLUE)
    c.db(493,502,255,118,'vault Docker volume',['vault.jsonl','Ciphertext envelopes only'])
    c.node(493,668,255,76,'External AES key','Hospital read-only mount','key',VIOLET,kind='file')
    c.node(834,513,254,100,'External TLS files',['Per-container identities','Read-only mounts'],'file',VIOLET,kind='file')
    c.edge([(185,350),(185,235)],'Public HTTPS',color='amber',lx=253,ly=303)
    c.edge([(328,386),(393,386),(393,338),(493,338)],'SSH tunnel',color='teal',lx=408,ly=372)
    c.edge([(748,322),(832,322)],'mTLS 1.3',lx=791,ly=308)
    c.edge([(832,365),(748,365)],'Enc(z)',lx=790,ly=389)
    c.edge([(621,394),(621,502)],'Persistent',color='violet',lx=681,ly=470)
    c.edge([(962,513),(962,394)],'TLS cert + CA',color='violet',dash=True,lx=1040,ly=470)
    c.edge([(834,563),(785,563),(785,457),(708,457),(708,394)],'Hospital TLS identity',color='violet',dash=True,lx=805,ly=642)
    c.edge([(493,706),(470,706),(470,475),(570,475),(570,394)],'Vault key',color='violet',dash=True,lx=469,ly=648)
    c.foot('Netlify does not host the interactive Hospital API. Optional two-host testing is a different topology.')
    return c.finish()


def protocol():
    c=Canvas('Encrypted evaluation / request sequence','UML-style sequence · time flows downward · dashed arrows are responses',900)
    lifelines=[(120,'Browser','browser',TEAL),(410,'Hospital','hospital',TEAL),(790,'Risk service','server',BLUE),(1080,'Vault','database',VIOLET)]
    for x,title,icon,color in lifelines:
        c.node(x-95,108,190,64,title,icon=icon,color=color)
        c.line(x,172,x,826,color,True)
    for x,y,h,color in [(404,226,574,TEAL),(784,348,194,BLUE),(1074,680,54,VIOLET)]:
        c.raw(f'<rect x="{x}" y="{y}" width="12" height="{h}" rx="3" fill="{BG2}" stroke="{color}" stroke-width="1.5"/>')
    c.edge([(120,230),(404,230)],'1 · Synthetic input',color='teal',ly=216)
    c.edge([(416,270),(490,270),(490,306),(416,306)],color='teal')
    c.lines(510,280,['Validate 19 integer features','Encrypt x with Paillier'],260,15,TEAL)
    c.edge([(416,350),(784,350)],'2 · mTLS 1.3 · POST /v2/evaluate',ly=335)
    c.edge([(796,382),(858,382),(858,415),(796,415)])
    c.lines(880,393,['Compute Enc(z)','z = B + Σ Wᵢxᵢ'],270,15,BLUE)
    c.group(729,449,300,68,'opt · SERVICE_EVIDENCE','Save wire bytes before HTTP 200.',VIOLET)
    c.edge([(784,540),(416,540)],'3 · HTTP 200 · Enc(z)',dash=True,ly=526)
    c.edge([(416,579),(490,579),(490,618),(416,618)],color='teal')
    c.lines(510,587,['Decrypt z; logit = z / 10⁹','Sigmoid → probability → threshold'],350,15,TEAL)
    c.edge([(416,680),(1074,680)],'4 · AES-256-GCM encrypted result',color='violet',ly=664)
    c.edge([(1074,730),(416,730)],'append + flush + fsync complete',color='violet',dash=True,ly=715)
    c.edge([(404,790),(120,790)],'5 · Risk + factors + timings',color='teal',dash=True,ly=776)
    c.foot('Risk service never decrypts z. The sigmoid and threshold run only in Hospital; public protocol metadata stays visible.')
    return c.finish()


def hospital():
    c=Canvas('Hospital / input, encryption and result flow','Flowchart · diamonds are decisions · cylinders are persistent stores',1090)
    c.node(386,110,330,66,'POST /api/evaluate',icon='browser',color=TEAL,kind='terminal')
    c.node(386,220,330,84,'Select synthetic input','Profile / random / custom','file',TEAL,kind='io')
    c.decision(551,390,300,130,'Valid input?','19 integers + schema ranges')
    c.node(877,352,245,80,'HTTP 400','Invalid request body','shield',RED,kind='terminal')
    c.node(386,504,330,90,'Paillier encryption','19 inputs → 19 ciphertexts','lock',TEAL)
    c.node(386,646,330,90,'Call risk service','POST /v2/evaluate · mTLS 1.3','server',BLUE)
    c.node(386,790,330,92,'Validate + decrypt','Match ID/model; sigmoid(z / 10⁹)','key',TEAL)
    c.node(877,715,245,90,'HTTP 502','Service/response error','shield',RED,kind='terminal')
    c.db(65,794,260,116,'AES-GCM vault',['Store synthetic evaluation','append / flush / fsync'])
    c.node(386,962,330,65,'Return risk + factors',icon='check',color=TEAL,kind='terminal')
    c.edge([(551,176),(551,220)],color='teal')
    c.edge([(551,304),(551,325)],color='teal')
    c.edge([(701,390),(877,390)],'No',color='red',ly=376)
    c.edge([(551,455),(551,504)],'Yes',color='teal',lx=580,ly=484)
    c.edge([(551,594),(551,646)],color='teal')
    c.edge([(551,736),(551,790)],'Enc(z)',lx=598,ly=771)
    c.edge([(716,691),(798,691),(798,760),(877,760)],'Error',color='red',lx=802,ly=704)
    c.edge([(716,836),(804,836),(804,780),(877,780)],color='red')
    c.edge([(386,836),(325,836)],'Save',color='violet',lx=354,ly=821)
    c.edge([(195,910),(195,994),(386,994)],'Stored',color='violet',lx=256,ly=977)
    c.note(877,516,250,'Only Hospital holds the Paillier private key and the vault key.',TEAL)
    c.foot('Browser and Hospital are inside the demo plaintext boundary. Service failure does not become a successful screening result.')
    return c.finish()


def service():
    c=Canvas('Risk service / validation and encrypted scoring','Flowchart · TLS client authentication happens before HTTP request handling',1110)
    c.node(375,110,350,66,'Authenticated request',icon='shield',kind='terminal')
    c.decision(550,275,300,130,'HTTP request valid?','Route / size / content type')
    c.node(45,235,260,80,'HTTP 404 / 413 / 415','Reject unsupported request','shield',RED,kind='terminal')
    c.decision(550,465,300,130,'Protocol valid?','Version · key · group · bounds')
    c.node(45,425,260,80,'HTTP 400','Invalid protocol/model','shield',RED,kind='terminal')
    c.node(375,600,350,96,'Homomorphic evaluator',['Enc(z) = Enc(B + Σ Wᵢxᵢ)','Re-randomize the ciphertext'],'model',BLUE)
    c.decision(550,795,260,112,'Audit enabled?','SERVICE_EVIDENCE')
    c.node(845,746,300,98,'Capture wire evidence',['Request + response bytes','Hashes + TLS metadata'],'file',VIOLET,kind='file')
    c.node(845,930,300,76,'HTTP 503','Evidence storage failed','shield',RED,kind='terminal')
    c.node(375,985,350,66,'HTTP 200 · Enc(z)',icon='lock',kind='terminal')
    c.edge([(550,176),(550,210)])
    c.edge([(400,275),(305,275)],'No',color='red',ly=260)
    c.edge([(550,340),(550,400)],'Yes',lx=582,ly=377)
    c.edge([(400,465),(305,465)],'No',color='red',ly=450)
    c.edge([(550,530),(550,600)],'Yes',lx=582,ly=570)
    c.edge([(550,696),(550,739)])
    c.edge([(680,795),(845,795)],'Yes',color='violet',ly=779)
    c.edge([(550,851),(550,985)],'No',lx=575,ly=924)
    c.edge([(845,823),(774,823),(774,1018),(725,1018)],'Saved',color='violet',lx=775,ly=908)
    c.edge([(995,844),(995,930)],'Failure',color='red',lx=1042,ly=897)
    c.foot('No private Paillier key. Audit capture completes before success; TLS authentication failure closes the connection.')
    return c.finish()


def entity(c,x,y,w,title,subtitle,fields,color=BLUE):
    """Logical record/entity with a header and typed field rows, not a process node."""
    h=88+len(fields)*31
    k=_key(color)
    c.raw(f'<g class="entity"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{BG1}" filter="url(#sh)"/>')
    c.raw(f'<path d="M{x} {y+61}V{y+10}Q{x} {y} {x+10} {y}H{x+w-10}Q{x+w} {y} {x+w} {y+10}V{y+61}Z" fill="{color}" fill-opacity=".2"/>')
    c.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="{color}" stroke-opacity=".65" stroke-width="1.4"/><path d="M{x} {y+61}H{x+w}" stroke="{color}" stroke-opacity=".55"/>')
    c.badge('database',x+30,y+31,color,17)
    c.text(x+58,y+28,title,17,INK,weight=750)
    c.text(x+58,y+48,subtitle,12,MUTED)
    for i,(name,typ) in enumerate(fields):
        yy=y+88+i*31
        if i%2==0:c.raw(f'<rect x="{x+6}" y="{yy-20}" width="{w-12}" height="29" rx="5" fill="#ffffff" fill-opacity=".028"/>')
        c.raw(f'<circle cx="{x+18}" cy="{yy-5}" r="3" fill="{color}" fill-opacity=".85"/>')
        c.text(x+30,yy,name,14.5,INK,mono=True)
        c.text(x+w-15,yy,typ,12.5,MUTED,'end')
    c.raw('</g>')
    return h


def relation(c,x1,y1,x2,y2,many=False,label='',lx=None,ly=None):
    """Horizontal logical one-to-one or one-to-many relation using crow's-foot ends."""
    c.line(x1,y1,x2,y2,VIOLET)
    direction=1 if x2>x1 else -1
    for dx in (10,16):c.line(x1+direction*dx,y1-7,x1+direction*dx,y1+7,VIOLET)
    end=x2-direction*17
    if many:
        c.line(end,y2,x2,y2-10,VIOLET);c.line(end,y2,x2,y2+10,VIOLET)
        c.raw(f'<circle cx="{x2-direction*26}" cy="{y2}" r="4" fill="{BG0}" stroke="{VIOLET}" stroke-width="1.4"/>')
    else:
        for dx in (10,16):c.line(x2-direction*dx,y2-7,x2-direction*dx,y2+7,VIOLET)
    if label:c.label(lx if lx is not None else (x1+x2)/2,ly if ly is not None else y1-16,label,VIOLET)


def vault():
    c=Canvas('Operational storage / encrypted record schema','Logical schema + cryptographic transformation · persisted envelope versus decrypted view',860)
    c.group(30,112,465,585,'HOSPITAL MEMORY · PLAINTEXT VIEW','This payload is encrypted before being written.',TEAL)
    entity(c,64,196,398,'Evaluation payload','Decrypted JSON object · not plaintext columns',[
        ('synthetic','boolean'),('profile','string'),('input','19 integer fields'),('probability','number'),('risk_high','boolean'),('date','Unix timestamp')],TEAL)
    c.node(80,560,360,92,'Paillier private key','Memory only · not the vault key','key',TEAL)
    c.group(770,112,397,585,'PERSISTENT DOCKER VOLUME','Append-only JSONL · one envelope per evaluation',VIOLET)
    entity(c,796,226,344,'Vault envelope','vault.jsonl · visible envelope fields',[
        ('id','string / logical ID'),('nonce','Base64 / 12 bytes'),('ct','Base64 / bytes + tag')],VIOLET)
    c.db(820,526,295,112,'vault.jsonl',['append → flush → fsync','Persists across restarts'])
    c.node(508,300,230,142,'AES-256-GCM',['AAD = request ID','96-bit random nonce','Authenticate + encrypt'],'lock',TEAL)
    c.edge([(462,360),(508,360)],color='teal')
    c.edge([(738,360),(796,360)],'ct',color='teal',ly=347)
    c.edge([(796,260),(752,260),(752,181),(478,181),(478,220),(462,220)],'Decrypted view · not a foreign key',color='violet',dash=True,lx=616,ly=168)
    c.node(510,568,225,98,'External AES key',['32 bytes · read-only','Stored outside Git'],'key',VIOLET,kind='file')
    c.edge([(622,568),(622,442)],'Key',color='violet',dash=True,lx=650,ly=514)
    c.edge([(968,407),(968,526)],'Save envelope',color='violet',lx=1047,ly=465)
    c.note(50,740,1090,'No SQL engine, patient table or CURP. The dashed reverse link is an in-memory decrypted view, not a foreign key. ID and nonce remain visible on disk.',VIOLET)
    c.foot('The hospital vault does not encrypt service audit files, operational logs, the complete VM disk or backups.')
    return c.finish()


def data_model():
    c=Canvas('Analytical data / logical entity relationships','Crow’s-foot notation = logical cardinality · arrows = aggregation/export, not patient linkage',960)
    c.text(913,112,'Logical key: (cve_ent, anio)',14,VIOLET,'middle')
    entity(c,38,130,330,'STATE CATALOG','entidades.csv · 32 rows',[
        ('cve_ent','logical key'),('nombre_corto','state name'),('region_sinave','region'),('delegaciones_imss','lookup list')],TEAL)
    entity(c,668,130,490,'STATE_YEAR_MART','cascada_entidad_anio.csv · 256 rows',[
        ('cve_ent','logical state reference'),('anio','year / key part'),('poblacion','population'),('casos_nuevos_t1','type 1 notifications'),('casos_nuevos_t2','type 2 notifications'),('defunciones','death count'),('egresos','discharge count'),('sis_en_tratamiento','monthly average'),('tasa_casos_100k','derived rate')],VIOLET)
    relation(c,368,218,668,218,True,'1 : N',ly=203)
    c.lines(510,285,['State-code lookup','8 years per state'],220,14,anchor='middle')
    entity(c,38,487,330,'STATE GEOMETRY','estados_mx.geojson · 32 features',[
        ('cve_ent','logical key'),('geometry','Polygon / MultiPolygon')],TEAL)
    # A vertical 1:1 relation between state and geometry, with endpoint bars.
    c.line(205,342,205,487,VIOLET)
    for y in (355,362,469,476):c.line(198,y,212,y,VIOLET)
    c.label(255,429,'1 : 1',VIOLET)
    c.node(420,498,225,106,'Aggregate + join',['State/year keys','Source-specific geography'],'split',BLUE)
    c.node(40,756,335,105,'Independent source files',['SINAVE · EDR · discharges','SIS · IMSS · CONAPO'],'file',AMBER,kind='file')
    c.node(733,562,359,106,'Public presentation export',['care_stages.json','English indicator keys'],'file',BLUE,kind='file')
    c.cloud(756,753,310,105,'Public state map','State-code geometry lookup')
    c.edge([(375,808),(531,808),(531,604)],'Aggregate by state/year',color='amber',lx=537,ly=715)
    c.edge([(645,549),(662,549),(662,389),(668,389)],'Build mart',color='blue',lx=594,ly=446)
    c.edge([(910,497),(910,562)],'Export',ly=537)
    c.edge([(910,668),(910,753)],'Indicators',ly=711)
    c.edge([(368,612),(415,612),(415,886),(911,886),(911,858)],'Geometry lookup',color='teal',lx=612,ly=879)
    c.foot('Selected fields shown. Files have logical keys, not SQL constraints. No patient-level joins to CDC, ENSANUT or the hospital vault.')
    return c.finish()


def model():
    c=Canvas('Screening model / training and held-out evaluation','Data lineage · parallel branches keep training, threshold selection and testing separate',920)
    c.db(420,106,360,104,'CDC UCI 891',['253,680 public survey records'])
    c.icon('split',575,252,BLUE,45)
    c.label(600,326,'Stratified 70 / 15 / 15 · seed 2026')
    c.db(45,374,300,100,'TRAIN · 70%',['177,576 records'],TEAL)
    c.db(451,374,300,100,'VALIDATION · 15%',['38,052 records'],BLUE)
    c.db(857,374,300,100,'TEST · 15%',['38,052 records'],VIOLET)
    c.node(45,545,300,105,'Fit model',['Scaler fit on training only','Logistic regression'],'model',TEAL)
    c.node(451,545,300,105,'Choose threshold',['Sensitivity target ≥80%','Validation labels only'],'chart',BLUE)
    c.node(857,545,300,105,'Evaluate frozen model',['AUC / AP / Brier / confusion','No tuning on test'],'chart',VIOLET)
    c.node(50,752,390,98,'Versioned model JSON',['Fold standardization into weights','Quantize W, B at scale 10⁹'],'file',TEAL,kind='file')
    c.node(747,752,410,98,'Metrics + numerical comparison',['Same labeled sample for all variants','Float ↔ fixed-point ↔ Paillier'],'file',VIOLET,kind='file')
    c.edge([(600,210),(600,252)])
    c.edge([(587,289),(195,289),(195,374)],color='teal')
    c.edge([(600,297),(600,374)])
    c.edge([(617,289),(1007,289),(1007,374)],color='violet')
    for x,col in [(195,'teal'),(600,'blue'),(1007,'violet')]:c.edge([(x,474),(x,545)],color=col)
    c.edge([(345,585),(451,585)],'Predict',color='teal',ly=572)
    c.edge([(751,585),(857,585)],'Freeze',ly=572)
    c.edge([(195,650),(195,752)],'Export weights',color='teal',lx=268,ly=707)
    c.edge([(600,650),(600,703),(350,703),(350,752)],'Threshold',lx=528,ly=696)
    c.edge([(1007,650),(1007,752)],'Report',color='violet',lx=1052,ly=707)
    c.foot('Repeated feature profiles can cross splits. ENSANUT is a separate reduced exploratory experiment, not clinical validation of this model.')
    return c.finish()


def forecast():
    c=Canvas('E5 forecasting / selection, reconciliation and evaluation','Data-flow DAG · aggregate notifications only; independent of encrypted patient screening',1030)
    c.db(44,130,290,112,'SINAVE weekly data',['222 aggregate series','2 types × 3 sexes × 37 areas'],AMBER)
    c.decision(548,186,270,110,'Complete calendar?','Finite weekly data')
    c.node(826,145,300,80,'Stop on gaps','No global interpolation','shield',RED,kind='terminal')
    c.group(47,328,1092,205,'ROLLING-ORIGIN SELECTION','Only observations before each origin enter its fit.',BLUE)
    c.node(88,405,296,88,'Seasonal naive','Repeat the prior 52 weeks','chart',BLUE)
    c.node(461,405,296,88,'ETS','Damped additive Holt–Winters','chart',BLUE)
    c.node(844,405,250,88,'Select model','SMAPE + MAE tie-break','check',BLUE)
    c.node(46,624,300,102,'Fit + forecast',['63 steps: 11 bridge + 52','Empirical error bands'],'model',TEAL)
    c.node(450,624,300,102,'Reconcile hierarchy',['National → region → state','Sparse fallback if required'],'split',TEAL)
    c.node(852,624,300,102,'Public forecast JSON',['Point / bands / evaluation','No patient identifiers'],'file',VIOLET,kind='file')
    c.node(852,836,300,98,'Forecast dashboard',['Filters / curves / quarters','Cost + source required'],'browser',BLUE)
    c.group(48,814,705,132,'OUTER EVALUATION · RE-RUN THE WHOLE PIPELINE','Two overlapping origins · selection → fit → fallback → reconciliation',VIOLET)
    c.lines(70,900,['Publish actual SMAPE and empirical 80/95% coverage.','Limited origins and undercoverage: bands remain exploratory.'],640,15,VIOLET)
    c.edge([(334,186),(413,186)],'Read',color='amber',ly=171)
    c.edge([(683,186),(826,186)],'No',color='red',ly=171)
    c.edge([(548,241),(548,292),(410,292),(410,388),(236,388),(236,405)],'Yes',lx=477,ly=282)
    c.edge([(410,388),(609,388),(609,405)])
    c.edge([(384,449),(420,449),(420,514),(819,514),(819,462),(844,462)],color='blue')
    c.edge([(757,439),(844,439)],'Compare',lx=799,ly=427)
    c.edge([(969,493),(969,568),(196,568),(196,624)],'Fit selected model on available history',color='teal',lx=589,ly=559)
    c.edge([(346,675),(450,675)],'Point + bands',color='teal',lx=398,ly=660)
    c.edge([(750,675),(852,675)],'Export',color='violet',lx=801,ly=660)
    c.edge([(1002,726),(1002,836)],'Static artifact',color='violet',lx=1080,ly=790)
    c.edge([(753,881),(802,881),(802,713),(852,713)],'Evaluation metrics',color='violet',dash=True,lx=798,ly=789)
    c.foot('E5 is unencrypted. No project unit cost is established; user-entered budget scenarios are not a validated operating budget.')
    return c.finish()


def evidence():
    c=Canvas('Release evidence / artifacts and final delivery gate','Artifact lineage + decision gate · observed execution and human approval are separate inputs',960)
    c.node(48,134,318,112,'Pinned source + model',['Clean source / commit identity','Code and model SHA-256'],'file',BLUE,kind='file')
    c.node(477,134,310,112,'Real target execution',['VM identity + containers','TLS / architecture / versions'],'server',TEAL)
    c.node(886,134,266,112,'Versioned metrics',['Process measurement','Hospital API + vault'],'chart',VIOLET,kind='file')
    c.node(46,378,320,112,'Original audit bundle',['Wire hashes + scoped checks','Retain raw logs outside Git'],'file',VIOLET,kind='file')
    c.node(477,378,310,112,'Human-owned records',['Labs / teammate review','Public video / AI approval'],'person',AMBER)
    c.node(886,378,266,112,'VM screenshots',['Provider / uname / CPU','Containers / OpenSSL'],'browser',TEAL,kind='file')
    c.decision(633,655,336,146,'Required records complete?','Final package gate')
    c.node(70,621,290,92,'DRAFT + missing list','Keep unmet gates open','file',AMBER,kind='file')
    c.node(885,621,270,92,'Final ZIP + manifest','Checksums / source identity','package',TEAL)
    c.node(885,820,270,80,'Leader submits','All four review first','check',TEAL,kind='terminal')
    c.edge([(366,190),(477,190)],'Build',ly=176)
    c.edge([(787,190),(886,190)],'Measure',color='teal',ly=176)
    c.edge([(632,246),(632,307),(206,307),(206,378)],'Audit mode',color='violet',lx=355,ly=297)
    c.edge([(716,246),(716,300),(1020,300),(1020,378)],'Capture',color='teal',lx=1072,ly=340)
    c.edge([(1020,246),(1020,274),(1170,274),(1170,574),(728,574),(728,623)],'Measurement JSON',color='violet',lx=1008,ly=562)
    c.edge([(206,490),(206,547),(566,547),(566,610)],color='violet')
    c.edge([(632,490),(632,582)],color='amber')
    c.edge([(1020,490),(1020,547),(704,547),(704,612)],color='teal')
    c.edge([(465,655),(360,655)],'No',color='amber',ly=640)
    c.edge([(801,655),(885,655)],'Yes',color='teal',ly=640)
    c.edge([(1020,713),(1020,820)],'Review + upload',color='teal',lx=1090,ly=785)
    c.foot('The gate rejects missing records; it cannot establish attendance, authentic provider identity or organizer decisions by itself.')
    return c.finish()


RENDERERS={'system':system,'deployment':deployment,'hospital':hospital,'service':service,
           'protocol':protocol,'vault':vault,'data-model':data_model,'model':model,
           'forecast':forecast,'evidence':evidence}
VIEW_TYPES={'system':('Container architecture','C4 / containers'),
            'deployment':('Deployment topology','Infrastructure'),
            'hospital':('Hospital flow','Flowchart'),
            'service':('Risk-service flow','Flowchart'),
            'protocol':('Request sequence','UML / sequence'),
            'vault':('Encrypted vault schema','Record schema'),
            'data-model':('Analytical data model','Logical ERD'),
            'model':('Model lifecycle','Data lineage'),
            'forecast':('Forecast pipeline','Data-flow DAG'),
            'evidence':('Release evidence','Artifact lineage')}
