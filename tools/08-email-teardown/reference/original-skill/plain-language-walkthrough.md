# Workflow: Figma → Email Format Bank + Format Library

Repeatable process for turning any brand's Figma email file into (a) a browsable, pixel-exact **Format Bank** of every approved email and (b) a deduped **Format Library** of reusable named templates.

**To run this for a new brand:** attach the brand's `.fig` file (leave all pages/frames checked), attach the brand's font pack if available, and say "run the email format bank workflow on this." Everything below is what I do; no further input needed until Stage 3.

---

## Stage 0 — Scope (5 min, one question form)
1. `fig_ls("/")` + `fig_read("/METADATA.md")` + `fig_read("/README.md")` — inventory pages, colors, fonts, component families.
2. `fig_grep("/<ApprovedPage>", "figma node: \\d+:\\d+ \\(SECTION\\)")` — this returns **every board section id in one call**. Sections are the unit of work (one section = one month/flow = one bank page).
3. Ask the user (one `ask_user` form) only what changes the build: deliverable shape (recreate-all vs dedupe-only vs both), what the code is for (design bank vs send-ready HTML), board priority order, format granularity, image handling.

Naming convention I default to (unless the user has one): board pages get a code prefix per board (`JAN26`, `FEBFL`, `NOVFL`, `WEL25`, `RESREQ`), emails auto-number within the board (`JAN26-04`); library formats are `FMT-01…NN`.

## Stage 1 — Read one board deeply, then bulk-import
1. Pick the newest board. `fig_read` its `index.jsx` fully (it's the exact-value ground truth) and `fig_read` every sibling component `.jsx` in one batched call. This is where I learn the brand's primitives: artboard width, CTA geometry, card/glow/divider treatments, type scale.
2. `fig_materialize({frames:[<section id>], dest:"boards/<slug>", moduleFormat:"bundle"})` for that board. `read_file` the emitted `Components.d.ts` to get the real global name.
3. Bulk-materialize the remaining sections, ~6 per turn in parallel calls, `dest: boards/<slug>`. **Record every `[asset-skipped]` warning** — those are the images to recover in Stage 4.
4. `fig_copy_files` each board's `index.jsx` into `vfs-src/<slug>.jsx`. These are the ground-truth transcriptions used later for auditing and image recovery.

## Stage 2 — Build one board page, then clone it 17×
Build ONE `Format Bank - <Board>.dc.html` and get it right, then generate the rest with `run_script` find-and-replace (board slug, global name, title, code prefix). Never hand-write 18 near-identical files.

The board page pattern (a DC with logic class):
- `<helmet>`: `<meta name="design_doc_mode" content="canvas">`, `<link rel="stylesheet" href="boards/<slug>/fig-assets.css">`, `<link rel="stylesheet" href="fonts.css">`.
- Header block: brand kicker, board title, one-line description with the code prefix.
- Mount: `<x-import component-from-global-scope="<Global>" from="./boards/<slug>/Components.bundle.js">` inside a crop container.
- Logic class does four things on an interval poll (bundles mount async):
  1. **Detect email artboards.** Do NOT rely on `data-name` (bundles don't emit it) and do NOT hardcode a width. Query all `div`s, keep `offsetWidth 550–820 && offsetHeight 500–6500 && getComputedStyle().overflow === "hidden" && borderRadius not %`, then drop any frame contained by another. (Widths vary per brand/board: I hit 600, 660, and 800 in one file.)
  2. **Crop to content.** Compute the bounding box of found frames, size the container to it, offset the mount negatively. Sort frames top-row-then-left-to-right; pad ~180px above for badges.
  3. **Badge each email** with `<CODE>-NN`, absolutely positioned above its frame.
  4. **Apply image patches** from `boards/<slug>/patch.json` (Stage 4) and **paint placeholders** (Stage 5).
- Fallback: if no frames match after ~50 polls, crop to the bounding box of all sizable divs so the page never shows dead space.

Then a hub page (`<Brand> Email Format Bank.dc.html`): a grid of cards linking every board page, tagged Campaign/Flows, newest first.

## Stage 3 — Fonts (do this early; it removes most "slop")
`fig_materialize` ships no `@font-face`, so everything renders in fallback metrics and text drifts/overlaps. Ask the user for the brand font pack.
1. `copy_files` the `.woff2` cuts into `fonts/`.
2. Write `fonts.css` mapping **every family alias the Figma file uses** (from METADATA's font list) to the real files — including trial/test aliases like `GT Super Ds Trial`, `Test Untitled Sans`, and junk aliases like `Untitled Sans Not Licensed for Desktop Use`. Use weight ranges (`font-weight: 500 700`) to cover missing cuts.
3. `run_script` to inject `<link rel="stylesheet" href="fonts.css">` before the `<style>` tag in every `.dc.html`.

## Stage 4 — Recover dropped images (the big one)
`fig_materialize` enforces a per-image (~4MB) and aggregate (~16MB) asset budget, silently dropping large photos — often 20–78 per board. Recovery pipeline, all via `run_script`:
1. Parse each `vfs-src/<slug>.jsx` for image references two ways: (a) inline `style={{...}}` blocks containing `url(./assets/<hash>.<ext>)` — capture `width`, `height`, and the full background shorthand (crop/position values matter); (b) component-override arrays (`{ xImage: "./assets/<hash>.png" }`) mapped against the component `.jsx`'s own geometry + background template.
2. Diff against what's actually in `boards/<slug>/assets/` and what `fig-assets.css` already serves.
3. `fig_copy_files` the missing bitmaps into `boards/<slug>/assets/` (batch ~50 per call; anything >20MB can't transfer — flag it for a placeholder).
4. Write `boards/<slug>/patch.json` = `{geo:[{w,h,file,bg,nth?}]}`.
5. In each board DC, `applyPatch(root)` fetches that JSON and, for each entry, finds unused divs whose rendered box matches `w×h` (±2px) with `backgroundImage === "none"`, then sets the background (rewriting `./assets/` to the board path). `nth` disambiguates when several boxes match. Occasionally a leftover placeholder SVG sits on top — hide SVGs at the matching size.

Keep script runs chunked (~6 boards per call) — parsing 18 large JSX files in one go times out.

## Stage 5 — Clear image placeholders
Anything still missing gets an obvious, sized placeholder (the user generates images later). In `markPlaceholders(root)`: for empty divs ≥90×90 inside a detected email frame with no background image and a transparent background, apply a diagonal striped gradient in the brand accent, a 2px inset outline, and a centered label reading `IMAGE <w>×<h>`. Restrict to detected frames so board chrome isn't hit.

## Stage 6 — Audit every board myself (don't outsource this)
For each board: `show_html`, then `save_screenshot` with a step that scales the crop container to fit (`document.body.style.zoom` is the most reliable scaler) and a 2–2.5s delay for the bundle + patches. Compare against `fig_screenshot(<section id>)` when something looks suspect — several "broken" emails were genuinely off-brand in Figma (e.g. co-branded blue Prime Day sends).

Failures this catches, in my experience: boards showing only 2 of 8 emails (width assumption too narrow), missing logos/product shots (component-default images the extractor dropped — find their rendered size in the DOM and add a `patch.json` entry), and leftover placeholder shapes covering restored images.

Debug technique that works: run a `save_screenshot` step whose code logs candidate element sizes/backgrounds to the console, then read `get_webview_logs`. Faster than screenshot-squinting.

## Stage 7 — Dedupe into the Format Library
Identify recurring layouts across boards (typically 6–10 distinct formats). Build ONE hand-coded `<Brand> Format Library.dc.html`:
- Each format is a 600px column, badged `FMT-NN · NAME`, built with **flex/grid and real brand tokens** (not absolute-position soup) so copy is editable in place.
- Every image is an `<image-slot id="fmtNN-x" placeholder="...">` (via `copy_starter_component("image_slot.js")`) — drag-and-drop, persists.
- Add a "Shared modules" section mounting the brand's Figma component library (`fig_materialize` the standalone components: preheader, header, nav, footer, CTA, link CTAs) so the canonical header/footer live in one place.
- Cross-link hub ↔ library.

Materialized components sometimes carry small absolute-positioning artifacts (underline strokes struck through text, colliding footer lines). Patch cosmetically with a small `module-fixes.js` loaded in the helmet, and note them for the code sweep.

## Stage 8 — Handoff
`design_handoff_<name>/README.md` covering: overview + mission, "these are design references not production code," fidelity, full file map (what each artifact is and how the runtime scaffolding works), exact design tokens (colors/type/primitives/artboard widths), the named format list plus extraction candidates, a prioritized fix list (residual overlaps, baked-in solid boxes → placeholders, un-transferable assets, folding runtime fixes into real code), and asset/licensing notes. Then `present_fs_item_for_download`.

---

## Gotchas worth remembering
- Board sections are huge (30,000×6,500px) with emails as a horizontal row — always crop, never render raw.
- Materialized bundles emit no `data-name`; detect by geometry + computed style.
- Email artboard widths vary within one file; never hardcode 600.
- `run_script` has a 30s timeout and cannot define reusable globals across calls — chunk work and inline helpers each time.
- File paths can't contain em dashes; use hyphens in filenames.
- `fig_screenshot` is cheap ground truth for a whole board at once — use it to settle "is this broken or is it just designed that way."
- Screenshot the user's actual page state rather than trusting the first render; bundles + patches need ~2.5s to settle.
