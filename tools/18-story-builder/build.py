#!/usr/bin/env python3
"""research-story — the command everyone already uses. The code is machine/build.py;
this file only forwards to it, so every old call keeps working.

    python3 story-builder/build.py --brand <brand>             # full run
    python3 story-builder/build.py --brand <brand> --dry-run   # free: no model, nothing written
    python3 story-builder/build.py --brand <brand> --dry       # no model; files the prompt as sent
    python3 story-builder/build.py --brand <brand> --label <run-label>
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "machine" / "build.py"), run_name="__main__")
