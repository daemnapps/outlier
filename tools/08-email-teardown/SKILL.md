---
name: email-teardown
description: Run the email-teardown lane — a Figma link in, every email design read block by block, grouped into named formats, spec'd for production. Use when Damon pastes a Figma link and says tear it down / run the format bank / code these emails / document our email designs / same process for [brand] / turn this Figma into templates / dedupe our email layouts, or asks what our email formats are. Documents and systematizes email DESIGN; does not write copy, plan sends, or build Klaviyo flows.
---

# Email teardown

The machine lives at `email-teardown/` in `~/Projects/ai-workspace`.
Damon's third teardown lane — video tears down a video, image tears down a
static, this tears down an email.

External dependencies (otherwise self-contained):

- `email-teardown/` — the machine. `README.md` is the doctrine and
  outranks this file on how it works; `WORKFLOW.md` is the same thing in
  Damon's language; `prompts/` holds one prompt per stage; `workflows/` holds
  the runbook for each pass.
- `brands/<brand>/email/design-formats/` — where the brand's own
  record lands: `source.json` (the Figma file + boards), the census, the
  formats, the tokens, the sweeps. **The brand owns its design record; the
  machine owns the process.** The shape is in the cabinet's `_TEMPLATE`.
- `email-production/` — the email machine downstream. `render_email.py`
  builds real emails from a filled block plan; `sweep/census.py` and
  `sweep/board_pass.py` do the measurement passes.

**Read `email-teardown/README.md` before doing anything.** This file
only says how to start.

## The input is a link

Damon pastes a Figma link. Never ask him for a file, an export, or an
attachment — that was the old lane (ruled 2026-08-31, links only).

1. `python3 tools/intake.py --brand <brand> --link "<url>"` — stands the brand
   up and registers the board with a unique code. Read `INTAKE.md` first; it is
   the standard for every brand. Never convert a `node-id=3589-29` to `3589:29`
   by hand, and never hand-edit the register — `intake.py` is its only writer.
2. Follow `workflows/workflow-a-import-and-bank.md`. Enumerate the frames with
   `get_metadata` first, save `frames.json`, then read frames one at a time.
3. Never call `get_design_context` on a board node — only on a single frame.
4. Save after every frame. The Figma connection is capped on the Starter plan
   and the cap arrives mid-board; anything unsaved is lost and the call is
   spent either way. Stop cleanly when it hits, report what landed, resume on
   reset. Never retry in a loop.

## Rules that cost a rebuild when broken

- **Find email frames by geometry, never by layer name and never by a
  hardcoded width.** 550–820px wide, 500–6500px tall, top-level in the board.
  A hardcoded 600 has silently dropped whole boards twice.
- **Exact values only** — copied verbatim from the file, never snapped to a
  4/8px grid, never a value that "looks right".
- **Never approximate imagery.** Recover the real bitmap or leave a labelled,
  sized placeholder. Damon generates images later from the slot brief.
- **Group formats by layout skeleton, never by campaign topic.**
- **Every block in a spec is one of the renderer's thirteen types** —
  preheader, headline, subhead, copy, image, quote, bullets, button, product,
  divider, signoff, ps, footer.
- **Audit the run yourself.** "I don't have time to look at everything" is the
  ask; self-audit is the deliverable, not a courtesy.

## After a run

Rebuild that brand's page — `python3 tools/build_page.py --brand <brand>` —
and republish the artifact registered in
`email-teardown/context/artifacts.md`. Never open a second artifact
for this subject.

## Not this skill's job

Email copy, what to send, when to send it, Klaviyo flows. Those belong to the
email machine. This settles what the emails look like.

*(Written 2026-08-31, INERT until graduation. It sits in the machine folder
rather than `.claude/skills/` because lab's quarantine rule bars in-development
skills from the auto-registered paths — including the personal one. Graduation
is Dayu's or Valentina's call; on approval this file moves to `.claude/skills/`
with the machine and starts triggering on its own.)*
