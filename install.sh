#!/usr/bin/env bash
# Open Source Outliers — one-line setup.
#
#   curl -fsSL https://raw.githubusercontent.com/daemnapps/outlier/main/install.sh | bash
#
# Safe to run more than once. It checks what you already have, installs only
# what's missing, and never touches anything outside ~/outlier and your key
# files. Read the whole thing before you run it — you should never pipe a
# script from the internet into bash without looking at it first.

set -u

REPO="${OSO_REPO:-https://github.com/daemnapps/outlier.git}"
DIR="${OSO_DIR:-$HOME/outlier}"

# ── looks ─────────────────────────────────────────────────────────────────
if [ -t 1 ]; then
  B=$'\033[1m'; D=$'\033[2m'; Y=$'\033[33m'; G=$'\033[32m'; R=$'\033[31m'; X=$'\033[0m'
else B=""; D=""; Y=""; G=""; R=""; X=""; fi

step()  { printf "\n${B}%s${X}\n" "$*"; }
ok()    { printf "  ${G}✓${X} %s\n" "$*"; }
warn()  { printf "  ${Y}!${X} %s\n" "$*"; }
die()   { printf "\n  ${R}✗ %s${X}\n\n" "$*"; exit 1; }
have()  { command -v "$1" >/dev/null 2>&1; }

printf "\n${B}Open Source Outliers${X}\n"
printf "${D}Setting up in %s${X}\n" "$DIR"

# ── 0. what are we on ─────────────────────────────────────────────────────
OS="unknown"
case "$(uname -s)" in
  Darwin) OS="mac" ;;
  Linux)  OS="linux" ;;
  *)      die "This installer handles Mac and Linux. On Windows, open the walkthrough and follow the steps by hand." ;;
esac

# ── 1. git ────────────────────────────────────────────────────────────────
step "1/6  Git"
if have git; then
  ok "already installed ($(git --version | awk '{print $3}'))"
else
  if [ "$OS" = "mac" ]; then
    warn "not installed — opening Apple's installer"
    xcode-select --install 2>/dev/null || true
    die "Finish the installer that just opened, then run this command again."
  else
    die "Install git first:  sudo apt install git   (or your distro's equivalent)"
  fi
fi

# ── 2. python ─────────────────────────────────────────────────────────────
step "2/6  Python"
if have python3; then
  PYV=$(python3 -c 'import sys;print("%d.%d"%sys.version_info[:2])' 2>/dev/null || echo 0)
  MAJOR=${PYV%%.*}; MINOR=${PYV##*.}
  if [ "${MAJOR:-0}" -ge 3 ] && [ "${MINOR:-0}" -ge 9 ]; then
    ok "already installed (${PYV})"
  else
    die "Python ${PYV} is too old. Install 3.9 or newer from python.org, then run this again."
  fi
else
  die "Python isn't installed. Get it from https://www.python.org/downloads/ then run this again."
fi

# ── 3. claude code ────────────────────────────────────────────────────────
step "3/6  Claude Code"
if have claude; then
  ok "already installed"
else
  printf "  installing…\n"
  if curl -fsSL https://claude.ai/install.sh | bash >/dev/null 2>&1; then
    # the installer adds it to PATH for *new* shells; find it for this one
    for p in "$HOME/.local/bin" "$HOME/.claude/bin" "/usr/local/bin"; do
      [ -x "$p/claude" ] && export PATH="$p:$PATH"
    done
    if have claude; then ok "installed"
    else warn "installed, but not on PATH in this window yet — that's normal"; fi
  else
    die "Claude Code failed to install. Try https://claude.ai/download instead, then run this again."
  fi
fi

# ── 4. the toolkit ────────────────────────────────────────────────────────
step "4/6  The toolkit"
mkdir -p "$DIR" || die "Couldn't create $DIR"
if [ -d "$DIR/.git" ]; then
  ok "already here — pulling the latest"
  git -C "$DIR" pull --ff-only >/dev/null 2>&1 && ok "up to date" || warn "couldn't pull; your local copy is unchanged"
elif [ -n "$(ls -A "$DIR" 2>/dev/null)" ]; then
  die "$DIR already exists and has files in it. Move or rename it, then run this again."
else
  git clone --depth 1 "$REPO" "$DIR" >/dev/null 2>&1 \
    && ok "downloaded" \
    || die "Couldn't download the toolkit. Check your internet, then run this again."
fi

# ── 5. extras ─────────────────────────────────────────────────────────────
step "5/6  Extras"
if python3 -c 'import playwright' 2>/dev/null; then
  ok "browser tool already installed"
else
  printf "  installing browser tool…\n"
  python3 -m pip install --user --quiet playwright 2>/dev/null \
    && ok "browser tool installed" \
    || warn "couldn't install it — competitor page capture won't work, everything else will"
fi

if have ffmpeg; then
  ok "video tool already installed"
elif [ "$OS" = "mac" ] && have brew; then
  printf "  installing video tool…\n"
  brew install ffmpeg >/dev/null 2>&1 && ok "video tool installed" \
    || warn "couldn't install it — video work won't run, everything else will"
else
  warn "video tool (ffmpeg) not installed — optional, only needed for video work"
fi

# ── 6. keys ───────────────────────────────────────────────────────────────
step "6/6  Keys"
printf "  ${D}These live on your machine only. You pay the providers directly.${X}\n"

if [ -s "$HOME/.gemini.env" ]; then
  ok "Google Gemini key already saved"
else
  printf "\n  Google Gemini powers video analysis. Free tier is generous.\n"
  printf "  ${B}Get one here:${X} https://aistudio.google.com/apikey\n"
  printf "  Paste it here (or press Return to skip): "
  if [ -t 0 ]; then read -r GK; else GK=""; fi
  if [ -n "${GK:-}" ]; then
    printf 'GEMINI_API_KEY=%s\n' "$GK" > "$HOME/.gemini.env"
    chmod 600 "$HOME/.gemini.env"
    ok "saved to ~/.gemini.env"
  else
    warn "skipped — add it later by running this again"
  fi
fi
printf "  ${D}Claude Code will ask for your Anthropic key the first time you run it.${X}\n"

# ── done ──────────────────────────────────────────────────────────────────
printf "\n${G}${B}Done.${X}\n\n"
printf "  Two lines to start:\n\n"
printf "    ${B}cd %s${X}\n" "$DIR"
printf "    ${B}claude${X}\n\n"
printf "  Then type this and press Return:\n\n"
printf "    ${D}Read the README and tell me what this toolkit can do.${X}\n\n"
printf "  ${D}Stuck? Questions go here — not to a group chat:${X}\n"
printf "    ${D}https://github.com/daemnapps/outlier/issues/new?template=question.yml${X}\n\n"
if ! have claude; then
  printf "  ${Y}Close this Terminal window and open a new one first${X} —\n"
  printf "  that's the one that knows Claude Code exists.\n\n"
fi
