# Workflow C — Image Recovery

Get the real imagery out of the file, and label what could not come. Run
straight after A, before anything is looked at.

**Why it is its own workflow:** in the Desktop lane the extractor silently
dropped 20–78 images per board against its asset budget, and the boards
rendered flat color where hero photos belong. Damon's words for it were
"broken / not full". The link lane fails differently — but it does fail, so
the check is the same.

---

## 1. Pull the assets

```
download_assets(fileKey, nodeId=<frame>, ...)
```

per frame, into `runs/<brand>-<board>/frames/<CODE>-NN/`. Ask for the real
bitmaps, not a re-render — a re-render of a photo is an approximation, and
approximated imagery is banned in this lane.

## 2. Diff against the structure record

Every `[SLOT: …]` in the stage-1 record must have a file. Every file must have
a slot. Both directions:

- **slot with no file** — the recovery target. Try the frame's own node, then
  the parent, then the component the fill came from. Component-default images
  are the ones that hide: the fill lives on the component, not the instance,
  so a per-frame pull never sees it.
- **file with no slot** — the record missed a block. Re-read the frame; do not
  quietly drop the file.

## 3. What cannot come, gets labelled

Anything still missing becomes a placeholder that states its own size:
`IMAGE 600×760`, on a striped ground, with a 2px inset outline.

**Never approximate imagery.** Do not generate a stand-in, do not substitute a
similar photo, do not redraw. Damon generates the real images later from the
slot brief — a labelled gap is useful to him and a plausible fake is not.

Two assets in the <brand> run were too large to transfer at all. They are
placeholders, they are named in the handoff, and that is the correct outcome.

## 4. Verify on the worst frame

Take the frame with the most missing slots and check it end to end. If that
one is whole, the pass worked. Checking the easy ones proves nothing.

---

## Done when

Every recoverable image is in the run with its original crop, every
unrecoverable one shows a labelled, sized placeholder, and Damon has been told
by name which ones could not come.
