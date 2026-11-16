"""Redraw the BTT / FTT cheatsheet figures with the shared diagram helpers from diagrams.py.
Run from the rtt folder:  python3 -I viz/gen_sheets.py
Each figure is found by the start of its <figcaption>; only the <svg> before it is replaced (captions untouched
unless listed in CAPFIX). Idempotent: reads the pristine fragments in viz/orig/.
"""
import re, runpy, math, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
G = runpy.run_path('diagrams.py')
svg, rect, line, text, path, circle, vehicle, bg, roads, R, P, S, fillet = (G[k] for k in
    'svg rect line text path circle vehicle bg roads R P S fillet'.split())
tagbox, badge, dim, ped, painted_arrow, _tag, _q, left_of = (G[k] for k in 'tagbox badge dim ped painted_arrow _tag _q left_of'.split())
W, H = 300, 220

def tile(body, uid):   # 80x80 marking tile
    return svg(body, uid, 80, 80)

def car(x, y, hd, kind="car", **k):
    return vehicle(x, y, hd, None, kind, scale=.78, **k)

def tl(lit, flash=False):
    b = rect(27, 3, 26, 74, "sv-pole", 7)
    for i, (k, cls) in enumerate((("red", "sv-lr"), ("amber", "sv-la"), ("green", "sv-lg"))):
        b += circle(40, 17 + i * 23, 8.5, cls if lit == k else "sv-loff")
    if flash:
        b += '<path d="M15,40 H21 M59,40 H65 M17,30 L22.5,33 M63,30 L57.5,33 M17,50 L22.5,47 M63,50 L57.5,47" class="sv-flash"/>'
    return f'<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">{b}</svg>'

FIG = {}   # (test, caption-prefix) -> svg

# ================= BTT =================
FIG['btt', '<b>Red</b>'] = tl('red'); FIG['btt', '<b>Amber</b>'] = tl('amber')
FIG['btt', '<b>Flashing amber</b>'] = tl('amber', True); FIG['btt', '<b>Green</b>'] = tl('green')

b = bg(80, 80) + roads(R(12, -5, 56, 90))
b += ''.join(rect(15 + k * 7.6, 26, 4.4, 20, "sv-zebra") for k in range(7))
b += line(40, 54, 40, 80, "sv-centre") + line(40, 0, 40, 20, "sv-centre") + car(26, 65, 0)
FIG['btt', '<b>Zebra crossing</b>'] = tile(b, 801)

b = bg(80, 80) + roads(R(12, -5, 56, 90))
b += ''.join(rect(15 + k * 7.6, 5, 4.4, 16, "sv-zebra") for k in range(7))
for x0, d in ((15, 5), (65, -5)):
    b += f'<polyline points="{" ".join(f"{x0 + (d if i % 2 else 0)},{80 - i * 6}" for i in range(9))}" class="sv-edge" fill="none" stroke-linejoin="round"/>'
b += car(40, 60, 0)
FIG['btt', '<b>Zig-zag lines</b>'] = tile(b, 802)

b = bg(80, 80) + roads(R(12, -5, 56, 90))
b += line(38.4, 0, 38.4, 80, "sv-edge") + line(41.6, 0, 41.6, 80, "sv-edge") + car(25, 58, 0) + car(55, 22, 180)
FIG['btt', '<b>Double white lines</b>'] = tile(b, 803)

def buslane(red, uid):
    b = bg(80, 80) + roads(R(8, -5, 80, 90))
    if red: b += rect(27, 0, 2.4, 80, "sv-rfill")
    b += rect(31, 0, 2.4, 80, "sv-yfill")
    if not red: b += rect(25, 17, 7, 2, "sv-yfill") + rect(25, 61, 7, 2, "sv-yfill")
    x = 17.5 if red else 19.5
    b += text(x, 39, "BUS", "sv-buslane") + text(x, 47, "LANE", "sv-buslane")
    b += line(57, 0, 57, 80, "sv-lane")
    return tile(b, uid)
FIG['btt', '<b>Bus lane: yellow line</b>'] = buslane(False, 804)
FIG['btt', '<b>Bus lane: red line too</b>'] = buslane(True, 805)

b = bg(80, 80) + roads(R(-5, 44, 90, 26))
b += car(16, 57, 90, "youcar") + car(64, 57, 90)
b += circle(48, 39, 2.8, "sv-post") + '<path d="M28,28 H48 M28,24 V32 M48,24 V36" class="sv-dim"/>' + text(38, 20, "2 s", "sv-cap")
FIG['btt', '<b>Two-second rule</b>'] = tile(b, 806)

b = bg(80, 80) + roads(R(-5, 44, 90, 30), R(28, -5, 24, 52), fillet(28, 44, -1, -1, 5), fillet(52, 44, 1, -1, 5))
b += line(4, 47.5, 22, 47.5, "sv-nopark") + line(58, 47.5, 76, 47.5, "sv-nopark")
b += text(14, 63, "6 m", "sv-tiletxt") + text(66, 63, "6 m", "sv-tiletxt")
FIG['btt', '<b>Junction</b>'] = tile(b, 807)

b = bg(80, 80) + roads(R(-5, 24, 90, 34))
b += rect(29, 28, 22, 12, "sv-ybox") + text(40, 36.4, "BUS", "sv-buslane")
b += line(3, 27.5, 27, 27.5, "sv-nopark") + line(53, 27.5, 77, 27.5, "sv-nopark")
b += text(15, 49, "9 m", "sv-tiletxt") + text(65, 49, "9 m", "sv-tiletxt")
FIG['btt', '<b>Bus stop</b>'] = tile(b, 808)

b = bg(80, 80) + roads(R(-5, 20, 90, 40), R(20, -5, 40, 90))
b += f'<clipPath id="yc809"><rect x="20" y="20" width="40" height="40"/></clipPath><g clip-path="url(#yc809)">'
b += ''.join(line(20 + k, 20, 60 + k, 60, "sv-ybl") + line(60 - k, 20, 20 - k, 60, "sv-ybl") for k in range(-40, 41, 10)) + '</g>'
b += rect(20, 20, 40, 40, "sv-ybox")
FIG['btt', '<b>Yellow box</b>'] = tile(b, 809)

def tee(uid, giveway):   # you come up the stem (left half) to the major road across the top
    b = bg(80, 80) + roads(R(-5, -5, 90, 27), R(22, 20, 36, 70), fillet(22, 22, -1, 1, 5), fillet(58, 22, 1, 1, 5))
    b += line(40, 80, 40, 36, "sv-centre")
    if giveway:
        b += line(23.5, 25.5, 40, 25.5, "sv-giveway") + line(23.5, 29.5, 40, 29.5, "sv-giveway")
    else:
        b += line(23.5, 27, 40, 27, "sv-stop")
    return tile(b + car(31, 58, 0, "youcar"), uid)
FIG['btt', '<b>Two broken lines across</b>'] = tee(810, True)
FIG['btt', '<b>One solid line across</b>'] = tee(811, False)

# ================= FTT =================
FIG['ftt', '<b>Green ahead</b>'] = tl('green'); FIG['ftt', '<b>Amber</b>'] = tl('amber')
FIG['ftt', '<b>Flashing amber</b>'] = tl('amber', True); FIG['ftt', '<b>Red</b>'] = tl('red')

# 1 side gaps
b = bg(W, 190)
for i, (ttl, d, gap) in enumerate((("Parked car", "1 m", 16), ("Facing you", "1 m", 16), ("Back to you", "1.5 m", 24))):
    x0 = 12 + i * 96
    b += roads(R(x0 + 14, -10, 70, 210))
    if i == 0:
        b += vehicle(x0 + 25, 78, 0); edge = x0 + 33
    else:
        hd = 180 if i == 1 else 0
        b += ped(x0 + 24, 78); edge = x0 + 28.2
        b += path(f"M{x0 + 24},{78 + (14 if i == 1 else -15)} L{x0 + 24},{78 + (30 if i == 1 else -33)}", 701, "sv-path2")
    cx = edge + gap + 8
    b += vehicle(cx, 78, 0, kind="youcar") + (_tag(cx, 50) if i == 0 else '')
    b += f'<path d="M{edge},120 H{edge + gap} M{edge},116 V124 M{edge + gap},116 V124" class="sv-dim"/>'
    b += text(edge + gap / 2, 136, d, "sv-cap2") + text(x0 + 49, 174, ttl, "sv-cap2")
FIG['ftt', "Parked or facing you: 1 m."] = svg(b, 701, W, 190)

# 2 two-second rule (cars heading east keep to the top half)
b = bg(W, 136) + roads(R(-10, 62, 320, 60))
b += line(0, 92, W, 92, "sv-centre")
b += vehicle(66, 77, 90, kind="youcar", tag='l') + vehicle(232, 77, 90) + path("M252,77 L284,77", 702, "sv-path2")
b += rect(184, 44, 4, 16, "sv-pole", 2) + circle(186, 44, 5, "sv-post") + line(186, 62, 186, 92, "sv-leader")
b += '<path d="M82,34 H186 M82,29 V39" class="sv-dim"/>' + text(134, 25, "2 s", "sv-cap")
b += text(198, 47.5, "Fixed point", "sv-cap", "start")
FIG['ftt', "Car ahead passes a post"] = svg(b, 702, W, 136)

# 3 stopping distance (a chart, so no road frame; wet total = 2 x dry total)
b = text(40, 30, "Dry", "sv-ink", "end") + rect(50, 17, 38, 20, "sv-react", 3) + rect(90, 17, 48, 20, "sv-brake", 3)
b += text(40, 62, "Wet", "sv-ink", "end") + rect(50, 49, 38, 20, "sv-react", 3) + rect(90, 49, 134, 20, "sv-brake", 3) + text(232, 62, "×2", "sv-ink", "start")
b += rect(50, 86, 10, 10, "sv-react", 2.5) + text(65, 95, "Reaction", "sv-ink", "start") + rect(124, 86, 10, 10, "sv-brake", 2.5) + text(139, 95, "Braking", "sv-ink", "start")
FIG['ftt', "Stopping = reaction"] = f'<svg viewBox="0 0 300 110" xmlns="http://www.w3.org/2000/svg">{b}</svg>'

# 4 expressway lanes
b = bg() + roads(R(52, -10, 210, 240))
b += rect(52, 0, 36, H, "sv-shoulder") + line(88, 0, 88, H, "sv-edge") + line(146, 0, 146, H, "sv-lane") + line(204, 0, 204, H, "sv-lane")
b += f'<text x="70" y="110" text-anchor="middle" class="sv-cap2" transform="rotate(-90 70 110)">Shoulder</text>'
for i, t in enumerate(("Keep left", "Don't hog", "Overtake")):
    b += text(117 + i * 58, 34, t, "sv-cap2") + painted_arrow(117 + i * 58, 84, "straight")
b += vehicle(117, 160, 0, kind="youcar", tag='b')
FIG['ftt', "Left lane unless overtaking."] = svg(b, 704)

# 5 bend
d = "M70,232 L70,128 Q70,62 136,62 L312,62"
b = bg() + roads(S(d, 60)) + f'<path d="{d}" class="sv-centre"/>'
pts = {"a": (55, 192), "c": (214, 47)}
x, y, hd = _q((70, 128), (70, 62), (136, 62), .5); bx, by = left_of(x, y, hd)
pts["b"] = (bx, by)
b += path(f"M{bx - 8:.1f},{by - 8:.1f} L{bx - 26:.1f},{by - 26:.1f}", 705, "sv-pathd") + text(46, 22, "Pushed out", "sv-capd")
for k, (px, py) in pts.items():
    b += badge(px, py, k, r=8.5)
for i, t in enumerate(("a  Slow, change down", "b  Steady, light gas", "c  Gas as the wheel straightens")):
    b += text(124, 136 + i * 16, t, "sv-cap", "start")
FIG['ftt', "Faster = stronger outward push"] = svg(b, 705)

# 6 blind spots
b = bg(W, 200) + roads(R(60, -10, 180, 230)) + line(120, 0, 120, 200, "sv-lane") + line(180, 0, 180, 200, "sv-lane")
b += '<polygon points="138,74 126,200 98,200" class="sv-beam"/><polygon points="162,74 174,200 202,200" class="sv-beam"/><polygon points="144,98 156,98 172,200 128,200" class="sv-beam"/>'
b += rect(66, 60, 50, 56, "sv-zone", 6) + rect(184, 60, 50, 56, "sv-zone", 6)
b += vehicle(150, 70, 0, kind="youcar", scale=1.6) + rect(134.5, 58, 4, 5, "sv-you", 1.5) + rect(161.5, 58, 4, 5, "sv-you", 1.5)
b += vehicle(91, 92, 0, kind="bike") + text(91, 74, "Blind", "sv-cap2") + text(209, 92, "Blind", "sv-cap2")
b += text(150, 186, "Mirror view", "sv-cap2")
FIG['ftt', "Neither mirror covers the amber zones."] = svg(b, 706, W, 200)

# 7 narrow left turn
b = bg() + roads(R(130, 40, 50, 200), R(-10, 40, 190, 50))
b += '<path d="M150,172 L150,112 Q148,76 108,74 L22,74" class="sv-pathd"/>'
b += path("M163,160 L163,96 Q163,56 118,56 L22,56", 707)
b += vehicle(160, 180, 0, kind="youcar", steer=0)
b += line(196, 60, 216, 60, "sv-path") + text(222, 63.5, "Front wheels", "sv-cap", "start")
b += line(196, 78, 216, 78, "sv-pathd") + text(222, 81.5, "Rear wheels", "sv-capd", "start") + text(222, 94.5, "cut in", "sv-capd", "start")
b += text(194, 184, "Start to the right", "sv-cap", "start")
FIG['ftt', "Left turn in a narrow course"] = svg(b, 707)

# 8 long vehicles
b = bg() + roads(R(70, -10, 50, 240), R(-10, 30, 90, 46), fillet(70, 30, -1, -1, 6), fillet(70, 76, -1, 1, 6), R(184, -10, 96, 240))
b += line(232, 0, 232, H, "sv-centre")
b += path("M96,128 C122,100 116,56 76,53 L16,53", 708, "sv-pathd") + vehicle(95, 158, 0, kind="lorry", signal="left")
b += path("M207,128 C190,104 190,64 212,52 C240,38 258,60 256,128", 708, "sv-pathd") + vehicle(208, 158, 0, kind="lorry", signal="right")
b += text(34, 204, "Left turn", "sv-cap") + text(152, 204, "U-turn", "sv-cap")
FIG['ftt', "Turning left, a long vehicle swings right first"] = svg(b, 708)

# 9 reversing into a lot
b = bg(W, 200) + roads(R(30, -10, 240, 172, 0))
for xx in (52, 101, 150, 199, 248):
    b += line(xx, 0, xx, 76, "sv-edge")
b += vehicle(76.5, 40, 0, scale=1.25) + vehicle(174.5, 40, 0, scale=1.25)
b += path("M139,112 Q128,90 126,56", 709, "sv-path2")
b += vehicle(152, 124, 138, kind="youcar", scale=1.25)
b += path("M176,150 Q200,152 204,124", 709, "sv-pathd") + text(212, 184, "Front swings out", "sv-capd")
FIG['ftt', "Reversing in, the front swings out"] = svg(b, 709, W, 200)

# 10 parking on a slope (kerb on the left)
b = bg()
for i, (ttl, st, lab) in enumerate((("Wheels out, 1st", 28, "Facing uphill"), ("Wheels in, reverse", -28, "Facing downhill"))):
    x0 = 22 + i * 146
    b += roads(R(x0, -10, 110, 240))
    b += vehicle(x0 + 24, 104, 0, kind="youcar", scale=1.6, steer=st)
    b += path(f"M{x0 + 70},128 L{x0 + 70},84", 710) + text(x0 + 70, 146, lab.split()[1].capitalize(), "sv-cap2")
    b += text(x0 + 55, 24, lab, "sv-cap2") + text(x0 + 55, 204, ttl, "sv-cap2")
FIG['ftt', "On a slope: handbrake fully up"] = svg(b, 710)

# 11 rear skid
b = bg(W, 200) + roads(R(40, -10, 130, 230)) + line(105, 0, 105, 200, "sv-leader")
b += vehicle(105, 104, -22, kind="youcar", scale=1.7, steer=34)
b += path("M128,150 L166,150", 711, "sv-pathd") + text(182, 153.5, "Rear slides right", "sv-capd", "start")
b += path("M100,52 L128,30", 711, "sv-paths") + text(182, 33.5, "Steer right", "sv-caps", "start")
FIG['ftt', "Rear skids: off the accelerator"] = svg(b, 711, W, 200)

CAPFIX = {}

for t in ('btt', 'ftt'):
    s = open(f'viz/orig/{t}/sheet.part.html').read()
    for (tt, cap), new in FIG.items():
        if tt != t: continue
        i = s.find('<figcaption>' + cap); assert i > 0 and s.count('<figcaption>' + cap) == 1, (t, cap)
        a = s.rfind('<svg', 0, i); e = s.rfind('</svg>', 0, i) + 6
        old = s[a:e]; assert old.count('<svg') == 1
        m = re.search(r'aria-label="[^"]*"', old)
        attr = f' role="img" {m.group(0)}' if m else ' aria-hidden="true"'
        new = re.sub(r'^<svg([^>]*?)( role="img")?>', lambda mm: f'<svg{mm.group(1)}{attr}>', new, count=1)
        s = s[:a] + new + s[e:]
    for a, b2 in CAPFIX.get(t, []):
        assert s.count(a) == 1; s = s.replace(a, b2)
    open(f'{t}/sheet.part.html', 'w').write(s)
    print(t, 'figures redrawn:', sum(1 for k in FIG if k[0] == t))
