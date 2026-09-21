# Worked Example — <brand> Email Design System

The real end-to-end run this skill was extracted from. Aug 2026. Every number here is what actually happened, including the failures.

## Input
One `.fig` ("<brand> -> Damon"), 193,626 nodes, 4 pages (`Design—Flow`, `Approved`, `Landing-Page`, `Archive`), all frames checked. No font pack initially.

## Scope answers
Both (recreate everything, then dedupe) · design bank now, send-ready HTML later · all of `Approved` · both granularities · mixed exact-images and slots · naming left to me.

## What got built
- **18 board pages** from the 18 SECTIONs on `Approved` — Jan 2025 → Jan 2026 campaigns plus 5 flow boards (welcome series, Feb flows, Nov flows, FLOW 2026, customer-results request). ~250 emails total.
- **Hub page** linking all 18, tagged Campaign/Flows, newest first.
- **Format Library** — 8 formats (FMT-01…08) + 4 shared modules (MOD-01…04).
- **fonts.css** mapping 6 Figma aliases → 5 real `.woff2` cuts.
- **Handoff package** with a 6.7KB brief.

## Brand tokens extracted
Ink `rgb(12,16,15)` · deep green `rgb(6,43,20)` · cream `rgb(242,246,234)` · sage `rgb(199,207,173)` · soft sage `rgb(187,199,158)` @0.3 in radial glows · co-brand Prime blue `rgb(16,92,240)` family. Serif `GT Super Ds Trial` 50–86px @0.9–1.1 (often italic); sans `Untitled Sans` body 24px/1.2, CTA 18px/500/uppercase/-0.02em. CTA box 450×61.5 (some 70.4). Glass card `linear-gradient(270deg, rgba(12,16,15,0.5), rgba(199,207,173,0.3))` + `inset 0 0 0 1px rgba(242,246,234,0.3)`, radius 20–30. Artboards: 600px standard, 660px (results-request), 800px (Aug 2025).

## Four failures, and what they taught
**1. Detection by `data-name` → every board blank.** The materialized bundles emit plain inline-styled divs with no `data-name`, so the frame scan found zero and all 18 pages showed an empty corner of a 30,000px board. Earlier screenshots had looked fine only because my capture script manually scaled the container, masking it. → Detect by geometry + computed style. Never trust a first render that a debug tweak touched.

**2. Hardcoded 600px width → two boards blank or partial.** The results-request flow uses 660px artboards; August 2025 uses 800px and showed 2 of 8 emails. → Accept 550–820px and add `overflow:hidden` + non-percentage border-radius as the artboard signature (this excludes the 800px radial glow circles that would otherwise match).

**3. Silent asset dropping → "stuff is broken / not full."** Aggregate warnings across boards: 20 skipped on Dec, 78 on Feb-flow, 63 on Sep, and so on. Recovered ~105 bitmaps by parsing `vfs-src` and re-copying; two 21MB textures exceeded the 20MB transfer cap and became placeholders. October's Amazon Prime logos and product box needed hand-measured entries (`440×88`, `430×88`, `contain` on white) because their fills came from component defaults the parser never saw.

**4. Fallback fonts read as layout slop.** The user's "there's still slop in these" was mostly fallback font metrics. Wiring the real pack fixed the bulk of it in one pass — which is why the skill now says get fonts before auditing.

## Cost profile
Roughly: 1 turn inventory + scope, 2 turns deep-read, 3 turns bulk materialize (18 boards), 1 turn master page, 1 turn clone ×17, 4 turns image recovery, ~20 turns self-audit (this is the expensive part and it is not optional), 1 turn library, 1 turn handoff.

## What the user asked for that I did not anticipate
- "I don't have time to look at everything — do that work for me." Auditing all 18 boards myself was the deliverable, not a courtesy. Budget for it.
- "We will generate images, so we just need clear placeholders." Labeled, sized placeholders beat approximated imagery. Never redraw a photo.
