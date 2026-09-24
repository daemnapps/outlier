# PRIZM LABS — the tools

A production studio for generative advertising, giving away its machine.

Take a video that already worked — a competitor's ad, an organic post,
anything — keep its structure, and rebuild it for your own brand in whatever
world you like. You get a script, a shot list, and a prompt for every frame.

**Free. MIT licensed. One way to use it:** clone this repo into Higgsfield
Supercomputer (or Claude Code) and tell it what you want. No kits, no copies.

**→ [daemn.co](https://daemn.co)** — see it working, with the same ad rebuilt
three different ways.

---

## Start here

Everything is plain text. Clone it and it is all there; say "pull for
updates" and it stays current.

| | What it is | Read it |
|---|---|---|
| **01** | **Your brand folder** — the one thing you fill in. Every tool reads it, so you set your brand up once and never explain it again. | [`brands/_TEMPLATE/`](brands/_TEMPLATE/) |

### Take something apart

Something already worked. These pull it down to the structure underneath, then
put your brand where the other brand was.

| | What it is | Read it |
|---|---|---|
| **02** | **Video teardown** — any video in, your brief out. Written for someone who has never done this. | [`tools/02-video-teardown/`](tools/02-video-teardown/) |
| **03** | **Organic swipe pack** — 48 formats pulled apart from 377 posts that worked, some past a hundred million views. Rebuilt 2026-09-22. | [`tools/03-organic-swipe-pack/`](tools/03-organic-swipe-pack/) |
| **04** | **Paid ad swipe pack** — 6,269 live competitor ads across nine markets, reduced to the ten angle shapes that keep working. Rebuilt 2026-09-22. | [`tools/04-paid-ad-swipe-pack/`](tools/04-paid-ad-swipe-pack/) |
| **06** | **Image teardown** — the same chain pointed at a single frame. | [`tools/06-image-teardown/`](tools/06-image-teardown/) |
| **07** | **Copy teardown** — for a piece of writing rather than a video. | [`tools/07-copy-teardown/`](tools/07-copy-teardown/) |
| **08** | **Email teardown** — an email pulled apart into its structure. | [`tools/08-email-teardown/`](tools/08-email-teardown/) |
| **09** | **Page teardown** — a landing page, same treatment. | [`tools/09-page-teardown/`](tools/09-page-teardown/) |

### Make something

| | What it is | Read it |
|---|---|---|
| **05** | **AI video production** — the brief becomes scenes, motion and finished shots. The chain that builds a brief from scratch. | [`tools/05-ai-video-production/`](tools/05-ai-video-production/) |
| **10** | **Image production** — stage two for statics, the twin of the video line. | [`tools/10-image-production/`](tools/10-image-production/) |
| **11** | **Email production** — the writing chain. Copy first, images second, never both at once. | [`tools/11-email-production/`](tools/11-email-production/) |
| **12** | **Marketing calendar** — nine layers on real dates, holidays placed first. What the email chain runs off. | [`tools/12-marketing-calendar/`](tools/12-marketing-calendar/) |
| **13** | **Pages** — swipe, construct, inject, base, then one variation per sub-avatar. No page gets written freehand. | [`tools/13-pages/`](tools/13-pages/) |
| **14** | **Copywriter** — the copy chain. | [`tools/14-copywriter/`](tools/14-copywriter/) |

### Plan it and finish it

| | What it is | Read it |
|---|---|---|
| **15** | **Outlier brief** — the second door. Start from your own idea instead of someone else's video. | [`tools/15-outlier-brief/`](tools/15-outlier-brief/) |
| **16** | **Video edit** — cut sheets, in plain words rather than a timeline. | [`tools/16-video-edit/`](tools/16-video-edit/) |
| **17** | **Premiere line** — drives Adobe Premiere directly, if you use it. | [`tools/17-premiere-line/`](tools/17-premiere-line/) |
| **18** | **Story builder** — drafts your brand's story, the part that is not the product. | [`tools/18-story-builder/`](tools/18-story-builder/) |
| **19** | **Intake** — one front door for everything you swipe. | [`tools/19-intake/`](tools/19-intake/) |
| **20** | **Asset index** — a folder of footage becomes records you can search. | [`tools/20-asset-index/`](tools/20-asset-index/) |
| **21** | **Editor onboarding** — the front door for editors and designers: the walkthrough, the SOP, the two prompts they paste into Higgsfield, and the brief queue. | [`tools/21-editor-onboarding/`](tools/21-editor-onboarding/) · [the page](https://daemn.co/onboarding.html) |
| **22** | **Swipe library** — one front door to everything swiped: the formats, the torn-down videos, one feed per customer type, every competitor's live ads. Public half on the site, the rest on Drive. | [`tools/22-swipe-library/`](tools/22-swipe-library/) · [the page](https://daemn.co/swipe-library.html) |

### The shared parts

The tools import these. You do not run them yourself, but nothing runs without
them: the chain runner, the element system, the marketing doctrine, the run
layout, the name maps, the research gatherer and the quality checks.
[`components/`](components/)

**Do 01 first.** Nothing else works well on an empty brand folder — the tools
are built to say *"I don't know this"* rather than invent an answer, so an
empty file shows up as a question instead of a fake.

Then read
[`tools/02-video-teardown/HOW-TO-RUN-IT.md`](tools/02-video-teardown/HOW-TO-RUN-IT.md)
— the whole process in seven numbered steps.

---

## What you need

1. **Higgsfield Supercomputer** with this repo cloned into it — where the
   video gets watched, the chain runs and your scenes get made.
   ([affiliate link](https://higgsfield.ai?fpr=damon61) — costs you nothing
   extra.) Claude Code with the repo cloned works the same way.
2. **Google Drive** — where finished briefs and delivered work live, so the
   people who make the ads can reach them. `tools/21-editor-onboarding`.

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
