# How to build a portal — no technical anything

You need your **brand folder**, **Claude**, and **Higgsfield Supercomputer**.
The player is already built. You are writing a world for it to play.

If you can fill in a document and paste text into a chat box, you can do
this.

---

## Before you start

Your brand folder has to be filled in — especially the avatar profile, the
language file, the product file and the offer bank. The portal is built
almost entirely from those four. If any of them is thin, the chain will
tell you which, and you should go fill that in first.

One thing the brand folder does not usually have, and this needs: **the
place.** Somewhere your customer goes, physically, that is bound up with
the problem your product solves. Stage 0 finds it. You will know it when
you read it back, because you will be able to smell it.

---

## The seven steps

### Step 1 — Find the place

Open Claude. New chat. Paste `the-chain/01--stage-0-ritual.md`, then your
avatar profile and their language file.

Claude comes back with three candidate places, each with what happens
there, what the customer feels there, and where the problem shows up in
it. Pick one. Pick the one you can smell.

### Step 2 — Build the world bible

Same chat. Paste `the-chain/02--stage-1-world.md`.

You get the world bible: the place written down the way someone who has
been there a hundred times would write it. The sounds, the wait, the
regulars, the objects nobody explains, the one moment that makes a man
check his neck. This is the document everything else is cut from. **Read
it. Add what it got wrong.** You know this place; the machine only knows
what you told it.

### Step 3 — Find the lesson

Same chat. Paste `the-chain/03--stage-2-lesson.md`, then your product
file.

Claude finds the one true thing about the problem that can be *shown* —
a mechanism, a mistake, a before-and-after that happens in seconds — and
writes it as something to watch, not something to read, with the three
or four things to actually do about it. The product enters at the last of
those, without its name.

### Step 4 — Cut the missions

Same chat. Paste `the-chain/04--stage-3-scenes.md`.

Out come the missions: eight to eleven, each one a place to stand, a
marker to walk to, a few lines of subtitle, and one thing to do. Every
wheel in the world is a question your quiz funnel would have asked, in
disguise. Every scene carries a prompt for its wide plate and every
marker a prompt for its close look.

### Step 5 — Assemble the world file

Same chat. Paste `the-chain/05--stage-4-assemble.md`, then your offer
bank.

Claude writes `world.js` — the exact file the player reads — and
`prompts.md`. Save them as `worlds/your-place/`. It should look like
`worlds/barbershop/world.js`, with your place in it.

### Step 6 — Make the pictures

Open Supercomputer. Make your reference elements first, once: the room
(a few real photos of the place, or your shop set), each character, and a
photograph of the real product. Then, for each prompt in `prompts.md`,
generate with GPT Image 2.5 and the references attached.
`WHICH-MODELS.md` has the settings and the style block.

- Keep the look: the style block goes at the top of every prompt, word
  for word. It is what makes this a game and not a photo album.
- Keep the room and the people: they are references, not descriptions.
  Describe what is in the reference, not the name.
- The product is real: drawn from a reference of the real thing, and the
  only logo in any frame.
- Plates are 16:9 (you look around them). Looks are 9:16 (they fill the
  phone).

Save the pictures next to the world file as `media/p-….jpg` (plates) and
`media/l-….jpg` (looks), named exactly as the world file expects. If you
keep them on Supercomputer's CDN for now, list them in `frames.json` and
the site's fetch job pulls them in.

### Step 7 — Wire it and watch it

Paste `the-chain/06--stage-5-wire.md`. It tells you where to point the ad,
what the exit link carries, and what to look at after a week.

Open `engine/index.html` with your world. Play it on your phone: drag to
look around, walk to the marker, take the wheel. Then play it with
`?director=1` on the end of the address — that shows every mission (tap
one to jump there), what the world has learned, and the exit link it
would send.

---

## When it goes wrong

**"It feels like a slideshow."** They are reading. Cut lines. Put more of
the mission in the plate and the marker and the wheel, less in the
subtitles. Every mission needs something to walk to and one thing to do,
not a paragraph.

**"It doesn't feel like the place."** The world bible is thin. Go back to
step 2 and add the details only a regular would know. The blue jar. The
chair pedal. The clock that lies.

**"The lesson is a paragraph."** It is telling, not showing. Step 3 again:
what changes, in front of your eyes, in ten seconds?

**"It sells too early."** The product appears before the lesson, or the
barber sounds like a salesman. In the world, the product is handed over
by someone who has no reason to lie. Move it later. Cut the pitch.

**"The store gets nothing."** The exit link is missing the context, or the
store isn't reading it. Step 7's wiring section, and check the director's
view: the exit link is printed at the bottom.

---

## What good looks like

Send it to someone who lives in that world. If they say *"that's exactly
what it's like"* before they say anything about the product, it worked.
