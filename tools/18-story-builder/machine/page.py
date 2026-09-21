#!/usr/bin/env python3
"""Render the story builder's page: the chain, its prompt verbatim, and every
brand's story block.

    python3 story-builder/page.py      -> story-builder/story-builder.html

Everything is read off disk — the prompt file, each brands/<brand>/story.md,
and the latest run under runs/research-story/<brand>/ (or the older runs/story-builder/) — so a new brand or a
prompt edit shows up on the next render with no hand edits.
"""
import difflib, glob, html, json, os, re

import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import story_paths as P  # noqa: E402  (the workspace is found by walking up; AI_WORKSPACE wins)

HERE = str(P.TOOL)                 # the tool's folder — the page and prompts/ sit there, not in machine/
WS = str(P.WS)
E = html.escape
OUT = os.path.join(HERE, "story-builder.html")


def newest_prompt():
    ps = glob.glob(os.path.join(HERE, "prompts", "stage2-draft-v*-damon.md"))
    return max(ps, key=lambda p: int(re.search(r"-v(\d+)-", p).group(1)))


def brand_rows():
    out = []
    for f in sorted(glob.glob(os.path.join(WS, "brands", "*", "story.md"))):
        b = f.split(os.sep)[-2]
        if b.startswith("_"):
            continue
        s = open(f).read()
        m = re.search(r"## The story block.*?```\n(.*?)```", s, re.S)
        block = m.group(1).strip() if m else ""
        stories = re.findall(r"^### (\S+) — (.+)$", s, re.M)
        conf = re.search(r"confirmed by:\s*(.+)", block)
        # runs file under research-story since 2026-09-20; older ones sit under story-builder
        runs = sorted((glob.glob(os.path.join(WS, "runs", "story-builder", b, "*", "run.json"))
                       + glob.glob(os.path.join(WS, "runs", "research-story", b, "*", "run.json"))),
                      key=lambda p: os.path.basename(os.path.dirname(p)))
        run = json.load(open(runs[-1])) if runs else None
        out.append({"brand": b, "block": block, "stories": stories,
                    "confirmed": (conf.group(1).strip() if conf else "open"),
                    "run": run, "path": os.path.relpath(f, WS)})
    return out


def verify_counts(run):
    st = (run or {}).get("stages", {}).get("stage3", {})
    return st.get("verified"), st.get("flagged")


VT = os.path.join(WS, "components", "video-teardown", "prompts")
# Where {story} is wired in the video machine: board id, name, what it does,
# the prompt before and after. The diff below each is read off disk.
WIRED = [
    ("1b", "Audience", "Picks ONE story and ONE teller for the run, from the stories whose Fits include the avatar it chose. Recorded on the run.",
     "stage-1b-audience/stage1b-audience-v7-damon.md", "stage-1b-audience/stage1b-audience-v8-damon.md"),
    ("2f", "Compose (framework lane)", "Every beat of the picked story gets a phase able to carry it; the construct stays brand-free.",
     "stage-2f-compose/stage2f-compose-v3-damon.md", "stage-2f-compose/stage2f-compose-v4-damon.md"),
    ("3", "Injection: the main one", "The swipe keeps its structure; the story decides whose it is. The teller goes on screen; before, turn and after fill the source's timing. New check: every beat mapped to a timestamp.",
     "stage-3-injection/stage3-injection-v10-damon.md", "stage-3-injection/stage3-injection-v11-damon.md"),
    ("4b", "Hooks", "At least one hook is the first line of the teller's story, in a buying moment, marked STORY OPENER.",
     "stage-4-loop/4b-hook/stage4b-hook-v13-damon.md", "stage-4-loop/4b-hook/stage4b-hook-v14-damon.md"),
    ("4d", "Expansion", "The middle of the script (what was tried, why it failed, what turned) is the story's REASON TO SWITCH and TURN.",
     "stage-4-loop/4d-expansion/stage4c-expansion-v12-damon.md", "stage-4-loop/4d-expansion/stage4c-expansion-v13-damon.md"),
    ("4g", "Spice", "The spoken script goes in the teller's mouth: a barber sounds like a barber.",
     "stage-4-loop/4g-spice/stage4g-spice-v3-damon.md", "stage-4-loop/4g-spice/stage4g-spice-v4-damon.md"),
]


def diff_html(a, b):
    A = open(os.path.join(VT, a)).read().splitlines()
    B = open(os.path.join(VT, b)).read().splitlines()
    out, add = [], 0
    for ln in difflib.unified_diff(A, B, lineterm="", n=1):
        if ln.startswith(("---", "+++")):
            continue
        cls = "h" if ln.startswith("@@") else "a" if ln.startswith("+") else "r" if ln.startswith("-") else "c"
        add += cls == "a"
        out.append(f'<span class="{cls}">{E(ln)}</span>')
    return "\n".join(out), add


def slot_rows(block):
    rows = []
    for line in block.splitlines():
        k, _, v = line.partition(":")
        rows.append(f'<div class="row{" lock" if k.strip()=="confirmed by" else ""}">'
                    f'<span class="key">{E(k.strip())}</span><span class="val">{E(v.strip())}</span></div>')
    return "".join(rows)


def main():
    prompt_path = newest_prompt()
    prompt = open(prompt_path).read()
    brands = brand_rows()
    P = []
    A = P.append
    A("""<title>The Story Builder</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{--ground:#F4F3EF;--surface:#FFFFFF;--ink:#1D2230;--body:#3A4050;--muted:#6B7080;--rule:#DAD8D0;
--accent:#3547A8;--accentsoft:#E4E7F6;--code:#15192A;--codeink:#E3E6F2;--codekey:#9FB0FF;--open:#B5540B;--ok:#2F7A4A;
--serif:"Fraunces",Georgia,serif;--sans:"IBM Plex Sans",system-ui,sans-serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ground:#12141C;--surface:#1A1D28;--ink:#EEF0F6;--body:#C8CCD8;--muted:#8D92A3;--rule:#2A2E3C;--accent:#9FB0FF;--accentsoft:#232A48;--code:#0B0D14;--codeink:#DCE0EE;--codekey:#9FB0FF;--open:#F0A35E;--ok:#6CC08C}}
:root[data-theme="dark"]{--ground:#12141C;--surface:#1A1D28;--ink:#EEF0F6;--body:#C8CCD8;--muted:#8D92A3;--rule:#2A2E3C;--accent:#9FB0FF;--accentsoft:#232A48;--code:#0B0D14;--codeink:#DCE0EE;--codekey:#9FB0FF;--open:#F0A35E;--ok:#6CC08C}
*{box-sizing:border-box}
body{background:var(--ground);color:var(--body);font:15.5px/1.6 var(--sans);padding-inline:20px;padding-block:0 64px}
.wrap{max-width:1000px;margin:0 auto}
h1,h2,h3{color:var(--ink);margin:0;text-wrap:balance}
h1{font:300 clamp(2.3rem,5.5vw,3.6rem)/1.05 var(--serif)}
h2{font:500 1.6rem/1.2 var(--serif)}
h3{font:600 1rem/1.3 var(--sans)}
p{margin:0;max-width:68ch}
.eyebrow{font:500 .7rem/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.lede{color:var(--muted)}
header,section{display:grid;gap:16px}header{padding-top:44px}section{padding-top:52px}
.stand{font:300 1.25rem/1.5 var(--serif);max-width:62ch}
.stages{display:grid;grid-template-columns:repeat(4,1fr);border-top:2px solid var(--ink)}
.stage{padding:16px 14px 18px;display:grid;gap:6px;align-content:start;border-bottom:1px solid var(--rule)}
.stage+.stage{border-left:1px solid var(--rule)}
.stage .n{font:500 .7rem/1 var(--mono);color:var(--accent);letter-spacing:.1em}
.stage .m{font:500 .68rem/1 var(--mono);color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
.stage p{font-size:.88rem}
.tbl{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.9rem}
th{font:500 .66rem/1.2 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);text-align:left;padding:8px 12px 8px 0;border-bottom:1px solid var(--ink)}
td{padding:10px 12px 10px 0;border-bottom:1px solid var(--rule);vertical-align:top}
td:first-child{color:var(--ink);font-weight:600}
.tag{font:500 .68rem/1 var(--mono);padding:5px 7px;border-radius:4px;background:var(--accentsoft);color:var(--ink);white-space:nowrap}
.tag.open{background:transparent;border:1px solid var(--open);color:var(--open)}
.tag.ok{background:transparent;border:1px solid var(--ok);color:var(--ok)}
.block{background:var(--code);color:var(--codeink);font:400 .78rem/1.6 var(--mono);padding:20px;overflow-x:auto}
.block .row{display:grid;grid-template-columns:150px 1fr;gap:14px;padding:3px 0}
.block .key{color:var(--codekey)}.block .lock .val{color:var(--open)}
.brand{display:grid;gap:14px;padding:20px;background:var(--surface);border:1px solid var(--rule)}
.brandhead{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:baseline}
.brandhead h3{font:500 1.35rem/1.2 var(--serif);text-transform:capitalize}
.stories{list-style:none;padding:0;margin:0;display:grid;gap:6px;font-size:.9rem}
.stories code{font:500 .78rem var(--mono);color:var(--accent);margin-right:6px}
details{background:var(--surface);border:1px solid var(--rule)}
summary{cursor:pointer;padding:14px 16px;font-weight:600;color:var(--ink)}
summary:focus-visible{outline:2px solid var(--accent)}
pre.diff{margin:0;padding:14px 16px;border-top:1px solid var(--rule);background:var(--code);color:var(--codeink);font:400 .74rem/1.55 var(--mono);white-space:pre-wrap;overflow-x:auto;max-height:60vh}
pre.diff .a{color:#8FE3A8}pre.diff .r{color:#F29B9B}pre.diff .h{color:var(--codekey)}pre.diff .c{color:#8D92A3}
.path{font:400 .72rem var(--mono);color:var(--muted);margin-left:8px}
pre.prompt{margin:0;padding:18px;border-top:1px solid var(--rule);background:var(--code);color:var(--codeink);font:400 .78rem/1.6 var(--mono);white-space:pre-wrap;overflow-x:auto;max-height:70vh}
.decide div{display:grid;grid-template-columns:22px 1fr;gap:10px;padding:12px 0;border-bottom:1px solid var(--rule)}
.decide .box{width:14px;height:14px;border:1px solid var(--ink);margin-top:5px}
footer{padding-top:44px;font-size:.8rem;color:var(--muted);display:grid;gap:4px}
code{font-family:var(--mono);font-size:.85em}
@media (max-width:720px){.stages{grid-template-columns:1fr 1fr}.stage:nth-child(3){border-left:0}}
@media (max-width:460px){.stages{grid-template-columns:1fr}.stage+.stage{border-left:0}.block .row{grid-template-columns:1fr;gap:0}}
</style>
<div class="wrap">
<header>
  <div class="eyebrow">Every brand · the storytelling layer beside the position</div>
  <h1>The Story Builder</h1>
  <p class="stand">Give it a brand and it drafts that brand's story file: the spine, who tells it, and a set of stories built only from what customers already said. Every quote is checked word for word against the brand's own files. Nothing is locked until a person confirms it.</p>
</header>
<section>
  <h2>Four steps, one model call</h2>
  <div class="stages">
    <div class="stage"><span class="n">1 · GATHER</span><span class="m">no model</span><p>Pulls story-shaped quotes from the brand's customer bank (hid it, tried everything, someone noticed, family, years, an authority, the after), with the position, avatars and sub-avatars.</p></div>
    <div class="stage"><span class="n">2 · DRAFT</span><span class="m">opus</span><p>Writes the story file in the one shape every brand uses, quoting only what step 1 handed it. The prompt is below, word for word.</p></div>
    <div class="stage"><span class="n">3 · VERIFY</span><span class="m">no model</span><p>Every quote must be found word for word. A story with a quote that can't be found drops to <em>open</em>.</p></div>
    <div class="stage"><span class="n">4 · CHECK THE SHAPE</span><span class="m">no model</span><p>Same slots, same order, every story has beats, a teller, who it fits and a receipt. The approved <brand> file set the shape.</p></div>
  </div>
  <p class="lede">A brand's story is written only when it has none yet. An existing one is never overwritten; a new draft waits beside the run for a person.</p>
</section>
<section>
  <h2>Every brand on the system</h2>
  <div class="tbl"><table><thead><tr><th>Brand</th><th>Stories</th><th>Quotes checked</th><th>Made by</th><th>Locked</th></tr></thead><tbody>""")
    for b in brands:
        v, f = verify_counts(b["run"])
        made = "the builder" if b["run"] else "by hand, the first one"
        q = f"{v} found · {f} flagged" if v is not None else "checked by hand"
        lock = ('<span class="tag open">open</span>' if b["confirmed"].startswith("open")
                else f'<span class="tag ok">{E(b["confirmed"])}</span>')
        A(f'<tr><td style="text-transform:capitalize">{E(b["brand"])}</td><td>{len(b["stories"])}</td>'
          f'<td>{E(q)}</td><td>{E(made)}</td><td>{lock}</td></tr>')
    A("</tbody></table></div></section>")
    for b in brands:
        A(f'<section><div class="brand"><div class="brandhead"><h3>{E(b["brand"])}</h3>'
          f'<span class="eyebrow">{E(b["path"])}</span></div>'
          f'<div class="block">{slot_rows(b["block"])}</div><ul class="stories">')
        for sid, line in b["stories"]:
            A(f'<li><code>{E(sid)}</code>{E(line)}</li>')
        A('</ul></div></section>')
    A("""<section>
  <h2>Wired into the video machine</h2>
  <p class="lede">The video machine is a line of steps. Six of them now read the brand's story. Every other step (triage, the teardown, the doctrine read, the construct, the frames) reads the swipe or the product, not our story, so it is left alone. A brand with no story file runs exactly as before.</p>
  <div class="tbl"><table><thead><tr><th>Step</th><th>What the story does there</th><th>Prompt</th></tr></thead><tbody>""")
    for sid, name, what, a, b in WIRED:
        A(f'<tr><td>{E(sid)} · {E(name)}</td><td>{E(what)}</td><td><code>{E(os.path.basename(b))}</code></td></tr>')
    A("</tbody></table></div>")
    for sid, name, what, a, b in WIRED:
        d, add = diff_html(a, b)
        A(f'<details><summary>{E(sid)} · {E(name)} — {E(os.path.basename(a))} → {E(os.path.basename(b))}'
          f'<span class="path">+{add} lines</span></summary><pre class="diff">{d}</pre></details>')
    A("</section>")
    A(f"""<section>
  <h2>The draft prompt, word for word</h2>
  <p class="lede">This is exactly what the model gets, before the brand's files are poured into the slots. Tighten a line here and every brand's next draft changes.</p>
  <details open><summary>{E(os.path.relpath(prompt_path, WS))}</summary><pre class="prompt">{E(prompt)}</pre></details>
</section>
<section>
  <h2>Yours to call</h2>
  <div class="decide">
    <div><span class="box"></span><span><b>Lock each brand's block</b>: nothing is confirmed until you are named on it.</span></div>
    <div><span class="box"></span><span><b><brand>'s spine</b> leans on the position's spine, which is still marked proposed.</span></div>
    <div><span class="box"></span><span><b>The builder writes into the brand folder</b> when a brand has no story yet. Brand folders are read-only to machines this phase; keep this one exception or have drafts wait beside the run.</span></div>
    <div><span class="box"></span><span><b>Read the two test runs</b>: Nuora&#x27;s biggest videos rebuilt for <brand> and <brand>, with the story in.</span></div>
  </div>
</section>
<footer><p>Run it: <code>python3 story-builder/build.py --brand &lt;brand&gt;</code> · Shape: <code>brands/_TEMPLATE/story.md</code> · Check: <code>components/marketing-doctrine/lint_story.py</code></p>
<p>Page rebuilt from disk by <code>story-builder/page.py</code>.</p></footer>
</div>""")
    open(OUT, "w").write("\n".join(P))
    print(OUT)


if __name__ == "__main__":
    main()
