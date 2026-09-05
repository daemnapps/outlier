# DÆMN STUDIO — the tools

A production studio for generative advertising, giving away its machine.

Take a video that already worked — a competitor's ad, an organic post,
anything — keep its structure, and rebuild it for your own brand in whatever
world you like. You get a script, a shot list, and a prompt for every frame.

**Free. MIT licensed. Nothing to install.** No account, no dashboard, no
server of ours holding your data.

**→ [daemn.co](https://daemn.co)** — see it working, with the same ad rebuilt
three different ways.

---

## Start here

Everything is plain text. Read it on GitHub, or download the zips from the
site if you would rather have it as a folder.

| | What it is | Read it | Download |
|---|---|---|---|
| **01** | **Your brand folder** — the one thing you fill in. Every tool reads it, so you set your brand up once and never explain it again. | [`brands/_TEMPLATE/`](brands/_TEMPLATE/) | [zip](https://daemn.co/downloads/brand-folder-kit.zip) |
| **02** | **Video teardown** — any video in, your brief out. Seven steps, written for someone who has never done this. | [`tools/02-video-teardown/`](tools/02-video-teardown/) | [zip](https://daemn.co/downloads/video-teardown-kit.zip) |
| **03** | **Organic swipe pack** — 48 formats pulled apart from 377 posts that worked, some past a hundred million views. | [`tools/03-organic-swipe-pack/`](tools/03-organic-swipe-pack/) | [zip](https://daemn.co/downloads/swipe-to-scene-kit.zip) |
| **04** | **Paid ad swipe pack** — 2,626 live competitor ads reduced to the ten angle shapes that keep working. | [`tools/04-paid-ad-swipe-pack/`](tools/04-paid-ad-swipe-pack/) | [zip](https://daemn.co/downloads/paid-ad-swipe-pack.zip) |

**Do 01 first.** Nothing else works well on an empty brand folder — the tools
are built to say *"I don't know this"* rather than invent an answer, so an
empty file shows up as a question instead of a fake.

Then read
[`tools/02-video-teardown/HOW-TO-RUN-IT.md`](tools/02-video-teardown/HOW-TO-RUN-IT.md)
— the whole process in seven numbered steps.

---

## What you need

1. **Claude** — the free chat at claude.ai, or Cowork.
2. **Higgsfield Supercomputer** — where the video gets watched and where your
   scenes get made. ([affiliate link](https://higgsfield.ai?fpr=damon61) —
   costs you nothing extra, everything here works without it.)
3. **Google Drive** — where your brand folder and finished briefs live.

Nothing gets installed. Nothing runs on your computer.

The exact models and settings are in
[`WHICH-MODELS.md`](tools/02-video-teardown/WHICH-MODELS.md) — don't leave it
on Auto.

---

## The two rules

**Copy the structure, not the content.** The shape is what earned the views;
your product is what changes. A scalp treatment and a countertop demo can be
the same format — that's the whole point.

**Nothing invented.** If your brand folder doesn't say what your product looks
like or how your customer talks, the tools tell you they don't know rather than
guessing. That's them working correctly. Go fill that part in.

---

## What it won't do

Publish anything. Spend anything on ads. Invent a customer quote. Make a
medical claim. Write in a voice it hasn't been given evidence for.

Those are hard stops in the prompts, not guidelines.

---

## What it costs

The tools are free and stay free. The models are not — you pay Higgsfield (or
whichever generator you use) directly, at their prices, from your own account.
Nothing bills through us.

Affiliate links to tools we actually use are the only way this project makes
money. They cost you nothing extra and everything works identically without
them.

---

## Also in here

| | |
|---|---|
| [`docs/`](docs/) | The site itself — daemn.co is served straight from this folder. Fork it. |
| [`SECURITY.md`](SECURITY.md) | What's exposed, what isn't, and the commit guard that keeps keys out. |
| [`receiver/`](receiver/) | An optional Cloudflare Worker, if you want forms that file themselves. Not required. |

MIT licensed. Take it, strip it, use it on your own brands.
