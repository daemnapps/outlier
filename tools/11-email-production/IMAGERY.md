# Imagery — the standing rule

**RULED 2026-09-09 (Damon): never generate a product or a person from a text
description. The real thing already exists — use it as the reference.**

> "dude, you're a lunatic, i literally have the flex base model imagery in
> higgsfield and the drive to use as a reference… park this in your workflow /
> MD anytime we are generating imagery in general"

This applies to every lane, not just email: video teardowns, ads, image
boards, email placeholders, anything.

## Where the real assets live

| Source | What is in it | How to reach it |
|---|---|---|
| **Higgsfield reference elements** | The canonical products and the casting roster, each with a written description and a reference frame | `show_reference_elements` on the Higgsfield connector |
| **The product files on Drive** | Per-product source frames, models, clips | `~/Library/CloudStorage/GoogleDrive-${DRIVE_ACCOUNT}/Shared drives/Shared Assets/brands/<brand>/products/<product>/` |
| **The storefront photos** | The live product photography, straight from the store | `brands/<brand>/products/images.json` |

<brand> reference elements on file (2026-09-09): `FLEX-real-CGI` (the canonical
FLEX, off the brand's own CGI turntable — supersedes every earlier FLEX),
`flex-360-true`, `WAR-storefront-LIVE`, `PRIME-storefront-LIVE`,
`CRUSH-storefront-LIVE`, `MIRO-storefront-LIVE`, `CORE-storefront-LIVE`,
`FIELD-real-CGI`, plus a casting roster: Ray, Marcus, Beto, Andre, Kit, Omar,
Tyrese, Javi, Amir, Hal, Brett, Cody, Dev — each with a written brief tying it
to a lane (fed-up-king, glow-up).

## People must look like UGC, never like AI

**RULED 2026-09-09 (Damon), and this outranks every other look note: anything
with a person in it has to read as real UGC — real people doing real things,
shot on an iPhone.** "While it might look like we're dumbing it down,
especially when we show people, it cannot look AI generated at all. Product
imagery is fine."

The register for any frame with a person in it:

- Shot on a phone. Direct on-camera flash, or plain bathroom/kitchen light, or
  daylight through a window. Never a studio rig.
- Framing slightly off: crooked horizon, subject not centred, cropped tight or
  too loose, arm's-length selfie distance.
- Skin as it is — texture, shine, pores, marks. No retouching, no smoothing.
- No bokeh, no rim light, no colour grade, no glow, no "editorial quality".
- Ordinary rooms: a bathroom mirror, a car seat, a kitchen counter, a locker
  room. Clutter in shot is good.
- Mild sensor noise and phone compression. Slight motion blur is fine.

**Never** in a people frame: cinematic lighting, dark moody studio, bronze
accent light, symmetrical composition, glossy skin, perfect focus. Those are
the tells that make it read as AI.

Product-only frames are the exception: clean studio packshots are correct
there, and the storefront photography is the first choice anyway.

## The avatars are cast, not described

**RULED 2026-09-09 (Damon): "when we're describing a man, you need to also
remember we have actual avatars to pull from".** A person in any brief is a
character on the roster, passed as a reference — never a description of a
stranger for the model to invent. The roster is written to the lanes:

| Lane | Who | Reference id |
|---|---|---|
| fed-up-king | Beto, 38, Latino, short black crop, thick moustache, heavy-set trades build, ingrown hairs and razor bumps on the neck and jaw | `75873578-2bae-4ff4-ad30-bcf673405137` |
| glow-up | Andre, 20, mixed-race, large loose curly afro, faint moustache, slim, inflammatory acne with dark marks across both cheeks | `2b96eb18-ad09-4db7-9ddd-54ffd23e896e` |
| glow-up | Kit, 25, Southeast Asian, long dark hair, thin moustache and soul patch, acne and shine on the forehead and cheeks | `5371b9dd-4fb0-4004-a545-1085071cb23c` |

Others on the roster: Ray, Marcus, Omar, Tyrese, Javi, Amir, Hal, Brett, Cody,
Dev. Read the current list with `show_reference_elements` beforeevery run — it
grows.

## The product references

| Product | Reference id |
|---|---|
| FLEX (canonical, off the brand's own turntable) | `0fa7420f-c30b-4197-aeb7-e35643bfcf8a` (`FLEX-real-CGI`) |
| FLEX 360 (seven real frames, handleless pod, domed base) | `8fad5612-d46f-4c19-baec-c3a636f22a4e` (`flex-360-true`) |
| WAR | `797158d0-bb68-4b50-81ed-b345bb523d71` |
| PRIME | `c9e9c9fa-8b4f-40c4-80f9-5103e78da92f` … see `show_reference_elements` |
| CRUSH | `a66c1b39-5ca0-4c7c-94af-41bfa7f554f5`-era `CRUSH-storefront-LIVE` |
| MIRO | `6d51cf59-b519-4377-b460-52157e4cd6a0`-era `MIRO-storefront-LIVE` |

## How a reference is passed

Higgsfield takes the element by id inside the prompt, in triple angle brackets,
with the element also listed on the call:

```
model: nano_banana_2 (or nano_banana_pro)
prompt: "… replace the device with <<<8fad5612-d46f-4c19-baec-c3a636f22a4e>>> — that exact device …"
medias: [{"value": "<media id>", "role": "image_references"}]
```

## The order of preference

1. **A real photograph of the thing** — the storefront image, or a frame from
   the asset bed. A packshot slot needs no generation at all.
2. **A generation with the reference attached** — Higgsfield, with the product
   or character reference element passed in, so the shape, the cap colour, the
   wordmark and the face all stay the brand's own.
3. **A generation from text alone** — only for a scene with no product and no
   named person in it (a cookout, a bathroom counter, weather), and even then
   the brand's `photo_register` from `design-formats/components.json` goes in
   the prompt.

## Never

- Never describe a product in words and let the model invent it. It invents a
  different bottle, a different cap, a different brush, every time.
- Never invent a face for a named customer or a named athlete. The roster
  exists; a person who is not on it is an open fact for a human to close.
- Never ship generated imagery as final art. It is a placeholder for the
  layout until the designer replaces it.
