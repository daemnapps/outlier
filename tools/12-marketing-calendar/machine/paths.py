#!/usr/bin/env python3
"""Where this tool is, and where everything it reads lives.

**Nothing here counts folders upward from this file**, and that is the point.
This tool moved from the email machine's folder into `components/` and back
into `lab/` inside one day, and every `parents[3]` in the tree broke on each
move — silently, because a wrong path just means a file "isn't there". So the
workspace is FOUND (the checkout this file sits in, via `brand-finder`'s
`checkout_of`), the env var `AI_WORKSPACE` overrides it, and the named default
is the last resort. The folder can move again for free.

Everything the tool reads or writes hangs off `WORKSPACE`:

    brands/<brand>/     brand content, read-only (rule-9, brand home)
    components/         shared engines this one borrows (language-layer)
    platform/data/      where finished results are filed
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent              # machine/
COMPONENT = HERE.parent                             # the tool's own folder
PROMPTS = COMPONENT / "prompts"
DEFINITIONS = COMPONENT / "definitions"
RUNS = COMPONENT / "runs"

_NAMED_DEFAULT = Path.home() / "Projects" / "ai-workspace"


def _locator():
    """brand-finder, wherever it is. Found the same way as everything else —
    by looking, not by counting."""
    for base in (_found_checkout(), _NAMED_DEFAULT):
        if base and (base / "components" / "brand-finder").is_dir():
            sys.path.append(str(base / "components" / "brand-finder"))
            try:
                import brand_finder
                return brand_finder
            except ImportError:
                pass
    return None


def _found_checkout():
    """The working tree this file sits in — the first ancestor with a .git."""
    for d in [HERE, *HERE.parents]:
        if (d / ".git").exists():
            return d
    return None


_finder = _locator()


def workspace():
    """The tree brand content is read from."""
    if _finder:
        return Path(_finder.workspace(_found_checkout() or _NAMED_DEFAULT))
    return Path(os.path.expanduser(os.environ.get("AI_WORKSPACE", "")) or
                _found_checkout() or _NAMED_DEFAULT)


WORKSPACE = workspace()
COMPONENTS = WORKSPACE / "components"
PLATFORM = WORKSPACE / "platform"


def brand_root(brand):
    return WORKSPACE / "brands" / brand


def rel(p):
    """A path written the way a person can follow it — relative to the
    workspace when it is inside one, absolute when it is not."""
    p = Path(p)
    try:
        return str(p.relative_to(WORKSPACE))
    except ValueError:
        return str(p)
