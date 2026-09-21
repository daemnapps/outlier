# Workflow D — Dev Handoff

Package the bank + library so Claude Code (or any developer) can run the cleanup sweep and build the production email system from it. Run last.

---

## 1. Write the brief
`design_handoff_<name>/README.md`. Self-sufficient — a developer who was not in the conversation implements from this alone.

Required sections:

**Overview + mission.** What is in the project (N emails across N boards, date range) and the two jobs: the cleanup sweep, and extracting the canonical production template set.

**About the design files.** State plainly that these are design references created in HTML, not production code to copy. Board pages render machine-extracted bundles — ground truth for LOOK only. The library is hand-coded and closer to shippable.

**Fidelity.** High — all geometry/color/type are exact transcriptions. Where an extraction artifact contradicts obvious intent, fix toward intent.

**File map.** Every artifact and what it does, including how the runtime scaffolding works (geometry-based frame detection, `patch.json` application, placeholder painting). Use `references/structure-map.md` as the source.

**Design tokens.** Exact values, no rounding: color roles with rgb values, both font families with the real file names and the size/leading/tracking conventions, and the recurring primitives (CTA box dimensions, glass-card gradient + inset stroke, radial glow spec, hairline divider, artboard widths in play).

**Named formats.** The FMT list plus the lane variants still to extract.

**The sweep — prioritized fix list.** Ordered, specific: residual text overlap (and that fonts.css already fixed the bulk of it); baked-in solid boxes that cannot be auto-detected because they carry a solid color, to be converted to the placeholder treatment; assets that could not transfer, by hash and where they appear; folding runtime `module-fixes.js` nudges into real component code; per-format bedrock extraction.

**Interactions.** Usually "static email designs; the bank scaffolding need not survive the sweep, the emails must."

**Assets + licensing.** Where bitmaps live, the wordmark, and that the fonts are commercially licensed — do not redistribute.

## 2. Ship it
`present_fs_item_for_download` on the whole project (the handoff needs the boards, assets, fonts, and `vfs-src` ground truth, so a folder-only zip is not enough). Keep the accompanying message short so the download card is not buried.

## 3. Offer, do not assume
Ask whether they want per-board screenshots bundled in. Do not include them by default.

---

## Done when
The README stands alone, the zip is downloadable, and the fix list is specific enough that the developer never has to ask what "clean up the spacing" means.
