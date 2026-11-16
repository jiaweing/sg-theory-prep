import json, re, os, runpy
os.chdir(os.path.dirname(os.path.abspath(__file__)))
G = runpy.run_path('diagrams.py')            # regenerates form/diagrams.json and gives us the drawing helpers

# ---------- data ----------
rtt = json.load(open('form/data.json'))
dg = json.load(open('form/diagrams.json'))
rtt['official'] = len(rtt['q'])
rtt['sets'].append('Diagram scenarios (unofficial)'); rtt['cats'].append('Scenario'); rtt['diagSet'] = len(rtt['sets']) - 1
for q, o, a, svgs, expl in dg: rtt['q'].append([q, o, a, rtt['diagSet'], svgs, expl])

def catname(t, s):
    s2 = s.lower()
    if t == 'ftt':
        for k, v in [('alcohol', 'Alcohol'), ('competency', 'Competency'), ('general', 'General'), ('road safety', 'Road safety'), ('traffic rules', 'Traffic rules')]:
            if s2.startswith(k): return v
    if t == 'btt':
        return {'Blind Spots / Road Safety / BTT-General': 'Blind spots & general', 'Ambulance / Bus Lane / Zig Zag lines': 'Ambulance, bus lane, zig-zag',
                'Right Lane / Traffic Lights': 'Right lane & lights', 'Lane Discipline / Overtaking': 'Lanes & overtaking', 'Rules and Regulations': 'Rules & regulations',
                'Alcohol/ Road Safety': 'Alcohol', 'Seat belt / 2 second rule': 'Seat belt & 2-second rule', 'Flood / Headlights': 'Flood & headlights'}.get(s, s)
    return s
ALL = {'rtt': rtt}
for t in ('btt', 'ftt'):
    b = json.load(open(f'{t}/bank.json'))
    ALL[t] = {'sets': b['sets'], 'cats': [catname(t, s) for s in b['sets']], 'q': b['q'], 'official': len(b['q'])}
    dpath = f'{t}/diagrams.json'
    if os.path.exists(dpath):
        dq = json.load(open(dpath))
        if dq:
            ALL[t]['sets'].append('Diagram scenarios (unofficial)'); ALL[t]['cats'].append('Scenario')
            ALL[t]['diagSet'] = len(ALL[t]['sets']) - 1
            for q, o, a, svgs, expl in dq: ALL[t]['q'].append([q, o, a, ALL[t]['diagSet'], svgs, expl])

# ---------- cheatsheets ----------
rsheet = open('sheet.part.html').read()
i = rsheet.index('<section'); j = rsheet.rindex('</div>')
rtt_sections = rsheet[i:j].rstrip()

def fig(svg, cap): return f'<figure class="diag">{svg}<figcaption>{cap}</figcaption></figure>'
bike = G['svg'](G['bike_top']('none'), 900)
junction = [q for q in dg if q[0].startswith('No traffic lights or signs. You\'re turning right. Car B')][0][3]
lx = G['lane_x']
gaps_body = (G['lanes_north'](901, 3, labels=False)
    + G['path'](f"M{lx(3, 2)},78 L{lx(3, 2)},40", 901, 'sv-path2')
    + G['vehicle'](lx(3, 0) - 10, 100, 0, None) + G['vehicle'](lx(3, 1) - 14, 104, 0, kind='you', tag='t') + G['vehicle'](lx(3, 2) - 4, 100, 0, None)
    + '<path d="M104,132 H129 M104,128 V136 M129,128 V136 M143,132 H182 M143,128 V136 M182,128 V136" class="sv-dim"/>'
    + G['text'](116.5, 148, '1 m', 'sv-cap2') + G['text'](157, 148, '1.5 m', 'sv-cap2')
    + G['text'](72, 104, 'Parked', 'sv-cap', 'end') + G['text'](228, 104, 'Moving', 'sv-cap', 'start'))
gaps = G['svg'](gaps_body, 901)
rtt_glance = f'''    <section class="sec">
      <div class="sec-title"><h2>At a glance</h2></div>
      {fig(bike, "Controls: A clutch · B front brake · T throttle (right grip) · C gear pedal (left foot) · D rear brake (right foot)")}
      {fig(gaps, "Gaps: 1 m from parked vehicles and pedestrians facing you; 1.5 m from moving vehicles and pedestrians with their back to you")}
      {fig(junction, "No lights or signs, turning right: give way to straight traffic from all directions (B and C)")}
    </section>
'''
def kv(rows): return ''.join(f'<div class="kv"><span class="k">{k}</span><span class="v">{v}</span></div>' for k, v in rows)
rtt_hb = '''    <section class="sec">
      <div class="sec-title"><h2>Handbook only</h2><p class="muted small">In the official handbook but not in the practice questions.</p></div>
      <div class="facts">
        <div class="fact"><span class="n">1.6 mm</span><span class="t">Minimum tyre tread depth</span></div>
        <div class="fact"><span class="n">10 years</span><span class="t">No pillion younger than this</span></div>
        <div class="fact"><span class="n">120°</span><span class="t">Angle of your arms on the handlebar, elbows slightly bent</span></div>
        <div class="fact"><span class="n">3,000–4,000</span><span class="t">Engine rpm to change up a gear</span></div>
        <div class="fact"><span class="n">0–20 / 15–35</span><span class="t">1st / 2nd gear speed range (km/h)<i>3rd 25–45, 4th 35–50, 5th above 50.</i></span></div>
        <div class="fact"><span class="n">¾ s</span><span class="t">Average reaction time</span></div>
        <div class="fact"><span class="n">0.5 m</span><span class="t">Gap from fixed obstacles</span></div>
        <div class="fact"><span class="n">12 s</span><span class="t">Scan this far ahead; an overtake takes about 10 s</span></div>
        <div class="fact"><span class="n">&gt;6 s / 8 s</span><span class="t">Turning right out of a minor road: traffic from the right / left</span></div>
        <div class="fact"><span class="n">20 m+</span><span class="t">Breakdown triangle behind your bike on the expressway</span></div>
        <div class="fact"><span class="n">80 / 90</span><span class="t">Speed limit on most expressways (km/h); KPE 70 / 80</span></div>
        <div class="fact"><span class="n">1 year</span><span class="t">Pass the practical within this time after the RTT, or retake the RTT</span></div>
        <div class="fact"><span class="n">2 years</span><span class="t">Provisional licence (PDL) validity</span></div>
        <div class="fact"><span class="n">&lt;200 cc</span><span class="t">Class 2B (2A: 200–400 cc; 2: above 400 cc)</span></div>
        <div class="fact"><span class="n">3 s / 6 s</span><span class="t">The newest booklet's following distances<i>The practice questions still use 2 s / 4 s. Answer with those.</i></span></div>
      </div>
      <p class="sub">Circuit courses</p>
      <div class="facts">
        <div class="fact"><span class="n">&lt; 11 s</span><span class="t">S course</span></div>
        <div class="fact"><span class="n">&lt; 6 s</span><span class="t">Crank course and pylon slalom</span></div>
        <div class="fact"><span class="n">≥ 6 s</span><span class="t">Narrow plank (slower is better)</span></div>
        <div class="fact"><span class="n">11 m</span><span class="t">Emergency brake: stop within this from about 30 km/h, wet</span></div>
      </div>
    </section>
'''
# put "At a glance" right after the first section (ten to know)
first_end = rtt_sections.index('</section>') + len('</section>')
rtt_full = rtt_sections[:first_end] + '\n' + rtt_glance + rtt_sections[first_end:] + '\n' + rtt_hb

def other(t):
    p = f'{t}/sheet.part.html'
    if os.path.exists(p): return open(p).read()
    return f'<section class="sec"><div class="sec-title"><h2>{t.upper()} cheatsheet</h2><p class="muted small">Coming soon.</p></div></section>'

sheet_html = f'''<!-- ================= CHEATSHEET ================= -->
  <div class="sheet" id="view-cheatsheet" role="tabpanel" aria-labelledby="tab-cheatsheet">
    <div class="sheet-bar">
      <div class="layout-seg" id="layoutSeg" role="group" aria-label="Cheatsheet layout">
        <button class="btn sm" type="button" data-layout="grid" aria-pressed="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>Grid</button>
        <button class="btn sm" type="button" data-layout="list" aria-pressed="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="3" width="16" height="7" rx="1.5"/><rect x="4" y="14" width="16" height="7" rx="1.5"/></svg>List</button>
      </div>
      <div class="layout-seg" id="colSeg" role="group" aria-label="Columns per row">
        <span class="seg-lab">Columns</span>
        <button class="btn sm" type="button" data-cols="0" aria-pressed="true">Auto</button>
        <button class="btn sm" type="button" data-cols="2" aria-pressed="false">2</button>
        <button class="btn sm" type="button" data-cols="3" aria-pressed="false">3</button>
        <button class="btn sm" type="button" data-cols="4" aria-pressed="false">4</button>
        <button class="btn sm" type="button" data-cols="5" aria-pressed="false">5</button>
      </div>
      <div class="layout-seg" id="widthSeg" role="group" aria-label="Maximum page width">
        <span class="seg-lab">Width</span>
        <button class="btn sm" type="button" data-maxw="0" aria-pressed="true">Full</button>
        <button class="btn sm" type="button" data-maxw="1920" aria-pressed="false">1920</button>
        <button class="btn sm" type="button" data-maxw="1600" aria-pressed="false">1600</button>
        <button class="btn sm" type="button" data-maxw="1280" aria-pressed="false">1280</button>
      </div>
      <div class="tool-seg" role="group" aria-label="Cheatsheet tools">
        <button class="btn sm" id="orderReset" type="button" hidden>Reset order</button>
        <button class="btn sm" id="quizToggle" type="button" aria-pressed="false">Hide numbers</button>
      </div>
    </div>
    <div class="sheet-test" data-test="rtt">
{rtt_full}
    </div>
    <div class="sheet-test" data-test="btt" hidden>
{other('btt')}
    </div>
    <div class="sheet-test" data-test="ftt" hidden>
{other('ftt')}
    </div>
  </div>
'''
t = open('template3.html').read()
js = json.dumps(ALL, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
out = t.replace('<!--__SHEET__-->', sheet_html).replace('/*__DATA__*/null', js)
assert '<!--__SHEET__-->' not in out and '/*__DATA__*/null' not in out
open('rtt-cheatsheet.html', 'w').write(out)
print('built', len(out) // 1024, 'KB;', {k: len(v['q']) for k, v in ALL.items()})
