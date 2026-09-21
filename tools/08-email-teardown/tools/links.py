#!/usr/bin/env python3
"""A Figma link in, the file + node a run needs out — and a register per brand
so a board is pasted once and named forever.

    python3 tools/links.py parse "<figma url>"
    python3 tools/links.py list  --brand <brand>
    python3 tools/links.py show  --brand <brand> --name "January 2026"

Deterministic, no network, no model. **Reading only.** The register belongs to
the brand — `brands/<brand>/email/design-formats/source.json` — and `intake.py`
is its only writer, so a board can never be registered two ways.

Why this exists: a Figma URL writes a node as `3589-29` and every tool wants
`3589:29`. Converting that by hand is how a run reads the wrong board.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

import paths

# /design/<key>/<name> — also /file/ (older links) and /board/ (FigJam, refused)
PATH = re.compile(r"^/(?P<kind>design|file|board|slides|make)/(?P<key>[0-9a-zA-Z]{22,128})(?:/(?P<name>[^/]*))?")


def parse_link(url):
    """Figma URL -> {kind, file_key, node_id, file_name}. Raises on anything
    this lane cannot read."""
    u = urlparse(url.strip())
    if "figma.com" not in (u.netloc or ""):
        raise ValueError(f"not a Figma link: {url!r}")
    m = PATH.match(u.path or "")
    if not m:
        raise ValueError(f"cannot find a file key in: {url!r}")
    kind = m.group("kind")
    if kind in ("board", "slides", "make"):
        raise ValueError(
            f"that is a Figma {kind} link. This lane reads design files only "
            f"(the URL says /{kind}/, it needs to say /design/)")

    node = None
    q = parse_qs(u.query or "")
    raw = (q.get("node-id") or q.get("node_id") or [None])[0]
    if raw:
        node = unquote(raw).replace("-", ":", 1)
        if not re.fullmatch(r"\d+:\d+", node):
            raise ValueError(f"node id in the link looks wrong: {raw!r}")

    return {
        "kind": kind,
        "file_key": m.group("key"),
        "node_id": node,
        "file_name": unquote(m.group("name") or "").replace("--", " ").strip("- ") or None,
        "url": url.strip(),
    }


def register(brand):
    """The brand's own board register. Read here, written only by intake.py."""
    p = paths.source_file(brand)
    if p.exists():
        return p, json.loads(p.read_text())
    return p, {"brand": brand, "boards": []}


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


MONTHS = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]


def code(name):
    """A board name -> its id prefix, following the bank's own convention:
    JAN26 campaigns, FEBFL / NOVFL flows, WEL25 welcome, RESREQ the results
    request. The prefix goes in front of every email id on the board
    (JAN26-04), so it has to say which board at a glance and it has to be
    unique — `unique_code` enforces the second part."""
    n = name.lower()
    yr = re.search(r"(19|20)(\d{2})", n)
    yy = yr.group(2) if yr else ""
    mon = next((m[:3].upper() for m in MONTHS if m in n), "")

    if "welcome" in n:
        return ("WEL" + yy) or "WEL"
    if "result" in n or "request" in n:
        return "RESREQ"
    if "flow" in n:
        return (mon + "FL") if mon else ("FLOW" + yy)
    if mon:
        return mon + yy

    words = re.findall(r"[A-Za-z]+|\d{4}|\d{2}", name)
    out = ""
    for w in words:
        out += w[-2:] if w.isdigit() else w[:3].upper()
        if len(out) >= 5:
            break
    return (out or re.sub(r"[^A-Z0-9]", "", name.upper()))[:6] or "BOARD"


def unique_code(name, taken):
    """Never hand two boards the same prefix — an ambiguous JAN25-04 points at
    two different emails and every downstream citation breaks."""
    base = code(name)
    if base not in taken:
        return base
    for i in range(2, 100):
        cand = f"{base[:5]}{i}"
        if cand not in taken:
            return cand
    raise ValueError(f"cannot find a free code for {name!r}")


def cmd_parse(a):
    print(json.dumps(parse_link(a.link), indent=2))


SECTION = re.compile(r"figma node: (\d+:\d+) \(SECTION\)")
BOARD_REF = re.compile(r"boards/([a-z0-9-]+)/")


def cmd_list(a):
    p, reg = register(a.brand)
    if not reg["boards"]:
        print(f"no boards registered for {a.brand} yet — stand it up with:\n"
              f'  python3 tools/intake.py --brand {a.brand} --link "<figma board url>"')
        return
    print(f"{a.brand} — {len(reg['boards'])} board(s)  ({p})")
    for b in reg["boards"]:
        print(f"  {b['code']:<7} {b['name']:<34} {b['file_key']}  {b['node_id']}")


def cmd_show(a):
    p, reg = register(a.brand)
    want = slug(a.name)
    for b in reg["boards"]:
        if b["slug"] == want or b["code"].lower() == a.name.lower():
            print(json.dumps(b, indent=2))
            return
    sys.exit(f"no board {a.name!r} for {a.brand}. `list` shows what is registered.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("parse", help="a link in, its file + node out")
    p1.add_argument("link")
    p1.set_defaults(fn=cmd_parse)

    p3 = sub.add_parser("list", help="every board registered for a brand")
    p3.add_argument("--brand", required=True)
    p3.set_defaults(fn=cmd_list)

    p4 = sub.add_parser("show", help="one board's file + node")
    p4.add_argument("--brand", required=True)
    p4.add_argument("--name", required=True)
    p4.set_defaults(fn=cmd_show)

    a = ap.parse_args()
    try:
        a.fn(a)
    except ValueError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
