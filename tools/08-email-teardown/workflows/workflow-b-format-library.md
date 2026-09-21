# Workflow B — Format Library

Dedupe the bank into the small set of layouts the brand actually reuses, then
spec each one so it can be built. Run after A and C.

---

## 1. Group by skeleton

Feed every structure record plus the census into
`prompts/stage2-format-dedupe-v1-damon.md`.

The one rule that decides everything: **group by layout skeleton, never by
topic.** A Black Friday email and a welcome email with the same block order
are one format. The campaign is not a property of the layout.

Do not aim for a number. The <brand> run landed on eight plus four candidates;
that is an observation about <brand>, not a target for the next brand.

## 2. Keep the orphans visible

Emails that fit nothing stay on the orphan list with a reason each. A long
orphan list is a real finding about how disciplined the brand's design is —
burying it to make the set look tidy destroys the only honest measure of that.

## 3. Spec each format

One pass of `prompts/stage3-format-spec-v1-damon.md` per format, most-used
first. Output goes to the brand, not here:
`brands/<brand>/email/design-formats/formats.md`.

The spec must satisfy the renderer's thirteen block types — `preheader ·
headline · subhead · copy · image · quote · bullets · button · product ·
divider · signoff · ps · footer`. A block plan that invents a fourteenth
cannot be built by `email-production/render_email.py`, which is the machine
that turns a filled spec into a real email.

## 4. Pull the shared modules out

Header, brand mark, nav, footer, CTA band, preheader — the pieces that live
across formats rather than inside one. Numbered `MOD-01…NN`, specified once,
referenced by code from every format spec. A change to a module changes every
email, which is the point and also the risk; say so in the handoff.

## 5. Update the tokens

The format set is only buildable if `components.json` holds the exact skin.
Take values from the structure records verbatim — never rounded to a 4 or 8px
grid, never a public brand library's defaults, never a value that "looks
right". v1 of the <brand> tokens guessed a typeface and had to be replaced;
that is the failure this rule exists to prevent.

## 6. Cross-link

The format set names its members by id; the census rows name their format.
Both directions, or the record only answers half the questions asked of it.

---

## Done when

Every recurring layout exists once as a named, spec'd format with named image
slots and a block plan the renderer accepts; every email in the record is
either a member, a candidate's member, or a listed orphan.
