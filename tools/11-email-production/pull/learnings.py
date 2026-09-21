#!/usr/bin/env python3
"""What the sending has taught, joined from what each email WAS and DID.

    python3 calendar/learnings.py --brand <brand>

Not a tally. Every cut here exists to answer "where is the opportunity" —
which categories and types earn, which are under-used relative to what they
earn, and what the timing data says.

Two caveats carried everywhere rather than stated once:
- **Open rate is not trustworthy.** Apple Mail privacy auto-opens inflate it,
  and a segment selected FOR engagement inflates it again. Click rate and
  revenue per recipient are the honest columns.
- **Small n is small n.** Any cut under ~5 sends is labelled, because at that
  size one email moves the average.

Reads only.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent

# The tool holds the code; the BRAND holds its own record. A puller writes into
# brands/<brand>/email/ so the next tool — statics, video — reads the
# same facts from the same place instead of each keeping a copy.
BRANDS = next(d for d in HERE.parents if (d / "brands").is_dir() and (d / "components").is_dir()) / "brands"


def chan(brand, name):
    d = BRANDS / brand / "email"
    d.mkdir(parents=True, exist_ok=True)
    return d / name

CATS = {"ask": "Promotional", "help": "Educational", "belong": "Cultural",
        "real": "Community", "brand": "Brand"}


def load(brand):
    B = BRANDS / brand / "email"
    perf = {r["groupings"]["campaign_id"]: r["statistics"]
            for r in json.loads((B / "performance.json").read_text())}
    cls = {x["file"]: x for x in json.loads((B / "classified.json").read_text())}
    idx = json.loads((B / "sends" / "index.json").read_text())
    # the sends index does not carry the campaign id — it was built for reading,
    # not joining. The ledger has it, keyed by the same (date, campaign name).
    led_rows = json.loads((B / "ledger.json").read_text())
    led = {x["id"]: x for x in led_rows}
    by_name = {(x["sent"], x["campaign"]): x["id"] for x in led_rows}
    rows = []
    for x in idx:
        cid = by_name.get((x.get("sent"), x.get("campaign")))
        if cid not in perf:
            continue
        c = cls.get(x["file"], {})
        s = perf[cid]
        rec = s.get("recipients") or 0
        if rec < 50:
            continue
        rows.append(dict(
            id=cid, sent=x.get("sent"), subject=x.get("subject"),
            category=c.get("category"), type=c.get("type"),
            audiences=led.get(cid, {}).get("audiences", []),
            hour=led.get(cid, {}).get("hour"),
            is_local=led.get(cid, {}).get("is_local"),
            recipients=rec,
            open_rate=(s.get("opens_unique") or 0) / rec,
            click_rate=(s.get("clicks_unique") or 0) / rec,
            conv=(s.get("conversions") or 0),
            revenue=(s.get("conversion_value") or 0),
            rpr=(s.get("revenue_per_recipient") or 0),
            unsub_rate=(s.get("unsubscribes") or 0) / rec,
            spam_rate=(s.get("spam_complaints") or 0) / rec))
    return rows


def agg(rows, keyfn):
    g = defaultdict(list)
    for r in rows:
        k = keyfn(r)
        if k:
            g[k].append(r)
    out = []
    for k, v in g.items():
        rec = sum(r["recipients"] for r in v)
        out.append(dict(
            key=k, sends=len(v), recipients=rec,
            revenue=sum(r["revenue"] for r in v),
            rpr=sum(r["revenue"] for r in v) / rec if rec else 0,
            click=sum(r["click_rate"] * r["recipients"] for r in v) / rec if rec else 0,
            open=sum(r["open_rate"] * r["recipients"] for r in v) / rec if rec else 0,
            unsub=sum(r["unsub_rate"] * r["recipients"] for r in v) / rec if rec else 0))
    return sorted(out, key=lambda x: -x["rpr"])


def table(rows, label, thin=5):
    L = [f"| {label} | Sends | Revenue | Rev/recipient | Click | Unsub |",
         "|---|---|---|---|---|---|"]
    for r in rows:
        n = f"{r['key']}" + (" *" if r["sends"] < thin else "")
        L.append(f"| {n} | {r['sends']} | ${r['revenue']:,.0f} | "
                 f"**${r['rpr']:.3f}** | {100*r['click']:.2f}% | {100*r['unsub']:.2f}% |")
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", default="<brand>")
    args = ap.parse_args()
    rows = load(args.brand)
    tot_rec = sum(r["recipients"] for r in rows)
    tot_rev = sum(r["revenue"] for r in rows)

    L = [f"# {args.brand} — what the sending has taught", "",
         f"{len(rows)} campaigns with both a classification and real reported",
         f"numbers. {tot_rec:,} recipients, ${tot_rev:,.0f} attributed.", "",
         "**Two caveats, carried rather than footnoted.** Open rate is not",
         "trustworthy — Apple Mail privacy auto-opens inflate it and an",
         "engagement-selected segment inflates it again; click rate and revenue",
         "per recipient are the honest columns. And a row marked `*` has fewer",
         "than five sends behind it, where one email moves the average.", "",
         "## By category", "",
         "The question this answers: what is each kind of email worth per person",
         "it reaches, and what does it cost in unsubscribes.", ""]
    bycat = agg(rows, lambda r: CATS.get(r["category"]))
    L += table(bycat, "Category")

    L += ["", "## By type — the top earners", ""]
    bytype = [t for t in agg(rows, lambda r: r["type"]) if t["sends"] >= 3][:14]
    L += table(bytype, "Type", thin=5)

    L += ["", "## By type — the ones that cost more than they earn", ""]
    worst = sorted([t for t in agg(rows, lambda r: r["type"]) if t["sends"] >= 3],
                   key=lambda x: x["rpr"])[:8]
    L += table(worst, "Type", thin=5)

    L += ["", "## By day of week", ""]
    import datetime as dt
    byday = agg(rows, lambda r: dt.date.fromisoformat(r["sent"]).strftime("%A")
                if r["sent"] else None)
    L += table(byday, "Day")

    L += ["", "## By send hour", "",
          "The hour the send was scheduled for. **This is the one timing lever",
          "that has actually been varied** — 13:00 carries about a third of all",
          "sends, but there is real spread across the evening and the small",
          "hours, so the comparison is honest.", ""]
    byhour = [h for h in agg(rows, lambda r: f"{r['hour']}:00" if r["hour"] else None)
              if h["sends"] >= 4]
    L += table(sorted(byhour, key=lambda x: -x["rpr"]), "Hour set")

    L += ["", "## Local time vs one fixed time", "",
          "Local-time send delivers at that hour in each person's own zone. It",
          "has been used on some sends and not others, which makes it the",
          "cleanest comparison on this page.", ""]
    L += table(agg(rows, lambda r: "each person's local time" if r["is_local"]
                   else "one fixed time for everyone"), "Method")

    L += ["", "## The opportunity", "",
          "Share of sends against share of revenue, per category. A category",
          "earning more than its share of the sending is one to send more of.", "",
          "| Category | Share of sends | Share of revenue | |", "|---|---|---|---|"]
    for c in sorted(bycat, key=lambda x: -x["revenue"]):
        ss = 100 * c["sends"] / len(rows)
        sr = 100 * c["revenue"] / tot_rev if tot_rev else 0
        verdict = "**under-sent**" if sr > ss * 1.25 else (
            "over-sent" if ss > sr * 1.25 else "balanced")
        L.append(f"| {c['key']} | {ss:.0f}% | {sr:.0f}% | {verdict} |")

    (BRAND_ROOT / args.brand / "email" / f"-learnings.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:8]))
    print(f"\n-> brands/{args.brand}-learnings.md")


if __name__ == "__main__":
    main()
