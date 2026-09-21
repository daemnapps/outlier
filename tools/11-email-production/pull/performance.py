#!/usr/bin/env python3
"""What every send actually did, joined to what it was.

    python3 calendar/performance.py --brand <brand> [--months 12]

The classification says what each email WAS. This says what it DID. Joined,
they answer the question the calendar exists to settle: what earns, by
category, by type, by segment, by day, by hour.

Metrics are pulled per campaign from the platform's own reporting, so nothing
is estimated. Open rate is reported but carries a caveat everywhere it appears:
Apple Mail privacy auto-opens inflate it, and a segment selected FOR engagement
inflates it again. Click and revenue per recipient are the honest columns.

Reads only.
"""
import argparse
import json
import sys
import time
import urllib.error
from collections import defaultdict
from pathlib import Path

import derive as D

HERE = Path(__file__).resolve().parent

STATS = ["recipients", "delivered", "opens_unique", "clicks_unique",
         "conversions", "conversion_value", "unsubscribes", "spam_complaints",
         "bounced", "revenue_per_recipient"]


def report(key, conversion_metric, timeframe_days):
    body = {"data": {"type": "campaign-values-report", "attributes": {
        "statistics": STATS,
        "timeframe": {"key": timeframe_days},
        "conversion_metric_id": conversion_metric,
        "filter": "equals(send_channel,'email')",
    }}}
    return D.post("campaign-values-reports", key, body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", default="<brand>")
    ap.add_argument("--timeframe", default="last_12_months")
    ap.add_argument("--conversion", default="Tyyrjv", help="the Placed Order metric")
    args = ap.parse_args()
    key = D.key_for(args.brand)

    for a in range(6):
        try:
            r = report(key, args.conversion, args.timeframe)
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** a)
                continue
            sys.exit(f"HTTP {e.code}: {e.read()[:400]}")
    else:
        sys.exit("rate limited out")

    rows = r["data"]["attributes"]["results"]
    out = BRAND_ROOT / args.brand / "email" / f"-performance.json"
    out.write_text(json.dumps(rows, indent=1) + "\n")
    print(f"{len(rows)} campaign rows -> {out.name}")

    # join to what each email WAS
    cls = {}
    cf = BRAND_ROOT / args.brand / "email" / f"-classified.json"
    idx = BRAND_ROOT / args.brand / "email" / f"-sends" / "index.json"
    if cf.is_file() and idx.is_file():
        byfile = {x["file"]: x for x in json.loads(cf.read_text())}
        for x in json.loads(idx.read_text()):
            c = byfile.get(x["file"])
            if c:
                cls[x.get("id") or x["file"]] = c
    print(f"classified emails available to join: {len(cls)}")
    return rows, cls


if __name__ == "__main__":
    main()
