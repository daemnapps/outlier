# research-story — the story builder

Drafts a brand's `story.md` — who tells the brand's story and what happens to
them — from what the brand already has on file. Nothing invented: every quote
in the draft is machine-checked against the brand's own files.

```
python3 story-builder/build.py --brand <brand>             # full run — ONE model call
python3 story-builder/build.py --brand <brand> --dry-run   # free: no model, nothing written; says where it would file
python3 story-builder/build.py --brand <brand> --dry       # no model; files the gather and the prompt as sent
python3 story-builder/build.py --brand <brand> --label <run-label>
```

## The four stages

| # | Stage | Model | What it does | Prompt |
|---|---|---|---|---|
| 1 | Gather | none | Pulls story-shaped verbatim rows from the brand's language bank — hid it, tried everything, someone noticed, family, years, partner, an authority figure, the founder or brand story, the after — keeping each row's id and source. Paid panels, creator audiences and the brand's own words are left out (not a customer speaking). Also cuts the excerpts a story needs: the position block, the thing nobody will say, the binding rules, each avatar profile, each sub-avatar card, the language rules, identity anchors, angles, before-and-afters, lanes | — (rules in `machine/build.py`: `PATTERNS`) |
| 2 | Draft | the video machine's claude helper (opus) | Writes `story.md` in the shape of `brands/_TEMPLATE/story.md`, quoting only what stage 1 handed over | `prompts/stage2-draft-v1-damon.md` |
| 3 | Verify | none | Every quoted string must be found verbatim in what was handed over (curly quotes, spacing, `*` and a trailing `…` are ignored; an elided quote is checked piece by piece). A story with an unfound quote is demoted to `open`; an unfound quote elsewhere is marked ⟨unverified⟩ | — |
| 4 | Lint | none | `components/marketing-doctrine/lint_story.py` on the result | — |

## The gates

| Gate | When | Holds the build when |
|---|---|---|
| inputs | before the model | the story template or the draft prompt is not on file |
| elements | before the model | the story framework (`story-testimonial`) or delivery (`storyteller`) the ARC slot names is not a real row in the element library — the refusal names the real ones |
| copy | after the lint | a quote outside any story was not found in the brand's files, or the file's shape fails the lint |

A held build writes `check.json`, says why, hands nothing to the brand and exits
2. A story demoted to `open` does not hold — that is the quote check doing its job.

## What a run leaves

`runs/research-story/<brand>/<run-label>/` (runs before 2026-09-20: `runs/story-builder/…`)

| File | What it is |
|---|---|
| `run.json` | the record: stages, timings, prompt file and hash, counts, what was written |
| `check.json` | each gate, `pass` or `HELD`, with the problems |
| `stage1--gathered.json` / `.md` | every row handed over, with its id, file, source and the patterns it matched; the sources read |
| `stage2--sent.md` | the prompt exactly as sent |
| `stage2--draft.md` | the model's raw draft |
| `stage3--verify.md` / `.json` | every quote, found or not, and where it was found |
| `stage4--lint.txt` | `clean`, or the lint's findings |
| `deliverable/story.md` | the verified draft |

`brands/<brand>/story.md` is written only when the brand has none yet and the
draft passed the copy gate. An existing story is never overwritten — the new draft
waits in `deliverable/` for a human.

## What a brand needs for a good draft

Any of these can be missing; a missing one becomes `open`, never a guess.

- `position.md` (the block, the thing nobody will say, the binding rules)
- `core-avatars/*/profile.md` and `core-avatars/*/sub-avatars/*.md` (their "One-line story")
- `core-avatars/*/language/**/*.json` and `sub-avatars/*/language/*.json` (verbatim rows)
- `core-avatars/*/language/rules.md` — a **Story Entry Points** section here fills the ENTRY slot
- `identity-anchors.md`, `strategy/angles.json`, `existing-content/angles.md`
- `before-afters.md` (in `core-avatars/` or the brand root), and a `*lane*.md` map if the brand runs audience lanes that must never blend

## Tests

`python3 story-builder/tests/test_research_story.py` — no network, no model, a temp workspace.

## Runs so far

| Brand | Run | Result |
|---|---|---|
| <brand> | `2026-09-19-2322` | 8 stories, 42 of 44 quotes verified, 2 stories demoted to open, lint clean → `brands/<brand>/story.md` written |
