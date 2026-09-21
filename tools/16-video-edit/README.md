# video-edit

Turns an approved kit — voice, A-roll, B-roll, music, sound effects — into the
finished captioned video, with two stops for Damon: the timeline, then the
captions. No timeline software, no editor.

    python3 machine/run.py start <kit-folder> --brand <brand> --label <label> --dry-run   # check, spend nothing
    python3 machine/run.py start <kit-folder> --brand <brand> --label <label>             # runs to the next stop
    python3 machine/run.py change  <run> timeline "bring the cutaway in later" --why "it covered her face"
    python3 machine/run.py approve <run> timeline
    python3 machine/run.py status  <run>

Rules, files and what is not built yet: CLAUDE.md. The page: context/artifacts.md.
