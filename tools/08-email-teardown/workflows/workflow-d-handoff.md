# Workflow D — Dev Handoff

Package the format set so someone who was not here builds the production
templates from it. Run last.

---

## 1. Write it

`prompts/stage4-production-handoff-v1-damon.md`, with the format set, the
specs and the measured record as input. Output:
`runs/<brand>-<board>/handoff.md`, or for a whole-brand pass,
`brands/<brand>/email/design-formats/handoff.md`.

The test the document has to pass: **a developer with no context and no way to
ask a question can build from it.** Every value they need is written out, even
where it repeats.

## 2. Say what the design files are

State plainly, in those words, that the bank is a design record and not
production code. Someone copying extracted markup into a live email has been
misled by the handoff, and that is the handoff's fault.

## 3. Order the fix list by cost of leaving it

Not by how easy it is. Every item names what is wrong, everywhere it occurs,
why, and what done looks like. Assets that could not transfer are named
individually — a placeholder is the right answer until the brand supplies a
replacement, and the handoff should say so rather than leaving it looking like
a bug.

## 4. Name what plugs into what

`email-production/render_email.py` already turns a filled block plan into a
real table-based email in the brand's skin, and `components.json` already
holds the tokens. The built templates satisfy those — they do not replace
them. A handoff that does not say this invites a parallel system.

## 5. End on the open questions

Every decision that could not be made from the record, each phrased so a
one-line answer unblocks it. Never guess in place of asking.

---

## Done when

The handoff stands alone, the fix list is specific enough that nobody has to
ask what a task means, and the open questions are in one place at the end
rather than scattered through the prose.
