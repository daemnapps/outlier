"""A chain, and one step of it.

The dry run lives INSIDE the step runner, so it is truly free — email.py's
ran stage 0 before its dry-run block and spent a call every time. A finished
step is reused only if its prompt is unchanged AND nothing it depends on
reran (pages/run.py:220-235). Every prompt is saved as sent, beside what came
back. Lifted, not invented.
"""
import time
from pathlib import Path

from . import model as M
from . import prompts as P
from .record import Record, now

DRY = "[dry run — not written]"


class Chain:
    """
    steps: [{"key": "stage3", "name": "Writer", "tier": "designs", "label": "draft",
             "depends": ["stage2"]}, ...]  — order is run order.
    """

    def __init__(self, tool, brand, label, out_dir, prompts_dir, steps, assignment=None,
                 dry=False, rerun_from=None, force_model=None, tiers=None, runner=None, echo=print):
        self.steps = {s["key"]: s for s in steps}
        self.order = [s["key"] for s in steps]
        if rerun_from and rerun_from not in self.steps:
            raise ValueError(f"rerun-from wants one of: {', '.join(self.order)}")
        self.out = Path(out_dir)
        self.out.mkdir(parents=True, exist_ok=True)
        self.prompts_dir = Path(prompts_dir)
        self.dry, self.rerun_from = dry, rerun_from
        self.force_model, self.tiers, self.runner, self.echo = force_model, tiers, runner, echo
        self.record = Record(self.out, tool, brand, label, assignment)
        self.reran = set()
        self.calls = 0

    # ------------------------------------------------------------------
    def _reusable(self, key, prompt_sha):
        step, old = self.steps[key], self.record.state["stages"].get(key) or {}
        out = self.out / f"{key}--{step['label']}.md"
        if not (old.get("status") in ("done", "reused") and out.is_file()):
            return None
        if self.rerun_from and self.order.index(key) >= self.order.index(self.rerun_from):
            return None
        if old.get("prompt_sha256_12") not in (None, prompt_sha):
            self.echo(f"     {key}: prompt changed since the last run — rewriting")
            return None
        hit = [d for d in step.get("depends", []) if d in self.reran]
        if hit:
            self.echo(f"     {key}: reads from {', '.join(hit)}, which reran — rewriting")
            return None
        return out.read_text().strip()

    def run(self, key, **fields):
        step = self.steps[key]
        pf = P.latest(self.prompts_dir, key)
        template = pf.read_text()
        filled = P.fill(template, fields)                      # refuses unfilled fields, even dry
        (self.out / f"{key}--sent.md").write_text(filled)
        psha = P.sha(pf)
        chosen, why = M.pick(step.get("tier", "designs"), len(filled), self.force_model, self.tiers)

        if self.dry:
            self.echo(f"  ~~ {key}  {step.get('name', '')}: {len(filled):,} chars → {chosen} ({why}) — dry")
            self.record.stage(key, status="dry", model=chosen, why_model=why, prompt_name=pf.name,
                              prompt_sha256_12=psha, chars_in=len(filled), wants=sorted(fields))
            return DRY

        kept = self._reusable(key, psha)
        if kept is not None:
            self.echo(f"  == {key}  (kept from the earlier run)")
            self.record.stage(key, **{**self.record.state["stages"][key], "status": "reused"})
            return kept

        self.echo(f"  -> {key}  {step.get('name', '')} ({pf.name}) on {chosen}" + ("" if why == step.get("tier") else f" — {why}"))
        t0 = time.time()
        text = M.call(filled, chosen, label=key, runner=self.runner)
        self.calls += 1
        out = self.out / f"{key}--{step['label']}.md"
        out.write_text(text + "\n")
        self.reran.add(key)
        self.record.stage(key, status="done", model=chosen, why_model=why, prompt_name=pf.name,
                          prompt_sha256_12=psha, wants=sorted(fields), seconds=round(time.time() - t0, 1),
                          chars_in=len(filled), chars_out=len(text), out=out.name, sent=f"{key}--sent.md",
                          finished=now())
        return text

    def skip(self, key, why):
        """A step that did not run is recorded with its reason, never left blank."""
        self.record.stage(key, status="skipped", why=why)
        self.echo(f"  -- {key}  skipped ({why})")
