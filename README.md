# Open Source Outliers

A marketing machine you run yourself. Same tools I use on real brands — the
swipe machine, the teardown chain, the brief generators, the prompts.

**Free. MIT licensed. Runs on your machine with your own keys.** There is no
account, no dashboard, and no server of mine holding your data.

Never used a terminal? Start with **[WALKTHROUGH.md](WALKTHROUGH.md)** — it
assumes you have never opened one.

---

## What's in here

> **Status: the guide is up, the toolkit is landing.** Right now this repo has
> the installer and the walkthrough. The four folders below are being moved in.
> Watch the repo and you'll see them arrive.


| | |
|---|---|
| `swipe/` | Competitor intelligence. Point it at a rival's domain, get their whole live ad library ranked by what they're actually spending behind. |
| `video-teardown/` | Creative → brief. Thirteen stages: triage, teardown, replication spec, injection, hooks, brief. |
| `prompts/` | Every prompt the chain runs. Plain markdown. Read them, change them. |
| `brands/` | Where your brands live — language bank, rules, offer bank. Yours, local. |

---

## Quick start

```bash
mkdir -p ~/outlier && cd ~/outlier
git clone https://github.com/daemnapps/outlier.git .
python3 -m pip install --user playwright
claude
```

Then, in Claude Code:

```
Read the README and tell me what this toolkit can do.
```

---

## What it does

**Writes** — static ads, video scripts, advertorials, landing pages, quiz
funnels, a month of email, post-purchase paths.

**Researches** — pulls a competitor's live ad library, clusters it into copy
blocks, ranks them by how hard the competitor is duplicating each one, and
captures the landing pages behind them.

**Tears down** — takes a single creative and returns an objective record, a
replication spec, and a brief you can hand to production.

## What it will not do

Publish anything. Spend anything on ads. Invent a customer quote. Make a
medical claim. Write in a voice it hasn't been given evidence for.

Those are hard stops in the prompts, not guidelines.

---

## What it costs

The code is free. The models are not — you pay Anthropic and Google directly
for what you use, on your own accounts.

Rough shape: a working session costs a few dollars in Claude credits. Image
and video generation costs more, and is optional.

**Affiliate disclosure.** Links to Claude, Higgsfield and other tools used by
this system are affiliate links. If you sign up through them I receive a
percentage of your spend at no additional cost to you. The software here is
free, unaffected by whether you use those links, and works identically if you
sign up directly. This is the only way this project makes money.

---

## Keys you need

| service | required | what for |
|---|---|---|
| Anthropic | yes | the writing |
| Google Gemini | yes | video analysis |
| Higgsfield | no | image + video generation |
| AdPlexity | no | competitor ad libraries (the swipe tools) |

Start with the first two. Add the others when you need them.

---

## Honest state of things

These are live experiments, not a maintained product. Things break. Prompts
change without warning. There is no roadmap and no SLA.

**Questions go in the Questions tab, not to me directly.** No group chat, no
support email, no DMs — one place, answered in the open so the next person
finds it already written. See **[ASK.md](ASK.md)**.

If you improve a prompt, send it back. That's the whole deal.

---

## Two rules

1. **Read what it writes before it goes anywhere.** It will not publish, send
   or spend on its own. The last check is always you.
2. **Correct it out loud.** It gets meaningfully better on the second run
   because you told it what was wrong on the first. People who skip this think
   the tools don't work.

---

MIT — do what you like with it.
