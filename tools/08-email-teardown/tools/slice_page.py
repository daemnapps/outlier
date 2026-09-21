#!/usr/bin/env python3
"""Cut a whole Figma page into one picture per email.

    python3 tools/slice_page.py --brand <brand> --page page.png \
        --boards "July 2026=JUL26,August 2026=AUG26"

**When to use this instead of the board bundles.** Some Figma files answer
`get_metadata` with more data than the connection can carry — the response is
truncated and no node ids come back, so frames cannot be enumerated or fetched
one by one. Screenshots still work. So: take the page as one image and find the
emails in it.

How the emails are found — the same principle as everywhere else in this lane,
**geometry, never names**: an email is a run of image columns that is not the
canvas ground, at least `--min-width` wide. Boards are separated by a gutter
several times wider than the gaps between emails on the same board.

This is a fallback and it says so: it produces true pictures at full
resolution, but no structure — no exact colours, no type sizes, no block
ledger. Those need the node data. Anything read off a picture is marked as
such so nothing downstream mistakes it for a file-exact value.
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

from PIL import Image

import paths

THUMB_W = 300
SAMPLE = 5            # sample every Nth row when testing a column
TOL = 24              # colour distance that counts as "not the ground"


def ground(im):
    """The canvas colour — taken from the page's own corners, never assumed."""
    w, h = im.size
    px = im.load()
    from collections import Counter
    c = Counter()
    for x, y in ((w - 3, h - 3), (3, h - 3), (w - 3, 3)):
        c[px[x, y]] += 1
    return c.most_common(1)[0][0]


def columns(im, bg, top, min_width):
    """Runs of columns holding content. Each run is one email."""
    w, h = im.size
    px = im.load()

    def d(p):
        return abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2])

    def has(x):
        n = 0
        for y in range(top, h, SAMPLE):
            if d(px[x, y]) > TOL:
                n += 1
                if n > 4:
                    return True
        return False

    runs, s = [], None
    for x in range(w):
        if has(x):
            if s is None:
                s = x
        elif s is not None:
            if x - s >= min_width:
                runs.append((s, x))
            s = None
    if s is not None and w - s >= min_width:
        runs.append((s, w))
    return runs


def vertical(im, bg, x0, x1, top):
    """Where this email starts and ends."""
    w, h = im.size
    px = im.load()

    def d(p):
        return abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2])

    ys = [y for y in range(top, h, 4)
          if any(d(px[x, y]) > TOL for x in range(x0, x1, 7))]
    if not ys:
        return None
    return min(ys), min(h, max(ys) + 4)


def group(runs):
    """Split the emails into boards on the wide gutters between sections."""
    if len(runs) < 2:
        return [runs]
    gaps = [runs[i + 1][0] - runs[i][1] for i in range(len(runs) - 1)]
    typical = sorted(gaps)[len(gaps) // 2]
    cut = max(typical * 2.5, typical + 60)
    out, cur = [], [runs[0]]
    for g, r in zip(gaps, runs[1:]):
        if g > cut:
            out.append(cur); cur = [r]
        else:
            cur.append(r)
    out.append(cur)
    return out


def thumb(png, out):
    im = Image.open(png).convert("RGB")
    im = im.resize((THUMB_W, max(1, int(im.height * THUMB_W / im.width))), Image.LANCZOS)
    if im.height > 1600:
        im = im.crop((0, 0, im.width, 1600))
    im.save(out, "JPEG", quality=82, optimize=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--brand", required=True)
    ap.add_argument("--page", required=True, help="the page, screenshotted at native size")
    ap.add_argument("--boards", required=True,
                    help='board names in left-to-right order: "July 2026=JUL26,August 2026=AUG26"')
    ap.add_argument("--top", type=int, default=0,
                    help="ignore everything above this y (section headers, subject cards)")
    ap.add_argument("--min-width", type=int, default=250)
    ap.add_argument("--file-key", help="record which Figma file these came from")
    ap.add_argument("--node", help="record which page node")
    a = ap.parse_args()

    im = Image.open(a.page).convert("RGB")
    bg = ground(im)
    runs = columns(im, bg, a.top, a.min_width)
    if not runs:
        sys.exit("found no emails — check --top and that the page is the native-size render")
    groups = group(runs)

    names = []
    for part in a.boards.split(","):
        n, _, c = part.partition("=")
        names.append((n.strip(), (c or n).strip().upper()))
    if len(names) != len(groups):
        print(f"WARNING: found {len(groups)} board(s) on the page but was given "
              f"{len(names)} name(s). Groups: {[len(g) for g in groups]}", file=sys.stderr)
        while len(names) < len(groups):
            names.append((f"board {len(names)+1}", f"B{len(names)+1}"))

    outdir = paths.designs_dir(a.brand)
    (outdir / "thumbs").mkdir(parents=True, exist_ok=True)
    idx_path = outdir / "index.json"
    index = json.loads(idx_path.read_text()) if idx_path.exists() else {}

    src_path = paths.source_file(a.brand)
    src = json.loads(src_path.read_text()) if src_path.exists() else \
        {"brand": a.brand, "channel": "email", "figma": {}, "boards": []}

    for (name, code), part in zip(names, groups):
        slug = name.lower().replace(" ", "-")
        print(f"{code}  {name} — {len(part)} emails")
        n = 0
        for x0, x1 in part:
            v = vertical(im, bg, x0, x1, a.top)
            if not v:
                continue
            y0, y1 = v
            n += 1
            eid = f"{code}-{n:02d}"
            crop = im.crop((x0, y0, x1, y1))
            png = outdir / f"{eid}.png"
            crop.save(png)
            thumb(png, outdir / "thumbs" / f"{eid}.jpg")
            index[eid] = {"id": eid, "board": slug, "n": n,
                          "w": crop.width, "h": crop.height,
                          "file": png.name, "thumb": f"thumbs/{eid}.jpg",
                          "source": "page slice",
                          "note": "picture only — no file-exact structure"}
            print(f"  {eid}  {crop.width}x{crop.height}")

        src["boards"] = [b for b in src["boards"] if b["slug"] != slug]
        src["boards"].append({
            "name": name, "slug": slug, "code": code,
            "node_id": a.node, "file_key": a.file_key or src["figma"].get("file_key"),
            "url": (f"https://www.figma.com/design/{a.file_key}/?node-id="
                    f"{(a.node or '').replace(':', '-')}" if a.file_key else None),
            "emails": n, "added": date.today().isoformat(), "source": "page slice",
        })

    src["boards"].sort(key=lambda b: b["slug"])
    if a.file_key:
        src["figma"].setdefault("file_key", a.file_key)
    src_path.parent.mkdir(parents=True, exist_ok=True)
    src_path.write_text(json.dumps(src, indent=2) + "\n")
    idx_path.write_text(json.dumps(index, indent=1, sort_keys=True) + "\n")
    print(f"\n{len(index)} emails in {outdir}")


if __name__ == "__main__":
    main()
