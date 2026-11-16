"""Diagram scenario questions for the Basic Theory Test (BTT, car).
Run from the rtt folder:  python3 btt/diagrams_btt.py   ->  btt/diagrams.json
Each item: [question, [3 options], correctIndex, svg, explanation]. Every rule comes from an official
BTT question (btt/qa.txt) or the Basic Theory of Driving handbook (btt/handbook.txt); the source is cited
in the explanation. Singapore drives on the LEFT: northbound traffic uses the left (west) half of a road,
eastbound traffic the top (north) half. Uses the shared helpers and sv-* classes from diagrams.py.
SVG ids: uid 2000+ (RTT < 1000, FTT 3000+).
"""
import json, os, runpy

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
G = runpy.run_path('diagrams.py')          # also regenerates form/diagrams.json (harmless)
svg, rect, line, text, path, circle, vehicle, bg, roads, R, P, S, fillet = (G[k] for k in
    'svg rect line text path circle vehicle bg roads R P S fillet'.split())
tagbox, badge, dim, ped, painted_arrow, _tag, lamp = (G[k] for k in 'tagbox badge dim ped painted_arrow _tag lamp'.split())
cross, roundabout, lanes_north, lane_x = (G[k] for k in 'cross roundabout lanes_north lane_x'.split())
W, H = 300, 220

Q = []
UID = [2000]


def add(q, opts, body, expl):
    assert len(opts) == 3
    Q.append([q, opts, 0, svg(body, UID[0]), expl])


def nxt():
    UID[0] += 1
    return UID[0]


def you(x, y, hd=0, tag='b', signal=None):
    return vehicle(x, y, hd, kind="youcar", tag=tag, signal=signal)


def zigzag(x0, d, y0, y1, step=8):
    """White zig-zag line along a kerb, from y0 down to y1 (x alternates x0, x0 + d)."""
    pts = " ".join(f"{x0 + (d if i % 2 else 0)},{y0 + i * step}" for i in range(int((y1 - y0) / step) + 1))
    return f'<polyline points="{pts}" class="sv-edge" fill="none" stroke-linejoin="round"/>'


def zebra(x0, x1, y, h=20, bw=5, gap=3.4):
    s, x = '', x0 + 2
    while x + bw <= x1 - 1:
        s += rect(x, y, bw, h, "sv-zebra")
        x += bw + gap
    return s


def big_lamp(x, y, lit, arrow=False, s=1.3):
    """Signal head, scale s. arrow=True draws a right-turn arrow head (lit aspect = coloured arrow on a dark disc)."""
    b = rect(x, y, 14 * s, 36 * s, "sv-pole", 4 * s)
    for i, (k, cls) in enumerate((("red", "sv-lr"), ("amber", "sv-la"), ("green", "sv-lg"))):
        cx, cy, r = x + 7 * s, y + (8 + i * 10) * s, 3.6 * s
        if not arrow:
            b += circle(cx, cy, r, cls if lit == k else "sv-loff")
        else:
            b += circle(cx, cy, r, "sv-loff")
            if lit == k:
                b += (f'<path d="M{cx - 3.8:.1f},{cy - 1.3:.1f} H{cx + .2:.1f} V{cy - 3.9:.1f} L{cx + 4.2:.1f},{cy:.1f} '
                      f'L{cx + .2:.1f},{cy + 3.9:.1f} V{cy + 1.3:.1f} H{cx - 3.8:.1f} Z" class="{cls}"/>')
    return b


def bus_lane_line(x, y0, y1, ticks=(), broken=False):
    """Yellow bus-lane line at x (bus lane on its LEFT), with short yellow ticks into the bus lane."""
    s = f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" class="sv-ybo"' + (' stroke-dasharray="9 7"' if broken else '') + '/>'
    for ty in ticks:
        s += line(x, ty, x - 28, ty, "sv-ybo")
    return s


# ---------------------------------------------------------------- 1 uncontrolled junction: straight vs straight from right
u = nxt(); b = cross(u, stop=False)
b += path("M232,125 L16,125", u, "sv-path2") + path("M135,164 L135,14", u)
b += you(135, 180) + vehicle(250, 125, 270, "A")
add("No traffic lights, signs or road markings. You're going straight across, and car A is going straight from your right. Who goes first?",
    ["Car A: you give way to it", "You: you're going straight too", "Whoever reaches the junction first"], b,
    "At an uncontrolled junction, if you're going straight across you must give way to traffic going straight from the right. (Handbook para 82(a))")

# ---------------------------------------------------------------- 2 give-way lines at a T-junction
u = nxt()
b = bg() + roads(R(-10, 70, W + 20, 60), R(120, 130, 60, H), fillet(120, 130, -1, 1), fillet(180, 130, 1, 1))
b += line(0, 100, W, 100, "sv-centre") + line(150, H, 150, 150, "sv-centre")
b += line(121.5, 136.5, 150, 136.5, "sv-giveway") + line(121.5, 140.5, 150, 140.5, "sv-giveway")
b += text(288, 60, "Major road", "sv-cap", "end") + text(192, 208, "Minor road", "sv-cap", "start")
b += path("M242,115 L16,115", u, "sv-path2")
b += you(135, 172, tag='l') + vehicle(260, 115, 270, "M")
add("Two broken white lines are painted across the end of your road. Car M is coming along the major road. What do the lines tell you?",
    ["Give way to traffic on the major road", "Stop at the line every time, even if the road is clear", "Traffic on the major road must give way to you"], b,
    "Parallel broken white lines across the road mean you must give way to traffic on the major road. A single solid white line is the one that means you must stop. (Handbook para 52(a), 52(b), 81)")

# ---------------------------------------------------------------- 3 roundabout entry
u = nxt(); b = roundabout(u, flows=(185, 285))
b += you(135, 197, tag='l')
b += vehicle(194, 131, 210, "E") + path("M184,146 A53,53 0 0 1 150,158", u, "sv-path2")
add("You're about to enter the roundabout. Car E is already in it, coming round from your right. What should you do?",
    ["Give way to traffic on your right, such as car E", "Always stop first, then enter", "Speed up to merge ahead of car E"], b,
    "Before entering a roundabout, give way to traffic on your right. Traffic goes round clockwise, so E is coming towards your entry. (Official question; Handbook para 89)")

# ---------------------------------------------------------------- 4 yellow box, straight, exit blocked
u = nxt(); b = cross(u, lights="green", yellow=True)
b += path("M135,164 L135,84", u)
b += you(135, 180, tag='r') + vehicle(135, 56, 0) + vehicle(135, 22, 0) + vehicle(135, -12, 0)
b += text(196, 40, "Queue on the", "sv-cap", "start") + text(196, 53, "far side", "sv-cap", "start")
add("Your light is green and you're going straight, but traffic on the far side of the yellow box has stopped. What do you do?",
    ["Wait behind the stop line until your exit is clear", "Enter the box: the light is green", "Enter and wait inside the box"], b,
    "Driving into a yellow box and causing an obstruction is an offence even when the lights are in your favour. Going straight, wait behind the stop line until you can clear the box. (Handbook para 94)")

# ---------------------------------------------------------------- 5 yellow box, waiting to turn right, lights turn red
u = nxt(); b = cross(u, lights="red", yellow=True)
b += path("M149,104 Q158,95 184,95 L284,95", u)
b += vehicle(141, 115, 32, kind="youcar") + _tag(135, 162)
b += vehicle(165, 48, 180) + vehicle(165, 14, 180)
b += text(90, 174, "Now red", "sv-cap", "end")
add("You entered the yellow box to turn right and waited for oncoming traffic. Now the light turns red. What do you do?",
    ["Complete your turn and clear the box", "Stay in the box until the next green", "Reverse back behind the stop line"], b,
    "Drivers turning right may wait in the yellow box for a gap in oncoming traffic. If the lights turn red, complete the turn and clear the box. (Handbook para 94(b))")

# ---------------------------------------------------------------- 6 amber, well back from the line
u = nxt()
b = bg() + roads(R(120, -10, 60, H + 20), R(-10, -10, W + 20, 70), fillet(120, 60, -1, 1), fillet(180, 60, 1, 1))
b += line(0, 25, 110, 25, "sv-centre") + line(190, 25, W, 25, "sv-centre") + line(150, H, 150, 84, "sv-centre")
b += line(121.5, 72, 150, 72, "sv-stop") + lamp(97, 74, "amber")
b += path("M135,162 L135,84", u) + you(135, 178, tag='l')
b += text(192, 150, "Far enough back", "sv-cap", "start") + text(192, 163, "to stop safely", "sv-cap", "start")
add("The light changes from green to amber. You're well back from the stop line and can stop without braking sharply. What should you do?",
    ["Slow down and stop at the stop line", "Speed up to clear the junction", "Stop only if there's a red-light camera"], b,
    "Amber means stop at the stop line, unless you're so close that sudden or sharp braking might cause an accident. (Official question; Handbook para 58)")

# ---------------------------------------------------------------- 7 amber after crossing the line
u = nxt(); b = cross(u, lights="amber")
b += path("M135,106 L135,14", u) + you(135, 124, tag='l')
b += text(196, 182, "Turned amber", "sv-cap", "start") + text(196, 195, "after you crossed", "sv-cap", "start") + text(196, 208, "the stop line", "sv-cap", "start")
add("The light turns amber just after your car has crossed the stop line. What should you do?",
    ["Continue through the junction", "Stop and reverse back to the stop line", "Stop immediately where you are"], b,
    "Once you've passed the stop line when the light turns amber, continue and clear the junction. Stopping in it or reversing is dangerous. (Official question)")

# ---------------------------------------------------------------- 8 flashing amber
u = nxt(); b = cross(u, lights="amber")
b += '<path d="M85,170 H92 M89,160.5 L94,163.5 M89,179.5 L94,176.5 M114,170 H118.5 M114,163.5 L118,161 M114,176.5 L118,179" class="sv-dim"/>'
b += text(81, 174, "Flashing", "sv-cap", "end")
b += path("M232,125 L16,125", u, "sv-path2") + path("M135,164 L135,14", u)
b += you(135, 180, tag='r') + vehicle(250, 125, 270, "A")
add("The amber light is flashing continuously. You're going straight, and car A is approaching from your right. What do you do?",
    ["Slow down, give way to car A and proceed with caution", "Stop at the line and wait for the light to turn green", "Drive through quickly before car A arrives"], b,
    "Flashing amber means the traffic lights are out of order. Slow down, look out for other vehicles, give way to traffic on the right and proceed with caution. (Official question; Handbook para 58)")

# ---------------------------------------------------------------- 9 green main light, red right-turn arrow
u = nxt(); b = cross(u)
b += big_lamp(40, 140, "green", s=1.5) + big_lamp(80, 140, "red", arrow=True, s=1.5)
b += text(50.5, 208, "Main", "sv-cap") + text(90.5, 208, "Arrow", "sv-cap")
b += path("M139,164 L139,124 Q140,96 168,95 L284,95", u)
b += you(139, 180, tag='r', signal="right")
b += text(238, 42, "No oncoming", "sv-cap") + text(238, 55, "traffic", "sv-cap")
add("The main light is green but the right-turn arrow is red. You want to turn right and nothing is coming the other way. What do you do?",
    ["Wait behind the stop line until the red arrow goes off", "Turn: there's no oncoming traffic", "Turn, because the main light is green"], b,
    "A red arrow means stop behind the stop line for that direction. Don't turn right even when there's no traffic from the opposite direction. (Handbook para 58, red arrow)")

# ---------------------------------------------------------------- 10 zig-zag: no overtaking
u = nxt()
b = bg() + roads(R(106, -10, 88, H + 20))
b += zebra(106, 194, 30) + line(150, 0, 150, 22, "sv-lane") + line(150, 60, 150, H, "sv-lane")
b += zigzag(109, 6, 58, H + 8) + zigzag(191, -6, 58, H + 8)
b += circle(98, 25, 5, "sv-you") + circle(202, 55, 5, "sv-you") + ped(92, 44)
b += text(96, 140, "Zig-zag", "sv-cap", "end") + text(96, 153, "lines", "sv-cap", "end")
b += vehicle(128, 96, 0, "A") + you(172, 168, tag='r')
add("You're in the zig-zag area before a zebra crossing. Car A, in the next lane, has slowed down. May you overtake it?",
    ["No, not even if you think it's safe", "Yes, once car A has come to a complete stop", "Yes, if you don't inconvenience pedestrians"], b,
    "Within the zig-zag lines of a pedestrian crossing you must not overtake, even if you think it's safe. A slowing car may be stopping for a pedestrian you can't see. (Official question; Handbook para 55(a), 73(a))")

# ---------------------------------------------------------------- 11 zig-zag: no stopping
u = nxt()
b = bg() + roads(R(90, -10, 120, H + 20))
b += zebra(90, 210, 22) + line(150, 0, 150, 14, "sv-centre") + line(150, 52, 150, H, "sv-centre")
b += zigzag(93, 6, 50, H + 8) + zigzag(207, -6, 50, H + 8)
b += circle(82, 17, 5, "sv-you") + circle(218, 47, 5, "sv-you")
b += path("M118,152 Q118,128 108,114", u, "sv-path2") + tagbox(108, 98, "1")
b += you(120, 172, tag='r', signal="left")
add("You want to stop at 1, on the zig-zag lines near a zebra crossing, to let a passenger out. Is that allowed?",
    ["No: you may not stop there at any time", "Yes, for an immediate drop-off only", "Yes, if your hazard lights are on"], b,
    "White zig-zag lines by the side of the road warn of a pedestrian crossing and mean no stopping at all times. Don't overtake or wait there either. (Handbook para 55(a))")

# ---------------------------------------------------------------- 12 double white lines
u = nxt()
b = bg() + roads(R(90, -10, 120, H + 20))
b += line(148.3, 0, 148.3, H, "sv-edge") + line(151.7, 0, 151.7, H, "sv-edge")
b += vehicle(120, 72, 0, kind="lorry") + text(84, 76, "Slow lorry", "sv-cap", "end")
b += you(120, 168)
b += text(222, 40, "Double", "sv-cap", "start") + text(222, 53, "white lines", "sv-cap", "start") + line(220, 47, 156, 47, "sv-leader")
add("A slow lorry is ahead and the other side of the road looks clear. The centre of the road has double continuous white lines. May you cross them to overtake?",
    ["No: crossing them is an offence", "Yes, if you're overtaking a slow vehicle", "Yes, if you don't inconvenience anyone"], b,
    "Crossing double continuous white lines is an offence because it's unsafe. Don't overtake unless you can stay entirely to the left of them. (Official question; Handbook para 53(c), 73(e))")

# ---------------------------------------------------------------- 13 normal bus lane hours
u = nxt(); x0 = 84
b = bg() + roads(R(x0, -10, 132, H + 20)) + line(172, 0, 172, H, "sv-lane")
b += bus_lane_line(128, 0, H, ticks=(36, 128, 200))
b += vehicle(106, 82, 0, kind="bus") + you(150, 168, tag='r')
b += tagbox(106, 166, "X")
b += text(78, 150, "Continuous", "sv-cap", "end") + text(78, 163, "yellow line", "sv-cap", "end")
add("Lane X is a normal bus lane (continuous yellow line only). On weekday mornings, when must you keep out of it?",
    ["7.30 am to 9.30 am", "7.00 am to 9.30 am", "7.15 am to 10.00 am"], b,
    "Normal bus lanes operate Mondays to Fridays, 7.30 am to 9.30 am and 5.00 pm to 8.00 pm, but not on Saturdays, Sundays or public holidays. (Official question; Handbook para 54(a))")

# ---------------------------------------------------------------- 14 full-day bus lane on Saturday
u = nxt()
b = bg() + roads(R(x0, -10, 132, H + 20)) + line(172, 0, 172, H, "sv-lane")
b += rect(123.4, -2, 2.4, H + 4, "sv-cross") + bus_lane_line(128, 0, H, ticks=(36, 128, 200))
b += vehicle(106, 82, 0, kind="bus") + you(150, 168, tag='r')
b += tagbox(104, 166, "X")
b += text(78, 150, "Red line", "sv-cap", "end") + text(78, 163, "beside yellow", "sv-cap", "end")
add("Lane X has a red line next to its yellow line, so it's a full-day bus lane. On a Saturday, when must you keep out of it?",
    ["7.30 am to 11.00 pm", "7.30 am to 8.00 pm", "5.00 pm to 8.00 pm"], b,
    "The extra red line marks a full-day bus lane: no driving or parking in it Mondays to Saturdays, 7.30 am to 11.00 pm, except Sundays and public holidays. (Official question; Handbook para 54(b))")

# ---------------------------------------------------------------- 15 broken yellow line to turn left
u = nxt()
b = bg() + roads(R(128, -10, 88, H + 20), R(-10, 22, 140, 52), fillet(128, 22, -1, -1), fillet(128, 74, -1, 1))
b += line(0, 48, 110, 48, "sv-centre")
b += bus_lane_line(172, 132, H, ticks=(196,)) + bus_lane_line(172, -4, 132, broken=True)
b += tagbox(172, 166, "1") + tagbox(172, 98, "2")
b += you(194, 190, tag='r', signal="left")
b += text(60, 14, "Side road", "sv-cap") + text(120, 196, "Bus lane", "sv-cap", "end")
b += text(120, 118, "Broken", "sv-cap", "end") + text(120, 131, "yellow line", "sv-cap", "end")
add("It's 8 am on a weekday and the left lane is a normal bus lane. You want to turn left into the side road. Where may you move into the bus lane?",
    ["At 2, where the yellow line is broken", "At 1, as early as possible", "Nowhere: turn left across the bus lane from your own lane"], b,
    "During bus lane hours you may use the bus lane only where its yellow line is broken, to turn into a side road (or to turn from a side road into the bus lane road). (Handbook para 54(a))")

# ---------------------------------------------------------------- 16 parking: 6 m from a junction
u = nxt()
b = bg() + roads(R(120, -10, 60, H + 20), R(-10, 40, 140, 56), fillet(120, 40, -1, -1), fillet(120, 96, -1, 1))
b += line(150, 0, 150, H, "sv-centre") + line(0, 68, 108, 68, "sv-centre")
b += vehicle(130, 168, 0, kind="youcar", tag='r')
b += dim(108, 96, 108, 153, "? m", 100, 128, "end")
b += text(60, 30, "Side road", "sv-cap")
add("You want to park on the left near this junction. At least how far from the junction must your car be?",
    ["6 metres", "9 metres", "12 metres"], b,
    "No parking within 6 metres of a junction. (Official question; Handbook para 97(g))")

# ---------------------------------------------------------------- 17 parking: 9 m from a bus stop
u = nxt()
b = bg() + roads(R(120, -10, 60, H + 20))
b += line(150, 0, 150, H, "sv-centre")
b += rect(122, 34, 24, 58, "sv-ybo") + rect(100, 42, 10, 40, "sv-pole", 3) + text(94, 66, "Bus stop", "sv-cap", "end")
b += vehicle(130, 168, 0, kind="youcar", tag='r')
b += dim(110, 92, 110, 153, "? m", 102, 126, "end")
add("You want to park on the left just before this bus stop (the yellow box). At least how far from the bus stop must your car be?",
    ["9 metres", "12 metres", "15 metres"], b,
    "No parking within 9 metres of a bus stop, measured from the edge of the yellow box or the tip of the bus bay. (Official question; Handbook para 97(h))")

# ---------------------------------------------------------------- 18 three-lane road, keep left
u = nxt(); b = lanes_north(u, 3, labels=False)
b += you(lane_x(3, 1), 160)
for i in range(3):
    b += tagbox(lane_x(3, i), 18, "XYZ"[i])
add("You're driving at 80 km/h on a three-lane carriageway and there's no traffic ahead. Which lane should you use?",
    ["X, the left lane", "Y, the middle lane", "Any lane"], b,
    "Keep to the left lane when the road ahead is clear. The right lane is for overtaking and emergency vehicles, and you shouldn't hog the middle. (Official question; Handbook para 62, 69)")

# ---------------------------------------------------------------- 19 overtaking on the left
u = nxt()
b = bg() + roads(R(90, -10, 120, H + 20), R(200, 18, W, 60), fillet(210, 18, 1, -1), fillet(210, 78, 1, 1))
b += line(150, 0, 150, H, "sv-centre") + line(222, 48, W, 48, "sv-centre")
b += path("M140,78 Q142,34 180,33 L250,33", u, "sv-path2")
b += vehicle(139, 100, 0, "A", signal="right")
b += path("M108,166 L108,22", u) + you(108, 182, tag='l')
b += text(256, 100, "Side road", "sv-cap")
add("Car A ahead is signalling right and waiting to turn into the side road. When may you pass a vehicle on its left?",
    ["When its driver has signalled to turn right", "When it's a heavy vehicle", "When you're sure it won't change direction"], b,
    "Always overtake on the right, except in a few cases, such as when the driver in front has signalled that they're turning right. (Official question; Handbook para 71(a))")

# ---------------------------------------------------------------- 20 emergency vehicle, one-way street
u = nxt(); b = lanes_north(u, 3, labels=False)
for i in range(3):
    b += painted_arrow(lane_x(3, i), 34, "straight")
b += you(150, 104, tag='l') + vehicle(150, 176, 0, kind="ambulance")
b += text(258, 40, "One-way", "sv-cap") + text(258, 53, "street", "sv-cap")
b += text(258, 172, "Ambulance,", "sv-cap") + text(258, 185, "siren on", "sv-cap")
add("You're on a one-way street and hear an ambulance's siren behind you. How do you give way?",
    ["Move to the left or the right", "Move to the left only", "Stop immediately where you are"], b,
    "Give way to an emergency vehicle by pulling to the nearest edge of the road, left or right depending on circumstances, and stop if necessary. Don't slam on your brakes in front of it. (Official question; Handbook para 156)")

# ---------------------------------------------------------------- 21 blind spot
u = nxt(); b = lanes_north(u, 2, labels=False)
b += path("M128,86 C128,58 172,62 172,28", u)
b += you(128, 102) + vehicle(172, 140, 0, "B")
b += text(204, 136, "B is in your", "sv-cap", "start") + text(204, 149, "blind spot", "sv-cap", "start")
add("You want to move into the right lane. Car B is in your blind spot. How do you check for it?",
    ["Turn your head and look over your shoulder", "Look into the wing mirror", "Look into the rear-view mirror"], b,
    "Blind spots are the areas your mirrors can't show. Before changing lanes, turn your head and look over your shoulder. (Official question; Handbook para 131)")

# ---------------------------------------------------------------- 22 following distance on a wet road
u = nxt()
b = bg() + roads(R(-10, 70, W + 20, 60)) + line(0, 100, W, 100, "sv-centre")
b += you(62, 85, 90, tag='') + _tag(62, 112) + vehicle(232, 85, 90, "A")
b += rect(184, 34, 4, 32, "sv-pole", 2) + circle(186, 34, 4, "sv-la") + line(186, 66, 186, 100, "sv-leader")
b += dim(78, 22, 186, 22, "? s", 132, 15)
b += text(198, 52, "Post", "sv-cap", "start") + text(150, 160, "Wet road", "sv-cap")
add("The road is wet. Car A has just passed the post. How far behind car A should you be?",
    ["More than 2 seconds behind", "2 seconds behind", "Less than 2 seconds behind"], b,
    "Count the time from A passing a fixed point to you reaching it. On a wet road braking distances are longer, so keep a bigger gap than normal. (Official question; Handbook para 136, 139. The current handbook uses a 3-second rule for normal conditions.)")

# ---------------------------------------------------------------- 23 dazzled by oncoming headlights
u = nxt()
b = bg() + roads(R(90, -10, 120, H + 20)) + line(150, 0, 150, H, "sv-centre")
b += '<polygon points="173,72 187,72 209,190 152,190" class="sv-yb"/>'
b += line(173, 72, 152, 190, "sv-ybl") + line(187, 72, 209, 190, "sv-ybl")
b += vehicle(180, 56, 180, "B") + you(120, 176, tag='l')
b += text(42, 26, "Night", "sv-cap") + text(218, 42, "High beam", "sv-cap", "start")
add("At night, oncoming car B's headlights are dazzling you. Where should you look?",
    ["Towards the left kerb", "Towards the right kerb", "Straight into B's lights, with your high beam on"], b,
    "If you're dazzled, look towards the left kerb, and slow down or stop if necessary. Don't retaliate with your high beam. (Official question; Handbook para 107)")

# ---------------------------------------------------------------- 24 turning left, pedestrians crossing the side road
u = nxt()
b = bg() + roads(R(-10, 110, W + 20, 60), R(120, -10, 60, 122), fillet(120, 110, -1, -1), fillet(180, 110, 1, -1))
b += line(0, 140, W, 140, "sv-centre") + line(150, 0, 150, 86, "sv-centre")
b += path("M80,125 Q136,125 135,92 L135,14", u)
b += you(62, 125, 90, tag='', signal="left") + _tag(62, 154)
b += ped(141, 96) + ped(163, 92)
b += text(190, 96, "Crossing", "sv-cap", "start") + text(108, 30, "Side road", "sv-cap", "end")
add("You're turning left into a side road. Pedestrians are crossing the side road near the junction. What should you do?",
    ["Wait for them to cross", "Wave them on", "Sound your horn"], b,
    "Give way to pedestrians crossing the road you're turning into. Wait for them to finish crossing; don't wave them on or hurry them with your horn. (Official question)")

json.dump(Q, open('btt/diagrams.json', 'w'), ensure_ascii=False)
print(len(Q), 'BTT diagram questions, uids', 2001, '-', UID[0])
