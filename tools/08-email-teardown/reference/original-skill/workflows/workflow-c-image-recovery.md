# Workflow C — Image Recovery

`fig_materialize` enforces a per-image (~4MB) and aggregate (~16MB) asset budget and **silently drops** everything over it — 20–78 images per board in the <brand> run. The board renders with flat color where a hero photo should be. This is the single biggest fidelity gap and the user WILL notice it. Run this before auditing.

Symptom: emails look "broken / not full" — large flat black, white, or cream rectangles where photos belong.

---

## 1. Copy the ground truth
```
fig_copy_files: /<page>/<Board>/index.jsx → vfs-src/<slug>.jsx   (all boards, one call)
```
The VFS JSX carries exact geometry AND the full background shorthand (crop/position/scale values), which the flat-filled bundle lost.

## 2. Diff refs against what shipped
`findMissingImages()` in `scripts/snippets.js`. It parses two reference kinds:

- **Inline style blocks** — `style={{ … width: N, height: M, background: "url(./assets/<hash>.png) 50% 100% / 112% 171% no-repeat" }}`. Capture width, height, and the FULL background string; a `center / cover` substitute will crop the photo wrong.
- **Component-override arrays** — `[{ }, { xImage: "./assets/<hash>.png" }, …].map((item, i) => (<Comp {...item} />))` followed by a `{/* N× → /path/Comp.jsx */}` comment. The per-instance file is in the array; the geometry and background template live in the component's own `.jsx`.

Diff both against `ls("boards/<slug>/assets")` and against `fig-assets.css` (anything it already serves is fine — skip it, or you will double-apply).

## 3. Pull the component files, then build the maps
`fig_copy_files` each needed component `.jsx` → `vfs-src/<slug>-c/<Name>.jsx`, then run `buildPatchMaps()`. Output per board: `boards/<slug>/patch.json` = `{geo:[{w,h,file,bg,nth?}]}`.

Chunk to ~6 boards per `run_script` call — parsing 18 large JSX files in one call exceeds the 30s timeout. `run_script` also cannot stash a helper on `window` for reuse across calls; inline the function each time.

## 4. Copy the bitmaps
`fig_copy_files` the missing files from `/<page>/<Board>/assets/<hash>.<ext>` → `boards/<slug>/assets/`. Batch ~50 per call. Files over 20MB fail to transfer — drop them from `patch.json` and let workflow-a §11 render a labeled placeholder instead; tell the user which ones.

## 5. Apply at runtime
`applyPatch(root)` in the MASTER fetches the board's `patch.json` and, for each entry, finds unused `div`s whose rendered box matches `w×h` (±2px) with `backgroundImage === "none"`, then sets `background`, rewriting `./assets/` → `boards/<slug>/assets/`. Chain `markPlaceholders` in `.finally()` so placeholders only paint over what recovery could not fix.

## 6. Handle the stubborn ones
Three failure modes and their fixes, all seen live:

**Several boxes match the same size.** Add `nth` to the entry to pick the right one (`ms[e.nth || 0]`).

**An element was never in `patch.json`** because its fill lived in a component default the parser did not reach (e.g. a logo overlay). Find it empirically: run a `save_screenshot` step that logs candidate boxes, then read the log —
```js
const c = document.querySelector('[data-screen-label]');
const whites = Array.from(c.querySelectorAll('div')).filter(d => {
  const cs = getComputedStyle(d), r = d.getBoundingClientRect();
  return cs.backgroundColor === 'rgb(255, 255, 255)' && r.width > 150 && r.height > 25;
});
console.log(JSON.stringify(whites.map(d => { const r = d.getBoundingClientRect();
  return [Math.round(r.width), Math.round(r.height), getComputedStyle(d).backgroundImage.slice(0, 40)]; })));
```
Then hand-add an entry with those measured dimensions. Divide by the zoom factor if you scaled the container. For a logo on a colored plate use `center / contain no-repeat <plate color>`, not `cover`.

**A placeholder shape covers the restored image.** The extractor sometimes leaves a solid SVG/`div` on top. Verify with `document.elementsFromPoint(x, y)` at the element's center, then hide the offender by matching its size:
```js
Array.from(root.querySelectorAll("svg")).forEach(s => {
  const r = s.getBoundingClientRect();
  if (Math.abs(r.width - W) < 5 && Math.abs(r.height - H) < 5) s.style.visibility = "hidden";
});
```

## 7. Verify the worst board
Re-open the board that had the most skipped assets and screenshot it. If that one renders full, the pipeline is working.

---

## Done when
Every recoverable image renders with its original crop, un-transferable assets show labeled placeholders, and you have named those exceptions to the user.
