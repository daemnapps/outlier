#!/usr/bin/env python3
"""The human layer over a planned month.

`slots.json` is the MACHINE's record of what it decided and why. This is the
separate file a reviewer writes into — status, edits, notes — so the two never
overwrite each other. Re-planning a month replaces slots.json and leaves every
judgement already made on it intact; a reviewer's rewrite is never lost to a
re-run, and a re-run is never quietly re-approved.

    review.json
    {
      "slots": {
        "sep-01": {
          "status": "approved" | "needs-work" | "cut" | "pending",
          "note":   "free text from the reviewer",
          "edits":  {"<field>": "<new value>", ...},          # overrides
          "by": "<who>", "at": "<iso timestamp>"
        }
      },
      "copy": {"sep-01": {"state": "queued|running|done|failed", "at": ...}}
    }

A field the reviewer never touched is absent from `edits`, so the board can
always show what the machine said beside what the human changed it to.
"""
import datetime
import json
from pathlib import Path

STATUSES = ("pending", "approved", "needs-work", "cut")

# The fields a reviewer may rewrite. Everything else on a slot is the
# machine's reasoning — readable, never editable, because editing a `why`
# would forge the record of why the send exists.
EDITABLE = ("date", "hour", "segment", "category", "type", "role",
            "offer", "product", "occasion", "angle")


def path(run_dir):
    return Path(run_dir) / "review.json"


def load(run_dir):
    try:
        d = json.loads(path(run_dir).read_text())
    except (FileNotFoundError, ValueError):
        d = {}
    d.setdefault("slots", {})
    d.setdefault("copy", {})
    return d


def save(run_dir, data):
    path(run_dir).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return data


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def for_slot(data, slot_id):
    return data["slots"].setdefault(
        slot_id, {"status": "pending", "note": "", "edits": {}})


def set_status(run_dir, slot_id, status, who="reviewer"):
    if status not in STATUSES:
        raise ValueError(f"unknown status {status!r}")
    d = load(run_dir)
    r = for_slot(d, slot_id)
    r.update(status=status, by=who, at=now())
    return save(run_dir, d)


def set_note(run_dir, slot_id, note, who="reviewer"):
    d = load(run_dir)
    r = for_slot(d, slot_id)
    r.update(note=note, by=who, at=now())
    return save(run_dir, d)


def set_edit(run_dir, slot_id, field, value, who="reviewer"):
    """An edit back to the machine's own value clears the override, so a
    reverted change stops reading as a change."""
    if field not in EDITABLE:
        raise ValueError(f"{field!r} is not a reviewer-editable field")
    d = load(run_dir)
    r = for_slot(d, slot_id)
    value = (value or "").strip()
    if value:
        r["edits"][field] = value
    else:
        r["edits"].pop(field, None)
    r.update(by=who, at=now())
    return save(run_dir, d)


def clear_edit(run_dir, slot_id, field):
    d = load(run_dir)
    for_slot(d, slot_id)["edits"].pop(field, None)
    return save(run_dir, d)


def applied(slots, data):
    """Every slot with the reviewer's overrides laid on top, plus the review
    state itself. This is what anything downstream should read — the copy
    machine must write the send the human approved, not the one the planner
    first proposed."""
    out = []
    for s in slots:
        r = data["slots"].get(s["id"], {})
        merged = dict(s)
        # What the PLANNER said, kept beside what the human made of it — the
        # board shows both, and a merge that forgot the original would show
        # the edit twice (caught on the first edit, 2026-09-13).
        orig = {f: s.get(f) for f in EDITABLE if f != "angle"}
        vs = s.get("variants") or []
        orig["angle"] = vs[0].get("angle") if vs else s.get("angle")
        merged["_orig"] = orig
        merged["variants"] = [dict(v) for v in vs]
        for f, v in (r.get("edits") or {}).items():
            if f == "angle":
                for var in merged.get("variants") or []:
                    var["angle"] = v
            elif f == "hour":
                try:
                    merged["hour"] = int(v)
                except ValueError:
                    merged["hour"] = v
            else:
                merged[f] = v
        if "segment" in (r.get("edits") or {}):
            merged["segments"] = [merged["segment"]]
        merged["_review"] = {"status": r.get("status", "pending"),
                             "note": r.get("note", ""),
                             "edits": r.get("edits", {}),
                             "at": r.get("at"), "by": r.get("by")}
        merged["_copy"] = data["copy"].get(s["id"], {})
        out.append(merged)
    return out
