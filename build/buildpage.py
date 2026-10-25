#!/usr/bin/env python3
"""Build the single-file Commercial Pilot study guide."""
import base64, collections, html, io, json, os, re, hashlib, datetime

# Runs from the working tree (flat) or from the repository root
# (python3 build/buildpage.py). Work out which, rather than assuming.
HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(HERE) == 'build':
    ROOT, BUILD, W = os.path.dirname(HERE), HERE, 'figures'
    def D(n): return os.path.join('data', n)
else:
    ROOT, BUILD, W = HERE, HERE, 'web'
    _ALT = {'acronyms.json': 'gsp/acronyms.json', 'figs.json': 'gs/figs.json'}
    def D(n): return _ALT.get(n, n)
os.chdir(ROOT)
def esc(s): return html.escape(s or '', quote=False)
def key(q): return hashlib.md5(q.encode('utf-8')).hexdigest()[:10]

db       = json.load(open(D('all.json')))
acr      = json.load(open(D('acronyms.json')))
sysd     = json.load(open(D('pa28-systems.json')))
wbd      = json.load(open(D('wb-data.json')))
wbw      = json.load(open(D('wb-worked.json')))
gsfigs   = json.load(open(D('figs.json')))
plan     = json.load(open(D('rideplan.json')))

# ---------------------------------------------------------------- figures
CAP = {
 'clouds':'Cloud types by altitude — high, middle, low, and vertical development',
 'airmass':'Air mass source regions: arctic (A), continental polar (cP), maritime polar (mP), continental tropical (cT), maritime tropical (mT)',
 'metarwx':'METAR present weather — qualifier and phenomena table, read in column order',
 'pirep':'PIREP encoding — the thirteen elements and their contractions',
 'vorsv':'VOR service volumes — terminal, low altitude, high altitude',
 'sectional':'Sectional chart legend',
 'inop':'Operating with inoperative instruments or equipment — the 91.213 decision path',
}
for k, v in gsfigs.items():
    CAP[k] = v['cap']

SVGCAP = {
 'avionics':'Two ways the same job gets done — one integrated system, or separate displays with a panel navigator. Know which one you are flying.',
 'cabinheat2':'Cabin heat, ventilation and defrost — heat is picked up off a shroud around the exhaust muffler, which is why a cracked muffler is a carbon monoxide problem.',
 'elec2':'A typical bus layout — what each bus feeds, and what is left when the main bus goes.',
 'steepspiral':'Steep spiral — three constant-radius gliding turns about a point, bank varying with groundspeed.',
 'chandelle':'Chandelle — bank set and held through the first 90 degrees while pitch rises; pitch held and bank rolled off through the second.',
 'lazy8':'Lazy eight — the 45, 90 and 135 degree reference points, and what should be true at each.',
 'pylons':'Eights on pylons — the ground track, the pivotal altitude arithmetic, and which way to correct.',
 'po180':'The power-off 180 — abeam at or below 1,000 ft AGL, and a touchdown within 200 ft beyond your point.',
}

# Gold Seal page renders attached to the question each one actually answers.
GSMAP = {
 'gs-alternate'  : 'What is the 1-2-3 rule for filing an alternate, and where does it come from?',
 'gs-asi'        : 'What does the white arc on the airspeed indicator represent?',
 'gs-oxygen'     : 'What are the Part 91 supplemental oxygen requirements?',
 'gs-icing'      : 'What is mixed icing?',
 'gs-lightgun'   : 'Which light gun signal means the same thing in the air and on the ground, and which one is ground only?',
 'gs-fourforces' : 'What are the four forces acting on an airplane in flight?',
 'gs-turns'      : 'How does load factor vary with bank angle in a level turn?',
 'gs-airspace'   : 'What is the airspace stack above a Class D airport that lies under a Class B shelf?',
 'gs-night'      : 'What are the three different definitions of night a commercial pilot must keep straight?',
 'gs-amilegal'   : 'What are the four elements of common carriage, and what does holding out mean?',
 'gs-metar'      : 'What sort of information appears in the remarks section of a METAR?',
 'gs-taf'        : 'What is a TAF, how often is it issued, and how long is it valid?',
 'gs-tstorm'     : 'What happens in the mature stage of a thunderstorm, and why is it the most dangerous?',
 'gs-chandelle'  : 'What is a chandelle and what is it meant to demonstrate?',
 'gs-lazy8'      : 'What is a lazy eight and what does it demonstrate?',
 'gs-steepspiral': 'What is a steep spiral and what does it demonstrate?',
 'gs-pylons'     : 'Why does the pivotal altitude change during eights on pylons?',
}

def norm(q): return re.sub(r'\s+', ' ', q).strip().lower()

# The research notes were written for a machine to read and shout whole clauses
# in capitals. Keep the real abbreviations, sentence-case the shouting.
KEEPCAPS = set("""POH TCDS CG VB FAA NTSB STC AD RPM KIAS KTAS MPH MSL AGL ACS DPE
LL US SAE PA O FBO CFI PIC VFR IFR ATC METAR TAF AC CFR NOTE NOTES SECTION OEM
ATP BFO ELT GPS VOR ILS ADF DME EGT CHT MP OAT TBO AFM II III IV VI
VII VIII IX XI XII XIII XIV XV XVI XVII QT QTS LB LBS GAL HP AMP AMPS DC
PDF JSON HTML""".split())
SHOUT = re.compile(r"^[A-Z][A-Z'./-]+$")
def unshout(s):
    """Lower-case a word only when it sits in a run of three or more shouted
    words, so 'THE HANDBOOK MISMATCH IS' softens but 'POH VB-1180' survives."""
    if not isinstance(s, str):
        return s
    toks = re.split(r'(\s+)', s)
    words = [j for j, t in enumerate(toks) if t.strip()]
    mark, run = set(), []
    for j in words + [None]:
        core = toks[j].strip(".,;:'\"()") if j is not None else ''
        if j is not None and SHOUT.match(core) and core not in KEEPCAPS \
           and not any(c.isdigit() for c in core):
            run.append(j)
        else:
            if len(run) >= 3:
                mark.update(run)
            run = []
    for j in mark:
        toks[j] = toks[j].lower()
    out = ''.join(toks)
    return re.sub(r'(^|[.!?]\s+)([a-z])',
                  lambda m: m.group(1) + m.group(2).upper(), out)
byq = {}
for s in db:
    for it in s['items']:
        byq.setdefault(norm(it['q']), it)

attached, missed = 0, []
for fkey, q in GSMAP.items():
    it = byq.get(norm(q))
    if it is None:
        missed.append(q); continue
    cur = it.get('img')
    if cur and cur != fkey:
        # keep both: the scanned page first, then the drawn diagram under it
        it['img'] = [fkey, cur] if not isinstance(cur, list) else [fkey] + cur
    else:
        it['img'] = fkey
    attached += 1
print('gold seal figures attached: %d  missed: %s' % (attached, missed))

# raster figures that are actually referenced
def imglist(it):
    v = it.get('img')
    if not v: return []
    return v if isinstance(v, list) else [v]

used = sorted({k for s in db for it in s['items'] for k in imglist(it)
               if os.path.exists(os.path.join(W, k + '.webp'))})
FIGB64 = {}
for k in used:
    with open(os.path.join(W, k + '.webp'), 'rb') as f:
        FIGB64[k] = 'data:image/webp;base64,' + base64.b64encode(f.read()).decode()
SVG = {}
for k in SVGCAP:
    p = os.path.join(W, k + '.svg')
    if os.path.exists(p):
        SVG[k] = open(p, encoding='utf-8').read()

# ------------------------------------------------- maneuver ordering
# The instructor flagged lazy eights as the weakest maneuver, so they lead.
# Scoring rather than first-match: a question that merely name-checks three
# maneuvers is a general one and belongs after all of them, not at the front
# because the words "lazy eight" happened to appear in it.
MANGROUPS = [('lazy eight',   ['lazy eight', 'lazy 8']),
             ('chandelle',    ['chandelle']),
             ('pylons',       ['eights on pylons', 'pylon', 'pivotal altitude']),
             ('steep spiral', ['steep spiral']),
             ('power-off 180',['power-off 180', 'power off 180', 'accuracy landing']),
             ('steep turn',   ['steep turn']),
             ('short field',  ['short-field', 'short field']),
             ('soft field',   ['soft-field', 'soft field'])]
def manrank(it):
    q, a = it['q'].lower(), it['a'].lower()
    sc = []
    for i, (_, words) in enumerate(MANGROUPS):
        n = sum(3 * q.count(w) + a.count(w) for w in words)
        sc.append((n, i))
    hits = [x for x in sc if x[0] > 0]
    if not hits:
        return (len(MANGROUPS) + 1, 0)
    best = max(h[0] for h in hits)
    top = [h for h in hits if h[0] == best]
    # a tie across maneuvers means the question is about all of them
    if len(top) > 1:
        return (len(MANGROUPS), 0)
    return (top[0][1], -best)
for s in db:
    if s['s'] == 'Commercial Maneuvers':
        s['items'].sort(key=manrank)
    # inside every section, the examiner's focus areas float to the top
    s['items'].sort(key=lambda it: 0 if it.get('focus') else 1)

SRCS = [('chs', 'CHS', 'CHS Flight School study guide'),
        ('fi',  'Flight Insight', 'CPL At A Glance'),
        ('gs',  'Gold Seal', 'Commercial Certificate — Everything You Need To Know'),
        ('poh', 'Warrior POH', 'PA-28-161 handbook, TCDS and registry'),
        ('aero','Maneuver', 'The aerodynamics behind each maneuver'),
        ('gouge','Gouge', 'Written to close gaps a real ride with this examiner exposed'),
        ('xc',  'Cross-country', 'The KRBW to 1A3 planning scenario'),
        ('acs', 'Added', 'Written in to close a gap')]
SRCN = dict((k, n) for k, n, _ in SRCS)

# ---------------------------------------------------------------- CSS
BASECSS = open(os.path.join(BUILD, 'rec_style.css'), encoding='utf-8').read()
EXTRA = """
/* ---- tabs ---- */
#tabs{display:flex;gap:4px;border-bottom:1px solid var(--line);margin:18px 0 0;overflow-x:auto;
-webkit-overflow-scrolling:touch;scrollbar-width:none}
#tabs::-webkit-scrollbar{display:none}
.tb{font:inherit;font-size:14.5px;font-weight:600;padding:10px 15px;border:0;background:none;
color:var(--ink3);cursor:pointer;border-bottom:2.5px solid transparent;white-space:nowrap;
-webkit-tap-highlight-color:transparent}
.tb.on{color:var(--accent);border-bottom-color:var(--accent)}
.pane{display:none}
.pane.on{display:block}
/* ---- focus badge: the four areas this examiner lives in ---- */
.tg.poh{color:var(--accent);background:var(--accent-soft);border:1px solid var(--accent-line)}
.tg.gs{color:var(--hook);background:var(--hook-soft);border:1px solid var(--hook-line)}
.fcs{display:inline-block;margin-left:7px;vertical-align:2px;font-family:var(--mono);
font-size:9.5px;letter-spacing:.07em;text-transform:uppercase;padding:1px 6px;border-radius:4px;
color:var(--warnc);background:var(--panel);border:1px solid var(--warnc);white-space:nowrap}
.fcs.aero{color:var(--ok);border-color:var(--ok-line);background:var(--ok-soft)}
.fcs.ride{color:var(--hook);border-color:var(--hook-line);background:var(--hook-soft)}
.fcs.fig{color:var(--accent);border-color:var(--accent-line);background:var(--accent-soft)}
.fcs.day{color:var(--warnc);border-color:var(--warnc);background:var(--panel)}
.tg.xc{color:var(--ok);background:var(--ok-soft);border:1px solid var(--ok-line)}
/* ---- run the ride ---- */
.rstage{border:1px solid var(--line);border-radius:11px;background:var(--panel);margin:0 0 12px;
overflow:hidden}
.rstage>summary,.ritem>summary{cursor:pointer;list-style:none;display:flex;align-items:center;
gap:10px;flex-wrap:wrap;-webkit-tap-highlight-color:transparent}
.rstage>summary::-webkit-details-marker,.ritem>summary::-webkit-details-marker{display:none}
.rstage>summary{padding:15px 17px}
.rstage>summary::before,.ritem>summary::before{content:"\u203A";font-size:18px;line-height:1;
color:var(--accent);transition:transform .15s;flex:none;width:12px}
.rstage[open]>summary::before,.ritem[open]>summary::before{transform:rotate(90deg)}
.rsn{font-family:var(--serif);font-size:19px;flex:1;min-width:0}
.rsc,.rc{font-family:var(--mono);font-size:12px;color:var(--ink3);flex:none}
.rsc b,.rc b{color:var(--ok)}
.ritem{border-top:1px solid var(--hair)}
.ritem>summary{padding:12px 17px 12px 20px}
.rq{flex:1;min-width:0;font-size:15px;line-height:1.45;color:var(--ink)}
.ritem.rdoneall .rq{color:var(--ink3)}
.cov{font-family:var(--mono);font-size:9.5px;letter-spacing:.06em;text-transform:uppercase;
padding:1px 6px;border-radius:4px;white-space:nowrap;flex:none}
.cov.thin{color:var(--hook);background:var(--hook-soft);border:1px solid var(--hook-line)}
.cov.none{color:var(--warnc);background:var(--panel);border:1px solid var(--warnc)}
.rnote{margin:0 17px 6px 20px;font-size:13px;color:var(--ink3);font-style:italic;line-height:1.45}
.rfix{margin:2px 17px 8px 20px;padding:10px 12px;border-radius:8px;font-size:13.5px;line-height:1.5;
border:1px solid var(--warnc);background:var(--panel);color:var(--ink)}
.rfix b{color:var(--warnc)}
.cov.fix{color:var(--warnc);background:var(--panel);border:1px solid var(--warnc)}
.ritem ul{padding:0 17px 12px 20px}
.ritem.hide,.rstage.hide{display:none}
.tg.gouge{color:var(--warnc);background:var(--panel);border:1px solid var(--warnc)}
.tg.aero{color:var(--ok);background:var(--ok-soft);border:1px solid var(--ok-line)}
/* ---- callout ---- */
.note{border:1px solid var(--hook-line);background:var(--hook-soft);border-radius:10px;
padding:13px 15px;margin:14px 0;font-size:14.5px;line-height:1.55}
.note b{color:var(--hook)}
.note.warn{border-color:var(--warnc);background:var(--panel)}
.note.warn b{color:var(--warnc)}
/* ---- acronyms ---- */
.ag{border:1px solid var(--line);border-radius:11px;background:var(--panel);margin:0 0 12px;
overflow:hidden}
.ag>summary{cursor:pointer;list-style:none;padding:14px 17px;display:flex;align-items:center;
gap:10px;-webkit-tap-highlight-color:transparent}
.ag>summary::-webkit-details-marker{display:none}
.ag>summary::before{content:"›";font-size:19px;line-height:1;color:var(--accent);
transition:transform .15s;flex:none;width:12px}
.ag[open]>summary::before{transform:rotate(90deg)}
.agn{font-family:var(--serif);font-size:18.5px;flex:1;min-width:0}
.agc{font-family:var(--mono);font-size:11.5px;color:var(--ink3)}
.ai{padding:11px 17px;border-top:1px solid var(--hair);display:flex;gap:11px;align-items:flex-start}
.ai.hide{display:none}
.ab{flex:none;width:26px;height:22px;border-radius:5px;font-family:var(--mono);font-size:11px;
font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:2px}
.t1{background:var(--warnc);color:#fff}
.t2{background:var(--hook-soft);color:var(--hook);border:1px solid var(--hook-line)}
.t3{background:var(--accent-soft);color:var(--accent);border:1px solid var(--accent-line)}
.t4{background:var(--hair);color:var(--ink3);border:1px solid var(--line)}
.at{font-family:var(--mono);font-size:14.5px;font-weight:700;color:var(--ink);letter-spacing:.02em}
.ax{font-size:14.5px;color:var(--ink);margin-top:2px}
.ad{font-size:13.5px;color:var(--ink2);margin-top:4px;line-height:1.5}
.areg{font-family:var(--mono);font-size:11.5px;color:var(--ink3);margin-top:4px}
.awhy{font-size:12px;color:var(--ink3);font-style:italic;margin-top:3px}
/* ---- aircraft / reference rows ---- */
.rsec{border:1px solid var(--line);border-radius:11px;background:var(--panel);margin:0 0 12px;
overflow:hidden}
.rsec>summary{cursor:pointer;list-style:none;padding:14px 17px;display:flex;align-items:center;
gap:10px;-webkit-tap-highlight-color:transparent}
.rsec>summary::-webkit-details-marker{display:none}
.rsec>summary::before{content:"›";font-size:19px;line-height:1;color:var(--accent);
transition:transform .15s;flex:none;width:12px}
.rsec[open]>summary::before{transform:rotate(90deg)}
.rn{font-family:var(--serif);font-size:18.5px;flex:1}
.cr{display:flex;gap:14px;padding:9px 17px;border-top:1px solid var(--hair);font-size:14.5px;
align-items:baseline}
.cr .ck{flex:0 0 42%;color:var(--ink2)}
.cr .cv{flex:1;font-weight:600;color:var(--ink);text-align:right;font-variant-numeric:tabular-nums}
.cr.wide{display:block}
.cr.wide .ck{margin-bottom:3px}
.cr.wide .cv{text-align:left;font-weight:600}
.cn{font-size:12.5px;color:var(--ink3);line-height:1.5;padding:0 17px 9px;margin-top:-4px}
.cn.bad{color:var(--warnc)}
.csrc{font-family:var(--mono);font-size:10.5px;color:var(--ink3);padding:0 17px 9px;margin-top:-4px}
.pl{font-family:var(--mono);font-size:12.5px;white-space:pre-wrap;background:var(--bg);
border:1px solid var(--line);border-radius:7px;padding:11px 13px;margin:9px 17px;color:var(--ink)}
/* ---- weight and balance ---- */
.wbg{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:4px 0 12px}
@media(max-width:560px){.wbg{grid-template-columns:1fr}}
.wf{display:flex;align-items:center;gap:9px;background:var(--panel);border:1px solid var(--line);
border-radius:9px;padding:9px 12px}
.wf label{flex:1;font-size:14px;color:var(--ink2)}
.wf input{width:84px;font:inherit;font-size:15px;padding:6px 9px;border-radius:7px;text-align:right;
border:1px solid var(--line);background:var(--bg);color:var(--ink);font-variant-numeric:tabular-nums}
.wf .wu{font-family:var(--mono);font-size:11px;color:var(--ink3);width:22px}
#wbout{border:1px solid var(--line);border-radius:11px;background:var(--panel);overflow:hidden;
margin:0 0 14px}
#wbout table{width:100%;border-collapse:collapse;font-size:14px}
#wbout th{text-align:right;font-family:var(--mono);font-size:10.5px;letter-spacing:.07em;
text-transform:uppercase;color:var(--ink3);font-weight:400;padding:10px 13px;
border-bottom:1px solid var(--line)}
#wbout th:first-child{text-align:left}
#wbout td{padding:8px 13px;border-bottom:1px solid var(--hair);text-align:right;
font-variant-numeric:tabular-nums}
#wbout td:first-child{text-align:left;color:var(--ink2)}
#wbout tr.tot td{font-weight:700;border-top:1.5px solid var(--line);border-bottom:0;color:var(--ink)}
.verd{padding:13px 15px;font-size:15px;font-weight:600;line-height:1.5}
.verd.ok{background:var(--ok-soft);color:var(--ok);border-top:1px solid var(--ok-line)}
.verd.no{background:var(--panel);color:var(--warnc);border-top:1.5px solid var(--warnc)}
.verd small{display:block;font-weight:400;font-size:13px;margin-top:4px;color:var(--ink2)}
.wbtn{display:flex;gap:7px;flex-wrap:wrap;margin:0 0 12px}
/* ---- misc ---- */
.kicker{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;
color:var(--ink3);margin:26px 0 9px;padding-top:8px;border-top:1px solid var(--line)}
.kicker:first-child{border-top:0;padding-top:0;margin-top:4px}
#nores{padding:26px 0;text-align:center}
#nores.hide{display:none}
.nrt{font-size:16px;color:var(--ink2)}
.nrs{font-size:14px;color:var(--ink3);margin-top:6px}
.it.hide,details.sec.hide,.ag.hide{display:none}
.it.ansm .qt::after{content:" \\2014 match in the answer";font-size:12px;color:var(--ink3);
font-style:italic}
mark{background:var(--hook-soft);color:var(--ink);border-radius:3px;padding:0 1px}
figcaption{font-size:12.5px;color:var(--ink3);line-height:1.45;margin-top:6px;font-style:italic}
"""

# ---------------------------------------------------------------- study pane
def figure_html(fkey):
    if fkey in SVG:
        return ('<figure class="fg vec">%s<figcaption>%s</figcaption></figure>'
                % (SVG[fkey], esc(SVGCAP.get(fkey, ''))))
    if fkey in FIGB64:
        cap = CAP.get(fkey, '')
        tail = ' <span style="font-style:normal">tap for a closer look</span>'
        return ('<figure class="fg"><img data-f="%s" alt="%s" loading="lazy">'
                '<figcaption>%s%s</figcaption></figure>'
                % (fkey, esc(cap[:90]), esc(cap), tail))
    return ''

def qrow(it, extra_cls=''):
    docs = it['doc'].split()
    tags = ''.join('<span class="tg %s">%s</span>' % (d, esc(SRCN[d])) for d in docs)
    if it.get('day'):
        tags += '<span class="fcs day">work on the day</span>'
    if it.get('g'):
        tags += '<span class="fcs ride">checkride</span>'
    if it.get('focus') == 'sys':
        tags += '<span class="fcs">systems</span>'
    elif it.get('focus') == 'aero' and 'aero' not in docs:
        tags += '<span class="fcs aero">maneuver</span>'
    fg = ''.join(figure_html(k) for k in imglist(it))
    if it.get('img'):
        tags += '<span class="fcs fig">figure</span>'
    return ('<li class="it%s" data-k="%s" data-d="%s"%s%s%s%s>'
            '<button class="tick" aria-label="mark done"></button><div class="qc">'
            '<button class="qb"><span class="qt">%s</span>%s</button>'
            '<div class="ans">%s%s</div></div></li>'
            % (extra_cls, key(it['q']), esc(it['doc']),
               ((' data-f="%s"' % it['focus']) if it.get('focus') else ''),
               (' data-g="1"' if it.get('g') else ''),
               (' data-img="1"' if it.get('img') else ''),
               (' data-day="1"' if it.get('day') else ''),
               esc(it['q']), tags, it['a'], fg))

study, nav = [], []
for s in db:
    items = s['items']
    nav.append('<a href="#s%s"><span>%s</span><span class="nc">%d</span></a>'
               % (key(s['s']), esc(s['s']), len(items)))
    rows = [qrow(it) for it in items]
    study.append(
      '<details class="sec qsec" id="s%s"><summary><span class="sname">%s</span>'
      '<span class="sprog"><b class="sdone">0</b> / <span>%d</span></span>'
      '<span class="sbar"><i></i></span></summary>%s<ul>%s</ul></details>'
      % (key(s['s']), esc(s['s']), len(items),
         '<p class="sb">%s</p>' % esc(s['b']) if s.get('b') else '', ''.join(rows)))

byk = {}
for sec in db:
    for it in sec['items']:
        byk[key(it['q'])] = it

COVLBL = {'good': '', 'thin': 'was thin \u2014 filled in',
          'none': 'the deck had nothing \u2014 written from scratch'}

# The headings quote the prior candidate verbatim. Where what he said was wrong,
# or where his airplane differed from this one, say so at the top of the item so
# the quote is not absorbed as the lesson.
CORRECTION = {
 7: "That airplane had no KOEL. Yours does \u2014 the Warrior handbook carries a kinds of "
    "operation equipment list at Section 2.19, and 91.213(d)(2) names it directly, so your "
    "chain is 91.205, then the KOEL, then the equipment list, then 91.213. The "
    "ATOMATOFLAMES-only route he took is the fallback for an airplane without one.",
 35:"His conclusion is defensible but his reasoning is backwards, and this is worth getting "
    "right before you repeat it. An airplane weathervanes into the wind: a crosswind from the "
    "LEFT pushes the tail right and the nose left, which adds to the left-turning tendencies "
    "you are already holding right rudder against. A RIGHT crosswind is the one that partly "
    "cancels them. Defend a runway choice on component size, length and the emergency return, "
    "not on rudder.",
 58:"The error here is the one to take away: ground reference maneuvers are entered DOWNWIND, "
    "with a tailwind, at the fastest groundspeed and so the highest pivotal altitude.",
 43:"There is no verbatim numbered list of stall stages in any FAA document. Describe them "
    "rather than reciting three words, and keep in mind that incipient is the FAA's term for a "
    "phase of a spin, not of a stall \u2014 which is probably what tripped him.",
}
ridehtml = []
for st in plan:
    blocks, nq_st = [], 0
    for item in st['items']:
        rows = [qrow(byk[k], ' rit') for k in item['k'] if k in byk]
        nq_st += len(rows)
        flag = ''
        if item['c'] != 'good':
            flag = '<span class="cov %s">%s</span>' % (item['c'], esc(COVLBL[item['c']]))
        note = ('<p class="rnote">%s</p>' % esc(item['n'])) if item.get('n') else ''
        gi = item.get('gi')
        if gi in CORRECTION:
            note = ('<p class="rfix"><b>Careful here.</b> %s</p>' % esc(CORRECTION[gi])) + note
        blocks.append(
          '<details%s><summary>'
          '<span class="rq">%s</span>%s%s'
          '<span class="rc"><b class="rdone">0</b>/%d</span>'
          '</summary>%s<ul>%s</ul></details>'
          % (' class="ritem fixed"' if item.get('gi') in CORRECTION else ' class="ritem"',
             esc(item['i']), flag,
             '<span class="cov fix">read the note</span>' if item.get('gi') in CORRECTION else '',
             len(rows), note, ''.join(rows)))
    ridehtml.append(
      '<details class="rstage" open><summary><span class="rsn">%s</span>'
      '<span class="rsc"><b class="rsdone">0</b> / %d</span>'
      '<span class="sbar"><i></i></span></summary>%s</details>'
      % (esc(st['t']), nq_st, ''.join(blocks)))

# ---------------------------------------------------------------- acronyms pane
agroups = []
for g in acr['groups']:
    rows = []
    for a in g['items']:
        t = int(a.get('tier', 3))
        rows.append(
          '<div class="ai" data-t="%d"><span class="ab t%d">%d</span><div>'
          '<div class="at">%s</div><div class="ax">%s</div><div class="ad">%s</div>%s%s'
          '</div></div>'
          % (t, t, t, esc(a['t']), esc(a['x']), esc(a['d']),
             '<div class="areg">%s</div>' % esc(a['reg']) if a.get('reg') else '',
             '<div class="awhy">%s</div>' % esc(a['why']) if a.get('why') else ''))
    agroups.append('<details class="ag" open><summary><span class="agn">%s</span>'
                   '<span class="agc">%d</span></summary>%s</details>'
                   % (esc(g['g']), len(g['items']), ''.join(rows)))

# ---------------------------------------------------------------- aircraft pane
def leaf_row(label, leaf):
    if not isinstance(leaf, dict) or 'value' not in leaf:
        return ''
    v = leaf.get('value')
    if v is None:
        val = '<span style="color:var(--ink3);font-weight:400">not published — see note</span>'
    elif isinstance(v, list):
        val = esc('; '.join(str(x) for x in v))
    elif isinstance(v, bool):
        val = 'yes' if v else 'no'
    else:
        val = esc(str(v))
    if leaf.get('unit') and v is not None and not isinstance(v, bool):
        val += ' <span style="color:var(--ink3);font-weight:400">%s</span>' % esc(str(leaf['unit']))
    wide = len(re.sub('<[^>]+>', '', val)) > 40 or isinstance(v, list)
    out = ['<div class="cr%s"><span class="ck">%s</span><span class="cv">%s</span></div>'
           % (' wide' if wide else '', esc(label), val)]
    if leaf.get('note'):
        bad = leaf.get('carries_to_1981') is False
        out.append('<div class="cn%s">%s</div>'
                   % (' bad' if bad else '', esc(unshout(leaf['note']))))
    if leaf.get('src'):
        out.append('<div class="csrc">%s</div>' % esc(str(leaf['src'])))
    return ''.join(out)

LBLCAPS = {'tcds':'TCDS','poh':'POH','cg':'CG','rpm':'RPM','kias':'KIAS','msl':'MSL',
           'agl':'AGL','faa':'FAA','stc':'STC','sae':'SAE','vb1180':'VB-1180','us':'US',
           'oat':'OAT','egt':'EGT','cht':'CHT','elt':'ELT','tbo':'TBO','acs':'ACS',
           'afm':'AFM','ac':'AC','dc':'DC','vne':'VNE','vno':'VNO','vfe':'VFE','va':'VA',
           'vso':'VSO','vs1':'VS1','vx':'VX','vy':'VY','gal':'gal','hp':'hp','lb':'lb'}
def pretty(k):
    words = k.replace('_', ' ').strip().split()
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if lw in LBLCAPS:
            out.append(LBLCAPS[lw])
        elif i == 0:
            out.append(w.capitalize())
        else:
            out.append(w.lower())
    return ' '.join(out)

FOCUS_FIRST = ['powerplant', 'oil', 'fuel', 'electrical']
REST = ['limitations', 'airspeeds', 'other_systems', 'emergency',
        'normal_procedures', 'servicing', 'aircraft']
TITLES = {'powerplant': 'Powerplant', 'oil': 'Oil system', 'fuel': 'Fuel system',
          'electrical': 'Electrical system', 'limitations': 'Limitations',
          'airspeeds': 'Airspeeds', 'other_systems': 'Other systems',
          'emergency': 'Emergency procedures', 'normal_procedures': 'Normal procedures',
          'servicing': 'Servicing', 'aircraft': 'The airplane'}

def build_block(d, depth=0):
    out = []
    for k, v in d.items():
        if k.startswith('_'):
            continue
        if isinstance(v, dict) and 'value' in v:
            out.append(leaf_row(pretty(k), v))
        elif isinstance(v, dict):
            inner = build_block(v, depth + 1)
            if inner:
                out.append('<div class="cr wide"><span class="ck" style="font-weight:600;'
                           'color:var(--ink)">%s</span></div>%s' % (esc(pretty(k)), inner))
        elif isinstance(v, list) and v and all(isinstance(x, str) for x in v):
            out.append('<div class="cr wide"><span class="ck">%s</span>'
                       '<span class="cv">%s</span></div>'
                       % (esc(pretty(k)), esc(' · '.join(v))))
        elif isinstance(v, str):
            out.append('<div class="cr wide"><span class="ck">%s</span>'
                       '<span class="cv">%s</span></div>' % (esc(pretty(k)), esc(v)))
    return ''.join(out)

acblocks = []
for grp, tag in [(FOCUS_FIRST, True), (REST, False)]:
    if tag:
        acblocks.append('<p class="kicker">The four the examiner lives in</p>')
    else:
        acblocks.append('<p class="kicker">Everything else</p>')
    for k in grp:
        if k not in sysd:
            continue
        body = build_block(sysd[k])
        if k == 'limitations' and sysd.get('placards'):
            pl = []
            for p in sysd['placards']:
                txt = p.get('text') or p.get('value') or ''
                where = p.get('location') or p.get('where') or ''
                pl.append('<div class="pl">%s%s</div>'
                          % (esc(txt), '\n\n— ' + esc(where) if where else ''))
            body += ('<div class="cr wide"><span class="ck" style="font-weight:600;'
                     'color:var(--ink)">Placards, verbatim</span></div>' + ''.join(pl))
        acblocks.append('<details class="rsec"%s><summary><span class="rn">%s</span>'
                        '</summary>%s</details>'
                        % (' open' if tag and k == 'powerplant' else '',
                           esc(TITLES.get(k, pretty(k))), body))

caveats = ''.join('<li style="margin-bottom:7px">%s</li>' % esc(unshout(c))
                  for c in sysd.get('serial_caveats', []))
unver = ''.join('<li style="margin-bottom:5px">%s</li>' % esc(unshout(str(u)))
                for u in sysd.get('unverified', []))
focusnotes = ''.join('<li style="margin-bottom:7px">%s</li>' % esc(unshout(n))
                     for n in sysd.get('examiner_focus_notes', []))

# ---------------------------------------------------------------- W&B pane
wbcases = []
for c in wbw['cases']:
    rows = ''.join(
      '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
      % (esc(r['item']), ('%.1f' % r['weight']), ('%.2f' % r['arm']), ('%.1f' % r['moment']))
      for r in c['rows'])
    ok = c['legal']
    wbcases.append(
      '<div id="wbout" style="margin-bottom:16px">'
      '<div style="padding:12px 13px 2px;font-family:var(--serif);font-size:17px">%s</div>'
      '<table><thead><tr><th>Item</th><th>Weight</th><th>Arm</th><th>Moment</th></tr></thead>'
      '<tbody>%s<tr class="tot"><td>Total</td><td>%.1f</td><td>%.2f</td><td>%.1f</td></tr>'
      '</tbody></table>'
      '<div class="verd %s">%s<small>Forward limit %.2f in at this weight · aft limit %.1f in · '
      'margin %+.2f in</small></div></div>'
      % (esc(c['name']), rows, c['total_weight'], c['total_arm'], c['total_moment'],
         'ok' if ok else 'no', esc(c['verdict']),
         c['fwd_limit_at_weight'], c['aft_limit'], c['margin_in']))

findings = ''.join('<li style="margin-bottom:8px">%s</li>' % esc(unshout(f)) for f in wbw['findings'])
wbcav = ''.join('<li style="margin-bottom:6px">%s</li>' % esc(unshout(c)) for c in wbd.get('caveats', []))

ae = wbd['assumed_empty']
arms = wbd['arms']
lim = wbd['limits']
fuel = wbd['fuel']

# ---------------------------------------------------------------- counts
nq = sum(len(s['items']) for s in db)
nfocus = collections.Counter(it.get('focus') for s in db for it in s['items'])
nride = sum(1 for s in db for it in s['items'] if it.get('g'))
nday = sum(1 for s in db for it in s['items'] if it.get('day'))
nacr = sum(len(g['items']) for g in acr['groups'])
ride = datetime.date(2026, 11, 24)
today = datetime.date.today()
days = (ride - today).days

chips = ''.join(
  '<button class="src on" data-src="%s" title="%s">%s</button>' % (k, esc(d), esc(n))
  for k, n, d in SRCS)

# ---------------------------------------------------------------- assemble
figblocks = ''.join(
  '<script type="text/plain" id="f_%s">%s</script>' % (k, FIGB64[k]) for k in used)

JS = open(os.path.join(BUILD, 'app.js'), encoding='utf-8').read()
JS = JS.replace('__WBDATA__', json.dumps({'limits': lim, 'arms': arms, 'fuel': fuel,
                                          'assumed': ae}))

doc = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Commercial Rating Study Guide</title>
<style>%(css)s%(extra)s</style></head><body><div class="wrap">
<header>
<h1>Commercial Rating Study Guide</h1>
<p class="sub">%(nq)s questions drawn from the CHS Flight School guide, CPL At A Glance, the Gold Seal
commercial guide and the PA-28-161 handbook. Checkride %(ride)s &mdash; %(days)s days.
Tap a question to see the answer, tick it when you own it. Progress is saved on this device.</p>
<div class="srow"><span class="slbl">Sources</span>%(chips)s</div>
<p class="shint" id="shint"></p>
</header>

<div id="tabs">
<button class="tb on" data-p="study">Study</button>
<button class="tb" data-p="ride">Run the ride</button>
<button class="tb" data-p="acr">Acronyms</button>
<button class="tb" data-p="air">The airplane</button>
<button class="tb" data-p="wb">Weight &amp; balance</button>
</div>

<div id="bar"><div class="brow">
<input id="q" type="search" placeholder="Search questions and answers" autocomplete="off">
<button class="fb on" data-m="all">All</button>
<button class="fb" data-m="todo">To do</button>
<button class="fb" data-m="ride">Checkride</button>
<button class="fb" data-m="day">On the day</button>
<button class="fb" data-m="fig">Figures</button>
<button class="fb" data-m="sys">Systems</button>
<button class="fb" data-m="aero">Maneuver</button>
<button class="fb" id="expand">Expand all</button>
<button class="fb" id="theme">Dark</button>
<button class="fb danger" id="reset">Reset progress</button>
</div><div id="prog"><i></i></div><div id="stat"></div></div>

<section class="pane on" id="p-study">
<nav>%(nav)s</nav>
<div id="nores" class="hide"><p class="nrt">Nothing matches <span id="nrq"></span></p>
<p class="nrs">Try fewer words, or <button class="fb" id="nrclear">clear the search</button></p></div>
%(study)s
</section>

<section class="pane" id="p-ride">
<p class="kicker">The checkride, in the order it happened</p>
<div class="note"><b>This is a rehearsal, not a filter.</b> Every heading below is something the
examiner actually did on a prior ride, in sequence \u2014 the oral from logbooks through to the
accident-reporting question, then the flight, then the debrief. Work down it and you have been
through his ride once before you fly it. Ticks are shared with the Study tab, so nothing is
counted twice.</div>
<div class="brow" style="margin-bottom:14px">
<button class="fb" id="rhide">Hide what I have ticked</button>
<button class="fb" id="rexp">Expand all</button>
<span id="rstat" style="font-family:var(--mono);font-size:12px;color:var(--ink3)"></span>
</div>
%(ridehtml)s
</section>

<section class="pane" id="p-acr">
<p class="kicker">%(nacr)s terms, ranked for this examiner</p>
<div class="note"><b>How the ranking works.</b> Tier 1 is near certain &mdash; asked on
essentially every commercial ride, or sitting inside this examiner's known focus on oil, fuel,
electrical and powerplant. Tier 2 is likely, tier 3 possible, tier 4 is there for completeness.
Work down, not across.</div>
<div class="brow" style="margin-bottom:14px">
<input id="aq" type="search" placeholder="Search terms" autocomplete="off">
<button class="fb on" data-at="0">All tiers</button>
<button class="fb" data-at="1">1 only</button>
<button class="fb" data-at="2">1 &amp; 2</button>
</div>
%(agroups)s
</section>

<section class="pane" id="p-air">
<p class="kicker">N84054 &mdash; 1981 PA-28-161 Warrior II, serial 28-8116257</p>
<div class="note warn"><b>Read this before you quote a number.</b> The handbook these figures come
from is Piper Report VB-1180, which covers serials 28-8316001 and up. This airplane is serial
28-8116257, covered by the earlier VB-880. The systems descriptions carry across unchanged; the
weights and the performance charts do not. Maximum gross is <b>2,325 lb</b> from TCDS 2A13 item
XVI-A, not the 2,440 lb printed in VB-1180. Anything that disagrees with the book in the airplane
loses.</div>
<details class="rsec" open><summary><span class="rn">What this examiner asks about</span></summary>
<div style="padding:4px 17px 14px"><ul style="padding-left:18px;font-size:14.5px;
line-height:1.55;color:var(--ink2)">%(focusnotes)s</ul></div></details>
%(acblocks)s
<details class="rsec"><summary><span class="rn">Where VB-1180 does not apply</span></summary>
<div style="padding:4px 17px 14px"><ul style="padding-left:18px;font-size:14.5px;line-height:1.55;
color:var(--ink2)">%(caveats)s</ul></div></details>
<details class="rsec"><summary><span class="rn">Still unverified &mdash; do not guess these</span>
</summary><div style="padding:4px 17px 14px"><ul style="padding-left:18px;font-size:14px;
line-height:1.5;color:var(--ink2)">%(unver)s</ul></div></details>
</section>

<section class="pane" id="p-wb">
<p class="kicker">Weight and balance</p>
<div class="note warn"><b>The empty weight below is an assumption, not this airplane.</b>
It is a real, equipped Warrior II of the same era and the same 2,325 lb gross, used as a
stand-in. Type the two numbers off the weighing record in N84054 and everything here
recomputes.</div>
<details class="rsec" style="margin-bottom:14px"><summary><span class="rn"
style="font-size:16px">Where that assumed figure comes from</span></summary>
<div style="padding:4px 17px 14px;font-size:14px;line-height:1.55;color:var(--ink2)">%(aebasis)s</div>
</details>
<div class="wbg">
<div class="wf"><label>Empty weight</label><input id="w_ew" type="number" step="0.1" value="%(aew).1f"><span class="wu">lb</span></div>
<div class="wf"><label>Empty CG arm</label><input id="w_ea" type="number" step="0.01" value="%(aea).2f"><span class="wu">in</span></div>
<div class="wf"><label>Pilot</label><input id="w_p1" type="number" step="1" value="220"><span class="wu">lb</span></div>
<div class="wf"><label>Front passenger</label><input id="w_p2" type="number" step="1" value="280"><span class="wu">lb</span></div>
<div class="wf"><label>Rear seats</label><input id="w_rr" type="number" step="1" value="0"><span class="wu">lb</span></div>
<div class="wf"><label>Baggage</label><input id="w_bg" type="number" step="1" value="25"><span class="wu">lb</span></div>
<div class="wf"><label>Fuel</label><input id="w_fu" type="number" step="0.5" value="%(fgal)s"><span class="wu">gal</span></div>
<div class="wf"><label>Fuel burned so far</label><input id="w_fb" type="number" step="0.5" value="0"><span class="wu">gal</span></div>
</div>
<div id="wbout"></div>
<p class="kicker">Worked cases</p>
%(wbcases)s
<p class="kicker">What the numbers show</p>
<div class="note"><ul style="padding-left:18px;margin:0">%(findings)s</ul></div>
<p class="kicker">Assumptions to replace</p>
<div class="note warn"><ul style="padding-left:18px;margin:0">%(wbcav)s</ul></div>
</section>

</div>
%(figblocks)s
<script>%(js)s</script>
</body></html>""" % dict(
    css=BASECSS, extra=EXTRA, nq='{:,}'.format(nq), ride=ride.strftime('%d %B %Y'), days=days,
    chips=chips, nav=''.join(nav), study=''.join(study), nacr=nacr,
    agroups=''.join(agroups), ridehtml=''.join(ridehtml), acblocks=''.join(acblocks), focusnotes=focusnotes,
    caveats=caveats, unver=unver, aebasis=esc(unshout(ae.get('basis', ''))),
    aew=ae['weight'], aea=ae['arm'], fgal=fuel['gal_usable'],
    wbcases=''.join(wbcases), findings=findings, wbcav=wbcav,
    figblocks=figblocks, js=JS)

open('commercial-study-guide.html', 'w', encoding='utf-8').write(doc)
mb = len(doc.encode('utf-8')) / 1048576.0
print('questions %d  systems %d  aero %d  asked-on-ride %d  acronyms %d  figures %d raster + %d svg'
      % (nq, nfocus['sys'], nfocus['aero'], nride, nacr, len(used), len(SVG)))
print('   on-the-day items: %d' % nday)
print('wrote commercial-study-guide.html  %.2f MB' % mb)
