---
name: figma-email-format-bank
description: Turns a brand's Figma email file into a pixel-exact, browsable Format Bank of every approved email (one page per board, auto-coded like JAN26-04) plus a deduped Format Library of named reusable templates, then a dev handoff for the production build. Works for ANY brand in any category — the .fig is the source of truth, never prior knowledge of the brand. ALWAYS trigger when Damon says "run the email format bank", "build the format bank", "code these emails", "document our email designs", "here's another brand's Figma", "same process for [brand]", "turn this Figma into templates", "our email design system", "dedupe our email layouts", or attaches a .fig of email designs. Also trigger when emails imported from Figma look broken, flat, or missing images. Plans and documents email DESIGN; does not write email copy, plan sends, or build Klaviyo flows.
---

# Figma Email Format Bank

One question this answers: **what are all our email designs, and which layouts do we actually reuse?**

Brands accumulate a year of approved emails inside one enormous Figma file that nobody can browse and no developer can build from. This turns that file into two artifacts: a pixel-exact bank of every send (coded, badged, browsable) and a small library of the layouts that recur — the bedrock for a production email system.

**What this does NOT do:** write email copy (that is the brand's customer-language skill + `email-copy-agent`), decide what to send or when (`email-concept-agent`, `marketing-calendar-system`), build Klaviyo/ESP flows, or generate imagery. It documents and systematizes design.

## The workflows

| Workflow | Name | Does | Detail file |
|---|---|---|---|
| A | Import & Bank | Inventory the .fig, materialize every board, build + clone board pages, fonts, self-audit | `references/workflows/workflow-a-import-and-bank.md` |
| B | Format Library | Dedupe recurring layouts into named clean templates + shared modules | `references/workflows/workflow-b-format-library.md` |
| C | Image Recovery | Recover the images the extractor silently dropped | `references/workflows/workflow-c-image-recovery.md` |
| D | Dev Handoff | Package the brief + project for the production sweep | `references/workflows/workflow-d-handoff.md` |

**Read the workflow file BEFORE executing it.** Run order: A → C → (audit) → B → D. Running C after auditing means auditing twice.

## Non-negotiables

1. **The .fig is the source of truth.** Even for a brand you know, extract tokens/components from the file. It carries custom themes and renamed variants the public brand does not.
2. **Detect email artboards by geometry + computed style**, never `data-name` (bundles do not emit it) and never a hardcoded width (one file used 600, 660, and 800). This has broken the build twice.
3. **Get the font pack before auditing.** Missing `@font-face` makes fallback metrics look like layout bugs, and you will audit everything twice.
4. **Always crop, never render raw.** Board sections run ~30,000 × 6,500px.
5. **Build one board page, verify it, then clone.** Never hand-write N near-identical files.
6. **Audit every board yourself.** The user's ask is "I don't have time to look at everything" — self-audit IS the deliverable. `fig_screenshot(<section id>)` settles "broken vs designed that way" cheaply.
7. **Never approximate imagery.** Recover the real bitmap or render a labeled, sized placeholder (`IMAGE 600×760`). Users generate images later.
8. **Exact values only.** Copy geometry, radii, type scale, and colors verbatim from `vfs-src` — never snapped to a 4/8px grid or a public library's defaults.

## Tooling constraints worth memorizing

- `run_script`: ~30s timeout, no globals across calls. Chunk boards ~6 per call; inline helpers every time.
- `fig_materialize`: per-image ~4MB / aggregate ~16MB asset budget, drops silently — read every `[asset-skipped]` warning. `fig_copy_files` refuses files >20MB.
- Component names derive from Figma layer names: always `read_file` the emitted `Components.d.ts` before writing code against a bundle.
- Filenames cannot contain em dashes.
- Bundles + runtime patches need ~2.5s to settle before a screenshot is meaningful.

## Files

- `assets/MASTER-board-page.md` — the board page template (DC template + logic class) every board is cloned from.
- `references/structure-map.md` — what each artifact is, which stage makes it, what is authoritative for what.
- `references/workflows/` — one file per workflow.
- `references/plain-language-walkthrough.md` — the whole process as one narrative read, in the user's own framing ("attach a .fig and say run it"). Good for onboarding a human or a quick orientation before opening a workflow file.
- `references/worked-example.md` — the <brand> run: 18 boards, ~250 emails, and the four failures that shaped the rules above.
- `scripts/snippets.js` — tested `run_script` bodies: clone board pages, link fonts, find missing images, build patch maps, sweep all boards.

## Companion skills

- **<brand>-customer-language** / brand language skills — for any copy that lands in these templates.
- **email-concept-agent**, **email-copy-agent**, **marketing-calendar-system** — what to send, when, and in what words. This provides the layouts they fill.
- **skill-forge** — upgrade this skill from the next run's corrections.
