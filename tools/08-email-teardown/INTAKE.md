# Intake — how a brand's emails enter

The standard. Every brand's email designs come in the same way and land in the
same shape, so nothing about the second brand is a fresh decision.

---

## The rule that decides everything

**The brand owns its design record. The machine owns the process.**

Nothing about a brand lives in this folder — not its Figma file, not its
boards, not its formats, not its tokens. A second tool will need every one of
those (the renderer needs the tokens, the sweep needs the boards, a future
asset pull needs the file), and the brand cabinet's standing test is *would a
second tool need it?* If yes, it lives in the brand.

## Where a brand's emails live

```
brands/<brand>/email/design-formats/
├── README.md          what this is, what state it is in, when it was last read
├── source.json        the Figma file + every board: name, code, node, count
├── census.json/.md    every email registered — the index
├── formats.md         the named format set + the template specs
├── components.json    the brand's email skin — the tokens the renderer builds with
└── sweep/<board>.json/.md    per-board measurement and defects
```

Pictures never enter git. They mirror the same path on Drive:
`Shared Assets/brands/<brand>/email/design-formats/`.

This shape is in the brand cabinet's `_TEMPLATE`, so a brand created from the
template already has the home — intake fills it rather than inventing it.

## Standing a brand up

```bash
python3 tools/intake.py --brand <brand> \
    --link "https://www.figma.com/design/<file>/<name>?node-id=<board>"
```

That one command:

1. creates `design-formats/` from the template if it is not there;
2. records the Figma file as the brand's design source;
3. registers the board — name, unique code, node id;
4. writes the brand's `README.md` with its real state;
5. prints what is registered and what to run next.

Paste more links to add more boards; each `intake.py --link` adds one. A brand
that already has a format-bank export skips the pasting entirely:

```bash
python3 tools/intake.py --brand <brand> --bank "<path to format-bank>" \
    --file-key <figma file key>
```

That reads the board ids out of the export's own transcriptions and registers
every board at once, spending no Figma calls. This is how <brand>'s 18 boards
were registered.

## The codes

Every board gets a prefix, and every email on it is that prefix plus its
number: `JAN26-04`. The convention, applied automatically:

| Board | Code |
|---|---|
| a month's campaign | `JAN26`, `SEP25` — month + year |
| a month's flows | `FEBFL`, `NOVFL` — month + FL |
| a welcome series | `WEL25` |
| a results / request flow | `RESREQ` |
| anything else | first letters + year |

**No two boards may share a code.** An ambiguous `JAN25-04` points at two
different emails and every citation downstream breaks. `intake.py` refuses a
duplicate rather than issuing one.

## What intake does not do

It does not read the designs. Intake is registration — the boards exist, they
are named, they are addressable. Reading them is workflow A, and it happens
board by board against the Figma cap.

## The order, once a brand is in

| | | |
|---|---|---|
| 1 | `workflows/workflow-a-import-and-bank.md` | read every board's frames |
| 2 | `workflows/workflow-c-image-recovery.md` | pull the imagery, label what cannot come |
| 3 | `workflows/workflow-b-format-library.md` | group into named formats, spec each |
| 4 | `workflows/workflow-d-handoff.md` | the document production builds from |

Then `python3 tools/build_page.py --brand <brand>` and republish that brand's
page.

## Second brand, third brand

Nothing above names a brand. The prompts carry no brand. The tokens come out
of the brand's own file every time — never from what we know about the brand,
never from a public library, never from the last brand we ran. A brand we have
never seen goes through exactly these five commands.
