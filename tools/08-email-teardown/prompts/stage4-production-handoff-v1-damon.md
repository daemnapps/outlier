Here is the format set: {format_set}

Here are the template specs: {specs}

Here is the measured record — every email registered, every board swept, every
defect found: {census_and_sweeps}

Write the **handoff**: the one document a developer who was not in any of this
builds the brand's production email system from.

**They have no context and cannot ask.** Every number they need is in this
document or they cannot work. No pointer to a conversation, no "as discussed",
no reference to a file they do not have. If a value matters, it is written out
here even if it appears in four other places.

**Say what these files are.** The bank is a design record — machine-extracted,
faithful to the look, not production code and not to be copied into a build.
The specs are the buildable thing. A developer who copies the bank's markup
into a live email has been misled by this document, and that is this
document's fault, not theirs.

**Fidelity is stated, not implied.** Where a value is an exact transcription,
say so. Where an extraction artifact contradicts obvious design intent, say
which way to build and why. Where something is unknown, say unknown.

**The fix list is ordered and specific.** "Clean up the spacing" is not a task.
"The footer's legal line overlaps the unsubscribe link on eleven boards
because the extractor absolutely positions both at the same top offset — build
it as two stacked table rows" is a task. Every item names what is wrong, where,
why it is wrong, and what done looks like.

---

Give me these eight sections.

**1. WHAT THIS IS AND WHAT THE JOB IS**

The brand, the record's size and date range, and the two jobs in order: build
the format set as production templates, and fold the known defects out on the
way. One paragraph each. Nothing aspirational.

**2. WHAT EACH ARTIFACT IS**

Every file and folder they have been given, what it is, what it is
authoritative for, and — explicitly — what it must not be used for. Mark the
design record as reference-only, in those words.

**3. THE TOKENS**

The complete design skin, exact values, no rounding: every color with its role
and its value, both type families with the real file names and every size /
weight / leading / tracking convention in use, the CTA geometry, the spacing
scale, the artboard widths in play, and each recurring primitive with its
verbatim gradient or shadow string.

**4. THE FORMATS TO BUILD**

The set in priority order — most-used first, because that is where the volume
is. For each: code, name, what it is for, its block plan in one line, its
reference member, and its slots. Then the candidates, marked as candidates,
with what would have to be true to promote one.

**5. THE SHARED MODULES**

Built once, used by every format. Each with its exact geometry and the list of
formats mounting it. Say plainly that a change here changes every email.

**6. THE FIX LIST**

Ordered, most-costly-to-leave first. Every defect the sweep found, grouped by
kind, each with: what is wrong, every place it occurs, why it happens, and
what done looks like. Include the ones that cannot be auto-detected and say
how to find them by hand. Include assets that could not be transferred, by
name and by where they appear, and say a placeholder is the correct answer
until the brand supplies a replacement.

**7. HOW IT PLUGS IN**

Where the built templates land, what already consumes them, and what the
contract is — the block vocabulary, the token file, the slot naming. If a
renderer already exists, name it and say the templates must satisfy it rather
than replace it.

**8. ASSETS, FONTS AND WHAT IS NOT OURS**

Where the imagery lives, which fonts are licensed and under what terms, what
must never be redistributed, and what the email clients will actually render
so nobody optimises for a face that never loads.

---

Close with **the open questions** — every decision you could not make from the
record, each phrased so a one-line answer unblocks it. Never guess in place of
asking, and never bury a question inside a paragraph.
