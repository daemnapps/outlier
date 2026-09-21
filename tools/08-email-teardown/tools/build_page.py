#!/usr/bin/env python3
"""Draws the email-teardown lane as one page: the stages, every prompt
verbatim, the boards registered, and what the record already holds.

    python3 tools/build_page.py                 # -> page.html + page.md
    python3 tools/build_page.py --brand <brand>  # include that brand's record

No model calls, no network. Reads the machine and the brand, renders both.
The prompts are rendered in full and never summarised — a rule Damon cannot
correct is a rule he cannot see.
"""
import argparse
import html
import json
import re
from datetime import date
from pathlib import Path

HOME = Path(__file__).resolve().parent.parent
BRANDS = HOME.parent / "brands"

STAGES = [
    ("1", "Read the design", "stage1-email-board-read-v1-damon.md",
     "One email design in, its structure out — every block, every exact value, every image slot named."),
    ("2", "Find the formats", "stage2-format-dedupe-v1-damon.md",
     "Every design in, the named format set out. Grouped by layout skeleton, never by campaign."),
    ("3", "Spec one format", "stage3-format-spec-v1-damon.md",
     "One format in, the page a writer fills and the machine builds out."),
    ("4", "Hand it over", "stage4-production-handoff-v1-damon.md",
     "The set in, the document a developer builds production templates from out."),
]


# ---------- the smallest markdown that renders these files honestly ----------
def md(text):
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i]); i += 1
            out.append("<pre><code>" + html.escape("\n".join(body)) + "</code></pre>")
        elif ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1]):
            head = [c.strip() for c in ln.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip("|").split("|")]); i += 1
            i -= 1
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f'<div class="tblwrap"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
        elif re.match(r"^#{1,4} ", ln):
            n = len(ln) - len(ln.lstrip("#"))
            out.append(f"<h{min(n + 1, 5)}>{inline(ln[n:].strip())}</h{min(n + 1, 5)}>")
        elif re.match(r"^[-*] ", ln):
            items = []
            while i < len(lines) and re.match(r"^[-*] ", lines[i]):
                items.append(f"<li>{inline(lines[i][2:])}</li>"); i += 1
            i -= 1
            out.append("<ul>" + "".join(items) + "</ul>")
        elif ln.strip() == "---":
            out.append("<hr>")
        elif ln.strip():
            para = [ln]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"^([-*#|>]|```)", lines[i + 1]):
                i += 1; para.append(lines[i])
            out.append(f"<p>{inline(' '.join(para))}</p>")
        i += 1
    return "\n".join(out)


def inline(s):
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def load_designs(brand):
    """The rendered designs, from the brand's own existing-content."""
    p = (BRANDS / brand / "existing-content" / "emails" / "designs" / "index.json")
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (ValueError, TypeError):
        return {}


def link_designs(brand):
    """The page server only serves pages/ — point it at the brand's designs."""
    src = BRANDS / brand / "existing-content" / "emails" / "designs"
    if not src.exists():
        return
    link = HOME / "pages" / "img" / brand
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.is_symlink() or link.exists():
        if link.is_symlink() and link.resolve() == src.resolve():
            return
        link.unlink()
    link.symlink_to(src)


def read(p, default=""):
    p = Path(p)
    return p.read_text() if p.exists() else default


def brand_record(brand):
    """What the brand already holds, if anything."""
    d = BRANDS / brand / "email" / "design-formats"
    if not d.exists():
        return None
    rec = {"dir": d, "formats": None, "census": None, "boards": 0, "emails": 0,
           "per_board": {}}
    cj = d / "census.json"
    if cj.exists():
        try:
            c = json.loads(cj.read_text())
            rows = c.get("emails") or c.get("rows") or []
            rec["emails"] = len(rows) if isinstance(rows, list) else 0
            per = c.get("per_board") or {}
            rec["boards"] = len(per) if per else len({r.get("board") for r in rows if isinstance(r, dict)})
            rec["census"] = c
            per_board = {}
            for r in rows:
                if isinstance(r, dict) and r.get("board"):
                    per_board[r["board"]] = per_board.get(r["board"], 0) + 1
            rec["per_board"] = per_board
            rec["boards"] = rec["boards"] or len(per_board)
        except (ValueError, TypeError):
            pass
    comp = d / "components.json"
    if comp.exists():
        try:
            rec["formats"] = json.loads(comp.read_text()).get("formats_bedrock")
        except (ValueError, TypeError):
            pass
    return rec


# Design plan — the page is shaped like the thing it describes.
#   Colour: paper #F6F7F2 / ink #141916 in light, ground #0E1211 / #ECF1EC in
#           dark; neutrals biased green so they read chosen, not defaulted.
#           One accent — sage, deepened to #40614A on paper so it holds
#           contrast, opened to #C7CFAD on the dark ground.
#   Type:   Instrument Serif for display (high-contrast, the register email
#           design actually uses), Public Sans for body, IBM Plex Mono for
#           every code and measurement — the machine's own vocabulary.
#   Layout: one narrow column, blocks stacked like an email, each stage
#           carrying a mono code badge the way a bank page badges a send.
FONTS = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Instrument+Serif:ital@0;1&family=Public+Sans:wght@400;500;600&'
         'family=IBM+Plex+Mono:wght@400;500&display=swap">')

CSS = """
:root{
  --bg:#f6f7f2;--panel:#fffffe;--sunk:#eef0e8;--line:#dbe0d3;
  --ink:#141916;--mute:#5c6a60;--accent:#40614a;--on-accent:#f6f7f2;
  --display:"Instrument Serif",Georgia,"Times New Roman",serif;
  --body:"Public Sans",-apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#0e1211;--panel:#161c1a;--sunk:#0a0e0d;--line:#26302d;
    --ink:#ecf1ec;--mute:#93a49b;--accent:#c7cfad;--on-accent:#0e1211;
  }
}
:root[data-theme="dark"]{
  --bg:#0e1211;--panel:#161c1a;--sunk:#0a0e0d;--line:#26302d;
  --ink:#ecf1ec;--mute:#93a49b;--accent:#c7cfad;--on-accent:#0e1211;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16.5px/1.62 var(--body);-webkit-font-smoothing:antialiased}
.wrap{max-width:760px;margin:0 auto;padding:64px 24px 120px;
  display:flex;flex-direction:column}
.kick{font-family:var(--mono);font-size:12px;letter-spacing:.18em;
  text-transform:uppercase;color:var(--accent)}
h1{font-family:var(--display);font-weight:400;font-size:clamp(42px,7vw,62px);
  line-height:1.02;margin:16px 0 14px;text-wrap:balance;letter-spacing:-.01em}
.sub{color:var(--mute);font-size:18px;max-width:60ch;margin:0}
h2{font-family:var(--display);font-weight:400;font-size:31px;line-height:1.15;
  margin:62px 0 4px;text-wrap:balance}
h3{font-size:19px;margin:0 0 8px;font-weight:600;letter-spacing:-.01em}
h4,h5{font-size:15px;margin:22px 0 4px;font-weight:600;color:var(--accent)}
p{margin:12px 0;max-width:66ch}
a{color:var(--accent)}
.rule{height:1px;background:var(--line);margin:14px 0 0}
.tally{display:flex;flex-wrap:wrap;gap:0;margin:30px 0 8px;
  border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--panel)}
.tally div{flex:1 1 128px;padding:16px 18px;border-right:1px solid var(--line)}
.tally div:last-child{border-right:0}
.tally .n{font-family:var(--display);font-size:34px;line-height:1;color:var(--accent);
  font-variant-numeric:tabular-nums}
.tally .l{font-size:12.5px;color:var(--mute);margin-top:7px;line-height:1.35}
.stage{background:var(--panel);border:1px solid var(--line);border-radius:14px;
  padding:22px 24px;margin:16px 0;display:flex;flex-direction:column;gap:2px}
.head{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:6px}
.badge{font-family:var(--mono);background:var(--accent);color:var(--on-accent);
  font-size:11.5px;font-weight:500;letter-spacing:.1em;padding:4px 8px;border-radius:4px}
.file{font-family:var(--mono);font-size:12px;color:var(--mute);margin-top:10px}
details{margin-top:16px;border-top:1px solid var(--line);padding-top:14px}
summary{cursor:pointer;color:var(--accent);font-size:14px;font-weight:600;
  font-family:var(--mono);letter-spacing:.02em}
summary:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:3px}
details[open] summary{margin-bottom:12px}
.prompt{background:var(--sunk);border:1px solid var(--line);border-radius:10px;
  padding:18px 20px;font-size:14.5px}
.prompt h2,.prompt h3{font-family:var(--body);font-size:16px;font-weight:600;margin:20px 0 4px}
.prompt p{max-width:none}
.prompt table{font-size:13px}
.tblwrap{overflow-x:auto;margin:16px 0}
table{border-collapse:collapse;width:100%;font-size:14.5px}
th,td{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}
th{background:var(--sunk);font-weight:600;font-size:13px;letter-spacing:.02em}
td.mono,.mono{font-family:var(--mono);font-size:12.5px;font-variant-numeric:tabular-nums}
code{background:var(--sunk);padding:1.5px 5px;border-radius:4px;
  font-family:var(--mono);font-size:.86em}
pre{background:var(--sunk);border:1px solid var(--line);border-radius:10px;
  padding:15px;overflow-x:auto}
pre code{background:none;padding:0}
hr{border:0;border-top:1px solid var(--line);margin:26px 0}
ul{margin:12px 0;padding-left:22px;max-width:66ch}
li{margin:4px 0}
.foot{color:var(--mute);font-size:13px;margin-top:64px;border-top:1px solid var(--line);
  padding-top:18px;font-family:var(--mono);line-height:1.7}
.warn{border-left:2px solid var(--accent);padding-left:14px;color:var(--mute)}
.bh{font-family:var(--body);font-size:15px;font-weight:600;margin:28px 0 10px;
  display:flex;align-items:center;gap:10px;color:var(--mute);
  text-transform:uppercase;letter-spacing:.08em}
.bh .ct{font-family:var(--mono);font-size:11px;background:var(--sunk);
  border:1px solid var(--line);border-radius:20px;padding:2px 9px;letter-spacing:0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(132px,1fr));
  gap:14px;margin-bottom:8px}
.shot{display:block;text-decoration:none;color:var(--mute)}
.shot img{width:100%;display:block;border:1px solid var(--line);border-radius:6px;
  background:var(--sunk);aspect-ratio:600/1400;object-fit:cover;object-position:top}
.shot:hover img{border-color:var(--accent)}
.shot .cap{display:flex;justify-content:space-between;gap:6px;margin-top:6px;
  font-family:var(--mono);font-size:10.5px}
.shot .cap em{font-style:normal;opacity:.6}
.shot .subj{display:block;margin-top:3px;font-size:11.5px;line-height:1.35;color:var(--ink)}
"""


def build(brand):
    boards = []
    src = BRANDS / brand / "email" / "design-formats" / "source.json" if brand else None
    if src and src.exists():
        boards = json.loads(src.read_text()).get("boards", [])
    rec = brand_record(brand) if brand else None

    P = []
    P.append('<div class="wrap">')
    P.append('<div class="kick">email teardown</div>')
    P.append("<h1>Tearing down an email</h1>")
    P.append('<p class="sub">The third lane. Video tears down a video, image tears down a static, '
             'this tears down an email — and the first thing it tore down was ours. '
             'Paste a Figma link; the designs come back read, grouped and spec\'d.</p>')

    # the numbers
    cards = [(str(len(boards)), "boards registered")]
    if rec:
        if rec["emails"]:
            cards.append((str(rec["emails"]), "emails on record"))
        if rec["boards"]:
            cards.append((str(rec["boards"]), "boards measured"))
        if rec["formats"]:
            n = len([k for k in rec["formats"] if k.startswith("FMT")])
            cards.append((str(n), "named formats"))
    cards.append(("4", "stages, each a prompt"))
    P.append('<div class="tally">' + "".join(
        f'<div><div class="n">{n}</div><div class="l">{l}</div></div>' for n, l in cards) + "</div>")

    # how a run starts
    P.append("<h2>How a run starts</h2>")
    P.append("<p>Damon gives a Figma link. That is the whole input. A link to a board runs the "
             "whole board; a link to one frame runs one email.</p>")
    if boards:
        per = (rec or {}).get("per_board", {})
        rows = "".join(
            f'<tr><td class="mono">{html.escape(b["code"])}</td><td>{html.escape(b["name"])}</td>'
            f'<td class="mono">{per.get(b["slug"], "—")}</td>'
            f'<td class="mono">{html.escape(b.get("node_id") or "—")}</td></tr>' for b in boards)
        P.append('<div class="tblwrap"><table><thead><tr><th>Code</th><th>Board</th>'
                 '<th>Emails</th><th>Node</th></tr>'
                 f"</thead><tbody>{rows}</tbody></table></div>")
        P.append(f"<p>Every board in the file, with its real Figma node — so any one of them "
                 f"runs without asking for another link. The codes follow the bank's own "
                 f"convention: months for campaigns, <code>FEBFL</code>/<code>NOVFL</code> for "
                 f"flows, <code>WEL25</code> for the welcome series, <code>RESREQ</code> for the "
                 f"results request. Each one prefixes its emails — <code>JAN26-04</code>.</p>")
    else:
        P.append('<p class="warn">No boards registered yet. A link is all it takes.</p>')

    # the stages, prompts verbatim
    P.append("<h2>The four stages</h2>")
    P.append("<p>Each stage is one prompt. The prompt is the product — every one is printed here in "
             "full, so a rule that is wrong can be seen and changed.</p>")
    for num, title, fname, line in STAGES:
        body = read(HOME / "prompts" / fname)
        P.append('<div class="stage">')
        P.append(f'<div class="head"><span class="badge">STAGE {num}</span>'
                 f"<h3>{html.escape(title)}</h3></div>")
        P.append(f"<p>{html.escape(line)}</p>")
        P.append(f'<div class="file">prompts/{html.escape(fname)}</div>')
        if body:
            P.append(f"<details><summary>Read the prompt in full</summary>"
                     f'<div class="prompt">{md(body)}</div></details>')
        else:
            P.append('<p class="warn">Prompt file missing.</p>')
        P.append("</div>")

    # the designs themselves
    designs = load_designs(brand)
    if designs:
        by_board = {}
        for d in designs.values():
            by_board.setdefault(d["board"], []).append(d)
        P.append("<h2>The designs</h2>")
        P.append(f"<p>{len(designs)} emails, rendered from the brand's own design file at "
                 f"full size. Click one to open it. They live with the brand, in "
                 f"<code>existing-content/emails/</code> — assets that ran, not process.</p>")
        order = {b["slug"]: i for i, b in enumerate(boards)}
        for slug in sorted(by_board, key=lambda s: order.get(s, 999)):
            rows = sorted(by_board[slug], key=lambda d: d["n"])
            title = next((b["name"] for b in boards if b["slug"] == slug), slug)
            P.append(f'<h3 class="bh">{html.escape(title)} '
                     f'<span class="ct">{len(rows)}</span></h3>')
            P.append('<div class="grid">')
            for d in rows:
                P.append(
                    f'<a class="shot" href="./img/{brand}/{html.escape(d["file"])}" '
                    f'target="_blank" title="{d["w"]}x{d["h"]}">'
                    f'<img loading="lazy" src="./img/{brand}/{html.escape(d["thumb"])}" '
                    f'alt="{html.escape(d["id"])}">'
                    f'<span class="cap">{html.escape(d["id"])}'
                    f'<em>{d["w"]}x{d["h"]}</em></span>'
                    + (f'<span class="subj">{html.escape(d["subject"])}</span>'
                       if d.get("subject") else "")
                    + "</a>")
            P.append("</div>")

    # what the record holds
    if rec and rec["formats"]:
        P.append("<h2>The formats we already found</h2>")
        rows = "".join(f'<tr><td class="mono">{html.escape(k)}</td><td>{html.escape(str(v))}</td></tr>'
                       for k, v in rec["formats"].items() if k.startswith("FMT"))
        P.append('<div class="tblwrap"><table><thead><tr><th>Code</th><th>Format</th></tr>'
                 f"</thead><tbody>{rows}</tbody></table></div>")
        cand = rec["formats"].get("candidates") or []
        if cand:
            P.append("<p><strong>Candidates</strong> — used once or twice, not yet a format: "
                     + ", ".join(html.escape(str(c)) for c in cand) + ".</p>")

    # the honest state
    P.append("<h2>Where it stands</h2>")
    P.append(md(read(HOME / "README.md").split("## Known holes, recorded not hidden")[-1]
                if "## Known holes" in read(HOME / "README.md") else ""))

    P.append(f'<div class="foot">Built {date.today().isoformat()} by '
             f'<code>tools/build_page.py</code> from the machine at '
             f'<code>email-teardown/</code>. Rebuild it after any prompt change.</div>')
    P.append("</div>")

    return ("<title>Tearing Down an Email</title>\n" + FONTS +
            "\n<style>" + CSS + "</style>\n" + "\n".join(P))


def build_md(brand):
    """The Markdown mirror — same page, the form the team reads."""
    boards, rec = [], brand_record(brand) if brand else None
    p = BRANDS / brand / "email" / "design-formats" / "source.json"
    if p.exists():
        boards = json.loads(p.read_text()).get("boards", [])

    L = ["# Tearing down an email", "",
         "The third lane. Video tears down a video, image tears down a static, this tears",
         "down an email — and the first thing it tore down was ours. Paste a Figma link;",
         "the designs come back read, grouped and spec'd.", ""]
    if rec:
        L += [f"**On record:** {rec['emails']} emails across {rec['boards']} boards, "
              f"{len([k for k in (rec['formats'] or {}) if k.startswith('FMT')])} named formats.", ""]
    L += ["## Boards registered", ""]
    if boards:
        per = (rec or {}).get("per_board", {})
        L += ["| Code | Board | Emails | Node |", "|---|---|---|---|"]
        L += [f"| {b['code']} | {b['name']} | {per.get(b['slug'], '—')} | "
              f"`{b.get('node_id') or '—'}` |" for b in boards]
    else:
        L += ["None yet — a link is all it takes."]
    L += ["", "## The four stages", "",
          "Each stage is one prompt, printed here in full. The prompt is the product.", ""]
    for num, title, fname, line in STAGES:
        L += [f"### Stage {num} — {title}", "", line, "", f"`prompts/{fname}`", "",
              "<details><summary>The prompt</summary>", "", "````markdown",
              read(HOME / "prompts" / fname).rstrip(), "````", "", "</details>", ""]
    if rec and rec["formats"]:
        L += ["## The formats we already found", "", "| Code | Format |", "|---|---|"]
        L += [f"| {k} | {v} |" for k, v in rec["formats"].items() if k.startswith("FMT")]
        L += [""]
    L += [f"*Built {date.today().isoformat()} by `tools/build_page.py`. "
          f"Rebuild after any prompt change.*"]
    return "\n".join(L) + "\n"


INDEX = """<title>Email Teardown</title>
{fonts}
<style>{css}
.brand{{display:block;background:var(--panel);border:1px solid var(--line);
  border-radius:14px;padding:20px 24px;margin:12px 0;text-decoration:none;color:var(--ink)}}
.brand:hover{{border-color:var(--accent)}}
.brand .nm{{font-family:var(--display);font-size:27px;line-height:1.1}}
.brand .st{{font-family:var(--mono);font-size:12.5px;color:var(--mute);margin-top:8px}}
</style>
<div class="wrap">
<div class="kick">email teardown</div>
<h1>The brands</h1>
<p class="sub">One page per brand. Paste a Figma link to put a new one in — the
lane stands it up, reads the boards, and names the formats.</p>
{rows}
<div class="foot">Rebuilt automatically whenever a prompt or a run changes.</div>
</div>
"""


def build_index():
    rows = []
    for page in sorted((HOME / "pages").glob("*.html")):
        # index is the page itself; _TEMPLATE is the cabinet's shape, not a brand
        if page.stem == "index" or page.stem.startswith("_"):
            continue
        rec = brand_record(page.stem) or {}
        src = BRANDS / page.stem / "email" / "design-formats" / "source.json"
        nb = len(json.loads(src.read_text()).get("boards", [])) if src.exists() else 0
        bits = [f"{nb} boards"] if nb else ["not read yet"]
        if rec.get("emails"):
            bits.append(f"{rec['emails']} emails")
        if rec.get("formats"):
            bits.append(f"{len([k for k in rec['formats'] if k.startswith('FMT')])} formats")
        rows.append(f'<a class="brand" href="./{page.name}"><div class="nm">'
                    f'{html.escape(page.stem)}</div><div class="st">'
                    f'{html.escape(" · ".join(bits))}</div></a>')
    if not rows:
        rows = ['<p class="warn">No brands yet.</p>']
    (HOME / "pages" / "index.html").write_text(
        INDEX.format(fonts=FONTS, css=CSS, rows="\n".join(rows)) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True,
                    help="which brand's record to draw (no default — this lane is "
                         "brand-agnostic by rule)")
    ap.add_argument("--out", help="defaults to pages/<brand>.html")
    a = ap.parse_args()
    if a.brand.startswith("_"):
        raise SystemExit(f"{a.brand!r} is a cabinet template, not a brand")
    out = Path(a.out) if a.out else (HOME / "pages" / f"{a.brand}.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    link_designs(a.brand)
    out.write_text(build(a.brand) + "\n")
    mirror = out.with_suffix(".md")
    mirror.write_text(build_md(a.brand))
    build_index()
    print(f"wrote {out} ({out.stat().st_size // 1024}KB) + {mirror.name} "
          f"({mirror.stat().st_size // 1024}KB) + index.html")


if __name__ == "__main__":
    main()
