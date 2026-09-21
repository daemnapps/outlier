#!/usr/bin/env python3
"""The element library — every format, structure, framework, style, delivery
value, template and doctrine term in the system, in one shape, and the one
place a tool asks "is this a real one?".

    python3 elements.py build                     # read every source, write library/
    python3 elements.py list                      # what's in it, per element
    python3 elements.py get format video song-ad  # one row, or refused
    python3 elements.py check format:video=song-ad style:image=candid-ugc

    import elements as E
    E.get("format", "video", "song-ad")           # the row, or raises Unknown
    E.check({("format", "video"): "song-ad"})     # [] or a list of problems

Damon, 2026-09-20: *"If we have these different formats, structures,
frameworks, styles, we need to define all these unique elements… Things
aren't enforced… Everything needs to be green light."*

WHAT IT DOES NOT DO: it never edits a source list. Every list stays where the
tool that uses it reads it (sources.json says where). A list is changed at its
source; `build` refreshes the library. Rows Damon has named that no list holds
yet live in additions.json, as drafts.

THE SAME FIELDS ON EVERY ROW: id · name · what · why_it_works · status ·
signed · examples · evidence · source · extra.
"""
import glob as _glob
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                                          # components/elements
REPO = next(d for d in HERE.parents if (d / "components").is_dir() and (d / "brands").is_dir())
LIBRARY = ROOT / "library"
FIELDS = ("id", "name", "what", "why_it_works", "status", "signed", "examples", "evidence")
APPROVED = {"approved", "proven"}


class Unknown(KeyError):
    """A value that is not on its list. Refused, never guessed."""


# ------------------------------------------------------------------ build

def _dig(d, dotted):
    for part in dotted.split("."):
        d = d[part]
    return d


def _rows_of(block):
    """A list of rows, or a {key: row} map turned into rows carrying @key."""
    if isinstance(block, dict):
        return [dict(v, **{"@key": k}) for k, v in block.items() if isinstance(v, dict)]
    return list(block)


def _shape(raw, src, asset, source_label):
    idf = src.get("id", "id")
    rid = raw.get(idf) if not idf.startswith("@") else raw.get(idf)
    row = {"id": rid}
    for f in FIELDS[1:]:
        key = (src.get("fields") or {}).get(f, f)
        v = raw.get(key)
        if isinstance(v, (list, dict)) and f in ("what", "evidence", "examples"):
            v = json.dumps(v, ensure_ascii=False)[:600]
        row[f] = v
    status = (row.get("status") or "draft")
    row["status"] = status
    row["approved"] = status in APPROVED
    row["source"] = source_label
    row["extra"] = {k: raw[k] for k in (src.get("extra") or []) if k in raw}
    return row


def build():
    spec = json.loads((ROOT / "sources.json").read_text())
    lists = {}
    for src in spec["sources"]:
        el = src["element"]
        units = []                                          # (asset, rows, label)
        if "inline" in src:
            units.append((src["asset"], src["inline"], "components/elements/sources.json (inline)"))
        elif "glob" in src:
            rows = []
            for f in sorted(_glob.glob(str(REPO / src["glob"]))):
                d = json.loads(Path(f).read_text())
                d["@stem"] = Path(f).stem
                rows.append(d)
            units.append((src["asset"], rows, src["glob"]))
        else:
            data = json.loads((REPO / src["path"]).read_text())
            if "groups" in src:
                g = src["groups"]
                for grp in _dig(data, g["path"]):
                    units.append((grp[g["id"]], _rows_of(grp[g["rows"]]), f'{src["path"]} › {grp[g["id"]]}'))
            else:
                units.append((src["asset"], _rows_of(_dig(data, src["rows"])), src["path"]))
        for asset, rows, label in units:
            key = f"{el}/{asset}"
            entry = lists.setdefault(key, {"element": el, "asset": asset, "source": label,
                                           "enforced_by": src.get("enforced_by"),
                                           "note": src.get("note"), "rows": []})
            for raw in rows:
                entry["rows"].append(_shape(raw, src, asset, label))
    # rows Damon has named that no source holds yet
    for add in json.loads((ROOT / "additions.json").read_text())["rows"]:
        key = f'{add["element"]}/{add["asset"]}'
        entry = lists.setdefault(key, {"element": add["element"], "asset": add["asset"],
                                       "source": "components/elements/additions.json",
                                       "enforced_by": None, "note": None, "rows": []})
        if any(r["id"] == add["id"] for r in entry["rows"]):
            continue                                        # the source has it now
        row = {f: add.get(f) for f in FIELDS}
        row["approved"] = False
        row["source"] = "components/elements/additions.json"
        row["extra"] = {}
        entry["rows"].append(row)
    LIBRARY.mkdir(exist_ok=True)
    index = {"built_from": "components/elements/sources.json + additions.json", "lists": []}
    for key, entry in sorted(lists.items()):
        ids = [r["id"] for r in entry["rows"]]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        entry["duplicates"] = dupes
        fname = key.replace("/", ".") + ".json"
        (LIBRARY / fname).write_text(json.dumps(entry, indent=1, ensure_ascii=False) + "\n")
        index["lists"].append({
            "element": entry["element"], "asset": entry["asset"], "file": f"library/{fname}",
            "source": entry["source"], "enforced_by": entry["enforced_by"], "note": entry["note"],
            "rows": len(entry["rows"]), "approved": sum(1 for r in entry["rows"] if r["approved"]),
            "duplicates": dupes})
    (LIBRARY / "index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n")
    return index


# ------------------------------------------------------------------ read

_cache = {}


def _list(element, asset):
    key = f"{element}.{asset}"
    if key not in _cache:
        f = LIBRARY / f"{key}.json"
        if not f.is_file():
            known = sorted(p.stem for p in LIBRARY.glob("*.json") if p.stem != "index")
            raise Unknown(f"no list for {element}/{asset} — the library has: {', '.join(known)}")
        _cache[key] = json.loads(f.read_text())
    return _cache[key]


def rows(element, asset):
    return _list(element, asset)["rows"]


def get(element, asset, id_):
    for r in rows(element, asset):
        if r["id"] == id_:
            return r
    ids = [r["id"] for r in rows(element, asset)]
    raise Unknown(f"`{id_}` is not a {element} for {asset} — known: {', '.join(ids) or 'none yet'}")


def check(labels, approved_only=False):
    """labels: {(element, asset): id or [ids]} → a list of problems, [] when clean."""
    problems = []
    for (el, asset), vals in labels.items():
        for v in ([vals] if isinstance(vals, str) else vals):
            try:
                r = get(el, asset, v)
                if approved_only and not r["approved"]:
                    problems.append(f"{el}/{asset} `{v}` is a {r['status']}, not approved")
            except Unknown as e:
                problems.append(e.args[0])
    return problems


# ------------------------------------------------------------------ cli

def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.split("\n\n")[1])
        return 0
    cmd = argv[0]
    if cmd == "build":
        idx = build()
        for l in idx["lists"]:
            flag = "" if l["rows"] else "   ← EMPTY"
            flag += f"   ← duplicate ids: {', '.join(l['duplicates'])}" if l["duplicates"] else ""
            print(f"  {l['element']:<10} {l['asset']:<16} {l['rows']:>4} rows · {l['approved']:>3} approved{flag}")
        print(f"-> {LIBRARY}/  ({sum(l['rows'] for l in idx['lists'])} rows in {len(idx['lists'])} lists)")
        return 0
    if cmd == "list":
        idx = json.loads((LIBRARY / "index.json").read_text())
        for l in idx["lists"]:
            print(f"  {l['element']}/{l['asset']}: {l['rows']} ({l['approved']} approved) — {l['source']}")
        return 0
    if cmd == "get" and len(argv) == 4:
        try:
            print(json.dumps(get(*argv[1:]), indent=1, ensure_ascii=False))
            return 0
        except Unknown as e:
            print(f"REFUSED: {e.args[0]}")
            return 2
    if cmd == "check":
        labels = {}
        for a in argv[1:]:
            k, _, v = a.partition("=")
            el, _, asset = k.partition(":")
            labels.setdefault((el, asset), []).append(v)
        probs = check(labels)
        print("clean" if not probs else "REFUSED:\n  " + "\n  ".join(probs))
        return 2 if probs else 0
    print(__doc__.split("\n\n")[1])
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
