#!/usr/bin/env python3
"""Placeholder pictures for the month's wireframes (Damon, 2026-09-09:
"generate basic images to place in there ... for the placeholders").

    python3 gen_placeholders.py [--brand <brand>] [--month 2026-09]

One image per picture slot in every wireframe, from the slot's own direction
plus the brand's photographic register (components.json). They are placeholders
for the layout, never final art — the designer replaces them.

Writes results/_placeholders/<run>-<n>.png and an index.json.
"""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import HERE
import fal_generate as FG
import figma_brief as FB

ap = argparse.ArgumentParser()
ap.add_argument("--brand", required=True, help="brand folder name under brands/ — there is no default brand")
ap.add_argument("--month", default=None, help="YYYY-MM — only that month's runs; omit for every run this brand has")
ap.add_argument("--model", default="fal-ai/flux/schnell")
a = ap.parse_args()

style = FG.photo_register(a.brand)
key = FG.fal_key()
out = HERE / "results" / "_placeholders"
out.mkdir(parents=True, exist_ok=True)
idx_f = out / "index.json"
idx = json.loads(idx_f.read_text()) if idx_f.is_file() else {}

# THIS BRAND'S RUNS, by each run's own run.json — never by a folder-name prefix,
# which silently left one brand's runs out.
sys.path.insert(0, str(HERE / "machine"))
import brand_facts as BF
runs = [p.name for p in BF.runs_of(a.brand, HERE / "results",
                                   BF.month_abbr(a.month) if a.month else None)]
made = 0
for r in runs:
    pics = [b["t"] for b in FB.wire_blocks(HERE / "results" / r, a.brand) if b["k"] == "P"]
    for n, direction in enumerate(pics):
        name = f"{r}-{n}.png"
        if (out / name).is_file():
            idx[name] = direction; continue
        d = direction.replace("product shot - ", "")
        prompt = f"{d}\n\n{style}"
        size = {"width": 1216, "height": 832}
        try:
            png = FG.generate(a.model, key, prompt, size)
        except Exception as ex:
            print(f"  FAILED {name}: {str(ex)[:100]}", flush=True); continue
        (out / name).write_bytes(png)
        idx[name] = direction
        made += 1
        print(f"  {name}  ({d[:60]})", flush=True)
        idx_f.write_text(json.dumps(idx, indent=1) + "\n")
idx_f.write_text(json.dumps(idx, indent=1) + "\n")
print(f"{made} new placeholder(s) -> {out}")
