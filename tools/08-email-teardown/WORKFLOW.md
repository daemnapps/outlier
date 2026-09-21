# How the email teardown runs

The whole thing in one read. No commands, no file paths you need to care
about — this is what happens when you paste a link.

---

## You paste a Figma link

That is the entire input.

- A link to a **board** — a month, a flow, a whole section — runs every email
  on it.
- A link to **one frame** runs that one email.

Say what it is if the name is not obvious ("this is the November flows"), and
that is the last thing asked of you until stage 2 has an answer.

## What happens to it

**It gets counted first.** Before anything is read, the board is opened and
every email on it is found and numbered — `JAN26-01`, `JAN26-02`, and so on.
The numbers are permanent. Every brief, every format, every note from here on
points back at one of them, so you can always get from an idea to the exact
design it came from.

Emails are found by their shape, not their layer names, because designers name
frames anything. A 600px-wide, 3,000px-tall box is an email. A card inside one
is not.

**Then each one gets read.** Two things are pulled per email — a picture of it,
and the real structure underneath: every measurement, every colour, every
typeface, exactly as the design file has them. Both go into the read.

What comes out is a record of one email: every block top to bottom, what each
block does to the reader, the copy word for word, and every image marked as a
slot with its size and a brief for what belongs there. Nothing rounded,
nothing guessed. If something cannot be read, it says so instead of inventing
a value.

**Then the images come out.** The real bitmaps, not re-renders. Anything that
cannot come out is marked with a labelled grey box that states its own size —
`IMAGE 600×760` — because a clear gap is useful to you and a plausible fake
is not. You generate those later from the slot brief.

**Then the formats fall out.** With every email read, the layouts that repeat
become obvious. They get grouped by **shape, not by campaign** — a Black
Friday email and a welcome email with the same block order are the same
format, and that is the whole point. Each one gets a code and a name:
`FMT-01 · HERO ANNOUNCEMENT`.

Emails that fit nothing stay on an orphan list with a reason. That list is not
a failure — it is the honest measure of how disciplined the design has been.

**Then each format becomes a page anyone can fill.** Block order, what goes in
each block, how many words, what each image must show. A writer works from
that page without opening Figma; the machine builds a real, sendable email
from the same page.

## What you get

- **Every email you have ever sent, registered.** Findable by what it looks
  like, not by remembering which month it was.
- **The formats you actually reuse**, named — so the next email is built as a
  known format instead of designed from nothing.
- **A fill sheet per format** that turns into a real email.
- **A handover document** for whoever builds the production templates.

## Where you look

The page — `page.html` in this folder, rebuilt after any change, and the
artifact mirror of it. Every stage's prompt is printed there in full, because
reading the outputs and tightening the prompts is the actual work.

## The one thing that slows it down

Figma limits how much a connection can read on the Starter plan, and the cap
gets hit part-way through a board. Nothing is lost — every email is saved the
moment it is read, and the run picks up where it stopped when the cap resets.

Two things would remove it, and both are yours to do: move the design file
into the Pro team seat, or generate a Figma access token. Either one and a
board reads in one pass.

## What this does not do

It does not write copy, decide what to send, plan a calendar, or build flows
in Klaviyo. Those are the email machine's job and it already does them. This
one settles what the emails **look like**, which is the part that was living
only in a design file nobody could browse.

It also does not yet tear down **somebody else's** email. That half — swipe
theirs, strip it, inject ours — is the next build.
