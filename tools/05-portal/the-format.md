# The format — what a portal is made of

Read this once. Everything in the chain assumes it.

## The claim

Every funnel is trying to do two things at once: learn who this person is,
and earn the right to tell them something. A quiz does the first by asking.
A landing page does the second by writing. Both make the person do work
they did not come to do.

A portal does both by putting the person somewhere they already know how
to be. Nobody has to be taught how to wait in a barbershop. Nobody has to
be told what the blue jar is. They walk in, and everything they do there —
what they order, how long it has been, what they admit to when the room
goes quiet — is the quiz, answered without noticing. And the one true
thing you needed to tell them is shown to them by someone in that world
who has no reason to lie.

## The four parts

**The place.** Somewhere physical the customer goes, bound up with the
problem. Not a metaphor, not a "brand world". A room with a smell. Found
by stage 0 from the avatar, and only from the avatar: if the profile does
not say where this person spends their Saturdays, the chain asks you.

**The beats.** Eight to ten. Each one is a picture, a few lines, and one
thing to do. The shape almost always runs:

1. *The threshold* — arriving. One tap. Establish the place in one breath.
2. *The wait* — being there. The first choice: what they came for.
3. *The texture* — the thing regulars know. A choice that is pure world,
   no data. This beat exists to prove the world is real.
4. *The turn* — the moment the problem surfaces on its own. The honest
   choice: what's actually going on with you.
5. *The chair* — closer. A choice about history: how long, how often.
6. *The mirror* — closest. A choice about method: what have you been
   doing.
7. *The lesson* — shown, not told. The one interaction in the world that
   is not a choice: a slider, a drag, a hold that makes a mechanism
   happen in front of them.
8. *The hand-over* — the product enters, from the hands of someone in
   the world, where it would really be.
9. *The feeling* — a beat with no question. A hold. The sting.
10. *The door* — out, with the product and with what the world learned
    said back to them.

Not every world has all ten. Every world has 1, 4, 7, 8 and 10.

**The lesson.** One true mechanism, drawn, with a control the person
moves. The barbershop's is a curly hair and a razor: slide it closer and
watch the tip go under the skin. The player has that one built in; a new
lesson is a new drawing, and the format file for it says what the drawing
must do — change in front of them, in under ten seconds, with the mistake
people make available as a button.

The lesson ends with three or four things to actually do. The last of
them is where the product lives, without its name. The product is named
one beat later, by a person, as an object.

**The context.** Every choice with a `key` is remembered. At the door the
world says it back — *your cut: low fade · your neck: bumps and marks* —
and the exit link carries it to the store as plain query fields, along
with whatever tags the ad click arrived with. Your landing page, your
quiz-result page, your Klaviyo flow: whatever reads those fields no longer
has to ask.

## The rules

**Nothing invented.** The place comes from the avatar. The lines come
from the language file and the world bible. The product card quotes real
reviews and states what the product file states. If a line cannot be
traced, it is cut.

**The product does not talk.** It is handed over by someone in the world.
That person describes it the way a person would — what it is, where it
sits, what to do with it — never what it "delivers". If the barber sounds
like a landing page the world collapses.

**One thing per beat.** One action. Never a choice and a hold. Never two
questions. If a beat needs two things, it is two beats.

**Every question is one the funnel would have asked.** If a choice does
not map to a field the store can use, it had better be there for the
world's sake (beat 3) — and there is only one of those.

**Short.** A sense line is one breath. A spoken line is one thing someone
would say out loud. The whole portal is under four minutes for a slow
reader, and nobody is made to read a paragraph.

**Honest on the exit.** The chips at the door say exactly what was
learned. Nothing is inferred that the person did not say.

## The player

`engine/` is three files and no build. It reads one world file and plays
it. Pictures fade and drift; text arrives a line at a time; the one action
appears last. Sound is synthesised — a room, a pair of clippers — and off
until asked for. Holds vibrate on phones that can.

It runs from a file on disk, from GitHub Pages, from a Shopify asset
folder. It phones nobody. Events go to `window.dataLayer` (so a tag
manager sees them), to a `portal` DOM event, and optionally to one URL
you name in the world file.

`?director=1` on the address shows the map, the context so far, the
exit link as it would be sent, and the event log. Walk every branch with
it before an ad points here.

## How you know it worked

The numbers, in the order they matter:

1. **Reached the lesson.** Of everyone who arrived, how many made it to
   beat 7. If this is under half, the world is boring or the wait is
   too long. Cut a beat.
2. **Moved the slider to the end.** Of those who reached the lesson, how
   many watched the bump form. If they don't, the lesson is unclear or
   the control is broken on their phone.
3. **Took it with them.** Exit clicks over arrivals. Compare to your
   quiz funnel's click-through at the same step.
4. **What the store did with it.** Conversion on the landing page for
   people who arrived with context fields versus without. This is the
   number that decides whether portals are a thing.

Time in the world is not a goal. A fast walk that ends at the door is
better than a slow one that ends at the chair.

## What it is not

Not a game. There is no score and no way to lose. Not a film — nothing
plays without them. Not a brand world — the brand is a guest. Not a quiz
with pictures — if the choices feel like a quiz, the world is not real
enough yet.

---

## EXAMPLES ARE EXAMPLES

The barbershop, the chair, the jar, the neck — illustrative only. The
place comes from the avatar in front of you. A supplement brand's portal
might be a pharmacy counter; a skincare brand's might be the passenger
seat of a car at a red light with the visor mirror down. Read the example
for the shape, then build the shape around what you actually have.
