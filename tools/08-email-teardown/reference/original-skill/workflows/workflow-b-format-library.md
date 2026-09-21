# Workflow B — Format Library

Dedupe the bank into a small set of named, reusable templates that become the brand's production email system. Run after workflow-a and workflow-c.

---

## 1. Identify the recurring formats
Walk the board screenshots you took in workflow-a §10 and group emails by **layout skeleton**, not by campaign topic. Expect 6–10 distinct formats across a year. From the <brand> run, the recurring set was:

| Code | Format | Signature |
|---|---|---|
| FMT-01 | Hero Announcement (dark) | wordmark → giant serif headline → CTA → product shot → body → repeat CTA |
| FMT-02 | Benefits Stack | intro → 3–5 glass rows, icon + title/desc → closing line → CTA |
| FMT-03 | Big Type + Steps | tracked uppercase kicker over an oversized accent word, then numbered circle steps |
| FMT-04 | Social Proof | 3×2 customer photo grid + alternating quote cards with quote-mark glyph |
| FMT-05 | Offer Countdown | serif lead-in over 120px+ uppercase two-word urgency, product, checklist |
| FMT-06 | Results Timeline | one glass panel, arrow-marked time milestones split by hairlines |
| FMT-07 | Light Editorial | cream background, serif headline, long-form centered copy, dark CTA |
| FMT-08 | Full-Bleed Hero | edge-to-edge photo with scrim + overlaid wordmark/headline, copy below |

Also note **lane variants** worth adding later: co-branded/retail lanes (e.g. Prime Day blue), seasonal treatments (BFCM torn paper), welcome-series and abandoned-cart ladders.

## 2. Build the library as ONE Design Component
`<Brand> Format Library.dc.html`. Header block explains the codes and links back to the bank hub. Then a horizontal row of format columns, each: a badge (`FMT-01 · HERO ANNOUNCEMENT (DARK)`) above a 600px artboard.

Non-negotiables:
- **Flex/grid with real brand tokens** — not absolute-position soup. The bank is the pixel record; the library is the maintainable source. Copy must be editable in place, which means real text nodes in the template, never `React.createElement` subtrees.
- **Inline styles only**, repeated literally per format (this is a DC — see the authoring spec).
- Include `<meta name="design_doc_mode" content="canvas">` so the user can pan/zoom the row.
- Every image is a `<image-slot id="fmtNN-name" placeholder="...">` — `copy_starter_component("image_slot.js")`, loaded via `<script src="./image-slot.js">` in the helmet. Distinct ids so drops persist.
- Reuse the brand's actual primitives verbatim: CTA geometry, glass-card gradient + inset stroke, radial glow, hairline divider, type scale. Take the numbers from `vfs-src`, never rounded to an 8px grid.

## 3. Add the shared modules
`fig_materialize` the brand's standalone components (typically Preheader, Header, Nav, Footer, CTA, Link CTA variants, Icons) to `components/`, `moduleFormat:"bundle"`, then `read_file components/Components.d.ts` for the real names. Mount each in a "Shared modules" section as `MOD-01…NN` via:
```html
<x-import component-from-global-scope="Footer" from="./components/Components.bundle.js" hint-size="600px,400px"></x-import>
```
This puts the canonical header/footer in one place instead of re-drawn per format.

## 4. Wordmark
`fig_copy_files` the brand SVG out of any board dir → `assets/<brand>.svg`. On dark backgrounds a cream wordmark exported as dark may need `filter: invert(1) brightness(2)`.

## 5. Patch module artifacts
Materialized components carry occasional absolute-positioning artifacts — underline strokes crossing through text, footer lines colliding. Fix cosmetically with a small `module-fixes.js` loaded in the helmet (poll on an interval, match by text content, nudge offsets/heights), and list them in the handoff so they get folded into real code.

## 6. Cross-link
Bank hub → library, library → bank. URL-encode spaces in hrefs (`<brand>%20Format%20Library.dc.html`).

---

## Done when
Every recurring layout exists once as a clean template with editable copy and labeled image slots, the shared modules render correctly, and both pages link to each other.
