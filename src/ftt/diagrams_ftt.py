"""Generate diagram scenario questions for the Final Theory Test (car), using the shared helpers in diagrams.py.
Run from the rtt folder:  python3 -I ftt/diagrams_ftt.py
Output: ftt/diagrams.json -> list of [question, options, answerIndex, svg, explanation]
Every rule comes from an official FTT question (ftt/qa.txt) or the Final Theory of Driving handbook (ftt/handbook.txt).
"You" is the yellow car ("youcar"). Singapore drives on the LEFT. Marker / clip ids use uids 3000+.
"""
import json, math, os, runpy
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
G = runpy.run_path('diagrams.py')            # (also regenerates form/diagrams.json, unchanged)
svg, rect, line, text, path, circle, vehicle, bg, roads, R, P, S, fillet = (G[k] for k in
    'svg rect line text path circle vehicle bg roads R P S fillet'.split())
tagbox, badge, dim, ped, painted_arrow, _tag, _q, left_of = (G[k] for k in 'tagbox badge dim ped painted_arrow _tag _q left_of'.split())
cross, roundabout, lanes_north, lane_x, bend_scene = (G[k] for k in 'cross roundabout lanes_north lane_x bend_scene'.split())
W, H = 300, 220
REFERS = ('both', 'above', 'all the', 'a and b', 'a & b')   # the app keeps option order fixed if one of these appears

Q = []
def add(q, opts, body, expl, uid, h=H):
    """opts[0] is the correct answer; it is moved to a varying position so the key isn't always A."""
    assert len(opts) == 3 and not any(r in o.lower() for o in opts for r in REFERS), opts
    pos = (len(Q) * 2 + 1) % 3
    o = opts[1:]; o.insert(pos, opts[0])
    Q.append([q, o, pos, svg(body, uid, W, h), expl])

def cyclist(x, y, hd, arm=None, scale=1.35):
    """Bicycle and rider from above (rider in the pedestrian blue). arm='right' draws a right-turn arm signal."""
    g = f'<g transform="translate({x:.1f},{y:.1f}) rotate({hd:.1f}) scale({scale})">'
    g += rect(-1.3, -13, 2.6, 9, "sv-tyre", 1.3) + rect(-1.3, 4, 2.6, 9, "sv-tyre", 1.3)
    if arm == 'right':
        g += rect(3, -1.2, 9, 2.6, "sv-ped", 1.3)
    g += f'<ellipse cx="0" cy="0.5" rx="5.6" ry="3.2" class="sv-ped"/>' + circle(0, 0.3, 2.5, "sv-helmet")
    return g + '</g>'

def blinkers(x, y, hw=8, hl=15):
    """Hazard lights on a north-facing car (all four corners)."""
    return ''.join(circle(x + sx * hw, y + sy * (hl - 2), 2.3, "sv-blink") for sx in (-1, 1) for sy in (-1, 1))

u = 3000
# 1. uncontrolled crossroads: straight vs straight from the right
u += 1; b = cross(u, stop=False)
b += path("M232,125 L16,125", u, "sv-path2") + path("M135,162 L135,14", u)
b += vehicle(135, 182, 0, kind="youcar", tag='b') + vehicle(250, 125, 270, "A")
add("No traffic lights or signs at this crossroads. You're going straight; car A is going straight from your right. Who goes first?",
    ["Car A: you give way to it", "You: car A must give way to you", "Whoever reaches the junction first"], b,
    "At an uncontrolled crossroads, give way to vehicles from the right. (Handbook 131a)", u)

# 2. uncontrolled: you turn right, oncoming car straight
u += 1; b = cross(u, stop=False)
b += path("M165,58 L165,206", u, "sv-path2") + path("M135,162 L135,120 Q136,95 166,95 L284,95", u)
b += vehicle(135, 182, 0, kind="youcar", tag='b') + vehicle(165, 40, 180, "C")
add("No traffic lights or signs. You're turning right; oncoming car C is going straight. What do you do?",
    ["Slow down or stop and give way to car C", "Turn first: car C must wait for you", "Turn quickly before car C reaches the junction"], b,
    "Turning vehicles give way to vehicles going straight, and before turning right you slow down or stop to give way to oncoming vehicles. (Handbook 131b; Official question)", u)

# 3. roundabout entry
u += 1; b = roundabout(u, flows=(185, 285))
b += vehicle(135, 197, 0, kind="youcar", tag='l')
b += vehicle(194, 131, 210, "E") + path("M184,146 A53,53 0 0 1 150,158", u, "sv-path2")
add("You're about to enter the roundabout. Car E is already in it, coming round from your right. What do you do?",
    ["Give way to car E", "Enter first: car E must give way to you", "Sound your horn and enter"], b,
    "When entering a roundabout, give way to traffic on your right in the roundabout. Traffic goes round clockwise. (Handbook 133a)", u)

# 4. roundabout: cyclist signalling right ahead of you
u += 1; b = roundabout(u, flows=(0,))
def ring(a, r=49):
    t = math.radians(a)
    return 150 + r * math.cos(t), 105 + r * math.sin(t), (math.degrees(math.atan2(-math.sin(t), -math.cos(t))) % 360)
yx, yy, yh = ring(100); cx_, cy_, ch = ring(172)
b += f'<path d="M{150 + 49 * math.cos(math.radians(186)):.1f},{105 + 49 * math.sin(math.radians(186)):.1f} A49,49 0 0 1 {150 + 49 * math.cos(math.radians(228)):.1f},{105 + 49 * math.sin(math.radians(228)):.1f}" class="sv-path2" marker-end="url(#ah{u}b)"/>'
b += vehicle(yx, yy, yh, kind="youcar") + cyclist(cx_, cy_, ch, arm='right')
b += _tag(yx + 2, yy + 30) + badge(cx_ - 20, cy_ + 8, "C", r=7)
add("You're following cyclist C round the roundabout. C is signalling to turn right. What do you do?",
    ["Give the cyclist plenty of room", "Overtake the cyclist on the right", "Give a horn warning"], b,
    "Give a cyclist signalling at a roundabout plenty of room: they may change direction at any moment. (Official question; Handbook 244)", u)

# 5. turning right at lights, view blocked by an oncoming right-turner
u += 1; b = cross(u, lights="green")
b += vehicle(139, 122, 0, kind="youcar", tag='l')
b += vehicle(162, 86, 180, None, kind="lorry", signal="right") + text(165, 34, "?", "sv-q")
b += text(240, 42, "Oncoming lorry", "sv-cap") + text(240, 55, "also turning right", "sv-cap")
add("The light is green (no arrow). You've moved up to turn right, but an oncoming lorry waiting to turn right blocks your view. What do you do?",
    ["Wait until you can see it's safe, or for the green arrow", "Edge out and turn: you have a green light", "Sound your horn and turn"], b,
    "Turning right at lights: move slowly towards the centre of the junction, give way to oncoming vehicles, and wait until it is safe to cross or for the green arrow signal to appear. You can't judge it safe with your view blocked. (Handbook 113, turning right)", u)

# 6. yellow box, road ahead congested
u += 1; b = cross(u, lights="green", yellow=True)
b += path("M135,162 L135,86", u)
b += vehicle(135, 182, 0, kind="youcar", tag='r') + vehicle(135, 56, 0, None) + vehicle(135, 22, 0, None) + vehicle(135, -12, 0, None)
add("The light is green and you're going straight, but traffic beyond the yellow box is backed up. What do you do?",
    ["Wait behind the stop line until the road ahead clears", "Go: the light is in your favour", "Move into the box and wait there"], b,
    "When the road ahead is congested, never proceed even if the light is in your favour, whether or not there is a yellow box. (Handbook 120)", u)

# 7. long vehicle signals left, swings right
u += 1
b = bg() + roads(R(-10, 20, W + 20, 60), R(120, 80, 60, H), fillet(120, 80, -1, 1), fillet(180, 80, 1, 1))
b += line(0, 50, W, 50, "sv-centre") + line(150, H, 150, 92, "sv-centre") + line(121.5, 91, 150, 91, "sv-stop")
b += path("M150,102 Q146,66 108,65 L18,65", u, "sv-path2")
b += vehicle(153, 130, 8, None, kind="lorry", signal="left")
b += vehicle(135, 196, 0, kind="youcar", tag='l')
b += text(192, 126, "Signalling left,", "sv-cap", "start") + text(192, 139, "moved out right", "sv-cap", "start")
add("You're following a long vehicle. It signals left but moves out to the right. What do you do?",
    ["Stay well back and give it more room", "Get closer so you can pass it quickly", "Pass it on the left as it moves out"], b,
    "Long vehicles may move right before turning left. Stay well back, and don't try to pass on the side it's turning into. (Official question; Handbook 259)", u)

# 8. narrow course, left turn: where to position
u += 1
b = bg() + roads(R(130, 40, 60, 200), R(-10, 40, 200, 50), fillet(130, 90, -1, 1, 7))
b += path("M160,128 Q160,66 114,65 L24,65", u, "sv-path2")
for i, xx in enumerate((141, 160, 179)):
    b += badge(xx, 152, str(i + 1), r=7.5)
b += vehicle(160, 198, 0, kind="youcar", tag='r')
b += text(60, 120, "Narrow course", "sv-cap")
add("You're about to turn left in a narrow course. Where should you position your car before the turn?",
    ["3, more to the right", "1, more to the left", "2, in the centre of the course"], b,
    "On a left turn the rear left wheel cuts closer to the kerb than the front, so position more to the right before turning. (Official question; Handbook 161–162)", u)

# 9. overtaking on the left: car ahead signalling right
u += 1
b = bg() + roads(R(70, -10, 160, H + 20), R(220, 36, 100, 56), fillet(230, 36, 1, -1), fillet(230, 92, 1, 1))
b += line(150, 0, 150, 30, "sv-centre") + line(150, 100, 150, H, "sv-centre") + line(232, 64, 300, 64, "sv-centre")
b += path("M139,62 Q140,50 162,50 L284,50", u, "sv-path2") + path("M100,160 L100,22", u)
b += vehicle(138, 80, 0, "A", signal="right") + vehicle(100, 180, 0, kind="youcar", tag='b')
add("Car A ahead has stopped, signalling right to turn into the side road. May you pass it on the left?",
    ["Yes, when it's safe: A is signalling to turn right", "No, you may never pass on the left", "Only if A is a heavy vehicle"], b,
    "You may overtake on the left if the driver in front signals the intention to turn right. (Official question)", u)

# 10. returning to the left lane after overtaking
u += 1; b = lanes_north(u, 2, labels=False, centre=1)
xl, xr = lane_x(2, 0), lane_x(2, 1)
b += vehicle(xl, 150, 0, "B") + path(f"M{xr},140 L{xr},18", u)
for k, (py) in {"1": 124, "2": 88, "3": 46}.items():
    b += line(xr, py, 222, py, "sv-leader") + circle(xr, py, 2.6, "sv-dot") + badge(230, py, k, r=8.5)
b += vehicle(xr, 166, 0, kind="youcar", tag='b')
add("You're overtaking car B. At which point should you start to move back to the left?",
    ["3: when you can see B in your interior rear-view mirror", "1: as soon as you're ahead of B", "2: when you can see B in your left wing mirror"], b,
    "Keep left after overtaking only when you can see the overtaken vehicle in your rear-view mirror inside the cabin. Signal before you move back. (Official question; Handbook 137j–k)", u)

# 11. joining the expressway
u += 1
b = bg() + roads(R(128, -10, 132, H + 20), P(f"M84,{H + 10} L84,128 Q84,78 128,34 L128,{H + 10} Z"))
b += line(172, 0, 172, H, "sv-lane") + line(216, 0, 216, H, "sv-lane") + line(128, 50, 128, H, "sv-merge") + line(128, 0, 128, 34, "sv-edge")
b += path("M106,158 Q108,100 146,62", u) + path("M150,128 L150,74", u, "sv-path2")
b += vehicle(106, 176, 0, kind="youcar", tag='l') + vehicle(150, 146, 0, "A") + vehicle(194, 80, 0, None)
b += text(72, 132, "Acceleration", "sv-cap", "end") + text(72, 145, "lane", "sv-cap", "end")
add("You're in the acceleration lane, joining the expressway. Car A is in the left lane. What do you do?",
    ["Build up speed, give way to A and merge smoothly", "Stop at the end of the acceleration lane and wait", "Merge now: A must make way for joining traffic"], b,
    "Build up your speed to that of expressway traffic and merge smoothly, giving way to traffic already on the expressway. Don't stop at the end of the acceleration lane. (Official questions; Handbook 262)", u)

# 12. leaving the expressway
u += 1
b = bg() + roads(R(128, -10, 132, H + 20), P("M128,-10 L84,-10 L84,64 Q84,108 128,150 Z"))
b += line(172, 0, 172, H, "sv-lane") + line(216, 0, 216, H, "sv-lane") + line(128, 150, 128, H, "sv-edge") + line(128, -10, 128, 132, "sv-merge")
for i, xx in enumerate((150, 194, 238)):
    b += tagbox(xx, 196, "XYZ"[i])
b += vehicle(238, 150, 0, kind="youcar", tag='') + _tag(238, 116) + vehicle(194, 60, 0, None)
b += text(72, 40, "Exit", "sv-cap", "end") + path("M106,60 L106,18", u, "sv-path2")
add("You want to take the exit ahead, on the left. You're in lane Z. What do you do?",
    ["Signal left and move into lane X well before the exit", "Stay in lane Z and cut across at the exit", "Drive along the road shoulder to the exit"], b,
    "Plan your exit early: signal left and move into the left lane well before the exit. If you miss it, carry on to the next exit. (Official question; Handbook 270)", u)

# 13. breakdown on the expressway: where the warning triangle goes
u += 1
b = bg() + roads(R(40, -10, 206, H + 20))
b += rect(40, 0, 50, H, "sv-shoulder") + line(90, 0, 90, H, "sv-edge") + line(142, 0, 142, H, "sv-lane") + line(194, 0, 194, H, "sv-lane")
b += f'<text x="20" y="150" text-anchor="middle" class="sv-cap" transform="rotate(-90 20 150)">Shoulder</text>'
b += blinkers(58, 50) + vehicle(58, 50, 0, kind="youcar", tag='') + _tag(58, 18)
b += badge(80, 50, "1", r=7.5) + badge(64, 98, "2", r=7.5) + badge(64, 196, "3", r=7.5)
b += path("M116,190 L116,140", u, "sv-path2") + vehicle(116, 200, 0, None) + vehicle(168, 120, 0, None)
add("Your car has broken down on the expressway and you've moved it onto the road shoulder. Where do you place the red warning triangle?",
    ["3: 20 metres or more behind your car", "2: a few metres behind your car", "1: beside your car"], b,
    "Switch on your hazard lights, get onto the road shoulder and place the breakdown triangle 20 metres or more behind the vehicle. Passengers stand behind the guardrail. (Official question; Handbook 271)", u)

# 14. three-lane carriageway, clear road
u += 1; b = lanes_north(u, 3, labels=False)
b += vehicle(lane_x(3, 1), 160, 0, kind="youcar", tag='b')
for i in range(3):
    b += tagbox(lane_x(3, i), 18, "XYZ"[i])
b += text(36, 112, "80 km/h", "sv-cap") + text(36, 125, "no traffic", "sv-cap")
add("You're driving at 80 km/h on a three-lane carriageway and there's no traffic ahead. Which lane should you use?",
    ["X, the left lane", "Y, the middle lane", "Any lane"], b,
    "Keep to the left lane when the road ahead is clear. The right-most lane is for overtaking (and turning right); don't hog the centre lane. (Official question; Handbook 108, 265–266)", u)

# 15. parking facing uphill
u += 1; b = bg()
for i, st in enumerate((-30, 0, 30)):
    x0 = 10 + i * 96
    b += roads(R(x0 + 6, 36, 78, H))
    b += vehicle(x0 + 26, 108, 0, kind="youcar", scale=1.6, steer=st)
    b += path(f"M{x0 + 66},160 L{x0 + 66},70", u, "sv-path2") + badge(x0 + 26, 170, str(i + 1), r=8.5)
b += text(150, 22, "Facing uphill, kerb on your left", "sv-cap")
add("You're parking facing uphill, next to the kerb on your left. Which front-wheel position is correct?",
    ["3: turned out, away from the kerb", "1: turned in, towards the kerb", "2: straight ahead"], b,
    "Facing uphill, turn the front wheels outward so that if the car rolls back, the kerb stops it. Pull the handbrake fully up and engage 1st gear. Facing downhill: wheels inward and reverse gear. (Handbook 209)", u)

# 16. rear skid
u += 1
b = bg() + roads(R(40, -10, 140, H + 20)) + line(110, 0, 110, H, "sv-leader")
b += vehicle(110, 104, -22, kind="youcar", scale=1.7, steer=0)
b += path("M136,150 L176,150", u, "sv-pathd") + text(186, 153.5, "Rear slides", "sv-capd", "start") + text(186, 166.5, "to the right", "sv-capd", "start")
b += text(186, 40, "Wet road", "sv-cap", "start")
add("The rear of your car starts to skid to the right. Which way do you steer?",
    ["To the right, the way the rear is sliding, foot off the accelerator", "To the left, away from the skid", "Keep straight and brake hard"], b,
    "If the rear skids sideways, take your foot off the accelerator at once, don't brake during the correction, and steer in the direction of the skid. (Handbook 195)", u)

# 17. bend: where to slow down
u += 1
d = "M70,232 L70,128 Q70,62 136,62 L312,62"
b = bend_scene(d, "Sharp bend")
x, y, hd = _q((70, 128), (70, 62), (136, 62), .5); bx, by = left_of(x, y, hd)
for k, (px, py) in {"1": (55, 150), "2": (bx, by), "3": (236, 77)}.items():
    b += badge(px, py, k, r=8.5)
b += vehicle(55, 196, 0, kind="youcar", tag='r')
add("You're approaching this sharp bend. Where should you slow down?",
    ["1: before you enter the bend", "2: as you drive round the bend", "3: as you leave the bend"], b,
    "Slow down (and change down) before you enter a bend, keep a steady speed through it, and accelerate as the wheel straightens. (Official question)", u)

# 18. blind spot before changing lanes
u += 1; b = lanes_north(u, 2, labels=False)
b += rect(152, 112, 40, 64, "sv-zone", 6)
b += path(f"M{xl},82 C{xl},58 {xr},62 {xr},34", u)
b += vehicle(xl, 100, 0, kind="youcar", tag='l') + vehicle(xr, 148, 0, "M", kind="bike")
b += text(214, 140, "Blind", "sv-cap", "start") + text(214, 153, "spot", "sv-cap", "start")
add("You want to move into the right lane. Motorcyclist M is in your blind spot. How do you check for M?",
    ["Look over your right shoulder", "Look in the rear-view mirror", "Look in the right side mirror"], b,
    "Neither mirror covers the blind spot. Before changing lanes, turn your head and look over your shoulder. (Official question)", u)

# 19. following distance on a wet road
u += 1; h = 150
b = bg(W, h) + roads(R(-10, 62, 320, 60))
b += line(0, 92, W, 92, "sv-centre")
b += vehicle(66, 77, 90, kind="youcar", tag='l') + vehicle(208, 77, 90, "A") + path("M228,77 L276,77", u, "sv-path2")
b += rect(184, 44, 4, 16, "sv-pole", 2) + circle(186, 44, 5, "sv-post") + line(186, 62, 186, 92, "sv-leader")
b += '<path d="M82,34 H186 M82,29 V39" class="sv-dim"/>' + text(134, 25, "?", "sv-cap")
b += text(198, 47.5, "Fixed point", "sv-cap", "start") + text(150, 140, "Wet road", "sv-cap")
add("The road is wet. Car A has just passed the post. How long should it take you to reach the post?",
    ["More than 2 seconds", "Exactly 2 seconds", "Less than 2 seconds"], b,
    "The two-second rule is for good conditions. On a wet road stopping distance is about twice as long, so keep more than 2 seconds behind. (Official questions)", u, h)

# 20. dazzle at night
u += 1; b = lanes_north(u, 2, labels=False, centre=1)
b += '<polygon points="164,74 180,74 206,186 132,186" class="sv-beam"/>'
b += vehicle(xr, 58, 180, "O") + vehicle(xl, 176, 0, kind="youcar", tag='l')
b += text(96, 34, "Night:", "sv-cap", "end") + text(96, 47, "O on high", "sv-cap", "end") + text(96, 60, "beam", "sv-cap", "end")
add("At night, oncoming car O won't dip its headlights and the glare is dazzling you. What do you do?",
    ["Slow down and look towards the left kerb", "Switch on your high beam in return", "Keep your speed and headlights as they are"], b,
    "Look to the left, using the edge of the road to guide you, and slow down. If the glare is blinding, stop by the side of the road. (Official question; Handbook 188)", u)

# 21. pedestrian walking with their back to you, no pavement
u += 1
b = bg() + roads(R(84, -10, 132, H + 20)) + line(150, 0, 150, H, "sv-centre")
b += ped(96, 86) + path("M96,70 L96,42", u, "sv-path2") + tagbox(68, 86, "P")
b += path("M124,150 L124,30", u) + vehicle(124, 170, 0, kind="youcar", tag='r')
b += '<path d="M101,108 H116 M101,104 V112 M116,104 V112" class="sv-dim"/>' + text(108.5, 124, "?", "sv-cap2")
b += text(42, 196, "No pavement", "sv-cap")
add("Pedestrian P is walking along a road with no pavement, with their back to you. What gap should you leave as you pass?",
    ["At least 1.5 metres", "At least 1 metre", "At least 0.5 metre"], b,
    "Keep at least 1.5 m from pedestrians with their back to traffic, and at least 1 m from those facing you. (Official questions; Handbook 241–242)", u)

# 22. ball from between parked cars
u += 1
b = bg() + roads(R(78, -10, 154, H + 20)) + line(170, 0, 170, H, "sv-centre")
for yy in (22, 70, 118):
    b += vehicle(92, yy, 0, None)
b += circle(116, 95, 4.2, "sv-post") + path("M98,95 L108,95", u, "sv-path2")
b += text(117, 84, "Ball", "sv-cap")
b += path("M134,170 L134,24", u) + vehicle(134, 188, 0, kind="youcar", tag='r')
b += text(40, 56, "Parked", "sv-cap") + text(40, 69, "cars", "sv-cap")
add("Driving past a line of parked cars, you see a ball bounce into the road ahead. What do you do?",
    ["Slow down and be prepared to stop for children", "Keep your speed and sound your horn", "Speed up to pass the ball quickly"], b,
    "A child may run out after the ball. Slow down and be ready to stop. (Official question; Handbook 228)", u)

# 23. turning left with a cyclist ahead on the left
u += 1
b = bg() + roads(R(120, -10, 60, H + 20), R(-10, 40, 140, 50), fillet(120, 40, -1, -1), fillet(120, 90, -1, 1))
b += line(150, 0, 150, 30, "sv-centre") + line(150, 100, 150, H, "sv-centre") + line(0, 65, 108, 65, "sv-centre")
b += path("M130,106 L130,16", u, "sv-path2") + cyclist(130, 132, 0) + badge(108, 132, "C", r=7)
b += path("M142,166 L142,108 Q142,78 108,78 L18,78", u)
b += vehicle(142, 186, 0, kind="youcar", signal="left", tag='r')
add("You're turning left into the side road. Cyclist C is ahead of you on the left, going straight on. What do you do?",
    ["Slow down and let C pass the junction first", "Speed up and turn before C reaches the junction", "Sound your horn to warn C you're turning"], b,
    "Slow down and allow the cyclist to pass the junction first. Never overtake a cyclist just before you turn left. (Official questions; Handbook 245)", u)

# 24. road works on your side, oncoming car
u += 1
b = lanes_north(u, 2, labels=False, centre=1)
b += rect(xl - 18, 66, 36, 44, "sv-works", 4) + text(xl, 91.5, "Works", "sv-workstxt")
b += path(f"M{xr},66 L{xr},206", u, "sv-path2")
b += vehicle(xl, 168, 0, kind="youcar", tag='l') + vehicle(xr, 48, 180, "O")
add("Road works block your side of a two-way road, and car O is coming the other way. What do you do?",
    ["Give way to car O, then pass the works", "Go first: you got to the works first", "Flash your headlights and go"], b,
    "If the obstruction is on your side, give way to oncoming vehicles before passing. Slow down so you can stop about one vehicle length from it. (Handbook 223–224)", u)

# 25. emergency vehicle behind on a one-way street
u += 1; b = lanes_north(u, 3, labels=False)
for i in range(3):
    b += painted_arrow(lane_x(3, i), 40, "straight")
b += vehicle(150, 112, 0, kind="youcar", tag='r')
b += vehicle(150, 186, 0, None, kind="ambulance")
b += text(52, 112, "One-way", "sv-cap") + text(52, 125, "street", "sv-cap")
b += text(248, 182, "Ambulance,", "sv-cap") + text(248, 195, "siren on", "sv-cap")
add("You're on a one-way street. An ambulance with its siren on comes up behind you. What do you do?",
    ["Give way by moving to the left or right", "Give way by moving to the left only", "Stop immediately where you are"], b,
    "On a one-way street you can give way to an emergency vehicle by moving to either side; slow down or stop if necessary. (Official question; Handbook 255)", u)

json.dump(Q, open('ftt/diagrams.json', 'w'), ensure_ascii=False)
print(len(Q), 'FTT diagram questions')
