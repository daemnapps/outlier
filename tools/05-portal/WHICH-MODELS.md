# Which models — for the pictures of the world

The player does not care where the pictures came from. These are the
settings that made the barbershop, and what to reach for when a frame is
wrong.

## The look

Every frame is drawn like a **GTA V loading screen**: cel-shaded flat
colour with hard-edged shadows, thick black ink outlines, oversaturated
cinematic colour, pulp-poster lighting. It is a look people recognise in
half a second and it is the reason the portal reads as a game and not as a
slideshow of photos. The style block that says it is at the top of
`worlds/barbershop/prompts.md`; it goes at the top of every prompt, word
for word.

## The model

| | Use |
|---|---|
| **Model** | GPT Image 2.5 (`gpt_image_2_5`), quality high, 2k |
| **References** | attached as `image_references`: the room, the people, the real product. This is what keeps one shop one shop |
| **Plates** | 16:9. The wide frames you look around in, one per scene. The player pans a 16:9 plate across a 9:16 phone, so you get three screens of world from one picture |
| **Looks** | 9:16. The close-ups a marker opens: a hand on the door, a face in the mirror, the tube held out |
| **Count** | 1 per prompt. Regenerate the ones that miss, do not pick from four |

**References, not descriptions.** The room is a reference image. Each
character is a reference image. The product is a reference image of the
real thing. Describe them in the prompt by what is in the reference ("the
older man from reference image 3, grey crop, white beard") rather than by
name, and GPT Image 2.5 keeps them the same across every frame. The
barbershop uses the brand's Higgsfield reference elements: the shop set
(`douxds-barbershop`, `set-shop-wall`, `set-shop-chair`, `set-shop-counter`,
`set-shop-mirror`), the casting roster (`douxds-marcus`, `douxds-omar`,
`douxds-ray`, `douxds-tyrese`) and the live product shot
(`CRUSH-storefront-LIVE`). Build the same set for your brand once and every
world after that is cheap.

**The product is real.** The only logo in any frame is on the product,
and the product is drawn from a photograph of the real one. That is the
opposite of the first cut of this tool, which never drew the product; with
a real reference the drawn product is the product.

**The player is never in frame** except as a reflection. First person means
your hands, your knees under the cape, and your face in the mirror. Ask for
"the reflection is the subject" and the model keeps the POV honest.

**No HUD, no text.** The player draws the HUD so it can move. Say "no
text, no HUD" at the end of every prompt. The exceptions are signs that
belong to the place (WALK-INS WELCOME, CASH ONLY): name them and let them
in.

## When a frame is wrong

- **A person drifted** — the reference was missing or named instead of
  described. Put the reference first and describe what is in it.
- **The room drifted** — same fix. Put the room reference first and say
  "the exact barbershop in reference image 1".
- **It came back photoreal** — the style block was cut. Put it back at the
  top, word for word.
- **It drew a HUD or a caption** — add "no text, no HUD" and regenerate.
- **A plate is too tight** — you asked for 9:16. Plates are 16:9 and say
  "wide panoramic composition".

## Cost

Three credits a frame at 2k with references. The barbershop is fifteen
frames: five plates, ten looks. Forty-five credits for the whole world.

## Motion

Not yet. The player pans, bobs and bounces the markers, the sound is
synthesised, and a still drawn like this already reads as a game. A 5s
Kling clip behind a plate is the next step and the `video` field on a
scene is reserved for it.
