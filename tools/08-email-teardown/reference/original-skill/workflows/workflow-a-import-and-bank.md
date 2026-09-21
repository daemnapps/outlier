# Workflow A — Import & Bank

Turn a brand's Figma email file into a browsable, pixel-exact bank of every approved email, one page per board.

**Prerequisite:** the brand's `.fig` is attached with all pages/frames checked. Ask for the font pack now (step 4) — it removes most apparent "slop" and you do not want to audit twice.

---

## 1. Inventory (3 calls, one turn)
```
fig_ls("/", depth: 2)
fig_read("/METADATA.md")
fig_read("/README.md")
```
From METADATA record: the top colors (these ARE the brand tokens), every font family incl. trial/test aliases, and the complete "Component families" list. From the page index, identify the page holding approved work (commonly `Approved`; there is usually also an `Archive` page to skip).

## 2. Enumerate boards (1 call)
```
fig_grep("/<ApprovedPage>", "figma node: \\d+:\\d+ \\(SECTION\\)")
```
Returns every board section id at once. One SECTION = one month or flow = one bank page. Assign each a slug (`jan-2026`) and a code prefix (`JAN26`).

## 3. Scope form (1 `ask_user`, then STOP)
Ask only what changes the build: deliverable shape (recreate-all / dedupe-only / both), what the code must serve (design bank now vs send-ready email HTML), board priority, format granularity (whole emails / modules / both), image handling (exact vs slots vs mix). Do not ask about visual style — the .fig is the answer. End the turn; answers arrive later.

## 4. Read one board deeply, then bulk-import
1. Newest board first: `fig_read` its `index.jsx` in full, plus every sibling component `.jsx` in ONE batched call. This is where you learn the brand's primitives — artboard width, CTA geometry, card/glow/divider treatments, type scale. Write them down; they become the Format Library tokens.
2. `fig_materialize({frames:["<section id>"], dest:"boards/<slug>", moduleFormat:"bundle"})`, then `read_file boards/<slug>/Components.d.ts` for the real global name (names derive from Figma layer names).
3. Bulk-materialize the rest, ~6 sections per turn in parallel calls. **Copy every `[asset-skipped]` warning into your notes** — those are workflow-c's input.
4. `fig_copy_files` each board's `index.jsx` → `vfs-src/<slug>.jsx`. Ground truth for auditing and image recovery.

## 5. Fonts — do this BEFORE auditing
`fig_materialize` ships no `@font-face`; fallback metrics cause text drift and overlap that look like layout bugs.
1. `copy_files` the brand `.woff2` cuts into `fonts/`.
2. Write `fonts.css` mapping **every alias in METADATA's font list** to the real files — including trial/test aliases (`GT Super Ds Trial`, `Test Untitled Sans`) and junk aliases (`… Not Licensed for Desktop Use`). Use weight ranges (`font-weight: 500 700`) to cover cuts the pack lacks.
3. `linkFonts()` from `scripts/snippets.js` injects the stylesheet link into every `.dc.html`.
4. Note missing cuts (italic, true bold) for the user — browsers synthesize them.

## 6. Build ONE board page (the MASTER)
Use `assets/MASTER-board-page.md` verbatim, substituting the brand tokens and the newest board's slug/global/title/code. `dc_write` it, then `show_html` + `save_screenshot` to confirm emails render and badges land.

Three rules that cost a rebuild each if broken:
- **Detect frames by geometry + computed style, never `data-name`** (bundles do not emit it) and **never a hardcoded width** (one file legitimately used 600, 660, and 800).
- **Always crop.** Board sections are ~30,000 × 6,500px with emails in a horizontal row.
- **Always have the no-match fallback**, so a page can never render dead space.

## 7. Clone to every other board
`cloneBoardPages()` in `scripts/snippets.js`. Then spot-check two clones — one campaign board, one flow board.

## 8. Hub page
`<Brand> Email Format Bank.dc.html`: header block plus a 3-column grid of cards linking every board page, each showing tag (Campaign/Flows) + code + title, newest first. Add a closing block linking the Format Library once workflow-b runs.

## 9. Recover images
Run **workflow-c** now. Do not audit before it — you will re-audit everything.

## 10. Audit every board yourself
The user should not have to find defects. For each board: `show_html`, then `save_screenshot` with a step that scales the crop container (`document.body.style.zoom` is the most reliable scaler) and a 2–2.5s delay for bundle + patches to settle.

- Suspect an email? `fig_screenshot(<section id>)` renders the whole board cheaply. Several "broken" emails in the <brand> run were genuinely off-palette in Figma (co-branded Prime Day blues) — confirm before "fixing."
- To inspect rather than squint: put diagnostic `console.log`s in the screenshot step's `code`, then `get_webview_logs`. Log candidate element sizes, computed backgrounds, and patch match counts.
- Defect classes actually caught this way: a board rendering 2 of 8 emails (width filter too narrow), missing logos/product shots (component-default images the extractor dropped — read their rendered size from the DOM and add a `patch.json` entry), leftover placeholder SVGs sitting on top of restored images, and excess dead space above the first email (`padTop`).

## 11. Placeholders
Anything still imageless gets an obvious sized placeholder — the user generates images later, so clarity beats guessing. `markPlaceholders` in the MASTER: striped accent gradient, 2px inset outline, centered `IMAGE <w>×<h>` label, restricted to detected email frames.

---

## Done when
Every board page renders every email with real fonts, correct imagery or a labeled placeholder, sequential format badges, and no dead space — and you have personally looked at all of them.
