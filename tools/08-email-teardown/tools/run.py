#!/usr/bin/env python3
"""email-teardown — one email in, its element labels and its construct out.

    python3 tools/run.py <source email> --brand <brand> [--label L] [--dry-run]
                         [--rerun-from tear1|tear2|tear3] [--model M]

Takes an email — words and pictures, as a sent-email file (`.md`/`.txt`) or an
`.html` export. Makes three things, filed to `runs/email-teardown/<brand>/<label>/`:

    tear1--record.md      THE MESSAGE / PAGE FURNITURE / SOURCE DEFECTS, kept apart
    elements.json         which library rows the email IS (format, template, framework)
    tear3--construct.md   the email's construct — brand-free, subject-free,
                          built from the message only

Does not write an email. Built on `components/run-kit` (`Chain`): every prompt
saved as sent, a finished step reused, `run.json`, and a dry run that spends
NOTHING — no model call, no file outside a temp folder that is removed.

There is no default brand. `--brand` names whose furniture words to read
(`brands/<brand>/email/simple.json` → `furniture`) and where the run files.
"""
import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
import paths as P                                             # noqa: E402
import furniture as F                                         # noqa: E402
import elements_label as L                                    # noqa: E402
import gates as G                                             # noqa: E402

sys.path.append(str(P.RUN_KIT))
sys.path.append(str(P.QUALITY))
from run_kit import model as M                                # noqa: E402
from run_kit import prompts as KP                             # noqa: E402
from run_kit.stage import Chain                               # noqa: E402
import quality_checks as Q                                    # noqa: E402

TOOL = P.TOOL
# Declared once. tier: reads = the answer is in the input · checks = applies
# rules that are written down · designs = makes the calls nobody wrote down.
# The model behind each tier is components/run-kit model.TIERS — no id here.
STEPS = [
    {"key": "tear1", "name": "Read the email — message, furniture, defects", "tier": "reads", "label": "record"},
    {"key": "tear2", "name": "Label its elements", "tier": "checks", "label": "labels", "depends": ["tear1"]},
    {"key": "tear3", "name": "The construct", "tier": "designs", "label": "construct", "depends": ["tear1"]},
]


def sha12(text):
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:12]


def _rel(path):
    try:
        return str(Path(path).resolve().relative_to(P.REPO.resolve()))
    except ValueError:
        return str(path)


def _old_source_sha(out):
    try:
        return json.loads((Path(out) / "run.json").read_text()).get("assignment", {}).get("source_sha256_12")
    except (OSError, ValueError):
        return None


def main(argv=None, runner=None, echo=print):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="the email to tear down: a sent-email .md/.txt file, or an .html export")
    ap.add_argument("--brand", required=True,
                    help="REQUIRED — there is no default brand. Whose furniture words to read, and where the run files")
    ap.add_argument("--label", help="the run's label (default: the source file's name)")
    ap.add_argument("--dry-run", "--dry", dest="dry", action="store_true",
                    help="spend nothing: show the inputs, the model per step and where it would file")
    ap.add_argument("--rerun-from", choices=[s["key"] for s in STEPS])
    ap.add_argument("--model", help="force one model for every step (default: each step's tier)")
    a = ap.parse_args(argv)

    label = a.label or Path(a.source).stem
    files_to = P.record_dir(a.brand, label)
    problems = G.input_problems(a.source, a.brand, STEPS)

    if a.dry:
        echo(f"DRY RUN — email-teardown · brand {a.brand} · label {label}")
        echo(f"  source      {_rel(a.source)}")
        if problems:
            for p in problems:
                echo(f"  MISSING     {p}")
            echo("  nothing was spent and nothing was written.")
            return 1
    else:
        files_to.mkdir(parents=True, exist_ok=True)
        try:
            G.inputs_gate(files_to, problems)
        except Q.Held as e:
            echo(str(e))
            return 2

    source = F.load(a.source)
    found = F.scan(source, a.brand)
    _, own_words = F.brand_words(a.brand)
    assignment = {"source": _rel(a.source), "source_sha256_12": sha12(source), "source_chars": len(source),
                  "brand_furniture_words": len(own_words),
                  "code_found": {"furniture_lines": len(found["furniture"]), "defects": len(found["defects"])}}

    tmp = Path(tempfile.mkdtemp(prefix="email-teardown-dry-")) if a.dry else None
    out = tmp or files_to
    rerun = a.rerun_from
    if not a.dry and not rerun and _old_source_sha(out) not in (None, assignment["source_sha256_12"]):
        echo("     the source email changed since the last run under this label — reading it again")
        rerun = "tear1"

    try:
        chain = Chain(TOOL, a.brand, label, out, P.PROMPTS, STEPS, assignment=assignment, dry=a.dry,
                      rerun_from=rerun, force_model=a.model, runner=runner, echo=echo)
        if a.dry:
            echo(f"  source      {len(source):,} chars · code found {len(found['furniture'])} furniture line(s), "
                 f"{len(found['defects'])} defect(s)")
            echo(f"  brand       brands/{a.brand}/email/simple.json names {len(own_words)} furniture word(s)")

        # 1 — the read: message, furniture and defects kept apart
        record = chain.run("tear1", furniture_words=", ".join(own_words) or "(this brand has none on file)",
                           code_findings=F.findings_text(found), source=source)
        strip = {"furniture_words": [], "defects": []}
        if not a.dry:
            G.record_gate(out, record)
            strip = F.strip_block(record)
            (out / "strip.json").write_text(json.dumps({"code_found": found, "record_says": strip},
                                                       indent=1, ensure_ascii=False) + "\n")
        message = F.message_only(record)

        # 2 — the labels: asked of the element library, never invented
        answer = chain.run("tear2", candidates=L.candidates(), record=message)
        if not a.dry:
            labels, label_problems = L.read(answer)
            (out / "elements.json").write_text(json.dumps(labels, indent=1, ensure_ascii=False) + "\n")
            chain.record.state["elements"] = {"labels": labels["labels"], "proposed": labels["proposed"],
                                              "refused": labels["refused"]}
            chain.record.save()
            G.elements_gate(out, label_problems)

        # 3 — the construct: from the message only
        construct = chain.run("tear3", record=message)
        if not a.dry:
            G.construct_gate(out, construct, strip, a.brand)
            chain.record.state["state"] = "filed"
            chain.record.save()
    except Q.Held as e:
        echo(str(e))
        echo(f"  the run is HELD — why is in {_rel(out / 'check.json')}. "
             f"Fix the prompt or the source, then run again with --rerun-from <step>.")
        return 2
    except (KP.PromptError, M.UsageLimit, M.StageFailed) as e:
        echo(f"STOPPED: {e}")
        return 3
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)

    if a.dry:
        echo(f"  would file  {_rel(files_to)}/  (tear1--record.md · elements.json · tear3--construct.md · "
             f"strip.json · run.json · check.json · every prompt as sent)")
        echo(f"  spent       0 model calls — a real run makes up to {len(STEPS)}")
        return 0
    echo(f"done -> {_rel(out)}  ({chain.calls} model call(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
