#!/usr/bin/env python3
"""Fill a run's image slots with FAL-generated candidates. (Stage 2, on
Damon's go 2026-08-31: "we will have FAL AI actually generate images".)

    python3 fal_generate.py results/<label> [--brand <brand>] [--model fal-ai/flux-pro/v1.1]

Reads the run's BLOCKS, takes every image/product block's image_brief as the
prompt (plus the brand's photographic register), generates one candidate per
slot, and writes results/<label>/images/slot-<n>.png + images.json.
render_email.py picks them up automatically on its next run.

The designer reviews everything (HANDOFF-TO-HUMANS ruling) — these are
candidates, not final art. Key: FAL_KEY in ~/.daemn/keys.env.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from paths import HERE, WORKSPACE

def photo_register(brand):
    """The brand's photographic register comes from ITS skin — the tool
    carries no look of its own (de-branded 2026-08-31)."""
    f = WORKSPACE / "brands" / brand / "email" / "design-formats" / "components.json"
    reg = json.loads(f.read_text()).get("photo_register") if f.is_file() else None
    if not reg:
        sys.exit(f"{brand} has no photo_register in its components.json — "
                 "a brand's look is never invented; extract it first")
    return reg


def fal_key():
    for line in (Path.home() / ".daemn" / "keys.env").read_text().splitlines():
        if line.startswith("FAL_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit("no FAL_KEY in ~/.daemn/keys.env")


def generate(model, key, prompt, size):
    # curl, not urllib: the chain runner email.py shadows the stdlib `email`
    # package, which urllib needs (hit 2026-08-31).
    body = json.dumps({"prompt": prompt, "image_size": size,
                       "safety_tolerance": "2"})
    r = subprocess.run(["curl", "-sS", "--max-time", "180",
                        "-H", f"Authorization: Key {key}",
                        "-H", "Content-Type: application/json",
                        "-d", body, f"https://fal.run/{model}"],
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:200])
    out = json.loads(r.stdout)
    if "images" not in out:
        raise RuntimeError(str(out)[:200])
    url = out["images"][0]["url"]
    r = subprocess.run(["curl", "-sSL", "--max-time", "120", url],
                       capture_output=True)
    if r.returncode:
        raise RuntimeError("download failed")
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--brand", required=True)
    ap.add_argument("--model", default="fal-ai/flux-pro/v1.1")
    a = ap.parse_args()
    run_dir = Path(a.run_dir)
    if not run_dir.is_absolute():
        run_dir = HERE / run_dir

    m = re.search(r"```BLOCKS\s*(\[.*?\])\s*```",
                  (run_dir / "stage8--blocks.md").read_text(), re.S)
    blocks = json.loads(m.group(1))
    style = photo_register(a.brand)
    key = fal_key()
    (run_dir / "images").mkdir(exist_ok=True)
    mapping, made = {}, 0
    for i, b in enumerate(blocks):
        if b.get("type") not in ("image", "product") or not b.get("image_brief"):
            continue
        brief = b["image_brief"]
        size = ({"width": 1024, "height": 1024} if b["type"] == "product"
                else {"width": 1216, "height": 832})
        prompt = f"{brief}\n\n{style}"
        name = f"slot-{i:02d}.png"
        print(f"  -> {name}  ({brief[:70]}…)", flush=True)
        try:
            png = generate(a.model, key, prompt, size)
        except Exception as ex:
            print(f"     FAILED: {str(ex)[:120]} — slot stays open", flush=True)
            continue
        (run_dir / "images" / name).write_bytes(png)
        mapping[str(i)] = f"images/{name}"
        made += 1
    (run_dir / "images.json").write_text(json.dumps(
        {"model": a.model, "style_suffix": style, "slots": mapping}, indent=1) + "\n")
    print(f"{made} image(s) generated -> {run_dir / 'images'}  (candidates; "
          "the designer reviews everything)")


if __name__ == "__main__":
    main()
