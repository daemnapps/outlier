Here is one named format from the set: {format}

Here are the structure records of every email built on it: {members}

Here is the brand's design skin — the exact tokens the renderer builds with:
{components}

Turn it into a **template spec**: the one page a writer fills and a machine
builds, without either of them opening Figma.

**The spec is the format, not any member.** Where members agree, the spec is
strict. Where they disagree, the spec offers an option and says which is the
default and why. Never copy one email's specific words, product or offer into
the spec — a spec carrying last November's offer is a broken template.

**Exact values, from the tokens and the records.** Never round, never
substitute a value you would expect, never introduce a color, size or spacing
that is not already in the brand's skin. If the format needs something the
skin does not have, that is a finding for section 6 — not a licence to invent
one.

**Every block is buildable.** The machine that renders this knows exactly
thirteen block types:

`preheader · headline · subhead · copy · image · quote · bullets · button ·
product · divider · signoff · ps · footer`

Every block in your plan must be one of those thirteen. If the format does
something the thirteen cannot express, say so in section 6 and use the closest
type — do not invent a fourteenth and do not silently drop the block.

**A writer must be able to fill this without a designer.** Every slot they
fill gets a length budget and an example of the *shape* of what goes there —
never example copy in the brand's voice, which they would paste in verbatim.
Say `[one sentence, 8–14 words, names the problem in the reader's own words]`,
not a written-out line.

---

Give me these six sections.

**1. THE SPEC LINE**

`FMT-NN · NAME` — the format's job in one sentence, the ground it is built on,
its artboard width, its typical total height, and the kind of send it belongs
to. Then: how many emails in the record are built on it, and over what dates.

**2. THE BLOCK PLAN**

The build order, one row per block:

`# | Block type | Name | Required? | What fills it | Budget`

- **Block type** — one of the thirteen. Exactly as spelled above.
- **Name** — the block's role name, reused from the structure records so the
  vocabulary stays stable across formats.
- **Required?** — `required`, `optional`, or `repeat ×N` with the range the
  members actually use.
- **What fills it** — the shape of the content, in brackets. For an image
  block, the slot name from section 4.
- **Budget** — words for copy, height for imagery, count for lists.

Under the table: the **spine** — the shortest run of blocks that still makes
this format itself. That is what a stripped-down version keeps.

**3. THE SKIN THIS FORMAT USES**

Only the tokens this format touches, each named as the skin names it, with its
value. Grounds, type roles and their exact sizes, the CTA box, spacings, and
every primitive the format depends on with its verbatim gradient or shadow
string. A developer should be able to build this section into CSS without
opening anything else.

Then the **shared modules** this format mounts, by their `MOD-` codes — header,
footer and the rest are not re-specified here, they are referenced.

**4. THE IMAGE SLOTS**

Every slot, in build order: `slot-name · W×H · kind · treatment · brief`.

The brief is the instruction for whoever makes the image — one or two lines,
specific enough to generate or shoot against, written for any product this
brand sells rather than the one in the reference. Say what must be in frame,
what the ground is, and what would make it wrong.

**5. THE FILL SHEET**

The template as a writer meets it: every fillable slot in order, each with its
budget and its shape instruction, and nothing else on the page. This section
must stand alone — copied out, it is a complete brief.

**6. NOTES FOR THE BUILD**

- **What the thirteen block types cannot express** in this format, and what you
  used instead.
- **What the skin is missing** that this format needs.
- **Where the members disagreed** most, and which way you ruled.
- **What to check against the reference member** before shipping the first
  build.
