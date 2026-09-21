**THIS PROMPT SUPPLIES NO CONTENT.** It names no brand, no product, no avatar,
no customer and no story. Every brand-specific word you write must come from
the labelled slots below, which the machine fills from the brand's own files.
Where this prompt shows a shape, the angle-bracket slot names what goes there;
it is never an example to copy. If a slot below is empty or says `open`, the
brand has not settled it — write `open`, never a guess.

Today is: {today}

---

## WHAT YOU ARE WRITING

The brand's `story.md`: the storytelling framework that sits beside its
`position.md`. The position says what the brand claims. The story file says
**who tells it, and what happens to them**. Every ad, page, email and static
the machines make will be one of the stories you write here, told by one of the
tellers you name here. A story you write that the evidence cannot carry will be
told to real buyers as if it were true, so the rule below is absolute.

## THE ONE RULE — QUOTE ONLY WHAT YOU WERE HANDED

- Every string you put in double quotes must be copied **character for
  character** from the ROWS slot or from one of the brand files handed to you
  below. You may quote a shorter piece of a row. You may not fix its spelling,
  tidy its grammar, join two rows into one quote, or change a word.
- A machine checks every quote against the exact text you were handed after you
  finish. A quote it cannot find demotes the whole story to `open`.
- Every quote names where it came from, the way the ROWS slot shows it:
  `"<verbatim>" (<file>, <who said it, where>)`.
- A story needs at least one receipt from ROWS or from the brand files. A story
  you can only half-receipt is still written, with **Open:** saying what is
  missing, and its id is marked `(open)` in STORIES.
- Never invent a customer, a name, an age, a number, a result, a timeline or a
  quote. Paraphrase is for Beats and Why it works only, and never inside quotes.
- A row whose source is a paid panel or a creator is not a customer speaking —
  never present it as one.

## THE SHAPE — FOLLOW IT EXACTLY

The template below is the contract. Same title line, same `##` sections in the
same order, the story block's fifteen labels in the same order, one per line,
no blank lines inside the fence, `confirmed by: open` last — always `open`; a
human locks it, never you. Each story is a `###` headed
`<kebab-case-id> — "<a verbatim line from its receipts>"` (or a plain line
naming it when no single line carries it), with **Beats:**, **Why it works:**,
**Teller:**, **Fits:**, **Receipts:** and, when something is missing, **Open:**.
Every angle-bracket slot in the template is replaced; none may survive. Keep the
template's italic lines as instructions to the reader of the file, reworded for
this brand. Copy the template's `## How a run uses this` text as it stands, and
in `## Where it lives in the chains` keep the template's paragraph and replace
its last slot with one line: the per-chain wiring is `open` until a chain reads
`{story}`.

Include `## The <name> lane — a separate block` **only** when the LANES slot
declares a second lane that must never be blended with the first. Otherwise
leave that section out entirely.

<template>
{template}
</template>

## HOW TO FILL EACH SLOT — WHERE EACH ONE COMES FROM

| Slot | Comes from |
|---|---|
| SPINE | POSITION → SPINE and MECHANISM, bent into before → turn → after. If POSITION's SPINE is marked PROPOSED, the story SPINE says so too |
| BEFORE | what the reader DID to live with the problem — the behaviour in AVATAR, receipted in ROWS |
| TURN | POSITION → MECHANISM, told as something found. Reference it, do not restate the whole mechanism |
| AFTER | the proof hierarchy in LANGUAGE RULES (someone else noticed, behaviour change); never a promise of weeks if POSITION → NEVER bans it |
| TELLERS | the reader first; the role in POSITION → AUTHORITY; any teller IDENTITY ANCHORS makes available (founder, creators, generated characters) — named by role, cast per IDENTITY ANCHORS |
| ENTRY | LANGUAGE RULES → a section on how stories are opened, if one exists; otherwise `open — the language rules carry no story entry points yet` |
| STORIES | the ids of the `###` stories you write, in the order written |
| ARC | ARC FRAME, by name and path, then "— this block is what <brand> puts in each phase" |
| REASON TO SWITCH | POSITION → DISPLACES, by reference, told as what the reader tried |
| OPENS IN | AVATAR's moments and buying times |
| PRODUCT ENTERS | at the turn, never the first line; one product, one price, one button unless POSITION says otherwise |
| PROOF | LANGUAGE RULES' proof hierarchy |
| VOICE | LANGUAGE RULES' register and tone rules, by reference |
| NEVER | "an invented customer · an invented number · a real customer's face generated or re-posed" plus the POSITION → NEVER items that bite on a story |

**The stories.** Write between four and eight. Each is the SPINE told from a
different door, and each door must be one the evidence already opens: a
cluster of ROWS saying the same thing (the patterns each row matched are shown
beside it), a sub-avatar's one-line story, the TRUST MOVE in POSITION, a
before-and-after on file. Name each story for what happens in it, in plain
words, kebab-case. **Fits** names sub-avatars by their file stem, as SUB-AVATARS
shows them. **Teller** is one of TELLERS.

**The lesson section.** The file this template was cut from was started off a
swipe whose brand kept its product line fixed and rotated who was talking and
why they switched. Write the table's "We do" column for this brand from
POSITION and the stories you wrote; keep "They do" as the template has it.
Start the section with one line saying the lesson is carried over from the
first brand's story file, and name no other brand.

**Open section.** List, one bullet each: the block is declared not confirmed;
every slot you wrote `open`; every story marked `(open)` and what would close
it; anything in POSITION marked PROPOSED that a story leans on; that the draft
was written by the story builder on {today} and every quote was machine-checked
(the check's report sits beside the draft).

## THE BRAND — LABELLED SLOTS

**BRAND:** {brand}

**POSITION (the block the machines read, verbatim):**
{position_block}

**POSITION — the thing nobody in the category will say (verbatim):**
{position_unsaid}

**POSITION — the binding rules (verbatim):**
{position_rules}

**AVATAR (each core avatar's profile, verbatim, trimmed):**
{avatar_profiles}

**SUB-AVATARS (file stem, then its card, verbatim, trimmed):**
{sub_avatars}

**LANGUAGE RULES (verbatim, trimmed):**
{language_rules}

**IDENTITY ANCHORS (who may appear, verbatim, trimmed):**
{identity_anchors}

**ANGLES (the brand's signed angles, as filed):**
{angles}

**BEFORE-AND-AFTERS on file:**
{before_afters}

**LANES the brand declares:**
{lanes}

**ARC FRAME (the doctrine's generic story arc — reference it, never restate it):**
{arc_frame}

**ROWS — the only customer words you may quote.** Each row: its id, the
verbatim text in quotes (a long row is cut with …; quote only what is shown),
then the file it lives in, who said it and where, and the story patterns it
matched.
{rows}

---

Return only the finished `story.md`, starting with its `#` title line. No
preamble, no notes after it, no code fence around the whole file.
