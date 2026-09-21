# Structure Map

What each artifact is, where it lives, and which stage creates it. Read this before touching a project mid-run so you know what already exists.

## Project shape after a full run

```
<project root>
├── <Brand> Email Format Bank.dc.html      # hub: links every board page          [workflow-a §7]
├── Format Bank - <Board>.dc.html × N      # one page per Figma board section      [workflow-a §5–6]
├── <Brand> Format Library.dc.html         # deduped named templates FMT-01…NN     [workflow-b]
├── fonts.css                              # every Figma family alias → real files [workflow-a §4]
├── fonts/                                 # brand .woff2 cuts                     [workflow-a §4]
├── assets/<brand>.svg                     # wordmark                              [workflow-b]
├── image-slot.js                          # drag-drop placeholder component       [workflow-b]
├── module-fixes.js                        # runtime nudges for module artifacts   [workflow-b §5]
├── boards/<slug>/
│   ├── Components.bundle.js               # the board render (plain JS globals)    [workflow-a §3]
│   ├── Components.d.ts                    # READ THIS for the global's real name
│   ├── fig-assets.css                     # hash → background rules
│   ├── assets/                            # extracted + recovered bitmaps         [workflow-a §3, workflow-c]
│   └── patch.json                         # {geo:[{w,h,file,bg,nth?}]}            [workflow-c]
├── vfs-src/<slug>.jsx                     # EXACT-VALUE ground truth per board    [workflow-a §3]
├── vfs-src/<slug>-c/<Component>.jsx       # component geometry for override images [workflow-c]
├── WORKFLOW - Email Format Bank.md        # plain-language process doc for the user
└── design_handoff_<name>/README.md         # dev handoff brief                     [workflow-d]
```

## What is authoritative for what

| Question | Source of truth |
|---|---|
| Exact geometry, color, type value | `vfs-src/<slug>.jsx` (transcribed from the .fig binary) |
| Does this email really look like that? | `fig_screenshot(<section id>)` — whole board at once |
| The global name to mount | `boards/<slug>/Components.d.ts` (names derive from layer names) |
| Every board section id | `fig_grep("/<page>", "figma node: \\d+:\\d+ \\(SECTION\\)")` |
| Brand fonts, colors, component families | `/METADATA.md` in the .fig VFS |
| Which images went missing | `[asset-skipped]` warnings in each `fig_materialize` result |

## Naming conventions

- Board dirs: lowercase-hyphen month/flow, e.g. `jan-2026`, `feb-2025-flow`, `flow-results-request`.
- Board codes: 3–6 uppercase chars, e.g. `JAN26`, `FEBFL`, `WEL25`, `RESREQ`. Emails auto-number: `JAN26-04`.
- Library formats: `FMT-01 · NAME`. Shared modules: `MOD-01 · NAME`.
- Page filenames: `Format Bank - <Board>.dc.html` (hyphens only — em dashes are rejected by the filesystem).
