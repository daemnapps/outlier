#!/usr/bin/env python3
"""Rebuilds the story builder's page. The code is machine/page.py; this file only
forwards to it, so the old command keeps working.

    python3 story-builder/page.py      -> story-builder/story-builder.html
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "machine" / "page.py"), run_name="__main__")
