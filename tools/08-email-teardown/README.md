# Email teardown — the third lane

Built 2026-08-31 from the process Damon ran to turn the <brand> design file
into a format bank. Video tears down a video. Image tears down a static.
**This tears down an email** — and the first thing it tore down was ours.

Read `WORKFLOW.md` next: the whole run as one page, no jargon.

---

## The lane has two halves. One is built.

| Half | What goes in | What comes out | State |
|---|---|---|---|
| **BANK** | our own design file — a year of approved emails | every design registered, deduped into a named format set the machine can build against | **built, run once (<brand>)** |
| **TEAR** | one email — ours or a swipe — words and pictures | its element labels and its construct: message kept apart from page furniture and source defects | **built 2026-09-20 — `tools/run.py`, see `CLAUDE.md`; first real run pending** |

They meet in the middle. The bank gives the **vocabulary** — FMT-01…08, what
each format is for, where its images go. The tear gives the **structure worth
stealing**. Injection is picking the format that carries the stolen structure
and filling it with our brand. That is the same shape as the video and image
lanes; email just needed the vocabulary first, because an email is a layout
before it is a script.

Prior art on the tear half: `lab/steph/email-teardown/` — a closed one-email
experiment (Aug 2026). Its finding stands: source plus screenshots together
beats a separate vision pass. Read it before building the tear half.

## The tear half, in one command

```
python3 tools/run.py <source email> --brand <brand> [--label L] [--dry-run] [--rerun-from tear1|tear2|tear3] [--model M]
```

A sent-email file (`brands/<brand>/email/sends/*.md`) or an `.html` export goes
in. Three steps: **read** (the message, the page furniture and the source
defects, each under its own heading) → **label** (format, template, framework —
asked of the element library, never invented) → **construct** (brand-free,
subject-free, built from the message only). The run files to
`runs/email-teardown/<brand>/<label>/` at the repo root. `--dry-run` spends
nothing. Prompts: `prompts/tear1-…`, `tear2-…`, `tear3-…`. Steps, gates and
where everything lands: `CLAUDE.md`.

## The bank half, stage by stage

Every stage has a prompt in `prompts/`. The prompt is the product — change the
prompt, not the code.

| Stage | Prompt | One line |
|---|---|---|
| 1 | `stage1-email-board-read-v1-damon.md` | one email design in → its structure record out (ground, type, blocks, image slots, primitives) |
| 2 | `stage2-format-dedupe-v1-damon.md` | every structure record in → the named format set out, by layout skeleton, never by topic |
| 3 | `stage3-format-spec-v1-damon.md` | one named format in → a build-ready template spec with named image slots |
| 4 | `stage4-production-handoff-v1-damon.md` | the format set in → the brief a developer builds the real thing from |

Two stages before those are **measurement, not judgment**, and they run in
code with no model involved:

- `python3 ../email-production/sweep/census.py` — registers every email in the
  bank and clusters the recurring families off measured features.
- `python3 ../email-production/sweep/board_pass.py` — one board, measured
  fully, plus the defect detectors (dead image boxes, text overlaps, missing
  assets).

Both already exist in the email machine and both write into the **brand**, not
here. That is correct and they stay where they are — the brand owns its own
design record. This lane owns the process.

## How a brand comes in

**Read `INTAKE.md` — it is the standard, and every brand follows it.** In one
line: paste a Figma link, and `tools/intake.py` stands the brand up.

```bash
python3 tools/intake.py --brand <brand> --link "<figma board url>"
```

**Damon gives a Figma link. That is the whole input.** (Ruled 2026-08-31 —
links, not file exports, not attachments.) A link to a board section runs the
whole board; a link to one frame runs one email.

```
https://www.figma.com/design/<file>/<name>?node-id=3589-29
                              ^ the file            ^ the board or the email
```

The board is registered once and named forever, in **the brand's own record** —
`brands/<brand>/email/design-formats/source.json`. `intake.py` is its only
writer; `tools/links.py list --brand <brand>` reads it back.

Then the session reads that node through the Figma connection — the board's
frames, each frame's real structure, a picture of each — and runs the stages.
Runbook: `workflows/workflow-a-import-and-bank.md`.

**The one live constraint:** the Figma connection is capped hard on the
Starter plan and the cap was hit again on 2026-08-31. It resets, so a board
comes in bursts rather than in one pass. Two things lift it, both Damon's
call: move the design file into the Pro team seat, or generate a Figma
personal access token so the tools read the file directly instead of through
the connection. Named again at the bottom of this file.

## Where everything is

| | |
|---|---|
| `prompts/` | the four judgment stages, one file each, highest `-vN-` wins |
| `workflows/` | the four runbooks — A import & bank, B format library, C image recovery, D handoff. Read the runbook before executing it |
| `reference/original-skill/` | the process exactly as it arrived, untouched. When this lane and that disagree, that one is the record of what actually worked |
| `reference/MASTER-board-page.md` | the board page template every bank page is cloned from |
| `reference/snippets.js` | the tested scripts from the <brand> run |
| `INTAKE.md` | **the standard** — how any brand's emails enter, and the shape they land in |
| `tools/intake.py` | stands a brand up: home, Figma source, boards, codes. The only writer of the register |
| `tools/links.py` | reads a Figma link into a file + node; lists a brand's boards. Read-only |
| `tools/paths.py` | where everything lives, so no tool guesses |
| `tools/build_page.py` | draws one brand's lane as a page — stages, prompts verbatim, boards, formats |
| `pages/<brand>.html` + `.md` | that page, one per brand. **Live at `http://localhost:8786`** — served and rebuilt automatically |
| `tools/run.py` | **the tear half's one entry** — read, label, construct; `furniture.py`, `elements_label.py`, `gates.py` beside it |
| `runs/<brand>-<board>/` | the bank half's OLD working folders — history, readable, never written. New runs file to `runs/email-teardown/<brand>/<label>/` at the repo root |

**The brand's side of it** — `brands/<brand>/email/design-formats/`:
`source.json` (the Figma file and every board), `census.json`/`.md` (every
email registered), `formats.md` (the format set and its specs),
`components.json` (the tokens `render_email.py` builds real emails from),
`sweep/<board>.{json,md}` (per-board measurement). **This shape is in the brand
cabinet's `_TEMPLATE`**, so a new brand has the home before it has a design.

**The heavy files never enter git** (workspace rule 3) — see "Where hundreds
of emails actually live" below.

## The other two ways in, and why they are not the default

The process arrived written for Claude Desktop, where you attach the `.fig`
and it unpacks itself. **That tooling does not exist in this repo** — no
`fig_ls`, no `fig_materialize`, no design canvas. The runbooks mark every call
that belongs to that lane so nobody wastes a turn trying it here.

| Lane | How designs get read | Standing |
|---|---|---|
| **Link** | a Figma link, read through the connection | **the default** (Damon, 2026-08-31) |
| **Desktop** | attach the `.fig` in Claude Desktop | how the <brand> bank was built. Still the only lane that materializes every board at pixel fidelity in one pass |
| **Local export** | the 476MB bank export + `fig-export/` already on Drive | the <brand> record. Read it rather than re-running that brand |

The Desktop lane is not retired — it is what produced the thing the rest of
the machine reads. It is just not what a new run starts from any more.

## What actually ran

One brand, once: <brand>, 2026-08-31. 18 boards, a year of approved sends plus
the flows. The census registers **385 email artboards** across them (the run
itself reported ~250 — the census counts every artboard, including flow
variants the run grouped). Eight formats came out, FMT-01…08, plus four shared
modules. The tokens are in the brand and `render_email.py` already builds real
table-based emails from them.

The bank itself is already parked on Drive (checked 2026-08-31) — 489MB of
board pages, recovered bitmaps, fonts and the exact-value transcriptions, plus
the 1.4GB design export beside it. The copy in `~/Downloads/<brand> email
format bank.zip` is a spare, not the original.

## Known holes, recorded not hidden

- **The tear half is built but has not had its first real run** (2026-09-20). Email production still does its own read of old emails; switching it to this tool is a later, side-by-side decision.
- **The bank's own pages need Claude Desktop to render.** They are design
  components (`x-import`, `sc-for`, a logic class) — opening one in a plain
  browser shows nothing. Damon's readable surface is the page `build_page.py`
  draws plus the brand's `census.md` / `formats.md`, not those files.
- **Two assets were too large to transfer** in the original run and are
  placeholders in the bank. Named in the handoff.
- **Only January 2026 got a hand-written format spec** (`formats.md` v1, seven
  frames). The other 17 boards are measured but not spec'd — that is stage 3's
  standing queue.
- **The link lane runs in bursts, not in one pass**, until the Figma cap is
  lifted.

## Where hundreds of emails actually live

A brand with a year of sends is hundreds of designs. They split into three
kinds of thing, and each kind has exactly one home.

| What | Where | Why there | Size, at <brand>'s 385 |
|---|---|---|---|
| **The record** — one file per email: blocks, exact values, copy verbatim, image slots | git, in this repo | it is words, it is searchable, and it must survive | 380KB today |
| **The index** — every email in one row: code, board, size, family, format | git — `brands/<brand>/email/design-formats/census.json` | one file answers "what do we have" without opening anything | 1 file |
| **The pictures** — frames, bitmaps, board pages, the design export | Drive — `Shared Assets/brands/<brand>/email/design-formats/` | media never enters git (workspace rule 3) | 1.9GB |

**The id is what joins them.** `JAN26-04` is the same email in the record, in
the index, and in the folder of pictures. Assign it once, never renumber, and
any one of the three gets you to the other two.

**A board is read once.** The census is append-only and the structure records
are permanent, so re-running a brand never re-reads what is already registered
— it picks up the boards that are not. That is what keeps this affordable at
hundreds and, later, at thousands across brands.

**Scale, honestly:** the words stay trivial forever — 385 emails is 380KB, so
ten brands at this size is under 5MB in git. The pixels are the whole weight
and they are already on Drive. Nothing about hundreds of emails is a storage
problem; the only cost that grows is reading them, which is the Figma cap.

**The account, so nobody "fixes" it:** `Shared Assets` lives on the
**<brand>.com** Drive and that is where it belongs — company assets sit
on the company's drive. Damon reaches it through
`${DRIVE_ACCOUNT}`, while keeping `${DRIVE_ACCOUNT}` as his
own account. Both are correct at once. A session that finds the media absent
from the <account> Drive has looked in the wrong place, not found a
problem.

## The one thing only Damon can do

**Move the design file into the Pro team seat, or generate a Figma personal
access token.** Either one lifts the cap that makes the link lane read a board
in bursts instead of one pass. Nothing else in this lane is waiting on him.
