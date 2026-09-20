# References — the shop as a game

What the build leans on, and where each piece came from. Nothing here is
invented; every line has a source you can open.

## 1. The look: GTA V loading-screen illustration

Stephen Bliss drew the GTA III → V key art and loading screens. The look:

- **cel-shaded** flat colour with hard-edged shadows, no soft gradients
- **thick black ink outlines** around every figure and object
- **oversaturated, cinematic colour**: sunburnt oranges, deep teals, hot pinks
- pulp-poster lighting and 1970s movie-poster composition
- a slight wide-angle lens on the world, characters caught mid-gesture

Sources: [Stephen Bliss, GTA Wiki](https://gta.fandom.com/wiki/Stephen_Bliss) ·
[Neon and Napalm: the art behind GTA V](https://neonandnapalm.blogspot.com/2017/06/the-art-behind-grand-theft-auto-v.html) ·
[stephenbliss.com](https://www.stephenbliss.com/)

Every scene is generated with **GPT Image 2.5** in this style, referencing the
real DOUXDS barbershop set, the casting roster and the live product shots that
already sit in Higgsfield as reference elements (see prompts.md).

## 2. The HUD: what GTA V puts on screen

| Element | Where | Behaviour |
|---|---|---|
| Radar / minimap | bottom-left, rounded square | player arrow at centre, objective marker in yellow, map rotates with view |
| Health bar (green) · armor (blue) · special ability (gold) | stacked under the radar | thin bars, drain/refill |
| Wanted stars | top-right | one to five white stars, flash when active |
| Cash | top-right, green, `$0,000` | counts up with a tick when it changes |
| Mission objective | bottom-centre, white with the key noun in **yellow** | fades in on each new objective |
| Notification | above the radar, small card with icon | slides in, holds, slides out |
| Subtitles | bottom-centre | speaker name in colour, line in white |
| Weapon / choice wheel | centre, radial, slows time | pick by direction |
| Mission passed | full-screen, black band, gold `MISSION PASSED`, stats list | title, then rows tick in one by one |

Sources: [Heads-Up Display, GTA Wiki](https://gta.fandom.com/wiki/Heads-Up_Display) ·
[Radar, GTA Wiki](https://gta.fandom.com/wiki/Radar) ·
[GTA 5 features guide, gtabase](https://www.gtabase.com/articles/grand-theft-auto-v/gta-5-features-guide-gameplay-hud-combat-money)

## 3. The plot shape: a GTA mission

Missions open with a **title card**, an **objective** in the HUD, and a place
to go on the radar. They chain: go there → talk to someone → something happens
→ a choice → a payoff → **MISSION PASSED** with stats. The player is always in
the world, never reading a page about it. That is the whole difference between
this build and a slideshow.

## 4. The shop itself: what the room actually says

From the barbershop-regular culture bank (Drive: `lab/damon/culture-bank/douxds/fed-up-king/barbershop-regular`, 40 torn-down barber posts). The comments under the biggest ones are the room talking:

- "those was the days walk ins was welcomed"
- "And that was $15" · "Back when cuts was 10$" · "$40 dollar cut these days"
- "Against the grain is wild" · "Them clippers hotter than a mfa"
- "head used to be tingling asl on the way back home"
- "Can't pay a mf to use a razor now. Just black spray lol"
- "Now they just draw chalk around your hairline for $50"
- "Nobody talking loud… barber not stopping to talk to anybody… there isn't a barber sitting in their chair eating… is this an episode of the twilight zone?"
- "he hasn't had any side conversations, didn't have to run to the store, go smoke, hadn't picked up the phone, had to grab something to eat, go talk to hustle man about some shoes or a TV, try to Holla at the mom"
- "This is why a lot of us was balding in our 20s"
- "Using a razor on a child under 8 is gambling!"

Shapes the room rewards (formats.md): the **mid-service interrupt bit**, the
**failed-result self-own**, the **transactional flex reveal**, the **POV
caption over a quiet clip**. The game uses all four as beats.

## 5. Real-shop imagery

Pinterest was the intended source for real-shop plates. Every route to it was
blocked from the build environment (scraper over quota, egress policy), so the
plates reference the DOUXDS set elements, which were themselves built from the
brand's own shop photography (`douxds-barbershop`, `set-shop-wall`,
`set-shop-chair`, `set-shop-counter`, `set-shop-mirror`) plus the MANË shelf.
Swap in Pinterest plates as extra `image_references` when they are to hand.
