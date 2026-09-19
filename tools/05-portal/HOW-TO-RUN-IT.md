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

### Step 4 — Cut the beats

Same chat. Paste `the-chain/04--stage-3-scenes.md`.

Out come the beats: eight to ten, each one a picture, a few lines, and
one thing to do. Every choice in the world is a question your quiz funnel
would have asked, in disguise. Every beat carries an image prompt for
Supercomputer.

### Step 5 — Assemble the world file

Same chat. Paste `the-chain/05--stage-4-assemble.md`, then your offer
bank.

Claude writes `world.js` — the exact file the player reads. Save it as
`worlds/your-place/world.js`. It should look like
`worlds/barbershop/world.js`, with your place in it.

### Step 6 — Make the pictures

Open Supercomputer. For each beat, paste its image prompt from the world
file and generate the frame. `WHICH-MODELS.md` has the model and settings.

- Keep the place consistent: every prompt carries the same anchor
  sentence describing the room. Do not shorten it.
- Keep people consistent: generate every frame of one person from the
  same starting frame.
- **Never generate the product.** The product is a card the player draws
  from your product file. A generated product is a product that is not
  yours.

Save the pictures next to the world file as `media/00-….jpg` and so on,
named exactly as the world file expects.

### Step 7 — Wire it and watch it

Paste `the-chain/06--stage-5-wire.md`. It tells you where to point the ad,
what the exit link carries, and what to look at after a week.

Open `engine/index.html` with your world. Walk through it on your phone.
Then walk through it with `?director=1` on the end of the address — that
shows the map, what the world has learned, and the exit link it would send.

---

## When it goes wrong

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
