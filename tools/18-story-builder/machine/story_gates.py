"""The gates this tool runs — the shared ones from components/quality-checks.

    inputs     before the model   the template and the draft prompt are on file
    elements   before the model   the story framework and the delivery the ARC
                                  slot names are real rows in the element
                                  library (components/elements)
    copy       after the lint     no quote still stands unchecked in the
                                  finished file, and it has the template's shape

`hold()` writes the gate-keyed `check.json` into the run and raises `Held`.
A story whose quote was not found is DEMOTED to open by the quote check — that
is the check's own remedy, not a failure, and it does not hold the build.
"""
import story_paths as P  # noqa: F401  (appends the shared folders to sys.path)
import quality_checks as Q
import elements as E

Held = Q.Held
# The arc every story file is built against — brands/_TEMPLATE/story.md names
# both. They are looked up in the library, never trusted from this file.
ARC_FRAMEWORK = "story-testimonial"
ARC_DELIVERY = "storyteller"


def arc_labels(framework=None, delivery=None):
    return {("framework", "all"): framework or ARC_FRAMEWORK,
            ("delivery", "delivery_style"): delivery or ARC_DELIVERY}


def elements_problems(framework=None, delivery=None):
    """[] when both are real rows; otherwise the library's own refusal, which
    names the real ids."""
    return E.check(arc_labels(framework, delivery))


def arc_row(framework=None):
    return E.get("framework", "all", framework or ARC_FRAMEWORK)


def inputs_problems(template, prompt_file):
    out = []
    if not template.is_file():
        out.append(f"the story template is not on file: {template}")
    if prompt_file is None:
        out.append("no draft prompt (stage2-*-vN-*.md) in the prompts folder")
    return out


def copy_problems(report, lint_findings):
    """What is still wrong with the FINISHED file. A demoted story is handled;
    a quote left standing outside a story, marked ⟨unverified⟩, is not."""
    out = []
    for q in report.get("detail", []):
        if not q["ok"] and not q.get("story"):
            out.append("a quote outside any story was not found in the brand's files: "
                       f"“{q['quote'][:110]}”")
    out += [f"story shape: {f}" for f in lint_findings]
    return out


def hold(gate, problems, run_dir):
    return Q.hold(gate, problems, run_dir)
