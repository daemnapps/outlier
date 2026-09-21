"""Where things are — FOUND by walking up, never counted with parents[N].

Two roots, and they are usually the same folder:

    code_repo()   the repo this file sits in — the shared CODE is imported from
                  here (components/quality-checks, components/elements/machine)
    workspace()   where the DATA is — the two swipe pools, brands/, runs/ and
                  the built element library. `AI_WORKSPACE` overrides it, which
                  is how a worktree reads the live pools and how the tests run
                  against a tiny fake workspace.
"""
import os
import sys
from pathlib import Path

TOOL = "intake"                                   # the name we say out loud: runs/<TOOL>/...
PAID_POOL = ("lab", "damon", "swipe-paid")        # where paid + own swipes LIVE
ORGANIC_POOL = ("lab", "damon", "swipe-organic")  # where organic swipes LIVE


def _walk_up(start):
    here = Path(start).resolve()
    for d in [here, *here.parents]:
        if (d / "components").is_dir() and (d / "brands").is_dir():
            return d
    raise FileNotFoundError("no workspace found upward of " + str(here))


def code_repo():
    return _walk_up(__file__)


def workspace():
    env = os.environ.get("AI_WORKSPACE")
    if env and (Path(env) / "brands").is_dir():
        return Path(env)
    return code_repo()


def paid_pool():
    return workspace().joinpath(*PAID_POOL)


def organic_pool():
    return workspace().joinpath(*ORGANIC_POOL)


def brands():
    """Every real brand — read from the folders, never typed."""
    d = workspace() / "brands"
    return sorted(p.name for p in d.iterdir() if p.is_dir() and not p.name.startswith(("_", ".")))


def run_dir(brand, label, make=True):
    """runs/intake/<brand>/<label>/ at the workspace root (CLAUDE.md §1)."""
    d = workspace() / "runs" / TOOL / brand / label
    if make:
        d.mkdir(parents=True, exist_ok=True)
    return d


def shared(*parts):
    """Put one shared code folder on the import path — APPENDED, never
    inserted at 0, so nothing here can shadow the standard library."""
    p = str(code_repo().joinpath("components", *parts))
    if p not in sys.path:
        sys.path.append(p)
    return p
