#!/usr/bin/env python3
"""research-story (the story builder): drafts a brand's story.md, for any brand.

    python3 story-builder/build.py --brand <brand>             # full run
    python3 story-builder/build.py --brand <brand> --dry-run   # free: no model, NOTHING written
    python3 story-builder/build.py --brand <brand> --dry       # no model; files the gather + the prompt as sent
    python3 story-builder/build.py --brand <brand> --label <run-label>

(`build.py` at the tool's root forwards here; this file is the code.)

Four stages, one model call:

  1 Gather  — no model. Pulls story-shaped verbatim rows out of the brand's
              language bank (hid it, tried everything, someone noticed, family,
              years, partner, authority figure, founder/brand story, the after)
              with their ids and sources, plus the position, avatar, sub-avatar,
              rules, anchors and angles excerpts a story needs.
  2 Draft   — the stronger model (the video machine's own claude helper) writes
              story.md in the shape of brands/_TEMPLATE/story.md, allowed to
              quote only what stage 1 handed it.
  3 Verify  — no model. Every quoted string must be found verbatim in what was
              handed over. A story with an unfound quote is demoted to `open`;
              an unfound quote anywhere else is marked ⟨unverified⟩.
  4 Lint    — components/marketing-doctrine/lint_story.py on the result.

Three gates (story_gates.py, the shared components/quality-checks hold):
inputs and elements before the model, copy after the lint. A held build writes
check.json, says why, hands nothing to the brand, and exits 2.

Everything a run writes goes to runs/research-story/<brand>/<run-label>/
(run.json, check.json, the gathered rows, the prompt as sent, the raw draft,
the verify report, the lint result, deliverable/story.md). Runs made before
2026-09-20 sit under the old name, runs/story-builder/. The brand's own
brands/<brand>/story.md is written ONLY when it does not exist yet and the
draft passed the copy gate — an existing story is never overwritten.
`confirmed by: open` always: a human locks it.
"""
import argparse, datetime, hashlib, json, math, re, shutil, sys, time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
import story_paths as P  # noqa: E402  (appends the shared folders — never first on the path)
import story_gates as G  # noqa: E402
import lint_story  # noqa: E402
from run_kit import filing  # noqa: E402

HERE = P.MACHINE_DIR
WS = P.WS
PROMPTS = P.PROMPTS
MACHINE = "research-story"
OLD_MACHINE = "story-builder"      # where runs were filed before 2026-09-20; read, never written
DOCTRINE = P.DOCTRINE
TEMPLATE = P.TEMPLATE

STAGES = [
    dict(key="stage1", id="1", name="Gather", model=None, label="gathered",
         blurb="Story-shaped rows from the language bank, plus the brand excerpts a story needs. No model."),
    dict(key="stage2", id="2", name="Draft", model="the video machine's claude helper", label="draft",
         blurb="Writes story.md in the template's shape, quoting only what stage 1 handed over."),
    dict(key="stage3", id="3", name="Verify", model=None, label="verify",
         blurb="Every quote checked verbatim against what was handed over. Unfound = story demoted to open."),
    dict(key="stage4", id="4", name="Lint", model=None, label="lint",
         blurb="The story gate — lint_story.py — on the verified draft."),
]

# --- stage 1: what makes a row story-shaped. Generic English, no brand words.
PATTERNS = {
    "hid-it": r"\b(hid|hide|hides|hiding|cover(?:ed|ing|s)? (?:up|them|it)|conceal\w*|long sleeves?|makeup"
              r"|wear(?:ing)? (?:hats?|long|pants|sleeves)|self[- ]conscious|embarrass\w*|ashamed"
              r"|avoid(?:ed|ing)? (?:photos?|pictures?|mirrors?|the camera|cameras?|going out)"
              r"|part of me|the way it is|gave up|given up)\b",
    "tried-everything": r"(tried everything|tried it all|tried (?:so many|every|them all)|nothing (?:has )?(?:ever )?"
                        r"(?:worked|works|helped|helps)|(?:didn'?t|doesn'?t|did not|does not|don'?t) "
                        r"(?:do a darn thing|work|help|do anything)|not really doing anything|hasn'?t done anything"
                        r"|lost cause|comes? (?:right )?back|came (?:right )?back|\blaser\w*|\bpeels?\b"
                        r"|wasted? (?:money|so much|hundreds)|spent (?:hundreds|thousands|so much|a fortune)"
                        r"|\bdoubts?\b|skeptic\w*)",
    "someone-noticed": r"\b(noticed|compliment\w*|asked (?:me )?what|asking (?:me )?what|what changed"
                       r"|people (?:ask|say|tell|keep)|told me (?:my|I|how)|can see (?:a|the) difference"
                       r"|(?:said|says) (?:my|I look))\b",
    "family": r"\b(husband|wife|daughter|son|mom|mother|dad|father|grand(?:daughter|son|kids?|children|ma"
              r"|mother|pa|father)|sister|brother|family|kids|niece|nephew|parents)\b",
    "years": r"(\b\d{1,2}\+? ?years\b|\bdecades?\b|\bsince I was\b|\bever since\b|\bfor years\b"
             r"|\bmy whole life\b|\bas a (?:kid|child|teen(?:ager)?)\b|\bgrowing up\b"
             r"|\bin my (?:twenties|thirties|forties|fifties|sixties|seventies|[2-8]0s)\b)",
    "partner": r"\b(boyfriend|girlfriend|husband|wife|partner|my (?:girl|man|guy)|fianc[eé]e?)\b",
    "authority": r"\b(doctor|dermatologist|derm|oncologist|esthetician|aesthetician|barber|pharmacist|nurse"
                 r"|physician)\b",
    "brand-story": r"\b(founder|your story|the story|family[- ](?:owned|based|business|recipe)"
                   r"|grandmother'?s|small business|built by)\b",
    "the-after": r"\b(finally|for the first time|first time in|now I can|no longer|don'?t have to (?:hide|cover)"
                 r"|I can (?:wear|show)|confident|confidence|lighten\w*|lighter|faded|fading|completely gone"
                 r"|disappeared|surprised|to believe it|don'?t write reviews|break my silence)\b",
}
PATTERNS_RX = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}
PER_PATTERN = 12          # rows kept per pattern
MAX_ROWS = 110            # rows handed to the draft, in all
ROW_CHARS = 400           # a longer row is cut, on a word, with …
# Not a customer speaking: never handed over as a quotable row.
NOT_CUSTOMER_SPEAKERS = {"creator audience", "creator", "brand"}
NOT_CUSTOMER_SOURCES = {"panel", "creator-comment"}
FUNNEL_WEIGHT = {"customer": 3, "churned": 2, "lead": 2, "prospect": 1}
# A buyer's own account outranks a forum post; a short first-person line
# outranks a long one that matched many patterns only because it is long.
SOURCE_WEIGHT = {"interview": 3, "review": 3, "survey": 2, "ticket": 2, "database": 1, "comment": 1}


def say(msg):
    print(msg, flush=True)


def sha(p):
    p = Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12] if p.is_file() else None


def rel(p):
    p = Path(p)
    try:
        return str(p.resolve().relative_to(WS))
    except ValueError:
        return str(p)


def strip_front(text):
    return re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S).strip()


def cap(text, n):
    text = text.strip()
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + " …[trimmed]"


def section(text, head):
    m = re.search(rf"^## {re.escape(head)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def latest_prompt(stage, must=True):
    """Same head rule as the other chains: highest -vN- wins."""
    best, best_v = None, -1
    for f in PROMPTS.glob(f"{stage}-*.md"):
        m = re.search(r"-v(\d+)-", f.name)
        if m and int(m.group(1)) > best_v:
            best, best_v = f, int(m.group(1))
    if not best and must:
        sys.exit(f"no prompt file for {stage} in {PROMPTS}")
    return best


def fill(template, fields):
    """One pass, so a value that itself holds {braces} is never re-filled."""
    return re.sub(r"\{(\w+)\}", lambda m: fields.get(m.group(1), m.group(0))
                  if m.group(1) in fields else m.group(0), template)


# ---------------------------------------------------------------- stage 1
def bank_files(bdir):
    out = []
    for av in sorted(p for p in (bdir / "core-avatars").glob("*") if p.is_dir()):
        out += sorted(av.glob("language/**/*.json"))
        out += sorted(av.glob("sub-avatars/*/language/*.json"))
    return out


def gather_rows(bdir):
    seen, cands, counts = set(), [], {"files": 0, "rows": 0, "excluded_not_customer": 0}
    for f in bank_files(bdir):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        if not isinstance(d, dict) or not isinstance(d.get("entries"), list):
            continue
        counts["files"] += 1
        for e in d["entries"]:
            if not isinstance(e, dict) or not isinstance(e.get("text"), str):
                continue
            counts["rows"] += 1
            src = e.get("source") if isinstance(e.get("source"), dict) else {}
            if e.get("status", "active") != "active":
                continue
            if (str(e.get("speaker", "")).lower() in NOT_CUSTOMER_SPEAKERS
                    or str(src.get("type", "")).lower() in NOT_CUSTOMER_SOURCES):
                counts["excluded_not_customer"] += 1
                continue
            text = e["text"].strip()
            key = re.sub(r"\W+", " ", text.lower()).strip()
            if len(text) < 25 or key in seen:
                continue
            hits = [k for k, rx in PATTERNS_RX.items() if rx.search(text)]
            if not hits:
                continue
            seen.add(key)
            sig = e.get("signal") if isinstance(e.get("signal"), dict) else {}
            likes = sig.get("likes") or 0
            score = (2 * min(len(hits), 3) + FUNNEL_WEIGHT.get(str(e.get("funnel")), 1)
                     + SOURCE_WEIGHT.get(str(src.get("type")), 0)
                     + min(2.0, math.log10(1 + likes) if isinstance(likes, (int, float)) else 0)
                     - max(0, len(text) - 250) / 250)
            cands.append(dict(bank_id=e.get("id"), text=text, file=str(f.relative_to(bdir)),
                              who=src.get("name") or src.get("type") or "unnamed source",
                              ref=src.get("ref"), date=src.get("date"), funnel=e.get("funnel"),
                              speaker=e.get("speaker"), sub=e.get("sub"), note=e.get("note"),
                              patterns=hits, score=round(score, 2)))
    cands.sort(key=lambda r: -r["score"])
    chosen, ids = [], set()
    for pat in PATTERNS:                      # every pattern gets its turn
        for r in [c for c in cands if pat in c["patterns"] and id(c) not in ids][:PER_PATTERN]:
            if len(chosen) >= MAX_ROWS:
                break
            chosen.append(r); ids.add(id(r))
    for i, r in enumerate(chosen, 1):
        r["row"] = f"R{i:03d}"
    counts["story_shaped"] = len(cands)
    counts["handed"] = len(chosen)
    counts["per_pattern"] = {p: sum(p in r["patterns"] for r in chosen) for p in PATTERNS}
    return chosen, counts


def render_rows(rows):
    lines = []
    for r in rows:
        t = r["text"] if len(r["text"]) <= ROW_CHARS + 20 else cap(r["text"], ROW_CHARS).replace(" …[trimmed]", " …")
        t = re.sub(r"\s+", " ", t)
        extra = f" · note: {r['note']}" if r.get("note") else ""
        lines.append(f'[{r["row"]}] "{t}" — {r["file"]} · {r["who"]}'
                     f'{" · sub: " + str(r["sub"]) if r.get("sub") else ""}'
                     f' · patterns: {", ".join(r["patterns"])}{extra}')
    return "\n".join(lines) if lines else "open — the bank holds no story-shaped customer rows"


def gather_excerpts(bdir):
    """-> {slot: (text, [source paths])}. A missing file says `open`, never a guess."""
    x = {}
    pos = bdir / "position.md"
    if pos.is_file():
        pt = pos.read_text()
        m = re.search(r"^```[^\n]*\n(.*?)^```", section(pt, "The line"), re.M | re.S)
        x["position_block"] = (m.group(1).strip() if m else "open — position.md has no block", [pos])
        x["position_unsaid"] = (section(pt, "The thing nobody in the category will say") or "open", [pos])
        x["position_rules"] = (section(pt, "The binding rules") or "open", [pos])
    else:
        for k in ("position_block", "position_unsaid", "position_rules"):
            x[k] = ("open — no position.md on file", [])
    profs = sorted((bdir / "core-avatars").glob("*/profile.md"))
    x["avatar_profiles"] = ("\n\n".join(f"### {p.parent.name}\n{cap(strip_front(p.read_text()), 9000)}"
                                        for p in profs) or "open — no avatar profile on file", profs)
    subs = sorted((bdir / "core-avatars").glob("*/sub-avatars/*.md"))
    x["sub_avatars"] = ("\n\n".join(f"### {p.stem} (avatar: {p.parent.parent.name})\n"
                                    f"{cap(strip_front(p.read_text()), 3500)}" for p in subs)
                        or "open — no sub-avatars on file", subs)
    rules = sorted((bdir / "core-avatars").glob("*/language/rules.md"))
    x["language_rules"] = ("\n\n".join(f"### {p.parent.parent.name}\n{cap(strip_front(p.read_text()), 7000)}"
                                       for p in rules) or "open — no language rules on file", rules)
    ia = bdir / "identity-anchors.md"
    x["identity_anchors"] = (cap(strip_front(ia.read_text()), 6000) if ia.is_file()
                             else "open — no identity-anchors.md on file", [ia] if ia.is_file() else [])
    ang, src = [], []
    aj = bdir / "strategy" / "angles.json"
    if aj.is_file():
        try:
            for a in json.loads(aj.read_text()).get("angles", []):
                ang.append(f"- {a.get('id')} — {a.get('name')} ({a.get('status')}): {a.get('what', '')}")
            src.append(aj)
        except Exception:
            pass
    am = bdir / "existing-content" / "angles.md"
    if am.is_file():
        ang.append("\nexisting-content/angles.md:\n" + cap(strip_front(am.read_text()), 2500)); src.append(am)
    x["angles"] = ("\n".join(ang) or "open — no angles on file", src)
    ba = [p for p in (bdir / "core-avatars" / "before-afters.md", bdir / "before-afters.md") if p.is_file()]
    x["before_afters"] = ("\n\n".join(cap(strip_front(p.read_text()), 4000) for p in ba)
                          or "open — no before-and-after file on record", ba)
    lanes = sorted(bdir.glob("*lane*.md"))
    x["lanes"] = ("\n\n".join(f"{p.name}:\n{cap(strip_front(p.read_text()), 3000)}" for p in lanes)
                  or "one lane — the brand has no audience lane map on file (channel lanes in "
                     "strategy/lanes.json are channels, not story lanes)", lanes)
    try:                                       # the arc is a row in the element library
        st = G.arc_row()
        arc = (f"{st['name']} — components/marketing-doctrine/ad-frameworks.json (`{G.ARC_FRAMEWORK}`); "
               f"its delivery is `{G.ARC_DELIVERY}` in components/marketing-doctrine/delivery.json")
    except Exception:                          # the elements gate holds the run before this is ever sent
        arc = (f"the doctrine's {G.ARC_FRAMEWORK} frame — components/marketing-doctrine/ad-frameworks.json "
               f"(`{G.ARC_FRAMEWORK}`); delivery `{G.ARC_DELIVERY}` in delivery.json")
    x["arc_frame"] = (arc, [DOCTRINE / "ad-frameworks.json"])
    return x


# ---------------------------------------------------------------- stage 3
QUOTE_RX = re.compile(r'"([^"\n]+?)"|“([^”\n]+?)”')


def norm(s):
    s = (s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
         .replace("*", ""))
    return re.sub(r"\s+", " ", s).strip()


def fragments(q):
    """A quote may elide with … — each piece must be found on its own."""
    q = norm(q)
    parts = re.split(r"\s*(?:…|\.\.\.)\s*", q)
    out = []
    for p in parts:
        p = p.strip().rstrip(".,;:!?").strip()
        if len(p) >= 2:
            out.append(p)
    return out


def find(frag, corpus):
    variants = {frag, frag[:1].swapcase() + frag[1:]}
    for label, text in corpus:
        if any(v in text for v in variants):
            return label
    return None


def verify(draft, corpus):
    """-> (text with demotions, report dict)."""
    # which story each character offset belongs to
    spans = []
    sb = re.search(r"^## The stories\s*$(.*?)(?=^## |\Z)", draft, re.M | re.S)
    if sb:
        heads = list(re.finditer(r"^### (.+?)\s*$", draft[sb.start(1):sb.end(1)], re.M))
        for i, h in enumerate(heads):
            s = sb.start(1) + h.start()
            e = sb.start(1) + (heads[i + 1].start() if i + 1 < len(heads) else len(sb.group(1)))
            sid = h.group(1).split(" — ")[0].strip()
            spans.append((s, e, sid))
    quotes = []
    for m in QUOTE_RX.finditer(draft):
        q = m.group(1) or m.group(2)
        if "{" in q or not re.search(r"[A-Za-z]", q):
            continue
        story = next((sid for s, e, sid in spans if s <= m.start() < e), None)
        frs = fragments(q)
        found = [find(f, corpus) for f in frs]
        quotes.append(dict(quote=q, story=story, start=m.start(), end=m.end(),
                           ok=bool(frs) and all(found), found_in=sorted({x for x in found if x}),
                           missing=[f for f, x in zip(frs, found) if not x]))
    bad_stories = sorted({q["story"] for q in quotes if not q["ok"] and q["story"]})
    loose = [q for q in quotes if not q["ok"] and not q["story"]]
    text = draft
    # mark loose unverified quotes, back to front so offsets hold
    for q in sorted(loose, key=lambda q: -q["end"]):
        text = text[:q["end"]] + " ⟨unverified⟩" + text[q["end"]:]
    # demote stories: an Open line at the end of the story, and (open) in STORIES
    for sid in bad_stories:
        miss = [q["quote"] for q in quotes if q["story"] == sid and not q["ok"]]
        note = ("- **Open:** demoted by the story builder's check — "
                f"{len(miss)} quote(s) not found verbatim in what the builder handed over: "
                + " · ".join(f"“{m[:90]}”" for m in miss) + ". Re-receipt it or cut it.\n")
        h = re.search(rf"^### {re.escape(sid)} — .*$", text, re.M)
        if h:
            nxt = re.search(r"^(### |## )", text[h.end():], re.M)
            at = h.end() + (nxt.start() if nxt else len(text) - h.end())
            text = text[:at].rstrip("\n") + "\n" + note + "\n" + text[at:]
        text = re.sub(rf"^(STORIES:.*?\b{re.escape(sid)}\b)(?! \(open\))", r"\1 (open)", text, count=1,
                      flags=re.M)
    n_bad = sum(not q["ok"] for q in quotes)
    if n_bad:
        m = re.search(r"^## Open\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
        line = (f"- **{n_bad} quote(s) failed the builder's verbatim check** — "
                f"{len(bad_stories)} stor{'y' if len(bad_stories) == 1 else 'ies'} demoted to `open`"
                f"{', and ' + str(len(loose)) + ' marked ⟨unverified⟩ in place' if loose else ''}. "
                "The run's stage3 report lists each one.\n")
        if m:
            at = m.end(1)
            text = text[:at].rstrip("\n") + "\n" + line + ("\n" if at < len(text) else "") + text[at:]
    report = dict(quotes=len(quotes), verified=sum(q["ok"] for q in quotes), flagged=n_bad,
                  demoted_stories=bad_stories, unverified_outside_stories=len(loose),
                  detail=[{k: v for k, v in q.items() if k not in ("start", "end")} for q in quotes])
    return text, report


def verify_md(rep):
    out = [f"# Verify — {rep['verified']} of {rep['quotes']} quotes found verbatim", "",
           f"Flagged: {rep['flagged']} · stories demoted to open: "
           f"{', '.join(rep['demoted_stories']) or 'none'} · unverified outside stories: "
           f"{rep['unverified_outside_stories']}", "",
           "| ok | story | quote | found in |", "|---|---|---|---|"]
    for q in rep["detail"]:
        where = ", ".join(q["found_in"]) if q["ok"] else "NOT FOUND: " + " · ".join(q["missing"])[:120]
        out.append(f"| {'yes' if q['ok'] else '**no**'} | {q['story'] or '—'} | "
                   f"{q['quote'][:110].replace('|', '/')} | {where.replace('|', '/')} |")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- run
def call_model(sent, raw, prompt_name):
    """THE ONE SPEND. The video machine's own claude helper: clean env, retries,
    chatter guard. Tests replace this function; nothing else calls a model."""
    P.add(P.VIDEO_MACHINE)
    import run as vt_run
    say(f"  2 draft    {prompt_name} → {vt_run.C.CLAUDE_MODEL} …")
    return vt_run.with_retry(lambda: vt_run.claude(sent, raw), "the draft")


def build_fields(brand, bdir, now):
    rows, counts = gather_rows(bdir)
    ex = gather_excerpts(bdir)
    fields = {k: v[0] for k, v in ex.items()}
    fields.update(today=now.strftime("%Y-%m-%d"), brand=brand, template=TEMPLATE.read_text().strip(),
                  rows=render_rows(rows))
    return rows, counts, ex, fields


def free_dry_run(a, bdir, out, pf, now):
    """--dry-run: no model, no folder, no file. Says what a real run would do."""
    say(f"research-story: {a.brand} — DRY RUN (no model call, nothing written)")
    say(f"  would file to   {rel(out)}/")
    say("                  run.json · check.json · stage1--gathered.json/.md · stage2--sent.md · "
        "stage2--draft.md · stage3--verify.json/.md · stage4--lint.txt · deliverable/story.md")
    would_hold = False
    for gate, problems in (("inputs", G.inputs_problems(TEMPLATE, pf)), ("elements", G.elements_problems())):
        would_hold = would_hold or bool(problems)
        say(f"  gate {gate:<9} {'pass' if not problems else 'WOULD HOLD'}")
        for p in problems:
            say(f"      {p}")
    say(f"  elements        framework `{G.ARC_FRAMEWORK}` · delivery `{G.ARC_DELIVERY}` (components/elements)")
    if would_hold:
        say("  a real run would be HELD before the model — nothing would be spent")
        return 2
    rows, counts, ex, fields = build_fields(a.brand, bdir, now)
    sent = fill(pf.read_text(), fields)
    say(f"  1 gather        {counts['handed']} rows would be handed over (of {counts['story_shaped']} "
        f"story-shaped, {counts['rows']} in {counts['files']} bank files)")
    opens = [k for k, v in ex.items() if not v[1] and k != "arc_frame"]
    if opens:
        say(f"                  nothing on file for: {', '.join(opens)} — the draft is told so, never handed a guess")
    say(f"  2 draft         {rel(pf)} (sha {sha(pf)}) — {len(sent):,} characters as sent · "
        "ONE model call, the only one in the run")
    say("  3 verify        no model — every quote checked against what stage 1 handed over")
    say("  4 lint          no model — then the copy gate: a quote left unchecked, or a broken shape, holds it")
    bs = bdir / "story.md"
    say(f"  hand-off        {rel(bs)} " + ("already exists — it would NOT be touched; the draft waits in deliverable/"
                                           if bs.is_file() else "does not exist — written only if the copy gate passes"))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--brand", required=True)
    ap.add_argument("--dry-run", dest="dry_run", action="store_true",
                    help="free: no model call and nothing written; prints where the run would file")
    ap.add_argument("--dry", action="store_true", help="gather and write the prompt as sent; no model")
    ap.add_argument("--label", help="run label (default: <date>-<hhmm>)")
    a = ap.parse_args(argv)

    bdir = WS / "brands" / a.brand
    if not bdir.is_dir() or a.brand.startswith("_"):
        sys.exit(f"no brand folder: {rel(bdir)}")
    now = datetime.datetime.now()
    label = a.label or now.strftime("%Y-%m-%d-%H%M") + ("-dry" if a.dry else "")
    out = WS / "runs" / MACHINE / a.brand / label
    for taken in (out, WS / "runs" / OLD_MACHINE / a.brand / label):
        if taken.exists():
            sys.exit(f"run folder already exists, pick another --label: {rel(taken)}")
    pf = latest_prompt("stage2", must=False)
    if a.dry_run:
        return free_dry_run(a, bdir, out, pf, now)

    out = filing.run_dir(MACHINE, a.brand, label, start=HERE)
    brand_story = bdir / "story.md"
    state = dict(tool=MACHINE, machine=MACHINE, brand=a.brand, label=label,
                 started=now.isoformat(timespec="seconds"),
                 dry=a.dry, status="running", stages={}, chain=[{k: s[k] for k in ("key", "id", "name", "blurb")}
                                                              for s in STAGES],
                 elements={"framework": G.ARC_FRAMEWORK, "delivery": G.ARC_DELIVERY}, check="check.json",
                 brand_story=rel(brand_story), brand_story_existed=brand_story.is_file())

    def save():
        (out / "run.json").write_text(json.dumps(state, indent=1, ensure_ascii=False) + "\n")

    def held(e):
        state.update(status=f"HELD at the {e.gate} gate", held=dict(gate=e.gate, problems=e.problems),
                     wrote_brand_story=False,
                     why=f"held at the {e.gate} gate — see check.json; nothing was handed to the brand",
                     finished=datetime.datetime.now().isoformat(timespec="seconds"))
        save()
        say(f"  ✗ {e}")
        say(f"  → {rel(out / 'check.json')}")
        return 2

    say(f"story builder: {a.brand} → {rel(out)}")

    # the gates before anything is spent
    try:
        G.hold("inputs", G.inputs_problems(TEMPLATE, pf), out)
        G.hold("elements", G.elements_problems(), out)
    except G.Held as e:
        return held(e)

    # 1 gather
    t0 = time.time()
    rows, counts, ex, fields = build_fields(a.brand, bdir, now)
    (out / "stage1--gathered.json").write_text(json.dumps(dict(counts=counts, rows=rows), indent=1,
                                                          ensure_ascii=False) + "\n")
    (out / "stage1--gathered.md").write_text(
        f"# Gathered for {a.brand}\n\n{counts['handed']} rows handed over, of {counts['story_shaped']} "
        f"story-shaped, of {counts['rows']} in {counts['files']} bank files "
        f"({counts['excluded_not_customer']} excluded as not a customer speaking).\n\n"
        + "\n".join(f"- {p}: {n}" for p, n in counts["per_pattern"].items()) + "\n\n## Rows\n\n"
        + fields["rows"] + "\n\n## Sources read\n\n"
        + "\n".join(f"- {k}: {', '.join(rel(p) for p in v[1]) or 'none — open'}" for k, v in ex.items()) + "\n")
    state["stages"]["stage1"] = dict(status="done", seconds=round(time.time() - t0, 1), model=None,
                                     out="stage1--gathered.json", counts=counts,
                                     sources={k: [rel(p) for p in v[1]] for k, v in ex.items()})
    say(f"  1 gather   {counts['handed']} rows handed (of {counts['story_shaped']} story-shaped, "
        f"{counts['rows']} in the bank)")

    # 2 draft
    sent = fill(pf.read_text(), fields)
    (out / "stage2--sent.md").write_text(sent)
    st2 = dict(prompt_file=rel(pf), prompt_name=pf.name, prompt_sha256_12=sha(pf), sent="stage2--sent.md",
               wants=sorted(fields))
    if a.dry:
        st2["status"] = "skipped — dry run"
        state["stages"]["stage2"] = st2
        state.update(status="dry — stopped before the model", finished=datetime.datetime.now()
                     .isoformat(timespec="seconds"))
        save()
        say(f"  2 draft    dry — prompt as sent: {rel(out / 'stage2--sent.md')}")
        return 0
    save()
    raw = out / "stage2--draft.md"
    t0 = time.time()
    try:
        model = call_model(sent, raw, pf.name)
    except Exception as e:
        st2.update(status="failed", error=str(e)[-600:])
        state["stages"]["stage2"] = st2
        state["status"] = "failed at stage2"
        save()
        sys.exit(f"the draft failed: {str(e)[-300:]}")
    draft = raw.read_text().strip()
    draft = re.sub(r"\A```[a-z]*\n(.*)\n```\s*\Z", r"\1", draft, flags=re.S).strip() + "\n"
    st2.update(status="done", seconds=round(time.time() - t0, 1), model=model, out=raw.name,
               chars_out=len(draft))
    state["stages"]["stage2"] = st2
    save()

    # 3 verify — against exactly what was handed over
    t0 = time.time()
    corpus = [(r["row"] + " " + r["file"], norm(r["text"])) for r in rows]
    corpus += [(k + ": " + (", ".join(rel(p) for p in v[1]) or k), norm(v[0])) for k, v in ex.items()
               if k != "arc_frame"]
    final, rep = verify(draft, corpus)
    (out / "stage3--verify.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False) + "\n")
    (out / "stage3--verify.md").write_text(verify_md(rep))
    state["stages"]["stage3"] = dict(status="done", seconds=round(time.time() - t0, 1), model=None,
                                     out="stage3--verify.md", quotes=rep["quotes"], verified=rep["verified"],
                                     flagged=rep["flagged"], demoted=rep["demoted_stories"])
    say(f"  3 verify   {rep['verified']}/{rep['quotes']} quotes found verbatim · demoted: "
        f"{', '.join(rep['demoted_stories']) or 'none'}")

    # 4 lint
    deliv = out / "deliverable"
    deliv.mkdir()
    (deliv / "story.md").write_text(final)
    fs = lint_story.check(deliv / "story.md")
    (out / "stage4--lint.txt").write_text("\n".join(fs) + "\n" if fs else "clean\n")
    state["stages"]["stage4"] = dict(status="done", model=None, out="stage4--lint.txt", clean=not fs,
                                     findings=fs)
    state["deliverable"] = rel(deliv / "story.md")
    say(f"  4 lint     {'clean' if not fs else str(len(fs)) + ' finding(s) — ' + fs[0]}")

    # the copy gate: a quote left standing unchecked, or a broken shape, holds the build
    try:
        G.hold("copy", G.copy_problems(rep, fs), out)
    except G.Held as e:
        return held(e)

    # the brand file: only when absent, only past the gate
    if brand_story.is_file():
        state["wrote_brand_story"] = False
        state["why"] = "brands/<brand>/story.md already exists — never overwritten; the draft is in deliverable/"
    else:
        shutil.copyfile(deliv / "story.md", brand_story)
        state["wrote_brand_story"] = True
    state.update(status="done", finished=datetime.datetime.now().isoformat(timespec="seconds"))
    save()
    say(f"  → {rel(brand_story) + ' written' if state['wrote_brand_story'] else state['why']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
