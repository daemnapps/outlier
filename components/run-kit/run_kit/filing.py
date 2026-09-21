"""Where a run lives: runs/<tool>/<brand>/<label>/ in the repo, and the same
path under Shared Assets/runs/ on Drive for media (runs/README.md, ruled
2026-09-17). The Drive mount is DISCOVERED, and its three failures are loud —
lifted from video-teardown chain.py:51-97."""
from pathlib import Path

from . import paths


class MountError(Exception):
    pass


def run_dir(tool, brand, label, start=None):
    d = paths.repo(start) / "runs" / tool / brand / label
    d.mkdir(parents=True, exist_ok=True)
    return d


def drive_runs():
    cloud = Path.home() / "Library" / "CloudStorage"
    mounts = sorted(cloud.glob("GoogleDrive-*<brand>.com")) if cloud.is_dir() else []
    if not mounts:
        raise MountError("no <brand> Google Drive is mounted on this machine")
    if len(mounts) > 1:
        raise MountError("more than one <brand> Drive is mounted: " + ", ".join(m.name for m in mounts))
    shared = mounts[0] / "Shared drives" / "Shared Assets"
    if not shared.is_dir():
        raise MountError(f"the Shared Assets drive is not visible under {mounts[0].name}")
    return shared / "runs"


def media_dir(tool, brand, label):
    d = drive_runs() / tool / brand / label
    d.mkdir(parents=True, exist_ok=True)
    return d
