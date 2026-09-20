# The Portal

A quiz funnel asks a stranger six questions and then shows them a page.
A portal drops them into a place they already know, first person, and
plays it like a mission: a yellow marker says where to go, the regulars
talk, the wheel asks what the quiz would have asked, and the product is
handed over where it would really be handed over. MISSION PASSED.

That is the whole idea. The click on the ad does not land on a page. It
lands on a Saturday, with a radar in the corner.

Nothing gets installed. The player is one HTML file. A world is one text
file and fifteen pictures you generate, drawn like a GTA loading screen
from your own shop set, cast and product references.

## What you need

1. **Claude** — the chat at claude.ai, or Claude Cowork.
2. **Higgsfield Supercomputer** — where the pictures of the world get made,
   with GPT Image 2.5 and your brand's reference elements.
3. **Your brand folder** — filled in. The portal reads the avatar, their
   words, the product file and the offer bank. An empty folder makes an
   empty world.
4. **Somewhere to put one folder of files** — GitHub Pages, Netlify, your
   Shopify theme's assets, anywhere that serves static files. No server
   code.

## Start here

**Read `HOW-TO-RUN-IT.md`.** It is the whole process in seven steps. The
chain files in `the-chain/` are what those steps tell you to paste.

Then open `engine/index.html` in a browser, or `docs/portal/` on the site
with the pictures in. That is the worked example — a Saturday at the
barbershop — and everything the runbook produces ends up looking like
that, with your place and your product in it.

## What is in this folder

- `HOW-TO-RUN-IT.md` — the seven steps. Start here.
- `the-format.md` — what a portal is made of, the rules, and how to know
  it worked. Read this once.
- `WHICH-MODELS.md` — the models and settings for the pictures.
- `the-chain/` — what you paste into Claude, one file per step, numbered.
- `engine/` — the player. Three files: the HUD, the world you look around,
  the wheel, the hold, the scan, the passed screen. You never edit these.
- `worlds/_TEMPLATE/` — the empty world to fill in.
- `worlds/barbershop/` — the worked example, with its picture prompts and
  the references it was built from.

## The two rules

**The place is theirs, not yours.** You are not building a brand world.
You are rebuilding, in detail, a place your customer has stood in a
hundred times — the chair, the smell, the wait, the argument. The product
is a guest in that place. If the world could only exist in an ad, it is
not a portal, it is an ad.

**Show the lesson, never say it.** The reason the portal exists is that
something true about the problem can be watched instead of read. A hair
curling back under the skin. A bump becoming a mark. If the lesson is a
paragraph, you have written a landing page with pictures.

**It has to feel like a game.** If the person is reading, it is a
slideshow. They should be looking around, walking to a marker, choosing
off a wheel, holding a button while something happens to them. The HUD is
there so that the first second tells them what kind of thing this is.

---

*Open Source Outliers — daemn.co. Free, MIT licensed.*
