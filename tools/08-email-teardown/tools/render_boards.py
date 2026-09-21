#!/usr/bin/env python3
"""Turn a board's design bundle into one real picture per email.

    python3 tools/render_boards.py --brand <brand> --board jan-2026
    python3 tools/render_boards.py --brand <brand> --all

The bank's board bundles are self-contained pre-transpiled React — no imports,
no dependencies, every component hung on `window`. Given React and the board's
own stylesheet they render pixel-exact in an ordinary browser, which is what
this uses: headless Chrome, one page per email, the window sized to the frame
so the capture IS the email.

Writes into the BRAND, not the machine — these are existing assets of the
business, so they belong in the cabinet's `existing-content/`:

    brands/<brand>/existing-content/emails/designs/<CODE>-NN.png
    brands/<brand>/existing-content/emails/designs/thumbs/<CODE>-NN.jpg
    brands/<brand>/existing-content/emails/designs/index.json

`index.json` is words and always in git. The pictures mirror to Drive at the
same path; whether they are also committed is a size call (workspace rule 3) —
see that folder's README.

Email frames are found by geometry — 550-820px wide, 500-6500 tall,
overflow:hidden, top-level in the board. Never by layer name, never a
hardcoded width; a hardcoded 600 has silently dropped whole boards twice.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import paths

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def _react():
    """A node_modules folder holding React's browser build. Found, never
    typed: EMAIL_TEARDOWN_REACT when set, else the first one under ~/devel."""
    import os
    env = os.environ.get("EMAIL_TEARDOWN_REACT")
    if env:
        return Path(env)
    hits = sorted((Path.home() / "devel").glob("*/node_modules/react/umd/react.production.min.js"))
    return hits[0].parents[2] if hits else Path.home() / "devel" / "node_modules"


REACT = _react()
THUMB_W = 300
MAX_H = 8000          # Chrome refuses very tall windows; taller emails tile


def bank_dir(brand):
    """The format-bank export on Drive — the boards' home."""
    return paths.media_dir(brand) / "format-bank"


# One page: React, the board's stylesheet, the bundle, and a script that
# isolates a single frame at natural size against the page origin.
PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="fonts.css">
<link rel="stylesheet" href="board/fig-assets.css">
<style>
  html,body{{margin:0;padding:0;background:{bg}}}
  #m{{position:absolute;left:-99999px;top:0}}
  #one{{position:absolute;left:0;top:0}}
</style></head><body>
<div id="m"></div><div id="one"></div>
<script src="react.js"></script><script src="react-dom.js"></script>
<script src="board/Components.bundle.js"></script>
<script>
window.__ready = false;
const G = {global!r};
ReactDOM.createRoot(document.getElementById('m')).render(React.createElement(window[G]));
function frames() {{
  let f = Array.from(document.querySelectorAll('#m div')).filter(n => {{
    if (n.offsetWidth < 550 || n.offsetWidth > 820) return false;
    if (n.offsetHeight < 500 || n.offsetHeight > 6500) return false;
    const cs = getComputedStyle(n);
    return cs.overflow === 'hidden' && !cs.borderRadius.endsWith('%');
  }});
  f = f.filter(x => !f.some(y => y !== x && y.contains(x)));
  // reading order: top row first, then left to right within a row
  f.sort((a, b) => {{
    const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
    return ra.top - rb.top > 400 ? 1 : rb.top - ra.top > 400 ? -1 : ra.left - rb.left;
  }});
  return f;
}}
function show(i) {{
  const f = frames();
  const one = document.getElementById('one');
  one.innerHTML = '';
  if (!f[i]) return null;
  const c = f[i].cloneNode(true);
  c.style.position = 'static';
  c.style.left = c.style.top = 'auto';
  one.appendChild(c);
  return [f[i].offsetWidth, f[i].offsetHeight];
}}
window.__list = () => frames().map(f => [f.offsetWidth, f.offsetHeight]);
setTimeout(() => {{ window.__ready = true; }}, 400);
</script></body></html>
"""

PROBE = """
new Promise(r => {
  const go = () => window.__ready ? r(JSON.stringify(window.__list()))
                                  : setTimeout(go, 120);
  go();
});
"""


def chrome(args, timeout=120):
    return subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                           "--hide-scrollbars", "--no-sandbox",
                           "--force-device-scale-factor=1",
                           "--virtual-time-budget=4000"] + args,
                          capture_output=True, text=True, timeout=timeout)


def stage(brand, board, workdir):
    """Assemble a self-contained render directory for one board."""
    bank = bank_dir(brand)
    src = bank / "boards" / board
    if not (src / "Components.bundle.js").exists():
        sys.exit(f"no bundle for board {board!r} at {src}")
    shutil.copytree(src, workdir / "board")
    for name, rel in (("react.js", "react/umd/react.production.min.js"),
                      ("react-dom.js", "react-dom/umd/react-dom.production.min.js")):
        p = REACT / rel
        if not p.exists():
            sys.exit(f"React not found at {p} — needed to render the bundles")
        shutil.copy(p, workdir / name)
    fonts = bank / "fonts.css"
    (workdir / "fonts.css").write_text(fonts.read_text() if fonts.exists() else "")
    if (bank / "fonts").is_dir():
        shutil.copytree(bank / "fonts", workdir / "fonts")

    dts = (src / "Components.d.ts").read_text()
    # the global's real name comes from the .d.ts, never from the folder name
    import re
    m = re.search(r"interface Window \{\s*(\w+):", dts) or re.search(r"declare const (\w+):", dts)
    if not m:
        sys.exit(f"cannot find the component global in {src/'Components.d.ts'}")
    return m.group(1)


def render_board(brand, board, code, outdir, verbose=True):
    work = Path(tempfile.mkdtemp(prefix=f"render-{board}-"))
    try:
        g = stage(brand, board, work)
        page = work / "page.html"
        page.write_text(PAGE.format(**{"global": g, "bg": "#000"}))

        sizes = probe_sizes(work, page)
        if not sizes:
            print(f"  {code}: no email frames found", file=sys.stderr)
            return []

        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "thumbs").mkdir(exist_ok=True)
        rows = []
        for i, (w, h) in enumerate(sizes, 1):
            eid = f"{code}-{i:02d}"
            png = outdir / f"{eid}.png"
            shot_frame(work, page, i - 1, w, min(h, MAX_H), png)
            if png.exists():
                thumb(png, outdir / "thumbs" / f"{eid}.jpg")
                rows.append({"id": eid, "board": board, "n": i,
                             "w": w, "h": h, "file": png.name,
                             "thumb": f"thumbs/{eid}.jpg",
                             "truncated": h > MAX_H})
                if verbose:
                    print(f"  {eid}  {w}x{h}")
        return rows
    finally:
        shutil.rmtree(work, ignore_errors=True)


def probe_sizes(work, page):
    """Ask the page for its frame list, via a tiny screenshot-free run."""
    js = work / "probe.html"
    js.write_text(page.read_text().replace(
        "</body>",
        "<script>window.addEventListener('load',()=>{setTimeout(()=>{"
        "document.title=JSON.stringify(window.__list());},900);});</script></body>"))
    r = chrome(["--dump-dom", str(js)], timeout=180)
    import re
    m = re.search(r"<title>(\[.*?\])</title>", r.stdout, re.S)
    if not m:
        return []
    try:
        return json.loads(m.group(1))
    except ValueError:
        return []


def shot_frame(work, page, idx, w, h, out):
    """One email, at natural size, as a PNG."""
    one = work / f"one-{idx}.html"
    one.write_text(page.read_text().replace(
        "</body>",
        f"<script>window.addEventListener('load',()=>{{setTimeout(()=>show({idx}),700);}});"
        "</script></body>"))
    chrome([f"--screenshot={out}", f"--window-size={w},{h}", str(one)], timeout=180)


def thumb(png, out):
    from PIL import Image
    im = Image.open(png).convert("RGB")
    ratio = THUMB_W / im.width
    im = im.resize((THUMB_W, max(1, int(im.height * ratio))), Image.LANCZOS)
    # a very tall email becomes an unusable sliver — keep the top of it
    if im.height > 1600:
        im = im.crop((0, 0, im.width, 1600))
    im.save(out, "JPEG", quality=82, optimize=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--brand", required=True)
    ap.add_argument("--board", help="one board slug, e.g. jan-2026")
    ap.add_argument("--all", action="store_true", help="every registered board")
    a = ap.parse_args()

    src = paths.source_file(a.brand)
    if not src.exists():
        sys.exit(f"{a.brand} has no registered boards — run intake.py first")
    boards = json.loads(src.read_text())["boards"]
    if a.board:
        boards = [b for b in boards if b["slug"] == a.board]
        if not boards:
            sys.exit(f"no board {a.board!r} registered for {a.brand}")
    elif not a.all:
        sys.exit("pass --board <slug> or --all")

    outdir = paths.designs_dir(a.brand)
    index_path = outdir / "index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {}

    for b in boards:
        print(f"{b['code']}  {b['name']}")
        rows = render_board(a.brand, b["slug"], b["code"], outdir)
        for r in rows:
            index[r["id"]] = r
        outdir.mkdir(parents=True, exist_ok=True)
        index_path.write_text(json.dumps(index, indent=1, sort_keys=True) + "\n")
        print(f"  -> {len(rows)} emails")

    print(f"\n{len(index)} emails rendered into {outdir}")


if __name__ == "__main__":
    main()
