# Prompts — the shop, drawn like a GTA loading screen

Every frame is made with **GPT Image 2.5** (`gpt_image_2_5`, quality high,
2k) with the brand's own reference elements attached as `image_references`.
That is what keeps the room the same room, the faces the same faces and the
product the real product across every frame. Regenerate for your own shop by
swapping the references; keep the style block word for word.

## The style block (goes at the top of every prompt)

> Grand Theft Auto V loading-screen illustration style: cel-shaded flat colour
> with hard-edged shadows, thick black ink outlines around every figure and
> object, oversaturated cinematic colour, pulp poster lighting, slight
> wide-angle lens. First-person point of view. No text, no HUD, no logos except
> on the real product.

## References (Higgsfield elements, this workspace)

| Ref | Element | What it pins |
|---|---|---|
| room | `douxds-barbershop` | the one room: shelving, mirror left, chair, counter, fluorescent tiles |
| wall | `set-shop-wall` | the product wall, square on |
| chair | `set-shop-chair` | the chair three-quarters on |
| counter | `set-shop-counter` | the counter at waist height, combs in the blue jar |
| mirror | `set-shop-mirror` | the station mirror with the ledge |
| Marcus | `douxds-marcus` | the player. 29, short taper fade, razor bumps on neck and jaw. Only ever seen in a mirror |
| Omar | `douxds-omar` | the barber. 45, bald, goatee, wire-frame glasses |
| Ray | `douxds-ray` | the old head. 61, grey crop, full white beard, heavy-set |
| Tyrese | `douxds-tyrese` | the young one. 18, short cornrows, lanky |
| CRUSH | `CRUSH-storefront-LIVE` | the live tube: black, ribbed shoulder, gold cap |
| shelf | `mane-house-look` | the white-over-cobalt MANË bottles that share the shelf |

## Plates · 16:9 · you pan across these

**p-street** (room) — Standing on the pavement across from a small corner
barbershop on a Saturday morning: brick front, striped pole turning, hand
lettered WALK-INS WELCOME card in the window, a folding chair outside, a car
double parked, the shop interior glowing through the glass. Wide panoramic.

**p-wait** (chair, room, Ray, Tyrese) — Sitting in the waiting chairs. Packed.
Ray two chairs down holding court with a hand raised mid-story, Tyrese slumped
in the next chair scrolling his phone. Wall TV playing a game, tall blue
Barbicide jar of combs and a spray bottle on the counter, clippings on the
floor, a cape over the chair arm.

**p-door** (room) — Looking at the front door from the waiting chairs as a
striking woman in her early thirties walks in holding her seven year old son's
hand, every man in the room a little straighter. Bell above the door mid-swing,
daylight behind her, the wait list clipboard on the wall.

**p-chair** (mirror, Marcus, Omar, CRUSH) — Sitting in the barber chair under a
black cape looking straight into the station mirror. Marcus's own reflection
centre frame, fresh taper in progress; Omar standing at his shoulder with
clippers in hand. On the ledge under the mirror: spray bottle, neck brush, an
open pomade, and the CRUSH tube standing on its cap.

**p-counter** (counter, wall, CRUSH, shelf) — Standing at the counter. Combs
in the blue Barbicide jar front and centre, a folded towel, hair clippings,
the till with a taped CASH ONLY card; the product wall behind with white and
cobalt MANË bottles and black and gold DOUXDS tubes, paper price tags.

## Looks · 9:16 · the close-ups

**l-bell** (room) — Your own hand pushing the shop door open, the brass bell
on its coil above the glass mid-ring, the room beyond.

**l-ray** (Ray, chair) — Ray, from the next chair, mid-story, one finger up,
eyebrows raised, the TV glow on his glasses-less face, cape on his lap.

**l-tyrese** (Tyrese, chair) — Tyrese leaning over to show you his phone: a
photo of a haircut with a chalk-drawn hairline. He is trying not to laugh.

**l-mom** (room) — From your seat: she stands at the counter with her son,
head tilted, asking how long. The boy is looking at the pole.

**l-pump** (chair) — Looking down at your own lap under a black cape as
Omar's foot pumps the chrome hydraulic pedal, the floor dropping away a few
inches, hair clippings on the tiles.

**l-neck** (mirror, Marcus, CRUSH) — Marcus in the mirror, leaning in, two
fingertips on his jawline, razor bumps on the neck and jaw visible, cape on,
strip light above; the CRUSH tube on the ledge below.

**l-jar** (counter) — The blue Barbicide jar filled with combs, close, on the
counter, the room soft behind it, a drop running down the glass.

**l-crush** (counter, Omar, CRUSH) — Omar leaning across the counter holding
the CRUSH tube out toward the camera, large and sharp in the foreground, combs
in the blue jar beside his elbow.

**l-aftershave** (mirror, Marcus, Omar) — In the mirror: Omar's hand slapping
aftershave on to the back of Marcus's neck, Marcus wincing, eyes shut, the
cape still on.

**l-fresh** (mirror, Marcus) — Marcus in the mirror, cape off, fresh fade and
a clean line, chin up, the smallest nod. The station ledge under him.

## Notes

- Ask for the reflection as the subject when the player is in frame; GPT
  Image keeps the POV honest that way.
- If the room drifts, put `room` first in the references and say "the exact
  barbershop in reference image 1" in the prompt.
- Faces stay closest to the roster when the character is named by what is in
  the reference ("the older man from reference image 3") rather than by name.
- Never let the model draw the HUD. The engine draws it, so it can move.
