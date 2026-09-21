"""Paths are FOUND by walking up, never counted with parents[N].
Lifted from components/email-production/paths.py — written after a folder
move made parents[3] silently point one level too high."""
import os
from pathlib import Path


def repo(start=None):
    """The workspace root: the first folder upward holding components/ and brands/."""
    env = os.environ.get("AI_WORKSPACE")
    if env and (Path(env) / "brands").is_dir():
        return Path(env)
    here = Path(start or __file__).resolve()
    for d in [here, *here.parents]:
        if (d / "components").is_dir() and (d / "brands").is_dir():
            return d
    raise FileNotFoundError("no workspace found upward of " + str(here))


def component(*parts, start=None):
    return repo(start).joinpath("components", *parts)


def lab(*parts, start=None):
    return repo(start).joinpath("lab", "damon", *parts)


def brand(name, *parts, start=None):
    return repo(start).joinpath("brands", name, *parts)
