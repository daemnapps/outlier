Take this EMAIL DESIGN and break it down completely so I can rebuild it.

Structure read from the design file: {design_context}

Picture of the same frame: {frame_image}

An email is a single vertical scroll, not a page and not a video. There is no
timeline and no fold — there is an order, and the order is the argument. Break
down every block, top to bottom, in the order a reader meets it. Go deep. A
long, heavily detailed record is what I want — do not compress or summarize.

You are building a reproduction spec: a developer who has never seen this
email must be able to rebuild it in HTML — every block, every measurement,
every color, every word, every image and what belongs in it — from your record
alone.

**Describe the email in front of you, not a default.** Every example in this
prompt is illustrative only — a width, a color, a block name, a type size —
and none of them describe the email you are looking at. Never carry over the
framing of a previous read. Never reach for what emails in this category
usually do. A record that describes a different email is worthless no matter
how detailed it is.

**The file is the source of truth, and you have it.** Geometry, color, type
and spacing come from the structure read, verbatim. Never round to a grid,
never snap to a round number, never substitute a value you would expect. If
the file says 61.5, you write 61.5. The picture is for reading the words, the
imagery and the order — not for measuring.

**This is observation, not evaluation.** Record what is demonstrably there.
Not whether it is good. Not what you would change. Section 5 is the only place
mechanism belongs, and even there you are describing how the layout works, not
scoring it.

Three laws govern everything:

**Accuracy law.** Never guess. If a value is missing from the structure read
and not legible in the picture, write `[UNCLEAR: <what>]`. Mark anything
inferred rather than read with `(inferred)`. Typeface names are inferences
unless the file names them — take the name from the file when it is there,
including trial and test aliases, exactly as written.

**Consistency law.** Every block gets ONE name, used identically everywhere.
Name it for what it does — `hero product`, `proof grid`, `closing CTA` — never
for its content. Every detail cited anywhere must already exist in section 2.

**Slot law.** Every image is a slot with a name, a size and a brief. An image
is never described as "a photo" — it is `[SLOT: hero-product · 600×760 ·
product cutout on transparent ground, single bottle, front three-quarter]`.
Slots are what the next brand fills. A slot without a size is not a slot.

---

Give me these six sections.

**1. THE FORMAT LINE**

One line: what kind of email this is, its artboard width, its total height,
its ground (light / dark / deep / other, with the exact color), and whether it
is type-led or image-led. Nothing else.

**2. THE BLOCK LEDGER**

The core section. Every block top to bottom, in reading order, one row each:

`# | Block name | Function | What is in it | Height | Fixed or flexes?`

- **Function** — what the block does to the reader, in one clause. "Names the
  problem in the reader's words." "Puts a face on the claim."
- **What is in it** — the copy verbatim inside quotes, the slot reference for
  imagery, or both. Never paraphrase copy. Ever.
- **Height** — the block's height from the file.
- **Fixed or flexes** — whether the block's height is set by its content or by
  the design. A CTA band is fixed. A copy block flexes.

Then, under the table, the **scroll depth**: total height, and the percentage
depth at which each CTA lands.

**3. THE DESIGN SYSTEM THIS EMAIL USES**

Exact values only, from the file:

- **Grounds** — every background color used, as it appears in the file.
- **Type** — every family (as the file names it), and for each: the sizes,
  weights, line heights, letter spacing and casing actually used here. Say
  which family carries display and which carries body.
- **CTA** — the button's exact box: width, height, radius, fill, label
  treatment. How many times it repeats and at what depths.
- **Primitives** — the recurring design objects this email uses, each with its
  exact spec: glows, glass cards, dividers, chips, rating rows, confetti,
  masks, whatever is actually here. Give the gradient or shadow string
  verbatim. If a primitive is absent, do not list it.

**4. THE IMAGE SLOTS**

Every slot, numbered, with: name, exact rendered size, what kind of image it
is (product cutout / customer photo / lifestyle / texture / logo / screenshot
/ other), how it is treated (mask, radius, crop, scrim), and a one-line brief
for what a replacement must show. Flag any slot whose image is missing from
the file as `[MISSING IN FILE]` — that is a real finding, not an error.

**5. HOW THE LAYOUT ARGUES**

Now mechanism. Not copy quality — layout mechanism.

- **What reads first** and why the design makes it read first.
- **The order of the argument** — the blocks re-stated as the case being
  made, in sequence.
- **Where the weight sits** — which block gets the most height, the biggest
  type, the strongest contrast, and what that prioritises.
- **What the scroll costs** — how far a reader travels before each CTA, and
  what is being asked of them at that depth.
- **Who this is designed for** — read only from what is in frame: the register
  of the copy, who is pictured, what is assumed known. If the email does not
  support a call, say so.

**6. THE SIGNATURE**

One line built for matching, in this exact form, so stage 2 can group this
email against every other:

`<ground>/<display-or-image-led>/<length band>/<primitives present> — <block
skeleton in 5–8 words>`

Length bands: short under 2,000px, mid 2,000–3,500px, tall above 3,500px.

Then the honest note: **what in this email is one-off** — built for this send
and not part of any reusable format — and **what is clearly the house
pattern**. One sentence each.
