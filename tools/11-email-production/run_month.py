#!/usr/bin/env python3
"""Produce every email a month's board calls for — the chain, then the
brand-skinned mockup, for every slot and every variant inside it.

    python3 run_month.py results/calendar-2026-09 [--limit N] [--only sep-01,sep-02]

Reuses brief.py's variant_runs/chain_argv so a slot with three avatars in it
produces three real emails, each carrying the angle the cells stage picked —
never the composer's flattened "mixed" guess. Runs with bounded concurrency
so this doesn't try to open sixty Claude subprocesses at once; logs to
production.log inside the run folder so progress survives if this is
watched rather than waited on.
"""
import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from paths import HERE, WORKSPACE, calendar_tool
import brief

sys.path.insert(0, str(HERE / "machine"))
import email_elements as EE          # asks components/elements: is this type a real one?   # noqa: E402

CONCURRENCY = 4


def log(f, msg):
    line = f"{time.strftime('%H:%M:%S')}  {msg}"
    print(line, flush=True)
    f.write(line + "\n")
    f.flush()


PUSH = False


def one_run(label, argv, brand, logf):
    t0 = time.time()
    log(logf, f"start {label}  (writing)")
    r = subprocess.run(argv, cwd=HERE, capture_output=True, text=True)
    if r.returncode:
        # stdout too: `email.py` reports a usage limit or a refused offer there
        return label, "chain-fail", (r.stderr + r.stdout)[-800:], round(time.time() - t0, 1)
    # THE SIMPLE EMAIL (Damon, 2026-09-19): logo, headline, one picture, the
    # copy, an optional offer picture, one button — pictures by GPT, and with
    # --push a Klaviyo DRAFT. Replaces the designed-template step.
    build = ["python3", "simple_email.py",
             str(WORKSPACE / "runs" / "email-production" / brand / label), "--brand", brand]
    if PUSH:
        build.append("--push")
    log(logf, f"      {label}  written in {round(time.time() - t0, 1)}s — pictures and layout"
              + (" and the Klaviyo draft" if PUSH else ""))
    render = subprocess.run(build, cwd=HERE, capture_output=True, text=True)
    if render.returncode:
        return label, "build-fail", (render.stderr + render.stdout)[-800:], round(time.time() - t0, 1)
    return label, "done", render.stdout.strip().splitlines()[-1], round(time.time() - t0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--limit", type=int, default=None,
                    help="produce only the first N runs — a pilot batch")
    ap.add_argument("--only", default=None,
                    help="comma-separated slot ids — produce only these")
    # ONE AVATAR PER BRAND (Damon, 2026-09-15: "don't worry about different
    # avatars at this stage"). A slot targeting three avatars produces three
    # emails, which is right when the month ships and wrong while the writing
    # itself is being judged — three versions of one send tell you nothing
    # extra about whether the copy is good, and cost three times as much to
    # find out. A send with NO avatar (an affiliate feature, a sitewide note)
    # is not a second avatar and is kept: omitting the avatar is a declaration
    # the chain is told about, not a gap.
    ap.add_argument("--avatar", default=None,
                    help="produce only this avatar's version of each send "
                         "(plus sends that carry no avatar at all)")
    ap.add_argument("--concurrency", type=int, default=CONCURRENCY)
    ap.add_argument("--push", action="store_true",
                    help="put each finished email into Klaviyo as a DRAFT")
    ap.add_argument("--from-date", default=None, metavar="YYYY-MM-DD",
                    help="skip sends dated before this day — a send whose day "
                         "has passed is not written")
    args = ap.parse_args()
    global PUSH
    PUSH = args.push

    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = HERE / run_dir
    slots = json.loads((run_dir / "slots.json").read_text())
    run = json.loads((run_dir / "run.json").read_text())
    brand = run["brand"]

    # A month is planned by the calendar and then CORRECTED by a person on its
    # review board. Read the merged view, never raw slots.json: reading the
    # plan alone would write the send the planner first proposed instead of the
    # one the reviewer approved, and silently throw away every rewrite
    # (marketing-calendar CONTRACT.md, 2026-09-13). A slot the reviewer cut is
    # not produced at all.
    notes = {}
    try:
        sys.path.append(str(calendar_tool("machine")))
        import review as _rev
        _state = _rev.load(run_dir)
        slots = _rev.applied(slots, _state)
        cut = [s["id"] for s in slots if s["_review"]["status"] == "cut"]
        slots = [s for s in slots if s["_review"]["status"] != "cut"]
        notes = {s["id"]: s["_review"]["note"] for s in slots if s["_review"]["note"]}
        edited = sum(1 for s in slots if s["_review"]["edits"])
        if cut or notes or edited:
            print(f"review: {edited} slot(s) rewritten, {len(notes)} note(s), "
                  f"{len(cut)} cut" + (f" ({', '.join(cut)})" if cut else ""))
    except Exception as e:                                      # noqa: BLE001
        print(f"review layer unreadable ({e}) — producing the plan as written")

    only = set(args.only.split(",")) if args.only else None
    jobs = []
    skipped = []
    blocked = []
    # a month folder named calendar-YYYY-MM-<brand> belongs to a second brand: its runs get a <brand>- prefix
    prefix = (brand + '-') if run_dir.name.endswith('-' + brand) else ''
    for slot in slots:
        if only and slot["id"] not in only:
            continue
        if args.from_date and (slot.get("date") or "") < args.from_date:
            continue
        # an email type nobody has defined is not written (the elements gate)
        why = EE.type_problem(brand, slot.get("type"))
        if why:
            blocked.append((slot["id"], why))
            continue
        for av, angle, label in brief.variant_runs(slot, brand):
            if args.avatar and av not in (args.avatar, None, "none", "mixed"):
                continue
            if prefix and not label.startswith(prefix):
                label = prefix + label           # results/<brand>-sep-01… when the month folder carries a brand suffix
            argv = brief.chain_argv(slot, brand, av, angle, label,
                                    note=notes.get(slot["id"]))
            if argv is None:
                skipped.append(label)
                continue
            jobs.append((label, argv))
    if args.limit:
        jobs = jobs[:args.limit]

    logf = (run_dir / "production.log").open("a")
    log(logf, f"=== production run: {len(jobs)} email(s) to build "
              f"({len(skipped)} skipped — no source), concurrency {args.concurrency} ===")
    if skipped:
        log(logf, "skipped (no source fits): " + ", ".join(skipped))
    for sid, why in blocked:
        log(logf, f"BLOCKED {sid} — {why[:200]}")

    done, failed = [], []
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = {ex.submit(one_run, label, argv, brand, logf): label
                   for label, argv in jobs}
        for fut in as_completed(futures):
            label, status, detail, seconds = fut.result()
            if status == "done":
                done.append(label)
                log(logf, f"OK    {label}  ({seconds}s)  {detail}")
            else:
                failed.append(label)
                log(logf, f"FAIL  {label}  [{status}]  ({seconds}s)")
                log(logf, "      " + detail.replace("\n", "\n      "))

    log(logf, f"=== done: {len(done)} built, {len(failed)} failed, "
              f"{len(skipped)} skipped ===")
    logf.close()
    print(f"\n{len(done)}/{len(jobs)} emails built · {len(failed)} failed · "
          f"{len(skipped)} skipped (no source)")
    if failed:
        print("failed: " + ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
