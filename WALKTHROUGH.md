# Getting started

**This guide assumes you have never used GitHub, never opened a terminal, and
do not write code.** That is fine. Nothing here requires you to.

Read every step in order. Do not skip. If something on your screen does not
match what is written here, stop and ask in the group rather than guessing.

**Time:** about 45 minutes the first time.
**Cost:** the software is free. The AI models charge for what you use — see
step 7.

---

## What you are actually doing

Four things, in this order:

1. Installing a program called **Claude Code** — the thing that runs all of this
2. Making a **folder** on your computer for the work
3. **Copying the toolkit** into that folder
4. Giving it **your keys** so it can talk to the AI models

That is it. There is no account to make with me and no software of mine to
install.

---

## Step 1 — Open the Terminal

The Terminal is a window where you type instructions instead of clicking.
It looks intimidating. It is not. You will type about eight lines total.

**On a Mac**
1. Press `Command` and `Space` at the same time. A search bar appears.
2. Type `terminal`
3. Press `Return`.

A window opens with white or black text. Leave it open.

**On Windows**
1. Click Start.
2. Type `powershell`
3. Click **Windows PowerShell**.

> **How to use this guide from here on:** when you see a grey box, copy the
> line inside it, paste it into the Terminal, and press `Return`. Copy the
> whole line. Do not add anything.

---

## Step 2 — Check you have the basics

Paste this and press Return:

```bash
git --version
```

- If you see something like `git version 2.39.5`, good. Continue.
- If you see `command not found`, you need Git first:
  - **Mac:** paste `xcode-select --install` and click through the installer,
    then come back and try `git --version` again.
  - **Windows:** download from https://git-scm.com/downloads, run the
    installer, accept every default, then close and reopen PowerShell.

Now check Python:

```bash
python3 --version
```

You want `3.9` or higher. If it says `command not found`, install from
https://www.python.org/downloads/ — tick **"Add Python to PATH"** during
install if you are on Windows.

---

## Step 3 — Install Claude Code

This is the program that actually runs the toolkit.

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Wait for it to finish. Then **close the Terminal window completely and open a
new one** — this matters, the new window is what knows the program exists.

Check it worked:

```bash
claude --version
```

If you see a version number, you are past the hardest part.

> If `curl` is not found on Windows, install Claude Code from
> https://claude.ai/download instead and follow the installer.

---

## Step 4 — Make your folder

You want one folder that holds everything. We will put it in your home
directory and call it `outlier`.

```bash
mkdir -p ~/outlier
```

```bash
cd ~/outlier
```

`mkdir` makes the folder. `cd` moves you into it. Nothing visible happens —
that is normal. To prove it worked:

```bash
pwd
```

It should print something ending in `/outlier`.

> **Where is this folder?** On a Mac, open Finder, press
> `Command-Shift-H`, and you will see `outlier` sitting there. It is a
> normal folder. You can open it, look inside it, and drag files into it.

---

## Step 5 — Copy the toolkit into it

Make sure you are still in the folder (`pwd` should end in `/outlier`), then:

```bash
git clone https://github.com/daemnapps/outlier.git .
```

The dot at the end matters. It means "put it here, not in a subfolder".

When it finishes, check:

```bash
ls
```

You should see a list of folders — `swipe`, `video-teardown`, `prompts`, and
a few files. If you see them, the toolkit is on your computer.

---

## Step 6 — Install the two extra pieces

Two things the toolkit needs that do not come with your computer.

**A browser it can drive** (used for capturing competitor pages):

```bash
python3 -m pip install --user playwright
```

**A video tool** (used for pulling frames out of clips):

- **Mac:** `brew install ffmpeg`
  (if `brew` is not found, first run
  `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`)
- **Windows:** download from https://ffmpeg.org/download.html and follow
  their Windows instructions.

---

## Step 7 — Get your keys

A "key" is a long password that lets the toolkit use an AI service on your
account. **You are paying these companies directly.** Nothing goes through me.

You need two to start. The others are optional.

### Anthropic — required
Powers the writing. Sign up, add a payment method, create a key.
→ https://console.anthropic.com

### Google Gemini — required
Powers video analysis. Free tier is generous.
→ https://aistudio.google.com/apikey

### Higgsfield — optional
Image and video generation. Only needed if you want the toolkit making
visuals as well as words.
→ https://higgsfield.ai?fpr=damon61

### AdPlexity — optional, and it is not cheap
Competitor ad libraries. Only needed for the swipe tools. Skip it at first.
→ https://adplexity.com

> **On the links above:** the Higgsfield and Claude links in the OSO page are
> affiliate links. If you sign up through them I earn a percentage of what you
> spend, at no extra cost to you. If you would rather not, go to their sites
> directly — everything works identically either way.

### Saving your keys

Each key lives in a small file in your home folder. Paste these one at a time,
replacing `PASTE_YOUR_KEY_HERE` with the actual key:

```bash
echo 'GEMINI_API_KEY=PASTE_YOUR_KEY_HERE' > ~/.gemini.env
```

Claude Code will ask for your Anthropic key the first time you run it, so you
do not need to save that one manually.

---

## Step 8 — First run

Still in your folder:

```bash
cd ~/outlier
```

```bash
claude
```

Claude Code starts. The first time, it will ask you to sign in — follow the
prompts in your browser.

Once you see a prompt, type this and press Return:

```
Read the README and tell me what this toolkit can do.
```

It will read the folder and explain itself. **That is the moment it is
working.**

From there, a real first task:

```
Set up a brand called <your brand>. Here is our website: <your url>.
Read it and build the language bank.
```

---

## What to do when something breaks

It will. These are live experiments.

**"command not found"** — the program is not installed, or you did not open a
new Terminal window after installing it. Close the window, open a new one, try
again.

**"permission denied"** — you are trying to write somewhere your user cannot.
Make sure you ran `cd ~/outlier` first.

**"No such file or directory"** — you are in the wrong folder. Run `pwd` to
see where you are, then `cd ~/outlier`.

**It produced something bad** — tell it so, in plain words. "This sounds like
marketing, rewrite it against the actual reviews." It keeps the correction.

**Anything else** — open a question and paste the red text into it. Someone has
probably hit it already.

---

## Two rules

1. **Read what it writes before it goes anywhere.** The toolkit will not
   publish, send or spend on its own — that is deliberate, and it means the
   last check is always you.
2. **Correct it out loud.** It gets meaningfully better on the second run
   because you told it what was wrong on the first. People who skip this step
   think the tools do not work.

---

## Where to get help

The Questions tab on the repo. That is the only place — there is no support
email, no group chat and no DMs.

  https://github.com/daemnapps/outlier/issues/new?template=question.yml

It opens a short form. Fill it in, press the green button. Paste the red text
from your Terminal into it — all of it. Never paste an API key; if the error
text has one, replace it with XXXX first.

Answers get written under your question and stay there, so the next person who
hits the same wall finds it already answered.

