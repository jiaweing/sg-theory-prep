"""Generate diagram scenario questions (unofficial, based on Riding Theory Booklet rules).
Singapore drives on the LEFT. Screen: up = north.
Output: form/diagrams.json  -> list of [question, options, answerIndex, svg, explanation]

Visual system (all colours come from the sv-* classes / --sv-* tokens in template3.html):
  canvas 300x220 clipped to a rounded frame; grass background; roads = kerb outline + asphalt;
  junction lane = 30, straight-road lane = 44; cars are white with glass at the FRONT and red tail
  lights at the back, lettered on the roof; the rider is the yellow motorcycle with a "You" pill;
  your path = solid arrow, other traffic = dashed dimmer arrow; captions sit on the grass.
"""
import json, math

W, H = 300, 220
LW = 44          # lane width on straight-road scenes
_uid = [0]

def svg(body, uid, w=W, h=H, label=None, frame=True):
    def mk(i, cls):
        return (f'<marker id="{i}" viewBox="0 0 10 10" refX="7.5" refY="5" markerWidth="11" markerHeight="11" '
                f'markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M1,1.2 L9.6,5 L1,8.8 L3.2,5 z" class="{cls}"/></marker>')
    defs = '<defs>' + mk(f'ah{uid}', 'sv-ah') + mk(f'ah{uid}b', 'sv-ah2')
    if f'#ah{uid}d' in body: defs += mk(f'ah{uid}d', 'sv-ahd')
    if f'#ah{uid}s' in body: defs += mk(f'ah{uid}s', 'sv-ahs')
    if frame:
        defs += f'<clipPath id="cl{uid}"><rect x="0" y="0" width="{w}" height="{h}" rx="10"/></clipPath>'
        body = f'<g clip-path="url(#cl{uid})">{body}</g>'
    defs += '</defs>'
    aria = f' aria-label="{label}"' if label else ''
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img"{aria}>{defs}{body}</svg>'

def _n(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.') if isinstance(v, float) else str(v)

def rect(x, y, w, h, cls, rx=0):
    return f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" rx="{rx}" class="{cls}"/>'

def line(x1, y1, x2, y2, cls):
    return f'<line x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(x2)}" y2="{_n(y2)}" class="{cls}"/>'

def text(x, y, t, cls="sv-cap", anchor="middle"):
    return f'<text x="{_n(x)}" y="{_n(y)}" text-anchor="{anchor}" class="{cls}">{t}</text>'

def path(d, uid, cls="sv-path"):
    m = f'ah{uid}' + {"sv-path": "", "sv-pathd": "d", "sv-paths": "s"}.get(cls.split()[0], "b")
    return f'<path d="{d}" class="{cls}" marker-end="url(#{m})"/>'

def circle(cx, cy, r, cls):
    return f'<circle cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(r)}" class="{cls}"/>'

# ---------- roads ----------
def R(x, y, w, h, rx=0): return ('r', x, y, w, h, rx)
def P(d): return ('p', d)
def C(cx, cy, r): return ('c', cx, cy, r)
def S(d, width): return ('s', d, width)

def fillet(x, y, dx, dy, r=9):
    """Rounded kerb in the corner at (x, y); (dx, dy) points into the grass quadrant."""
    return P(f'M{x + dx * r},{y} L{x},{y} L{x},{y + dy * r} A{r},{r} 0 0 {1 if dx * dy > 0 else 0} {x + dx * r},{y} Z')

def roads(*shapes):
    """Draw every piece once as kerb (slightly fatter) and once as asphalt, so the union gets one clean kerb line."""
    def one(s, kerb):
        k = s[0]
        if k == 'r': return rect(s[1], s[2], s[3], s[4], 'sv-kerb' if kerb else 'sv-road', s[5])
        if k == 'p': return f'<path d="{s[1]}" class="{"sv-kerb" if kerb else "sv-road"}"/>'
        if k == 'c': return circle(s[1], s[2], s[3], 'sv-kerb' if kerb else 'sv-road')
        return f'<path d="{s[1]}" class="{"sv-kerbline" if kerb else "sv-roadline"}" stroke-width="{s[2] + (3.2 if kerb else 0)}"/>'
    return ''.join(one(s, True) for s in shapes) + ''.join(one(s, False) for s in shapes)

def bg(w=W, h=H):
    return rect(0, 0, w, h, "sv-bg")

# ---------- vehicles & labels ----------
def _tag(x, y):
    return rect(x - 14, y - 6.5, 28, 13, "sv-youtag", 6.5) + text(x, y + 3.1, "You", "sv-youtxt")

def badge(x, y, t, cls="sv-lblbg", tcls="sv-lbl", r=8):
    return circle(x, y, r, cls) + text(x, y + 3.3, t, tcls)

def tagbox(x, y, t, w=16):
    """Lane / point label: a small neutral chip."""
    return rect(x - w / 2, y - 8, w, 16, "sv-chip", 5) + text(x, y + 3.6, t, "sv-chiptxt")

def dim(x1, y1, x2, y2, t=None, tx=None, ty=None, anchor="start"):
    """Dimension line with end ticks."""
    L = math.hypot(x2 - x1, y2 - y1); nx, ny = -(y2 - y1) / L * 4, (x2 - x1) / L * 4
    d = f'M{_n(x1)},{_n(y1)} L{_n(x2)},{_n(y2)} M{_n(x1 - nx)},{_n(y1 - ny)} L{_n(x1 + nx)},{_n(y1 + ny)} M{_n(x2 - nx)},{_n(y2 - ny)} L{_n(x2 + nx)},{_n(y2 + ny)}'
    s = f'<path d="{d}" class="sv-dim"/>'
    if t: s += text(tx, ty, t, "sv-cap", anchor)
    return s

def ped(x, y, heading=0):
    """Pedestrian pictogram (always upright; `heading` is accepted for symmetry with vehicle())."""
    return rect(x - 3.6, y - 2.5, 7.2, 11.5, "sv-ped", 3.6) + circle(x, y - 6.5, 3.3, "sv-ped")

def vehicle(x, y, heading, label=None, kind="car", tag=None, signal=None, scale=1, steer=None):
    """heading: 0=north(up), 90=east(right), 180=south, 270=west.
    tag ("you" / "youcar"): where the "You" pill goes: 'b' below, 't' above, 'l' left, 'r' right, '' none.
    steer: draw the four tyres, front pair turned by this many degrees (+ = to the vehicle's right)."""
    g = f'<g transform="translate({_n(x)},{_n(y)}) rotate({heading})' + (f' scale({scale})' if scale != 1 else '') + '">'
    if kind in ("you", "bike"):
        g += rect(-1.9, -13.5, 3.8, 8.5, "sv-tyre", 1.9) + rect(-2.3, 5.5, 4.6, 8.5, "sv-tyre", 2.3)
        g += rect(-3.4, -8.5, 6.8, 18.5, "sv-you" if kind == "you" else "sv-car", 3.4)
        g += '<path d="M-7,-5.6 L7,-5.6" class="sv-hbar"/>'
        g += f'<ellipse cx="0" cy="2.6" rx="6.4" ry="3.7" class="{"sv-you" if kind == "you" else "sv-car"}"/>' + circle(0, 1.6, 3, "sv-helmet")
        hw, hl = 7, 14
    else:
        w, h = {"car": (16, 30), "youcar": (16, 30), "lorry": (20, 48), "bus": (20, 52), "ambulance": (17, 32)}[kind]
        hw, hl = w / 2, h / 2
        body = "sv-you" if kind == "youcar" else "sv-car"
        if steer is not None:
            for sx in (-hw - .6, hw + .6):
                g += f'<rect x="{_n(sx - 1.8)}" y="{_n(-hl + 4.5)}" width="3.6" height="7.5" rx="1.4" class="sv-tyre" transform="rotate({steer} {_n(sx)} {_n(-hl + 8.25)})"/>'
                g += rect(sx - 1.8, hl - 12, 3.6, 7.5, "sv-tyre", 1.4)
        if kind == "lorry":
            g += rect(-hw, -hl + 13, w, h - 13, "sv-car2", 2.5) + rect(-hw + 1, -hl, w - 2, 12, body, 3.5)
            g += f'<path d="M{-hw + 3.5},{-hl + 4} H{hw - 3.5} L{hw - 4},{-hl + 8.5} H{-hw + 4} Z" class="sv-glass"/>'
        else:
            g += rect(-hw, -hl, w, h, body, 4.5 if kind != "bus" else 3.5)
            f0 = -hl + (6.5 if kind in ("car", "youcar") else 4)
            g += f'<path d="M{-hw + 2.4},{f0} H{hw - 2.4} L{hw - 3.4},{f0 + 5} H{-hw + 3.4} Z" class="sv-glass"/>'
            g += f'<path d="M{-hw + 3.4},{hl - 7.5} H{hw - 3.4} L{hw - 2.6},{hl - 4.5} H{-hw + 2.6} Z" class="sv-glass"/>'
            if kind == "bus":
                g += rect(-4, -10, 8, 6, "sv-roof", 1.5) + rect(-4, 8, 8, 6, "sv-roof", 1.5)
            if kind == "ambulance":
                g += '<path d="M-1.6,-3 h3.2 v3.4 h3.4 v3.2 h-3.4 v3.4 h-3.2 v-3.4 h-3.4 v-3.2 h3.4 z" class="sv-cross"/>'
        g += rect(-hw + 1.2, hl - 2.4, 3.4, 1.5, "sv-tail", .7) + rect(hw - 4.6, hl - 2.4, 3.4, 1.5, "sv-tail", .7)
        if signal:
            sx = -hw if signal == "left" else hw
            g += circle(sx, -hl + 2, 2.3, "sv-blink") + circle(sx, hl - 2, 2.3, "sv-blink")
    g += '</g>'
    if kind == "you":
        if tag is None:
            tag = 'b' if (heading % 180 == 0 and y + 30 <= H - 2) else 'l'
        off = {'b': (0, 23), 't': (0, -23), 'l': (-25, 0), 'r': (25, 0)}.get(tag)
        if off: g += _tag(x + off[0], y + off[1])
    elif kind == "youcar" and tag:
        ex, ey = (hl, hw) if heading % 180 else (hw, hl)     # half extents on screen
        off = {'b': (0, ey * scale + 10), 't': (0, -ey * scale - 10), 'l': (-ex * scale - 18, 0), 'r': (ex * scale + 18, 0)}[tag]
        g += _tag(x + off[0], y + off[1])
    elif label:
        r = math.radians(heading); k = 2.5 if kind in ("car", "youcar") else 6
        g += badge(x - math.sin(r) * k, y + math.cos(r) * k, label, r=6.6)
    return g

# ---------- scenes ----------
def lamp(x, y, lights):
    """Small three-aspect signal symbol (red on top)."""
    b = rect(x, y, 14, 36, "sv-pole", 4)
    for i, (k, cls) in enumerate((("red", "sv-lr"), ("amber", "sv-la"), ("green", "sv-lg"))):
        b += circle(x + 7, y + 8 + i * 10, 3.6, cls if lights == k else "sv-loff")
    return b

def cross(uid, lights=None, yellow=False, stop=True):
    # vertical road x 120-180, horizontal road y 80-140 (lane 30)
    b = bg() + roads(R(120, -10, 60, H + 20), R(-10, 80, W + 20, 60),
                     fillet(120, 80, -1, -1), fillet(180, 80, 1, -1), fillet(120, 140, -1, 1), fillet(180, 140, 1, 1))
    if yellow:
        b += f'<clipPath id="yc{uid}"><rect x="120" y="80" width="60" height="60"/></clipPath>'
        b += rect(120, 80, 60, 60, "sv-yb")
        b += f'<g clip-path="url(#yc{uid})">' + "".join(line(120 + k, 80, 180 + k, 140, "sv-ybl") + line(180 - k, 80, 120 - k, 140, "sv-ybl") for k in range(-60, 61, 15)) + '</g>'
        b += rect(120, 80, 60, 60, "sv-ybo")
    e = 14 if stop else 9   # where the centre lines end, short of the junction
    b += line(150, 0, 150, 80 - e, "sv-centre") + line(150, H, 150, 140 + e, "sv-centre")
    b += line(0, 110, 120 - e, 110, "sv-centre") + line(W, 110, 180 + e, 110, "sv-centre")
    if stop:  # each stop line covers the approaching (left-hand) half only
        b += line(121.5, 151, 150, 151, "sv-stop") + line(150, 69, 178.5, 69, "sv-stop")
        b += line(109, 81.5, 109, 110, "sv-stop") + line(191, 110, 191, 138.5, "sv-stop")
    if lights:
        b += lamp(97, 152, lights)
    return b

def tjunction(uid):
    # major road y 70-130 (eastbound y85, westbound y115), minor road x 120-180 from y 130 down
    b = bg() + roads(R(-10, 70, W + 20, 60), R(120, 130, 60, H), fillet(120, 130, -1, 1), fillet(180, 130, 1, 1))
    b += line(0, 100, W, 100, "sv-centre") + line(150, H, 150, 142, "sv-centre")
    b += line(121.5, 141, 150, 141, "sv-stop")
    b += text(288, 60, "Major road", "sv-cap", "end") + text(192, 208, "Minor road", "sv-cap", "start")
    return b

def roundabout(uid, flows=(0, 180)):
    cx, cy = 150, 105
    b = bg() + roads(R(120, -10, 60, H + 20), R(-10, 75, W + 20, 60), C(cx, cy, 68))
    b += circle(cx, cy, 30, "sv-island")
    b += line(150, H, 150, 184, "sv-centre") + line(150, 0, 150, 26, "sv-centre")
    b += line(0, 105, 71, 105, "sv-centre") + line(W, 105, 229, 105, "sv-centre")
    # give-way lines (two broken lines) across each entry lane
    b += line(121.5, 174.5, 150, 174.5, "sv-giveway") + line(121.5, 178.5, 150, 178.5, "sv-giveway")
    b += line(150, 35.5, 178.5, 35.5, "sv-giveway") + line(150, 31.5, 178.5, 31.5, "sv-giveway")
    b += line(80.5, 76.5, 80.5, 105, "sv-giveway") + line(76.5, 76.5, 76.5, 105, "sv-giveway")
    b += line(219.5, 105, 219.5, 133.5, "sv-giveway") + line(223.5, 105, 223.5, 133.5, "sv-giveway")
    # clockwise flow arrows (left-hand traffic); angles are clockwise from east
    for a in flows:
        a0, a1 = math.radians(a - 24), math.radians(a + 24)
        b += (f'<path d="M{cx + 49 * math.cos(a0):.1f},{cy + 49 * math.sin(a0):.1f} A49,49 0 0 1 {cx + 49 * math.cos(a1):.1f},{cy + 49 * math.sin(a1):.1f}" '
              f'class="sv-flow" marker-end="url(#fl{uid})"/>')
    b += (f'<marker id="fl{uid}" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="9" markerHeight="9" markerUnits="userSpaceOnUse" orient="auto">'
          f'<path d="M1,1.5 L9,5 L1,8.5 z" class="sv-flowah"/></marker>')
    return b

def lanes_north(uid, n, x0=None, lw=LW, arrows=None, labels=True, ybot=H, centre=None):
    """n lanes going north. centre=i draws line i as the two-way centre line."""
    if x0 is None: x0 = (W - n * lw) / 2
    b = bg() + roads(R(x0, -10, n * lw, H + 20))
    for i in range(1, n):
        b += line(x0 + i * lw, 0, x0 + i * lw, H, "sv-centre" if i == centre else "sv-lane")
    if labels:
        for i in range(n):
            b += tagbox(x0 + i * lw + lw / 2, H - 14, str(i + 1))
    return b

def lane_x(n, i, lw=LW):
    """Centre x of lane i (0-based, from the left) on an n-lane lanes_north road."""
    return (W - n * lw) / 2 + i * lw + lw / 2

def painted_arrow(cx, cy, kind):
    # road-marking arrows pointing north
    s = f'<g transform="translate({_n(cx)},{_n(cy)})" class="sv-paint">'
    if kind in ("straight", "straight-right", "straight-left"):
        s += '<path d="M0,16 L0,-10"/><path d="M-4.5,-7 L0,-16 L4.5,-7 Z" class="sv-paintfill"/>'
    if kind in ("right", "straight-right"):
        y = 3 if kind != "right" else -4      # a shared arrow branches lower so both heads stay distinct
        s += f'<path d="M0,16 L0,{y + 7} Q0,{y} 7,{y}"/><path d="M6,{y - 4.5} L14,{y} L6,{y + 4.5} Z" class="sv-paintfill"/>'
    if kind in ("left", "straight-left"):
        y = 3 if kind != "left" else -4
        s += f'<path d="M0,16 L0,{y + 7} Q0,{y} -7,{y}"/><path d="M-6,{y - 4.5} L-14,{y} L-6,{y + 4.5} Z" class="sv-paintfill"/>'
    s += '</g>'
    return s

Q = []
def add(q, opts, ans, body, expl, uid):
    Q.append([q, opts, ans, svg(body, uid), expl])

u = 0
# 1. straight vs straight from right
u += 1; b = cross(u, stop=False)
b += path("M232,125 L16,125", u, "sv-path2") + path("M135,164 L135,14", u)
b += vehicle(135, 180, 0, kind="you") + vehicle(250, 125, 270, "A")
add("No traffic lights or signs. You're going straight across, and car A is going straight from your right. Who goes first?",
    ["Car A goes first", "You go first", "Whoever reaches the junction first"], 0, b,
    "Going straight at an uncontrolled junction, you give way to traffic going straight from the right. (Handbook 162a)", u)

# 2. turning left vs straight from right
u += 1; b = cross(u, stop=False)
b += path("M232,125 L122,125", u, "sv-path2") + path("M135,164 Q135,125 104,125 L16,125", u)
b += vehicle(135, 180, 0, kind="you") + vehicle(250, 125, 270, "A")
add("No traffic lights or signs. You're turning left; car A is going straight from your right. What do you do?",
    ["Give way to car A", "Go first: left turns don't cross anyone", "Go first if you signalled"], 0, b,
    "Turning left at an uncontrolled junction, you give way to traffic going straight from the right. Car A ends up in the same lane you're turning into. (Handbook 162b)", u)

# 3. turning right vs straight from both directions
u += 1; b = cross(u, stop=False)
b += path("M165,58 L165,206", u, "sv-path2") + path("M68,95 L128,95", u, "sv-path2")
b += path("M135,164 L135,120 Q136,95 166,95 L284,95", u)
b += vehicle(135, 180, 0, kind="you") + vehicle(165, 40, 180, "C") + vehicle(50, 95, 90, "B")
add("No traffic lights or signs. You're turning right. Car B (from your left) and car C (oncoming) are both going straight. Who must you give way to?",
    ["Both B and C", "Only C, the oncoming car", "Only B, the car from your left"], 0, b,
    "Turning right at an uncontrolled junction, you give way to traffic going straight from all directions. (Handbook 162c)", u)

# 4. turning right vs oncoming turning left
u += 1; b = cross(u, stop=False)
b += path("M165,58 Q165,89 194,89 L240,89", u, "sv-path2")
b += path("M135,164 L135,126 Q136,100 166,100 L284,100", u)
b += vehicle(135, 180, 0, kind="you") + vehicle(165, 40, 180, "D")
add("No traffic lights or signs. You're turning right. Oncoming car D is turning left into the same road. Who goes first?",
    ["Car D goes first", "You go first", "Whoever is faster"], 0, b,
    "When turning right you also give way to traffic turning left from the opposite direction. (Handbook 162c)", u)

# 5. you straight, car from left turning right across you
u += 1; b = cross(u, stop=False)
b += path("M68,95 Q160,95 165,130 L165,206", u, "sv-path2") + path("M135,164 L135,14", u)
b += vehicle(135, 180, 0, kind="you") + vehicle(50, 95, 90, "B")
add("No traffic lights or signs. You're going straight. Car B, on your left, wants to turn right. Who goes first?",
    ["You go first", "Car B goes first", "Car B, because it's on the major road"], 0, b,
    "A vehicle turning right gives way to traffic going straight from all directions, so B waits for you. Still ride defensively in case B doesn't. (Handbook 162c)", u)

# 6. roundabout entry
u += 1; b = roundabout(u, flows=(185, 285))
b += vehicle(135, 197, 0, kind="you", tag='l')
b += vehicle(194, 131, 210, "E") + path("M184,146 A53,53 0 0 1 150,158", u, "sv-path2")
add("You're about to enter the roundabout. Car E is already in it, coming round from your right. What do you do?",
    ["Give way to car E", "Enter first: you're on the left", "Sound your horn and enter"], 0, b,
    "When entering a roundabout, give way to traffic on your right already in the roundabout. Traffic goes round clockwise. (Handbook 169a)", u)

# 7. roundabout leaving signal
u += 1; b = roundabout(u, flows=(0, 270))
b += path("M95,139 Q84,122 16,120", u) + vehicle(105, 151, 320, kind="you", tag='b')
add("You're in the roundabout and about to leave at the next exit (arrow). Which signal do you give?",
    ["Signal left", "Signal right", "No signal: everyone can see you"], 0, b,
    "Signal left when you're about to leave the roundabout. (Handbook 170d)", u)

# 8. roundabout exit blocked
u += 1; b = roundabout(u, flows=())
b += path("M135,182 L131,160 A56,56 0 1 1 205,90", u)
b += vehicle(135, 197, 0, kind="you", tag='l')
b += vehicle(236, 90, 90, None) + vehicle(270, 90, 90, None) + vehicle(304, 90, 90, None)
b += text(262, 160, "Exit jammed", "sv-cap")
add("Your exit (to the right) is jammed with stopped traffic. The roundabout itself is clear. What do you do?",
    ["Wait: don't enter until your exit is clear", "Enter and wait inside the roundabout", "Enter and go round until it clears"], 0, b,
    "Don't enter a roundabout if you can see that your exit is blocked. (Handbook 169c)", u)

# 9. filter lane: main road y 50-110 (westbound lane y 80-110), side road x 180-240, slip lane peeling off to the left
u += 1
slip = "M165,232 L165,172 Q165,112 84,97"
b = bg() + roads(R(-10, 50, W + 20, 60), R(179, 110, 61, H), S(slip, 30), fillet(240, 110, 1, 1))
b += line(0, 80, W, 80, "sv-centre") + line(210, H, 210, 122, "sv-centre") + line(181.5, 121, 210, 121, "sv-stop") + line(180, 178, 180, H, "sv-edge")
for k in range(5):
    b += rect(152 + k * 5.8, 174, 3.2, 15, "sv-zebra")
b += line(100, 111.5, 152, 111.5, "sv-giveway") + line(104, 115.5, 153, 115.5, "sv-giveway")
b += path("M244,95 L176,95", u, "sv-path2") + path("M165,190 L165,172 Q165,112 84,97 L16,95", u)
b += vehicle(165, 205, 0, kind="you", tag='') + _tag(124, 207) + vehicle(262, 95, 270, "F")
b += ped(140, 181) + tagbox(124, 181, "P")
b += text(150, 40, "Main road", "sv-cap") + text(60, 150, "Filter lane", "sv-cap")
add("You're turning left using the filter lane. Pedestrian P is about to cross it, and car F is coming along the main road from your right. What's the right order?",
    ["Stop for P at the crossing, then give way to F at the give-way line", "Go before F, since filter lanes have priority", "Give way to F only; P waits for you"], 0, b,
    "In a filter lane, stop for pedestrians at the crossing, then give way to traffic from the right at the give-way line before merging. (Handbook 133)", u)

# 10. T-junction turning right: gaps
u += 1; b = tjunction(u)
b += path("M58,85 L112,85", u, "sv-path2") + path("M242,115 L188,115", u, "sv-path2")
b += path("M135,156 L135,104 Q136,85 162,85 L284,85", u)
b += vehicle(135, 172, 0, kind="you") + vehicle(40, 85, 90, "L") + vehicle(260, 115, 270, "R")
add("Turning right out of the minor road. How far away should traffic from your LEFT (car L) be before you go?",
    ["8 seconds", "More than 6 seconds", "3 seconds"], 0, b,
    "Turning right from a minor road: go when traffic from the right is more than 6 seconds away and traffic from the left is 8 seconds away. You join the left traffic's lane, so it gets the bigger gap. (Handbook 137)", u)

# 11. T-junction turning left gap
u += 1; b = tjunction(u)
b += path("M242,115 L188,115", u, "sv-path2") + path("M135,156 Q135,115 108,115 L16,115", u)
b += vehicle(135, 172, 0, kind="you") + vehicle(260, 115, 270, "R")
add("Turning left out of the minor road. Car R is coming from your right. When can you go?",
    ["When R is more than 6 seconds away", "Straight away: you're turning left", "Only when the major road is completely empty"], 0, b,
    "Turning left from a minor road: stop at the line and go when traffic from the right is more than 6 seconds away. (Handbook 131)", u)

# 12. green light turning right, oncoming straight
u += 1; b = cross(u, lights="green")
b += path("M165,54 L165,206", u, "sv-path2") + path("M135,164 L135,120 Q136,95 166,95 L284,95", u)
b += vehicle(135, 180, 0, kind="you") + vehicle(165, 36, 180, "G")
add("The light is green (no green arrow). You're turning right; oncoming car G is going straight. What do you do?",
    ["Give way to G, then turn when it's clear", "Turn first: you have a green light", "Wait for the light to turn red, then turn"], 0, b,
    "On a plain green, check oncoming traffic and only turn when it's safe. Straight-going oncoming traffic goes first. (Handbook 139F)", u)

# 13. view blocked by opposite right turner
u += 1; b = cross(u, lights="green")
b += vehicle(139, 122, 0, kind="you")
b += vehicle(162, 86, 180, None, kind="lorry", signal="right")   # faces south, so its right indicator is on screen-left
b += text(238, 42, "Oncoming lorry", "sv-cap") + text(238, 55, "also turning right", "sv-cap")
add("You've moved up to turn right, but an oncoming lorry waiting to turn right blocks your view. What do you do?",
    ["Don't go until the green arrow shows", "Edge forward and go when you think it's clear", "Sound your horn and turn"], 0, b,
    "If oncoming right-turning vehicles block your view, don't proceed until the green arrow appears. (Handbook 139G)", u)

# 14. yellow box going straight, exit jammed
u += 1; b = cross(u, lights="green", yellow=True)
b += path("M135,164 L135,84", u)
b += vehicle(135, 180, 0, kind="you") + vehicle(135, 56, 0, None) + vehicle(135, 22, 0, None) + vehicle(135, -12, 0, None)
add("The light is green and you're going straight, but traffic on the far side of the yellow box is backed up. What do you do?",
    ["Wait behind the stop line until your exit is clear", "Enter the box: the light is green", "Enter and wait halfway"], 0, b,
    "Entering a yellow box and causing an obstruction is an offence, even on a green light. Wait behind the line until you can clear it. (Handbook 167)", u)

# 15. yellow box turning right waiting
u += 1; b = cross(u, lights="green", yellow=True)
b += path("M149,104 Q158,95 184,95 L284,95", u)
b += vehicle(141, 115, 32, kind="you", tag='') + _tag(141, 160)
b += vehicle(165, 48, 180, None) + vehicle(165, 14, 180, None)
add("You're turning right and oncoming traffic is stopping you. May you wait inside the yellow box?",
    ["Yes, and if the light turns red, complete your turn", "No, never wait inside a yellow box", "Yes, but reverse out if the light turns red"], 0, b,
    "Riders turning right may wait in the yellow box for oncoming traffic. If the lights turn red, complete the turn and clear the box. (Handbook 167, situation two)", u)

# 16. expressway merge lane: carriageway x 128-260 (three lanes), acceleration lane joining from the left
u += 1
b = bg() + roads(R(128, -10, 132, H + 20), P(f"M84,{H + 10} L84,128 Q84,78 128,34 L128,{H + 10} Z"))
b += line(172, 0, 172, H, "sv-lane") + line(216, 0, 216, H, "sv-lane") + line(128, 50, 128, H, "sv-merge") + line(128, 0, 128, 34, "sv-edge")
b += path("M107,160 Q109,100 147,62", u)
b += vehicle(106, 176, 0, kind="you") + vehicle(150, 196, 0, None) + vehicle(194, 112, 0, None)
for i, xx in enumerate((150, 194, 238)):
    b += tagbox(xx, 18, "XYZ"[i])
b += text(72, 150, "Acceleration", "sv-cap", "end") + text(72, 163, "lane", "sv-cap", "end")
add("You're joining the expressway from the acceleration lane. Which lane do you merge into?",
    ["Lane X, the left lane, once you've matched speed", "Straight into lane Y, the middle lane", "Stop at the end of the acceleration lane and wait"], 0, b,
    "Build up speed in the acceleration lane, give way to traffic already on the expressway, and merge smoothly into the left lane. (Handbook 189)", u)

# 17. three-lane clear road
u += 1; b = lanes_north(u, 3, labels=False)
b += vehicle(lane_x(3, 1), 160, 0, kind="you")
for i in range(3):
    b += tagbox(lane_x(3, i), 18, "XYZ"[i])
add("You're riding at 80 km/h on a three-lane road and there's no traffic ahead. Which lane should you be in?",
    ["X, the left lane", "Y, the middle lane", "Z, the right lane"], 0, b,
    "Keep left when the road ahead is clear. Use the right lane only to overtake, and don't hog the middle. (Official question; Handbook 142–143)", u)

# 18. marked lanes going straight
u += 1; b = lanes_north(u, 4)
for i, k in enumerate(("left", "straight", "straight-right", "right")):
    b += painted_arrow(lane_x(4, i), 50, k)
b += vehicle(150, 150, 0, kind="you") + text(150, 126, "?", "sv-q")
add("You want to go straight at the junction ahead. Which lane is best?",
    ["Lane 2", "Lane 3", "Lane 2 or 3, it makes no difference"], 0, b,
    "Going straight, avoid the shared straight/right lane so you don't block riders turning right when the straight light turns red. (Handbook 163B)", u)

# 19. marked lanes turning right
u += 1; b = lanes_north(u, 4)
for i, k in enumerate(("left", "straight", "straight-right", "right")):
    b += painted_arrow(lane_x(4, i), 50, k)
b += vehicle(150, 150, 0, kind="you") + text(150, 126, "?", "sv-q")
add("You want to turn right at the junction ahead. Which lanes may you use?",
    ["Lane 3 or lane 4", "Only lane 4", "Any lane, as long as you signal"], 0, b,
    "Obey the lane arrows: both the right-only lane and the shared straight/right lane allow a right turn. In the shared lane, signal early so straight traffic can use another lane. (Handbook 144, 163A)", u)

# 20. after left turn -> nearest left lane (road y 20-110: oncoming lane on top, Y, then X nearest you)
u += 1
b = bg() + roads(R(120, 110, 60, H), R(-10, 20, W + 20, 90), fillet(120, 110, -1, 1), fillet(180, 110, 1, 1))
b += line(0, 50, W, 50, "sv-centre") + line(0, 80, W, 80, "sv-lane")
b += line(150, H, 150, 122, "sv-centre") + line(121.5, 121, 150, 121, "sv-stop")
b += path("M135,164 Q135,96 92,95 L62,95", u)
b += vehicle(135, 180, 0, kind="you") + vehicle(236, 35, 90, None)
b += tagbox(34, 65, "Y") + tagbox(34, 95, "X")
b += text(16, 38.5, "Oncoming side", "sv-cap2", "start")
add("You're turning left into a road with two lanes going your way (X and Y). Which lane do you turn into?",
    ["X, the nearest left lane", "Y, the outer lane", "Either, as long as you signal"], 0, b,
    "After turning left, turn into the nearest left lane, then look far ahead. (Handbook 134H)", u)

# 21. after right turn -> nearest right lane (road y 10-130: Y, X, centre line, two oncoming lanes)
u += 1
b = bg() + roads(R(120, 130, 60, H), R(-10, 10, W + 20, 120), fillet(120, 130, -1, 1), fillet(180, 130, 1, 1))
b += line(0, 70, W, 70, "sv-centre") + line(0, 40, W, 40, "sv-lane") + line(0, 100, W, 100, "sv-lane")
b += line(150, H, 150, 142, "sv-centre") + line(121.5, 141, 150, 141, "sv-stop")
b += path("M135,170 L135,104 Q136,56 190,55 L228,55", u)
b += vehicle(135, 186, 0, kind="you") + vehicle(54, 115, 270, None)
b += tagbox(266, 55, "X") + tagbox(266, 25, "Y")
b += text(284, 88.5, "Oncoming side", "sv-cap2", "end")
add("You're turning right into a road with two lanes going your way (X and Y). Which lane do you turn into?",
    ["X, the nearest right lane", "Y, the outer left lane", "Whichever lane is emptier"], 0, b,
    "After turning right, turn into the nearest right lane, then move left when it's safe. (Handbook 139H)", u)

# 22. parked bus + car close behind in next lane
u += 1; b = lanes_north(u, 2, labels=False)
xl, xr = lane_x(2, 0), lane_x(2, 1)
b += path(f"M{xr},172 L{xr},26", u, "sv-path2")
b += vehicle(xl, 62, 0, None, kind="bus") + text(94, 66, "Parked", "sv-cap", "end")
b += vehicle(xl, 160, 0, kind="you") + vehicle(xr, 190, 0, "R")
add("A bus is parked ahead in your lane. Car R in the next lane is close behind you and moving fast. What do you do?",
    ["Slow down, let R pass, then change lanes", "Change lanes now and speed up", "Swerve out quickly before R catches up"], 0, b,
    "If the vehicle behind in the next lane is too close, slow down and let it pass before you change lanes. (Handbook 150)", u)

# 23. stationary vehicles in left lane
u += 1; b = lanes_north(u, 2, labels=False)
for yy in (28, 66, 104):
    b += vehicle(xl, yy, 0, None)
b += vehicle(xl, 170, 0, kind="you") + text(94, 70, "Stopped", "sv-cap", "end")
add("Several vehicles are stopped in the left lane ahead of you. The right lane is clear. What do you do?",
    ["Move into the right lane, pass them, then move back left", "Weave between the stopped vehicles", "Ride along the line between the two lanes"], 0, b,
    "Don't weave in and out. Use the next lane and move back to the left lane after you've passed them. (Handbook 206)", u)

# 24. obstruction on your side, oncoming car
u += 1
b = lanes_north(u, 2, labels=False, centre=1)
b += rect(xl - 18, 66, 36, 44, "sv-works", 4) + text(xl, 91.5, "Works", "sv-workstxt")
b += path(f"M{xr},66 L{xr},206", u, "sv-path2")
b += vehicle(xl, 168, 0, kind="you") + vehicle(xr, 48, 180, "O")
add("Road works block your side of a two-way road. Car O is coming the other way. Who goes first?",
    ["Car O: you wait behind the works", "You: you got there first", "Whoever flashes their lights first"], 0, b,
    "If the obstruction is on your side of the road, give way to oncoming vehicles before passing. Slow down so you can stop about a vehicle length from it. (Handbook 207, 210–211)", u)

# 25. long vehicle turning left swings right (your road x 120-180 meets a road y 20-80 at the top)
u += 1
b = bg() + roads(R(-10, 20, W + 20, 60), R(120, 80, 60, H), fillet(120, 80, -1, 1), fillet(180, 80, 1, 1))
b += line(0, 50, W, 50, "sv-centre") + line(150, H, 150, 92, "sv-centre") + line(121.5, 91, 150, 91, "sv-stop")
b += path("M150,102 Q146,66 108,65 L18,65", u, "sv-path2")
b += vehicle(153, 130, 8, None, kind="lorry", signal="left")
b += vehicle(135, 196, 0, kind="you", tag='l')
b += text(192, 126, "Signalling left,", "sv-cap", "start") + text(192, 139, "swung out right", "sv-cap", "start")
add("The lorry ahead is signalling left but has moved out to the right. What do you do?",
    ["Stay well back and give it room", "Pass it on the left", "Pass it on the right"], 0, b,
    "Long vehicles swing out to the right before turning left. Stay well back and don't try to pass on the left. (Official question)", u)

# 26. one-way street turning right
u += 1; b = lanes_north(u, 3)
for i in range(3):
    b += painted_arrow(lane_x(3, i), 50, "straight")
b += vehicle(lane_x(3, 1), 150, 0, kind="you") + text(258, 106, "One-way", "sv-cap") + text(258, 119, "street", "sv-cap")
add("You're on a one-way street (all lanes go the same way) and want to turn right at the end. Which lane?",
    ["Lane 3, the right-hand lane", "Lane 2, just left of the centre", "Any lane, depending on traffic"], 0, b,
    "On a one-way street, position in the right-hand lane to turn right. (Official question)", u)


# ---------- batch 2: postures, controls, procedures, circuit ----------
def _q(p0, c, p1, t):
    """Point and compass heading on a quadratic Bezier."""
    x = (1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * c[0] + t * t * p1[0]
    y = (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * c[1] + t * t * p1[1]
    dx = 2 * (1 - t) * (c[0] - p0[0]) + 2 * t * (p1[0] - c[0]); dy = 2 * (1 - t) * (c[1] - p0[1]) + 2 * t * (p1[1] - c[1])
    return x, y, math.degrees(math.atan2(dx, -dy))

def left_of(x, y, hd, off=15):
    """A point `off` to the LEFT of travel (the side we ride on)."""
    r = math.radians(hd)
    return x - math.cos(r) * off, y - math.sin(r) * off

def bend_scene(d, label, sign=None):
    b = bg() + roads(S(d, 60)) + f'<path d="{d}" class="sv-centre" fill="none"/>'
    b += text(W - 14, 191 if sign else 204, label, "sv-cap", "end")
    if sign:
        b += text(W - 14, 204, sign, "sv-cap", "end")
    return b

def bike_top(hl):
    b = bg()
    b += rect(143, 20, 14, 40, "sv-tyre", 7) + rect(141, 164, 18, 42, "sv-tyre", 9)       # wheels
    b += rect(139, 48, 22, 13, "sv-body", 5)                                                 # headlight / front fork
    b += rect(128, 66, 44, 58, "sv-body", 19) + rect(132, 116, 36, 64, "sv-seat", 15)       # tank, seat
    b += line(84, 70, 216, 70, "sv-bar")                                                     # handlebar
    b += rect(62, 63, 30, 14, "sv-grip", 6) + rect(208, 63, 30, 14, "sv-grip", 6)
    b += '<path d="M100,66 Q86,50 62,52" class="sv-lever"/><path d="M200,66 Q214,50 238,52" class="sv-lever"/>'
    b += rect(104, 136, 26, 8, "sv-pedal", 3) + rect(170, 136, 26, 8, "sv-pedal", 3)
    labels = {"A": (56, 38), "B": (244, 38), "T": (256, 70), "C": (86, 140), "D": (214, 140)}
    for k, (x, y) in labels.items():
        b += badge(x, y, k, "sv-hl", "sv-hltxt", 10) if k == hl else badge(x, y, k, r=10)
    b += text(150, 13, "Front", "sv-cap") + text(14, 208, "Seen from above", "sv-cap", "start")
    return b

u += 1
b = bend_scene("M70,232 Q90,120 160,90 Q230,62 312,58", "Gradual bend")
x, y, hd = _q((70, 232), (90, 120), (160, 90), .42); x, y = left_of(x, y, hd)
b += vehicle(x, y, hd, kind="you", tag='') + _tag(x - 30, y - 6)
add("You're riding round a gradual bend at normal speed. Which riding posture should you use?",
    ["Lean with: your body at the same angle as the bike", "Lean out: body upright, bike leaned under you", "Lean in: body leaned further than the bike"], 0, b,
    "Lean with is the posture for gradual bends: lean at the same angle as the motorcycle, head upright, knees gripping the tank. (Handbook, riding postures when cornering)", u)

u += 1
b = bend_scene("M120,232 L120,112 Q120,80 152,80 L312,80", "Sharp corner", "Low speed")
b += vehicle(105, 160, 0, kind="you", tag='l')
add("You're taking a sharp corner at low speed. Which riding posture should you use?",
    ["Lean out: lean your body away from the bike's angle", "Lean with: same angle as the bike", "Lean in: lean further than the bike"], 0, b,
    "Lean out is for sharp bends or corners at low speed: lean your body outwards, away from the bike's banking angle. (Handbook, riding postures when cornering)", u)

u += 1
b = bend_scene("M60,232 Q76,96 200,74 Q260,64 312,64", "Sweeping bend", "High speed")
x, y, hd = _q((60, 232), (76, 96), (200, 74), .36); x, y = left_of(x, y, hd)
b += vehicle(x, y, hd, kind="you", tag='') + _tag(x - 24, y - 20)
add("You're riding round a bend at high speed. Which riding posture should you use?",
    ["Lean in: lean further than the bike", "Lean out: lean away from the bike", "Sit upright and keep the bike upright"], 0, b,
    "Lean in is for bends taken at high speed: lean in more than the bike's banking angle, head upright. (Handbook, riding postures when cornering)", u)

u += 1; b = bike_top("A")
add("On a manual motorcycle, what does lever A (left hand) control?",
    ["The clutch", "The front brake", "The rear brake"], 0, b,
    "Left hand: clutch lever. Right hand: front brake lever and throttle. Left foot: gear pedal. Right foot: rear brake pedal. (Handbook 39, controls)", u)

u += 1; b = bike_top("B")
add("On a manual motorcycle, what does lever B (right hand) control?",
    ["The front brake", "The clutch", "Both front and rear brakes"], 0, b,
    "The right-hand lever works the front brake only. The rear brake is the right foot pedal. (Handbook 39)", u)

u += 1; b = bike_top("D")
add("What is pedal D, under your right foot?",
    ["The rear brake", "The gear pedal", "The front brake"], 0, b,
    "Right foot: rear brake pedal. Left foot (C): gear pedal. Rest your right toes on the brake pedal and press with the ball of your foot. (Handbook 39)", u)

u += 1; b = bike_top("B")
b += '<path d="M209,49 L227,65 M227,49 L209,65" class="sv-xmark"/>'
add("Your front brake (lever B) suddenly fails while riding. What do you do?",
    ["Hazard lights, rear brake, change down to 2nd for engine braking, pull over", "Pump lever B harder and keep riding", "Pull in the clutch and coast to a stop"], 0, b,
    "Front brake failure: hazard lights on, move to the side, use the rear brake, change down (preferably to 2nd) and release the clutch for engine braking, then switch off. (Handbook 263)", u)

u += 1; b = lanes_north(u, 2, labels=False)
b += path(f"M{xl},182 L{xl},146 C{xl},116 {xr},114 {xr},84 L{xr},18", u)
for k, (px, py, bx) in {"A": (xl, 172, 88), "B": (xl, 138, 88), "C": (150, 115, 88), "D": (xr, 44, 212)}.items():
    b += line(px, py, bx + (9 if bx < px else -9), py, "sv-leader") + circle(px, py, 2.6, "sv-dot") + badge(bx, py, k, r=8.5)
b += vehicle(xl, 198, 0, kind="you", tag='l')
add("You're changing to the right lane. What do you do at point A, before moving?",
    ["Check mirrors, signal for at least 3 seconds, check your blind spot", "Signal and move over straight away", "Speed up, then check your mirrors"], 0, b,
    "Changing lanes: at A check mirrors, signal at least 3 seconds, check blind spots; at B adjust speed; at C steer gently in when safe; at D cancel the signal. (Handbook 146)", u)

u += 1
b = lanes_north(u, 2, labels=False, centre=1)
b += path(f"M{xr},58 L{xr},104", u, "sv-path2")
b += vehicle(xl, 112, 0, None, kind="lorry") + text(94, 116, "Slow", "sv-cap", "end")
b += vehicle(xl, 190, 0, kind="you", tag='l')
b += vehicle(xr, 40, 180, "O")
b += dim(212, 24, 212, 176, "12 s", 220, 104)
add("You want to overtake the slow lorry, but oncoming car O is within your 12-second view ahead. What do you do?",
    ["Stay behind until the road ahead is clear for 12 seconds", "Overtake quickly before O arrives", "Overtake on the left instead"], 0, b,
    "Only overtake when oncoming traffic is beyond your 12-second scan. An overtake takes about 10 seconds, plus the 2-second gap before it. (Handbook 254)", u)

# U-turn: your carriageway x 52-140 (lanes 1, 2), divider 140-160 with an opening at y 70-130, far carriageway 160-248
u += 1
b = bg() + roads(R(52, -10, 196, H + 20))
b += rect(140, -12, 20, 82, "sv-island", 9) + rect(140, 130, 20, 110, "sv-island", 9)
b += line(96, 0, 96, H, "sv-lane") + line(204, 0, 204, H, "sv-lane")
b += path("M136,126 C136,92 164,92 164,124", u, "sv-path2")
b += vehicle(74, 188, 0, kind="you") + vehicle(226, 56, 180, None)
b += tagbox(74, 18, "1") + tagbox(118, 18, "2")
b += text(26, 106, "Divider", "sv-cap") + text(26, 119, "opening", "sv-cap") + line(44, 102, 132, 102, "sv-leader")
add("You want to make a U-turn at the divider opening ahead (a U-turn sign allows it). Which lane do you ride in before turning?",
    ["Lane 2, the right outer lane", "Lane 1, the left lane", "Either lane"], 0, b,
    "For a U-turn: signal right, check your blind spot and ride in the right outer lane, slow down, and stop behind the stop line in the opening if there is one. Only U-turn where a sign allows it. (Handbook 140)", u)

u += 1; b = cross(u, lights="red")
b += vehicle(135, 166, 0, kind="you", tag='r')
b += vehicle(135, 200, 0, None, kind="ambulance") + text(190, 198, "Ambulance,", "sv-cap", "start") + text(190, 211, "siren on", "sv-cap", "start")
add("You're stopped at a red light. An ambulance with its siren on comes up behind you. What do you do?",
    ["Don't enter the junction: pull to the nearest edge only if you can safely", "Ride into the junction to clear the way", "Stay exactly where you are, even if there's space to the side"], 0, b,
    "Give way by pulling to the nearest edge of the road, but never block an intersection doing it. Don't stop in front of it or follow it closely afterwards. (Handbook 145)", u)

u += 1
b = bg() + roads(R(18, 66, 264, 88, 12)) + rect(64, 103, 184, 14, "sv-plank", 3)
b += path("M96,110 L236,110", u)
b += text(150, 54, "Narrow plank", "sv-cap") + vehicle(78, 110, 90, kind="you", tag='t')
add("Circuit test: what is the target on the narrow plank?",
    ["Stay on it for 6 seconds or more", "Cross it in under 6 seconds", "Cross it as fast as you can"], 0, b,
    "The narrow plank tests slow-speed balance: stay on it for 6 seconds or more. Look ahead, use half-clutch and the rear brake to control speed. (Handbook 278)", u)

u += 1
b = bg() + roads(R(106, -10, 88, H + 20)) + rect(106, 38, 88, 5, "sv-paintbar") + line(106, 166, 194, 166, "sv-lane")
b += dim(210, 43, 210, 166, "11 m", 218, 108)
b += vehicle(150, 184, 0, kind="you") + text(94, 188, "30 km/h, wet", "sv-cap", "end")
add("Emergency brake course: riding at about 30 km/h on a wet surface, you must stop within…",
    ["11 metres", "6 metres", "20 metres"], 0, b,
    "Stop within 11 m from about 30 km/h on a wet surface, using both brakes without locking the wheels, and pull the clutch in just before you stop. (Handbook 282)", u)

json.dump(Q, open('form/diagrams.json', 'w'), ensure_ascii=False)
print(len(Q), 'diagram questions')
