"""Where things are — found by walking up, never counted with parents[N].

`AI_WORKSPACE` wins when it names a folder holding brands/ (a worktree, a test's
temp folder). Every folder this tool imports from is APPENDED to sys.path, never
put first, so nothing here can shadow another tool's module or the standard
library.
"""
import os
import sys
from pathlib import Path

MACHINE_DIR = Path(__file__).resolve().parent
TOOL = MACHINE_DIR.parent
PROMPTS = TOOL / "prompts"


def repo():
    env = os.environ.get("AI_WORKSPACE")
    if env and (Path(env) / "brands").is_dir():
        return Path(env)
    for d in MACHINE_DIR.parents:
        if (d / "components").is_dir() and (d / "brands").is_dir():
            return d
    raise FileNotFoundError("no workspace found upward of " + str(MACHINE_DIR))


WS = repo()
DOCTRINE = WS / "components" / "marketing-doctrine"
TEMPLATE = WS / "brands" / "_TEMPLATE" / "story.md"
RUN_KIT = WS / "components" / "run-kit"
QUALITY = WS / "components" / "quality-checks"
ELEMENTS = WS / "components" / "elements" / "machine"
VIDEO_MACHINE = WS / "components" / "video-teardown" / "machine"


def add(*folders):
    for f in folders:
        if str(f) not in sys.path:
            sys.path.append(str(f))


add(MACHINE_DIR, DOCTRINE, RUN_KIT, QUALITY, ELEMENTS)
