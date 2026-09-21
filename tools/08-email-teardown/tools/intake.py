#!/usr/bin/env python3
"""Stand a brand's email designs up. One command, same shape every brand.

    # a brand with a Figma link
    python3 tools/intake.py --brand <brand> --link "<figma board url>"

    # a brand that already has a format-bank export
    python3 tools/intake.py --brand <brand> --bank "<path>" --file-key <key>

    # what is registered
    python3 tools/intake.py --brand <brand> --status

Creates the brand's `email/design-formats/` home, records the Figma file as the
brand's design source, registers each board with a unique code, and writes the
brand's README with its real state. Deterministic — no model, no network.

It registers. It does not read the designs; that is workflow A.
"""
import argparse
import json
import sys
from datetime import date

import paths
from links import parse_link, unique_code, SECTION, BOARD_REF
from pathlib import Path

README = """# Email design formats — {brand}

The brand's own email designs, registered and read. Built and maintained by
the email-teardown lane (`email-teardown/`); the shape is the one
every brand uses — see that machine's `INTAKE.md`.

| | |
|---|---|
| `source.json` | the Figma file and every board — name, code, node id |
| `census.json` / `.md` | every email registered. The index: what do we have |
| `formats.md` | the named format set and each one's template spec |
| `components.json` | the brand's email skin — the tokens the renderer builds with |
| `sweep/` | per-board measurement and the defects found |

**Pictures are not here.** They mirror this path on Drive:
`Shared Assets/brands/{brand}/email/design-formats/`.

**Every email has a permanent id** — its board's code plus its number,
`{example}`. The same id names it in the census, in a format's member list,
and in the folder of pictures. Never renumber a board.

## State

{state}

*Last written {today} by `intake.py`.*
"""


def load(brand):
    p = paths.source_file(brand)
    if p.exists():
        return json.loads(p.read_text())
    return {"brand": brand, "channel": "email", "figma": {}, "boards": []}


def save(brand, src):
    src["boards"].sort(key=lambda b: b["slug"])
    p = paths.source_file(brand)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(src, indent=2) + "\n")
    return p


def ensure_home(brand):
    """The home, from the brand cabinet's shape. Never clobbers what is there."""
    d = paths.design_formats(brand)
    if not paths.brand_dir(brand).is_dir():
        sys.exit(f"no brand folder for {brand!r} at {paths.brand_dir(brand)}.\n"
                 f"Brands live in the cabinet ({', '.join(paths.known_brands()) or 'none yet'}) "
                 f"and are created from _TEMPLATE — create the brand first.")
    created = not d.exists()
    (d / "sweep").mkdir(parents=True, exist_ok=True)
    return d, created


MARKER = "by `intake.py`"


def write_readme(brand, src):
    """Never clobber a record someone else wrote by hand."""
    d = paths.design_formats(brand)
    existing = d / "README.md"
    if existing.exists() and MARKER not in existing.read_text():
        print(f"  (kept the hand-written {existing.relative_to(paths.LAB.parent.parent)} "
              f"— state is in source.json)")
        return
    boards = src["boards"]
    read = sum(1 for b in boards if b.get("emails"))
    if not boards:
        state = ("Home created; no boards registered yet. Paste a Figma link:\n\n"
                 "```\npython3 tools/intake.py --brand %s --link \"<figma board url>\"\n```" % brand)
    else:
        total = sum(b.get("emails") or 0 for b in boards)
        lines = ["| Code | Board | Emails | Node |", "|---|---|---|---|"]
        lines += [f"| `{b['code']}` | {b['name']} | {b.get('emails') or '—'} | "
                  f"`{b['node_id']}` |" for b in boards]
        state = (f"**{len(boards)} board(s) registered**"
                 + (f", {read} read, {total} emails on record." if total else
                    ", none read yet — that is workflow A.")
                 + "\n\n" + "\n".join(lines))
    example = (boards[0]["code"] + "-04") if boards else "JAN26-04"
    (d / "README.md").write_text(
        README.format(brand=brand, state=state, example=example, today=date.today().isoformat()))


def counts_from_census(brand):
    """If the brand already has a census, hang each board's count off it."""
    p = paths.census_file(brand)
    if not p.exists():
        return {}
    try:
        rows = json.loads(p.read_text()).get("emails") or []
    except (ValueError, TypeError):
        return {}
    out = {}
    for r in rows:
        if isinstance(r, dict) and r.get("board"):
            out[r["board"]] = out.get(r["board"], 0) + 1
    return out


def add_board(src, *, name, slug, node_id, file_key, url, source):
    boards = src["boards"]
    # one board, one row — keyed on the node it actually points at
    boards[:] = [b for b in boards if b["node_id"] != node_id and b["slug"] != slug]
    row = {
        "name": name, "slug": slug,
        "code": unique_code(name, {b["code"] for b in boards}),
        "node_id": node_id, "file_key": file_key, "url": url,
        "added": date.today().isoformat(), "source": source,
    }
    boards.append(row)
    return row


def from_link(brand, link, name=None):
    info = parse_link(link)
    if not info["node_id"]:
        sys.exit("that link points at the whole file, not a board. Open the board "
                 "in Figma, select it, and copy the link again.")
    src = load(brand)
    src["figma"].setdefault("file_key", info["file_key"])
    src["figma"].setdefault("file_name", info["file_name"])
    src["figma"].setdefault("url", f"https://www.figma.com/design/{info['file_key']}/")
    if src["figma"]["file_key"] != info["file_key"]:
        print(f"NOTE: this board is in a different Figma file "
              f"({info['file_key']}) than the brand's registered one "
              f"({src['figma']['file_key']}).", file=sys.stderr)
    label = name or info["file_name"] or info["node_id"]
    slug = __import__("re").sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    row = add_board(src, name=label, slug=slug, node_id=info["node_id"],
                    file_key=info["file_key"], url=link.strip(), source="link")
    return src, [row]


def from_bank(brand, bank, file_key):
    bank = Path(bank).expanduser()
    if not (bank / "vfs-src").is_dir():
        sys.exit(f"no vfs-src/ under {bank} — is that the format-bank folder?")
    titles = {}
    for page in bank.glob("Format Bank - *.dc.html"):
        m = BOARD_REF.search(page.read_text(errors="ignore"))
        if m:
            titles[m.group(1)] = page.name[len("Format Bank - "):-len(".dc.html")]

    src = load(brand)
    src["figma"].setdefault("file_key", file_key)
    src["figma"].setdefault("url", f"https://www.figma.com/design/{file_key}/")
    added = []
    for jsx in sorted((bank / "vfs-src").glob("*.jsx")):
        m = SECTION.search(jsx.read_text(errors="ignore")[:400_000])
        if not m:
            print(f"  no section id in {jsx.name} — skipped", file=sys.stderr)
            continue
        s = jsx.stem
        name = titles.get(s, s.replace("-", " ").title())
        added.append(add_board(src, name=name, slug=s, node_id=m.group(1),
                               file_key=file_key,
                               url=f"https://www.figma.com/design/{file_key}/"
                                   f"?node-id={m.group(1).replace(':', '-')}",
                               source="format-bank backfill"))
    return src, added


def report(brand, src):
    boards = src["boards"]
    print(f"\n{brand} — {len(boards)} board(s) registered")
    print(f"  source: {paths.source_file(brand)}")
    if src["figma"].get("file_key"):
        print(f"  figma:  {src['figma']['file_key']}")
    for b in boards:
        print(f"  {b['code']:<7} {b['name']:<38} {str(b.get('emails') or '—'):>4}  {b['node_id']}")
    unread = [b["code"] for b in boards if not b.get("emails")]
    print()
    if unread:
        print(f"Not read yet: {', '.join(unread)}")
        print("Next: workflows/workflow-a-import-and-bank.md, one board at a time.")
    else:
        print("Every registered board has emails on record.")
    print(f"Then: python3 tools/build_page.py --brand {brand}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--brand", required=True)
    ap.add_argument("--link", help="a Figma link to one board")
    ap.add_argument("--name", help="what to call that board (defaults to the file name)")
    ap.add_argument("--bank", help="an existing format-bank export to backfill from")
    ap.add_argument("--file-key", help="the Figma file the bank's boards live in")
    ap.add_argument("--status", action="store_true", help="show what is registered")
    a = ap.parse_args()

    d, created = ensure_home(a.brand)
    if created:
        print(f"created {d}")

    if a.status or not (a.link or a.bank):
        src = load(a.brand)
    elif a.bank:
        if not a.file_key:
            sys.exit("--bank needs --file-key (the Figma file its boards live in)")
        src, added = from_bank(a.brand, a.bank, a.file_key)
        print(f"{len(added)} board(s) from the bank")
    else:
        src, added = from_link(a.brand, a.link, a.name)
        print(f"registered {added[0]['code']} — {added[0]['name']}")

    for b in src["boards"]:
        n = counts_from_census(a.brand).get(b["slug"])
        if n:
            b["emails"] = n
    save(a.brand, src)
    write_readme(a.brand, src)
    report(a.brand, src)


if __name__ == "__main__":
    main()
