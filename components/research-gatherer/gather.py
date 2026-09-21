#!/usr/bin/env python3
"""CLI entry point for the research-gatherer engine — see
research_gatherer/engine.py.

    python3 components/research-gatherer/gather.py --brand B --avatar A --sub S
    python3 components/research-gatherer/gather.py --brand B --all
    python3 components/research-gatherer/gather.py --pick-thinnest --cap 150
    python3 components/research-gatherer/gather.py --brand B --avatar A --sub S --dry-run
    python3 components/research-gatherer/gather.py voiceprint --brand B --creator H
    python3 components/research-gatherer/gather.py voiceprint --brand B --all

Chain-agnostic — deep mode only. `inputs(st, chain_profile)` is a library
call: it needs a chain's own stage map (which language STAGE_USE keys to
query, where a run's own folder lives), so a chain's shim
(`components/video-teardown/machine/research.py`, and any sibling chain
that adopts this component) exposes it as its own `run` subcommand instead.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from research_gatherer.engine import main   # noqa: E402

if __name__ == "__main__":
    # `voiceprint` is its own module (research_gatherer/voiceprint.py): the
    # spoken profile of a brand's creators, measured off their own audio.
    if sys.argv[1:2] == ["voiceprint"]:
        from research_gatherer.voiceprint import main as vp_main   # noqa: E402
        sys.exit(vp_main(sys.argv[2:]))
    sys.exit(main())
