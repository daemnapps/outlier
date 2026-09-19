# Which models — for the pictures of the world

The player does not care where the pictures came from. These are the
settings that made the barbershop, and what to reach for when a frame is
wrong.

## Stills — one per beat

| | Use |
|---|---|
| **Model** | Nano Banana Pro, or Soul 2.0 when a person is the subject of the frame |
| **Aspect** | 9:16, always. The player is a phone. |
| **Resolution** | 2k. Then downsize to 810×1440 JPEG for the site — nobody will see the difference and the page loads in a second. |
| **Count** | 2 variants per prompt, pick one. |

**The anchor sentence.** Every prompt in a world ends with the same
description of the place, word for word: the floor, the light, the
mirrors, the lens. That sentence is what keeps nine separate generations
looking like one room. It is in the world file's `prompts.md`. Never
shorten it to make the prompt neater.

**People.** First-person POV frames (your own hand on the door, your knees
in the chair) need no consistency because you are never in frame. For the
characters who are — the barber, the regulars — generate their first frame,
then use it as the reference image for every later frame they appear in.
Two different barbers in one shop breaks the world faster than anything.

**Never the product.** No prompt in a portal describes your product. The
player draws the product as a card from your product file, and if you want
a photograph on that card it is a photograph, of the real thing, that you
took.

## When a frame is wrong

- **A person changed between frames** — you generated fresh instead of
  from a reference. Regenerate from the first frame of that person.
- **The room changed** — the anchor sentence was cut or edited. Put it
  back exactly.
- **Text appeared in the picture** — add "no text, no signage, no
  watermark" to the end and regenerate. The player puts the words on.
- **It looks like an ad** — too clean, too lit, too centred. Add "shot on
  35mm film, available light, slightly imperfect framing" and try again.
  The place should look like a phone photo a regular took, not a set.

## Motion

Not needed. The player drifts every still slowly, and the grain is
synthetic. If you want one beat to move — the cape snapping, the towel
steaming — generate a 4-second clip from the still in Supercomputer and
put its file name in the beat's `video` field. Keep it to one or two beats;
a portal that is all video is a film, and people watch films instead of
walking through them.

*(The `video` field is a hook the player reserves and does not yet play —
a plain `<video>` behind the still is the intended implementation. It is
listed here so world files written now stay valid.)*
