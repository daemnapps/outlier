"""One headless `claude -p` caller for every chain.

Lifted: tiers + size escalation + the usage-limit message from email.py
(:60-70, :167-195, :282-285); the clean environment, the anti-chatter guard and
transient-only retry from video-teardown run.py (:27-35, :484-521, :557-605).
New here: a timeout — no caller had one."""
import os
import subprocess
import time

TIERS = {
    "reads": "claude-haiku-4-5-20251001",     # the answer is in the input
    "checks": "claude-sonnet-5",              # applies rules that are written down
    "designs": "claude-opus-5",               # makes the calls nobody wrote down
}
SMALL_WINDOW_CHARS = 350_000                  # ~what a 200k-token window holds, kept conservative
TRANSIENT = ("overloaded", "rate limit", "429", "500", "502", "503", "529", "timeout",
             "timed out", "connection", "temporarily", "econnreset")
PURE_TEXT = ("You are one stage of a document pipeline. Return only the deliverable text. "
             "No tools, no preamble, no report about what you did.")
KEEP_ENV = ("HOME", "PATH", "TERM", "LOGNAME", "SHELL", "LANG", "LC_ALL", "TMPDIR")


class UsageLimit(Exception):
    """The account is out of usage — not a broken stage. Stop the whole run."""


class StageFailed(Exception):
    pass


def pick(tier, prompt_chars=0, forced=None, tiers=None):
    """The model for a step: a forced model wins; otherwise the step's tier —
    escalated when the prompt is too big for a small window. Returns (model, why)."""
    tiers = tiers or TIERS
    if forced:
        return forced, "forced"
    m = tiers[tier]
    if prompt_chars > SMALL_WINDOW_CHARS and m != tiers["designs"]:
        return tiers["designs"], f"escalated: prompt is {prompt_chars / 1e6:.2f}MB, past a small window"
    return m, tier


def _clean_env():
    return {k: v for k, v in os.environ.items() if k in KEEP_ENV}


def call(prompt_text, model, label="?", tries=4, wait=30, timeout=1800, runner=None):
    """Run one prompt. `runner(prompt, model) -> (code, stdout, stderr)` is the
    seam tests use; the default shells out to `claude -p`."""
    def default(p, m):
        r = subprocess.run(["claude", "-p", "--model", m, "--output-format", "text",
                            "--append-system-prompt", PURE_TEXT],
                           input=p, capture_output=True, text=True, env=_clean_env(), timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    runner = runner or default
    last = ""
    for attempt in range(1, tries + 1):
        try:
            code, out, err = runner(prompt_text, model)
        except subprocess.TimeoutExpired:
            code, out, err = 1, "", f"timed out after {timeout}s"
        if code == 0 and out.strip():
            return out.strip()
        both = f"{out}\n{err}".lower()
        if "limit" in both and ("usage" in both or "spend" in both):
            raise UsageLimit(f"stage {label} on {model} was refused: {(out or err).strip()[:240]}")
        last = (f"stage {label} failed on {model} (prompt {len(prompt_text) / 1e6:.2f}MB, exit {code})\n"
                f"  stderr: {err.strip()[:400] or '(empty — often the prompt exceeding the model window)'}\n"
                f"  stdout: {out.strip()[:200] or '(empty)'}")
        if not any(t in both for t in TRANSIENT) or attempt == tries:
            break                                   # a bad answer is not retried
        time.sleep(wait * attempt)
    raise StageFailed(last)
