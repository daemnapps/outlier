#!/usr/bin/env python3
"""Where things live. One file, so no tool guesses a path.

The rule these encode: **the brand owns its design record, the machine owns
the process.** Nothing brand-specific resolves inside the machine folder.
"""
import os
from pathlib import Path

MACHINE = Path(__file__).resolve().parent.parent      # email-teardown
LAB = MACHINE.parent                                   # lab/damon
TOOL = "email-teardown"                                # the name we say out loud


def _repo():
    """The workspace root — AI_WORKSPACE when it is set (a worktree, a test),
    otherwise found by walking up. Never counted with parents[N]."""
    env = os.environ.get("AI_WORKSPACE")
    if env and (Path(env) / "brands").is_dir():
        return Path(env)
    for d in MACHINE.parents:
        if (d / "components").is_dir() and (d / "brands").is_dir():
            return d
    raise FileNotFoundError("no workspace found upward of " + str(MACHINE))


REPO = _repo()
# Brand data moved to the repo root (brands/<brand>/); the old lab cabinet is
# used only where it still exists, so the bank half keeps reading what it read.
BRANDS = LAB / "brands" if (LAB / "brands").is_dir() else REPO / "brands"
RECORDS = REPO / "runs" / TOOL                         # runs/email-teardown/<brand>/<label>/
PROMPTS = MACHINE / "prompts"
RUN_KIT = REPO / "components" / "run-kit"
QUALITY = REPO / "components" / "quality-checks"
ELEMENTS = REPO / "components" / "elements"
TEMPLATE = BRANDS / "_TEMPLATE"

# Media mirrors the repo path on the company Drive (<brand> account —
# that is correct, see the machine README).
DRIVE = (Path.home() / "${DRIVE_ACCOUNT} - Google Drive"
         / "Shared drives" / "Shared Assets" / "lab" / "damon")


def brand_dir(brand):
    return BRANDS / brand


def design_formats(brand):
    """A brand's email design record — the home everything else hangs off."""
    return BRANDS / brand / "email" / "design-formats"


def source_file(brand):
    """The Figma file + the board register. A fact about the brand, not the run."""
    return design_formats(brand) / "source.json"


def census_file(brand):
    return design_formats(brand) / "census.json"


def sweep_dir(brand):
    return design_formats(brand) / "sweep"


def media_dir(brand):
    """Where the pictures go. Never git (workspace rule 3)."""
    return DRIVE / "brands" / brand / "email" / "design-formats"


def designs_dir(brand):
    """The brand's own email designs — existing assets of the business, so they
    live in the brand's `existing-content/`, the cabinet's slot for work that
    ran. Not in the machine: the machine is the process, these are the assets."""
    return BRANDS / brand / "existing-content" / "emails" / "designs"


def record_dir(brand, label):
    """Where a teardown run files: runs/email-teardown/<brand>/<label>/ at the
    repo root. Named here, made by the runner — never by a dry run."""
    return RECORDS / brand / label


def runs_dir(brand, board_slug):
    """The bank half's OLD working folder, beside the code. History: still
    readable, never written by the teardown runner."""
    return MACHINE / "runs" / f"{brand}-{board_slug}"


def known_brands():
    if not BRANDS.is_dir():
        return []
    return sorted(p.name for p in BRANDS.iterdir()
                  if p.is_dir() and not p.name.startswith("_") and p.name != "context")
