#!/usr/bin/env python3
"""Where the email system is, and where the brand context it reads lives.

The tool lives in daemn — Damon's repo, where he builds and tests. The brand
context it reads lives in the shared ai-workspace, read-only, the same way
his chain-variables map points into it. Those are two different trees, so
neither path may be derived by counting folders up from this file: that is
why this is named rather than derived by counting folders up from this file.

Override the brand tree with AI_WORKSPACE=/some/path when it moves, or pass
--brand-root to the runner for a one-off.

SHIM (BH-1, 2026-09-02). The LOCATOR — env override, else the named default —
moved to `components/brand-finder/` so rule-9's "where is brands/" has one
home; it had three, and this file's copy came from copy.py's. This file is the
same file it always was: same names, same answers, same command. **The default
below stays HERE**, because it is this machine's own policy. RULED 2026-09-09
(Damon, "it lives in the repo and everything's reflective"): the repo root,
the same as `copy/machine/paths.py` — the BH-1 divergence is closed. That divergence is written
down for the 09-03 Damon batch in
`new-workflow-design/builds/brand-home/DIVERGENCE.md`; nothing here decided it.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The tree that CONTAINS brands/ — the lab, not the repo root. Both this
# runner and copy's context.py resolve <root>/brands/<brand>, so they must be
# handed the same root or the scout indexes a different tree than the one
# the runner reads (which is exactly what broke the first <brand> attempt).
_DEFAULT_WS = Path.home() / "Projects" / "ai-workspace"      # brands/ at the repo root (Damon, 2026-09-09)

# FOUND, never counted: this folder moved email-production ->
# components/email-production on 2026-09-19, and parents[3] silently pointed one
# level too high the moment it did.
_REPO = next((d for d in Path(__file__).resolve().parents if (d / "components" / "brand-finder").is_dir()), None)
_COMPONENT = (_REPO / "components" / "brand-finder") if _REPO else None
if not _COMPONENT:                           # a workspace mounted elsewhere
    _COMPONENT = _DEFAULT_WS / "components" / "brand-finder"
sys.path.append(str(_COMPONENT))        # appended, never ahead of this machine
import brand_finder as _finder               # noqa: E402


def workspace():
    """The tree brand context is read from. Named, never guessed."""
    return Path(_finder.workspace(_DEFAULT_WS))


WORKSPACE = workspace()


def calendar_tool(sub=""):
    """The marketing-calendar tool's folder, FOUND rather than counted.

    That tool moved from this folder into `components/` and back into `lab/`
    inside one day, and every `parents[N]` pointing at it broke on each move —
    silently, because a wrong path only means a file "isn't there". So look for
    it instead: up the tree, in the places it actually lives. Returns None when
    it genuinely is not there, which is a real answer and not a crash.
    """
    here = Path(__file__).resolve()
    for d in [here.parent, *here.parents]:
        for cand in (d / "marketing-calendar",
                     d / "lab" / "damon" / "marketing-calendar",
                     d / "components" / "marketing-calendar"):
            if (cand / (sub or "machine")).exists():
                return cand / sub if sub else cand
    return None


def component(*parts):
    """A sibling component, found by walking up — never counted."""
    for d in Path(__file__).resolve().parents:
        cand = d.joinpath("components", *parts)
        if cand.exists():
            return cand
    return WORKSPACE.joinpath("components", *parts)


def lab_tool(*parts):
    """Another of Damon's machines, still in  — found by walking up,
    so this component can move again without every reach breaking."""
    for d in Path(__file__).resolve().parents:
        cand = d.joinpath("lab", "damon", *parts)
        if cand.exists():
            return cand
    return WORKSPACE.joinpath("lab", "damon", *parts)
