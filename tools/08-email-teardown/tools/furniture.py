#!/usr/bin/env python3
"""What in an email is NOT the message — found in code, for free, before and
after the model reads it.

    furniture.py scan <source email> --brand <brand>     print what the code finds

Three jobs, none of which spends anything:

  scan()          the source, line by line: which lines are page furniture
                  (logo row, nav, category links, social row, footer, legal)
                  and which carry damage (a merge tag showing as code, a
                  hidden character). Handed to the read step as a starting
                  list — the read step decides, this only points.
  strip_block()   the read step's own fenced ```STRIP block: the furniture
                  words and the defect quotes, as data the gate can check.
  message_only()  the record with its PAGE FURNITURE section taken out — the
                  construct step is never shown furniture words, so it cannot
                  carry them.

Which WORDS are a brand's furniture is the brand's own vocabulary and lives
with the brand: `brands/<brand>/email/simple.json` → `"furniture"`. No brand's
words are typed here. (The same file `components/email-production/machine/
brand_facts.py` reads; this is a small reader of that file, not an import of
that tool's internals.)
"""
import html.parser
import json
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
import paths as P                                             # noqa: E402

# Furniture every sender's email carries — no brand's words here.
GENERIC_ALTS = {"shop", "facebook", "instagram", "tiktok", "youtube", "twitter", "x",
                "pinterest", "linkedin", "logo", "custom"}
PLATFORMS = ("facebook", "instagram", "tiktok", "youtube")
SOCIAL_HOST = re.compile(r"->\s*https?://(?:www\.)?(facebook|instagram|tiktok|youtube|twitter|x|pinterest|linkedin)\.com", re.I)
LEGAL = re.compile(r"unsubscribe|no longer want to receive|view (?:this email )?in (?:your )?browser|"
                   r"manage (?:your )?preferences|all rights reserved|organization\.(?:name|full_address)", re.I)
MERGE = re.compile(r"\{\{.*?\}\}|\{%.*?%\}|\*\|[A-Z_:]+\|\*")
HIDDEN = re.compile("[​‌‍⁠﻿]")
IMAGE = re.compile(r"\[IMAGE alt=(.*?)\]\s+https?://", re.S)
# What a construct may never name: the frame every email arrives in.
FRAME_NOUNS = ("logo row", "navigation row", "nav row", "nav bar", "category links", "category tiles",
               "social row", "social icons", "footer", "unsubscribe", "view in browser", "postal address")


def brand_words(brand):
    """(exact furniture alt texts, the brand's own furniture list) — read from
    the brand's file at run time. A brand with nothing on file has none."""
    f = P.REPO / "brands" / brand / "email" / "simple.json"
    try:
        look = json.loads(f.read_text())
    except (OSError, ValueError):
        look = {}
    own = [str(w).strip().lower() for w in (look.get("furniture") or []) if str(w).strip()]
    names = {brand.lower()}
    alt = ((look.get("logo") or {}).get("alt") or "").strip().lower()
    if alt:
        names.add(alt)
    alts = set(GENERIC_ALTS) | names | set(own) | {f"{n} on {p}" for n in names for p in PLATFORMS}
    return alts, own


class _Reduce(html.parser.HTMLParser):
    """An HTML email as the same plain lines the sent-email files use:
    text, `[IMAGE alt=…] src`, `[LINK] … -> href`."""
    def __init__(self):
        super().__init__()
        self.out, self.href, self.skip = [], None, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("style", "script", "head", "title"):
            self.skip += 1
        elif tag == "a":
            self.href = a.get("href") or ""
            self.out.append("[LINK] ")
        elif tag == "img":
            self.out.append(f"[IMAGE alt={a.get('alt') or ''}] {a.get('src') or ''}")
        elif tag in ("p", "div", "tr", "br", "h1", "h2", "h3", "li", "table"):
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("style", "script", "head", "title"):
            self.skip = max(0, self.skip - 1)
        elif tag == "a":
            self.out.append(f" -> {self.href}\n" if self.href is not None else "\n")
            self.href = None

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.out.append(data.strip() + " ")


def load(source):
    """The source email as text. `.html` is reduced to plain lines; anything
    else is read as it stands."""
    f = Path(source)
    text = f.read_text(errors="replace")
    if f.suffix.lower() in (".html", ".htm"):
        r = _Reduce()
        r.feed(text)
        text = re.sub(r"\n\s*\n+", "\n\n", "".join(r.out)).strip() + "\n"
    return text


def scan(text, brand):
    """{furniture: [{line, why, text}], defects: [{line, kind, quote}]} — what
    the code can see without a model. Line numbers are the source's own."""
    alts, _ = brand_words(brand)
    furn, defects = [], []
    for n, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or not HIDDEN.sub("", s).strip():
            continue                                       # blank, or nothing but hidden characters
        m = IMAGE.search(s)
        alt = re.sub(r"[™®]", "", m.group(1)).strip() if m else ""
        why = None
        if LEGAL.search(s):
            why = "unsubscribe / address / legal line"
        elif SOCIAL_HOST.search(s):
            why = "links to a social platform"
        elif m and alt.lower() in alts:
            why = "its alt text is a standing furniture word"
        elif m and len(alt) < 60 and re.search(r"\blogo\b|\bheader\b|\bfooter\b", alt, re.I):
            why = "its alt text names a logo, header or footer"
        if why:
            furn.append({"line": n, "why": why, "text": s[:160]})
        if not (why and LEGAL.search(s)):                  # the footer's own tags are furniture, not damage
            for tag in MERGE.findall(s):
                defects.append({"line": n, "kind": "merge tag showing as code", "quote": tag})
        if HIDDEN.search(s):
            defects.append({"line": n, "kind": "hidden character inside a line", "quote": HIDDEN.sub("", s)[:80]})
    return {"furniture": furn, "defects": defects}


def findings_text(found):
    """The scan, as the read step is handed it."""
    out = ["Lines the code already flagged as page furniture (line · why · text):"]
    out += [f"- {f['line']} · {f['why']} · {f['text']}" for f in found["furniture"]] or ["- none found by the code"]
    out += ["", "Damage the code already found (line · kind · quoted):"]
    out += [f"- {d['line']} · {d['kind']} · {d['quote']}" for d in found["defects"]] or ["- none found by the code"]
    return "\n".join(out)


# ------------------------------------------------------------------ the record

HEADS = ("THE MESSAGE", "PAGE FURNITURE", "SOURCE DEFECTS")


def _head(name):
    return re.compile(rf"^#{{1,3}}\s*\**{name}\**\s*$", re.M)


# The block arrives as ```STRIP … ``` or as a `# STRIP` heading over a plain (or ```json) fence.
STRIP_RX = r"(?:```STRIP[ \t]*\n|^#+[ \t]*STRIP[ \t]*\n+```(?:json)?[ \t]*\n)(.*?)```"

def strip_block(record):
    """The fenced ```STRIP block → {"furniture_words": [...], "defects": [{id, quote, meant}]}."""
    m = re.search(STRIP_RX, record or "", re.S | re.M)
    if not m:
        raise ValueError("the record carries no ```STRIP block")
    try:
        got = json.loads(m.group(1))
    except ValueError as e:
        raise ValueError(f"the STRIP block is not valid JSON ({e})")
    if not isinstance(got, dict):
        raise ValueError("the STRIP block is not a JSON object")
    words = [str(w).strip() for w in got.get("furniture_words") or [] if str(w).strip()]
    defects = [d for d in got.get("defects") or [] if isinstance(d, dict) and d.get("quote")]
    return {"furniture_words": words, "defects": defects}


def record_problems(record):
    """The read step's answer must arrive in its labelled parts."""
    out = [f"the record has no `# {h}` heading" for h in HEADS if not _head(h).search(record or "")]
    try:
        strip_block(record)
    except ValueError as e:
        out.append(str(e))
    return out


def message_only(record):
    """The record without its PAGE FURNITURE section and without the STRIP
    block: the furniture is named by number only, never by its words."""
    rec = re.sub(STRIP_RX, "", record or "", flags=re.S | re.M)
    m = _head("PAGE FURNITURE").search(rec)
    if not m:
        return rec.strip() + "\n"
    nxt = _head("SOURCE DEFECTS").search(rec, m.end())
    end = nxt.start() if nxt else len(rec)
    ids = sorted(set(re.findall(r"\bF\d+\b", rec[m.start():end])), key=lambda x: int(x[1:]))
    note = ("# PAGE FURNITURE\n\n(Taken out by the code before this step. Items set aside: "
            + (", ".join(ids) or "none numbered") + ". Their words are withheld on purpose — "
            "nothing in them is part of what this email argues.)\n\n")
    return (rec[:m.start()] + note + rec[end:]).strip() + "\n"


def construct_problems(construct, strip, brand):
    """What the finished construct may not carry."""
    text = construct or ""
    body = re.split(r"^\**LEFT OUT:?\**", text, flags=re.M)[0]
    low = body.lower()
    out = []
    _, own = brand_words(brand)
    phrases = {w.lower() for w in strip.get("furniture_words", [])} | set(own)
    # A one-word furniture entry (a category name, an icon's alt) is an exact
    # ALT text, and an ordinary English word anywhere else — only phrases are
    # swept. One-word leaks are the subject-free test's job, in the prompt.
    for p in sorted(w for w in phrases if len(w.split()) >= 2):
        if re.search(rf"(?<!\w){re.escape(p)}(?!\w)", low):
            out.append(f"the construct carries page-furniture words: “{p}”")
    for noun in FRAME_NOUNS:
        if re.search(rf"(?<!\w){re.escape(noun)}(?!\w)", low):
            out.append(f"the construct names the sender's frame: “{noun}”")
    for d in strip.get("defects", []):
        q = str(d.get("quote") or "").strip()
        if len(q) >= 6 and q.lower() in low:
            out.append(f"the construct carries a source defect ({d.get('id', 'D?')}): “{q[:80]}”")
    tag = MERGE.search(body)
    if tag:
        out.append("the construct carries a merge tag as code: " + tag.group(0)[:60])
    for need in ("THE MOVES", "THE SEQUENCE LOGIC", "LOAD-BEARING"):
        if need not in text:
            out.append(f"the construct has no `{need}` part")
    if not re.search(r"^\**LEFT OUT:?", text, re.M):
        out.append("the construct does not end on its `LEFT OUT:` line")
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["scan"])
    ap.add_argument("source")
    ap.add_argument("--brand", required=True, help="the brand whose furniture words to read — there is no default")
    a = ap.parse_args()
    print(findings_text(scan(load(a.source), a.brand)))
