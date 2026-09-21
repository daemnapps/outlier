# Workflow A — Import & Bank (link lane)

Turn a Figma link into a registered set of email designs, each one read block
by block.

**Input: a link.** A board section link runs the whole board. A frame link
runs one email. That is the whole ask on Damon (ruled 2026-08-31).

**Read this whole file before executing it.** Run order across the lane:
A → C → B → D.

---

## 1. Resolve the link (no network)

```bash
python3 tools/links.py add --brand <brand> --name "<Board Name>" --link "<url>"
```

It prints the file key and the node id and records the board so it is named
once. `links.py show --brand <brand> --name "<board>"` gets them back later.

A Figma link carries `node-id=3589-29`; the tools want `3589:29`. `links.py`
does that conversion — never do it by hand and never guess a node id.

## 2. Enumerate the board's email frames

```
get_metadata(fileKey=<key>, nodeId=<board node>)
```

Returns the board's children with names, types, positions and sizes — the
whole inventory in one call. This is the cheapest call in the lane; it is how
you find out what you are dealing with before spending anything.

**Identify email artboards by geometry, not by name.** Names are helpful here
(unlike the Desktop lane, where the extracted bundles carry none) but they are
not reliable — designers name frames anything. The signature:

- width **550–820px** — never hardcode 600. One file legitimately used 600,
  660 and 800, and a hardcoded 600 has silently dropped whole boards twice.
- height **500–6500px**.
- **top-level within the board** — drop any frame contained by another, or you
  will read a card inside an email as an email.

Write the frame list to `runs/<brand>-<board>/frames.json` before reading
anything. That file is the run's spine: it survives the rate cap, and a
resumed run reads it instead of re-enumerating.

## 3. Number them

Board code prefix, then sequence: `JAN26-01`, `JAN26-02`. Codes are 3–6
uppercase characters. Order top-row-then-left-to-right, which is how the board
is laid out and how the designer thinks about it.

The id is permanent. Everything downstream — census rows, format members,
briefs — cites it, so never renumber a board after a run. A design removed
from Figma leaves a gap in the sequence; the gap is correct.

## 4. Read each frame

Two calls per email:

```
get_screenshot(fileKey, nodeId=<frame>)        # the picture — words, imagery, order
get_design_context(fileKey, nodeId=<frame>)    # the structure — exact values
```

**Never call `get_design_context` on the board node.** Board sections run to
30,000 × 6,500px and hundreds of nested layers; the response is unusable and
the call is spent either way. One frame at a time, always.

Then run `prompts/stage1-email-board-read-v1-damon.md` with both, and write
the record to `runs/<brand>-<board>/out/<CODE>-NN.md`.

## 5. Expect the cap, and run into it deliberately

The Figma connection is capped hard on the Starter plan. A board will not
finish in one pass. So:

- **Save after every frame.** Never hold a board's reads in memory to write at
  the end — the cap arrives mid-board and takes everything unsaved with it.
- **Mark progress in `frames.json`** (`read: true`) as each frame lands.
- When the cap hits, stop cleanly, tell Damon how many landed and how many are
  left, and say the run resumes when the cap resets. Do not retry in a loop.
- On resume, read `frames.json` and skip everything already marked.

## 6. Register the run

Append the run's emails to the brand's census so the record is one record, not
one per run:

```bash
python3 ../email-production/sweep/census.py --help
```

The census tool reads the Desktop lane's exact-value transcriptions. For a
link-lane run the structure records are the input instead — same rows, same
columns, and the census file is authoritative for **what exists**, never for
what a design means.

## 7. Then image recovery

Run **workflow C** now, before looking at anything. Auditing before recovery
means auditing twice, which is the single most expensive mistake in this lane.

---

## Desktop-lane only — do not attempt here

These calls belong to Claude Desktop with the `.fig` attached, and do not
exist in this repo. Named so nobody spends a turn discovering it:
`fig_ls`, `fig_read`, `fig_grep`, `fig_materialize`, `fig_copy_files`,
`fig_screenshot`, `run_script`, `dc_write`, `show_html`, `save_screenshot`,
`get_webview_logs`, `copy_starter_component`, `present_fs_item_for_download`.

The original process for that lane is preserved verbatim in
`../reference/original-skill/`. It is the record of what actually worked at
full fidelity — read it before assuming the link lane is strictly better. It
is not: it is lighter, and it is what Damon wants to hand over.

---

## Done when

Every email frame on the board has a structure record with exact values, a
permanent id, and a row in the census — and the frames that did not make it
are named, not silently missing.
