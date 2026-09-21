#!/usr/bin/env python3
"""Which library elements a torn-down email IS — asked of the element library,
never guessed.

    elements_label.py candidates        print the rows the labelling step is handed

The labelling step is handed the email's record and the candidate rows (id ·
name · what) out of `components/elements/library/`. Its answer comes back as
one fenced ```ELEMENTS block. This file is the other half: it reads that
block, asks `components/elements/machine/elements.py` `check()` whether every
id is a real row on its own list, and returns the record the run files as
`elements.json`.

**An id that is not in the library is REFUSED, with the real ids named — never
guessed, never "closest match".** `none-fits` is a legitimate answer: it
carries a one-line proposed row, which is recorded in the run and is how the
library grows. Nothing here edits the library. (Same pattern as
`image-teardown/tools/elements_label.py`.)
"""
import json
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
import paths as P                                             # noqa: E402

# The labels every email teardown records, as (element, asset). There is no
# structure list for email yet; when one exists it is added here.
LISTS = [("format", "email"), ("template", "email"), ("framework", "all")]
NONE = "none-fits"


def library():
    """The element library's own reader — components/elements/machine/elements.py."""
    machine = str(P.ELEMENTS / "machine")
    if machine not in sys.path:
        sys.path.append(machine)
    import elements as E
    return E


def key(el, asset):
    return f"{el}/{asset}"


def missing_lists():
    """Lists this tool labels against that the library does not hold."""
    E = library()
    out = []
    for el, asset in LISTS:
        try:
            E.rows(el, asset)
        except E.Unknown as e:
            out.append(e.args[0])
    return out


def candidates():
    """The candidate rows as the prompt is handed them: id · name · what."""
    E = library()
    out = []
    for el, asset in LISTS:
        out.append(f"### {key(el, asset)}\n")
        out.append("| id | name | what it is |\n|---|---|---|")
        for r in E.rows(el, asset):
            what = re.sub(r"\s+", " ", str(r.get("what") or "")).replace("|", "/")
            out.append(f"| `{r['id']}` | {r.get('name') or ''} | {what} |")
        out.append("")
    return "\n".join(out) + "\n"


def parse(text):
    """The ```ELEMENTS block as a dict. Raises ValueError saying what is wrong."""
    m = re.search(r"```ELEMENTS\s*\n(.*?)```", text or "", re.S)
    if not m:
        raise ValueError("the labelling answer carries no ```ELEMENTS block")
    try:
        got = json.loads(m.group(1))
    except ValueError as e:
        raise ValueError(f"the ELEMENTS block is not valid JSON ({e})")
    if not isinstance(got, dict):
        raise ValueError("the ELEMENTS block is not a JSON object")
    return got


def validate(answer):
    """(record, problems). Every id is checked against its own list by the
    library; what the library does not hold is refused, with the reason."""
    E = library()
    labels, why, proposed, refused, problems = {}, {}, {}, [], []
    for el, asset in LISTS:
        k = key(el, asset)
        a = answer.get(k)
        if isinstance(a, str):
            a = {"id": a}
        if not isinstance(a, dict) or not a.get("id"):
            problems.append(f"{k}: the answer gave no id")
            continue
        rid = str(a["id"]).strip().strip("`")
        if a.get("why"):
            why[k] = str(a["why"]).strip()
        if rid == NONE:
            line = str(a.get("proposed") or "").strip()
            if not line:
                problems.append(f"{k}: `{NONE}` with no proposed row — say what the new row would be, in one line")
            proposed[k] = line or None
            labels[k] = NONE
            continue
        bad = E.check({(el, asset): rid})
        if bad:
            refused.append({"list": k, "id": rid, "reason": bad[0]})
            problems.append(f"{k}: REFUSED — {bad[0]}")
            continue
        labels[k] = rid
    extra = sorted(set(answer) - {key(*l) for l in LISTS})
    if extra:
        problems.append("the answer labels lists nobody asked for: " + ", ".join(extra))
    record = {"labels": labels, "why": why, "proposed": proposed, "refused": refused,
              "library": "components/elements/library", "lists": [key(*l) for l in LISTS]}
    return record, problems


def read(answer_text):
    """The labelling step's answer → (record, problems). A refusal is data:
    the record comes back whether or not it is clean."""
    try:
        record, problems = validate(parse(answer_text))
    except ValueError as e:
        record = {"labels": {}, "why": {}, "proposed": {}, "refused": [],
                  "library": "components/elements/library", "lists": [key(*l) for l in LISTS]}
        problems = [str(e)]
    record["problems"] = problems
    return record, problems


if __name__ == "__main__":
    if sys.argv[1:2] == ["candidates"]:
        print(candidates())
    else:
        print(__doc__)
