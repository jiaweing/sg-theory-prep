"""Fact-check corrections for the BTT / FTT cheatsheets (from the independent reviews against the
official answers and handbooks). Runs after viz/gen_sheets.py; every replacement must match exactly once."""
import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
FIX = {
 'btt': [
  ('Already past the line: carry on.', 'Already past the line: continue through the junction.'),
  ('Wrong as "slow down quickly" for a siren, or when you "signal the driver to slow down".',
   'Wrong as "slow down quickly" for a siren, "slowing down" to give way to an emergency vehicle behind (move to the side), or when you "signal the driver to slow down".'),
  ('<span>Keep out Mon–Fri 7:30–9:30 am</span>', '<span>Keep out Mon–Fri 7:30–9:30 am (the test answer). The handbook adds 5–8 pm.</span>'),
  ('<span class="t">Bus lane closed to cars, Monday to Friday</span>', '<span class="t">Bus lane closed to cars, Monday to Friday mornings<i>The handbook also closes it 5–8 pm on weekdays.</i></span>'),
  ('Full-day lane. Saturday: keep out 7:30 am–11 pm.', 'Full-day lane: keep out Mon–Sat 7:30 am–11 pm.'),
  ('<span class="t">Saturday, full-day bus lane (red line)<i>', '<span class="t">Full-day bus lane (red line), Mon–Sat<i>'),
  ('<span class="sc">13 of 14</span><span class="ex">Alcohol and interior lights only ever make things worse. Seat belts reduce injury, not the chance of a collision.</span>',
   '<span class="sc">11 of 14</span><span class="ex">Alcohol and interior lights only ever make things worse. Seat belts reduce injury, not the chance of a collision. Also wrong: road hogging "reduces road accidents", alcohol "will not affect your reaction time".</span>'),
  ('"Driver only", "fine only", "certain speed only" are all wrong.', '"Driver only", "disqualification only", "certain speed only" are all wrong.'),
  ('At the line: check right and left, then go.', 'At the line: check oncoming traffic and traffic from the right and left, then go.'),
  ('<span>Brake firmly; clutch down as the car comes to a stop</span>', '<span>Stop. Brake firmly; clutch down as the car comes to a stop</span>'),
  ('<span class="k">Solid white centre</span><span class="v">No parking either side</span>', '<span class="k">Solid white centre</span><span class="v">No parking either side; cross only when clear and safe</span>'),
  ('<span class="k">Double yellow</span><span class="v">No parking at any time</span>', '<span class="k">Double yellow</span><span class="v">No parking at any time; immediate pick-up or drop-off is OK</span>'),
  ('<span class="n">$1,000</span><span class="t">Phone in hand', '<span class="n">≤ $1,000</span><span class="t">Phone in hand'),
  ('<span>You must not; disobeying is an offence</span>', '<span>You must not; disobeying is an offence. The example is a speed limit: do not exceed 50 km/h.</span>'),
  ('<span class="sc">1 of 43</span>', '<span class="sc">1 of 40</span>'),
 ],
 'ftt': [
  ('<span class="sc none">0 of 29</span><span class="ex">Nearest exception: a wobbly cyclist, "give yourself more time in overtaking".</span>',
   '<span class="sc">1 of 29</span><span class="ex">Right once: already out overtaking, accelerate and overtake as quickly as possible.</span>'),
  ('<span class="ph">Mirrors alone, no head turn</span><span class="sc none">0 of 9</span><span class="ex">Blind spots need a look over your shoulder.</span>',
   '<span class="ph">Mirrors alone, no head turn</span><span class="sc">1 of 10</span><span class="ex">Right for a normal stop: mirrors, signal, then stop. Blind spots always need a look over your shoulder.</span>'),
  ('<span class="ph">"Shorter" / "less than"</span><span class="sc none">0 of 5</span>',
   '<span class="ph">"Shorter" / "less than"</span><span class="sc none">0 of 5</span><span class="ex">Not the same as "lesser than": 3rd-gear engine braking is lesser than 2nd (right twice).</span>'),
  ('<span class="t">Check your mirrors this often, and before every lane change, overtake and turn</span>',
   '<span class="t">Check your mirrors this often, and before moving off, slowing down, stopping, changing lanes, overtaking and turning<i>The answer is "both A and B".</i></span>'),
  ('<span class="k">Look</span><span class="v">Through rear windscreen</span>', '<span class="k">Look</span><span class="v">Rear windscreen and mirrors</span>'),
  ('<span class="ph">Largest number</span><span class="sc">15 of 30</span>', '<span class="ph">Largest number</span><span class="sc">15 of 32</span>'),
  ('<span class="ph">Smallest number</span><span class="sc">10 of 30</span><span class="ex">1 year (probation, re-apply), 12 months, 2× wet, 1.6 mm, 7 pm, 1st/2nd gear for power.</span>',
   '<span class="ph">Smallest number</span><span class="sc">11 of 32</span><span class="ex">1 year (probation, re-apply), 12 months, 2× wet, 1.6 mm, 7 pm, 1st/2nd gear for power, 3 s signal before overtaking (not 5 or 7).</span>'),
  ('<span class="ph">Middle number</span><span class="sc">5 of 30</span><span class="ex">Only: 3 s signal (twice), 16 km/h, 1.5 m, 24 in 24 months.</span>',
   '<span class="ph">Middle number</span><span class="sc">6 of 32</span><span class="ex">Only: 3 s signal (twice), 16 km/h (twice), 1.5 m, 24 in 24 months.</span>'),
  ('<span class="ex">Right for: driving through a bend; amber when already past the stop line.</span>',
   '<span class="ex">Right for: driving through a bend; amber when already past the stop line; missed exit or phone ringing on the expressway: carry on to the next exit.</span>'),
  ('white stick = blind only.</span>', 'white stick = blind only; flashing amber = proceed only when safe.</span>'),
  ('<span class="v">Daily; first in a new car</span>', '<span class="v">Daily; first in an unfamiliar car</span>'),
  ('<span class="v">Prevents neck injury</span>', '<span class="v">Reduces neck injury risk</span>'),
  ('<span>Blue: high beam is on</span>', '<span>Comes on when the high beam is on</span>'),
  ('<span class="k">Parks, public car parks</span>', '<span class="k">Listed parks, public car parks</span>'),
  ('<span class="sc">1 of 13</span><span class="ex">Right only as "not change lanes".</span>', '<span class="sc">2 of 13</span><span class="ex">Right as "not change lanes" (traffic hold-up), and "changing lanes" as when to check your blind spot.</span>'),
  ('"Stay back" / "drop back" / "longer following distance"</span><span class="sc all">9 of 9', '"Stay back" / "drop back" / "longer following distance"</span><span class="sc all">8 of 8'),
  ('"Be prepared to stop" / "stop if necessary"</span><span class="sc">19 of 20', '"Be prepared to stop" / "stop if necessary"</span><span class="sc">17 of 18'),
  ('"Pull over" / "move to the side" / "keep left"</span><span class="sc">24 of 27', '"Pull over" / "move to the side" / "keep left"</span><span class="sc">21 of 24'),
  ('"Slow down" / "reduce speed"</span><span class="sc">48 of 64</span><span class="ex">Misses: oily patch = avoid it;', '"Slow down" / "reduce speed"</span><span class="sc">45 of 59</span><span class="ex">Misses: oily patch = avoid it; "slow down and turn sharply" is wrong;'),
  ('"Stop immediately" / "brake hard" / "step harder"</span><span class="sc none">0 of 21', '"Stop immediately" / "brake hard" / "step harder"</span><span class="sc none">0 of 18'),
  ('Handbrake" as the answer</span><span class="sc none">0 of 11', 'Handbrake" as the answer</span><span class="sc none">0 of 12'),
 ],
}
for t, pairs in FIX.items():
    p = f'{t}/sheet.part.html'; s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, (t, s.count(a), a[:70])
        s = s.replace(a, b)
    open(p, 'w').write(s)
    print(t, 'fact fixes applied:', len(pairs))

# BTT: move the sign-shape grid from "Handbook only" up into "Lights and markings" (the user asked for sign shapes in the sheet).
p = 'btt/sheet.part.html'; s2 = open(p).read()
a0 = s2.index('<p class="sub">Sign shapes</p>'); a1 = s2.index('<p class="sub">Markings</p>', a0)
block = s2[a0:a1]
s2 = s2[:a0] + s2[a1:]
lm = s2.index('<h2>Lights and markings</h2>'); end = s2.index('</section>', lm)
block = block.replace('<p class="sub">Sign shapes</p>', '<p class="sub">Sign shapes (from the handbook, not in the practice questions)</p>')
s2 = s2[:end] + '  ' + block.rstrip() + '\n    ' + s2[end:]
old_sub = 'Every one is in the official questions. Sign shapes are under Handbook only.'
assert s2.count(old_sub) == 1
s2 = s2.replace(old_sub, 'Lights and markings are all in the official questions; sign shapes come from the handbook.')
open(p, 'w').write(s2)
print('btt sign shapes moved')
