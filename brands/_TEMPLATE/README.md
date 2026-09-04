# Your brand folder

The teardown machine is brand-agnostic on purpose: it knows how to read a
video and rebuild it, and it knows nothing about you. Everything it needs
about your brand lives in one folder — this one — and it reads that folder
fresh on every run.

Copy this folder, rename it to your brand, fill it in once. Every tool in the
kit reads the same folder, so filling it in is the only setup you ever do.

```
your-brand/
  variables/video.md          ← THE CONTRACT. The machine reads this first.
  core-avatars/
    objection-bank.md         what stops them buying, in their words
    <avatar>/
      profile.md              who they are — the 6 categories
      language/rules.md       how they talk, and what you may never say
      language/prospects.json their real sentences, raw
      sub-avatars/            narrower versions of the same person
  products/
    <product>.md              what it is, exactly as it looks
    offer-bank.md             every offer, by avatar
  identity-anchors.md         names and claims the machine may use
  hook-ledger.md              hooks already spent, so they never repeat
```

## Fill it in this order

Nothing below is busywork — each file answers a question the machine will
otherwise get wrong, and it fails loudly rather than inventing an answer.

**1. `core-avatars/<avatar>/profile.md`** — one real person, not a segment.
Give the avatar a name that tells their story, never a demographic label.
"The Marks-That-Stay Kid" beats "Males 18–24"; the demographics go in the
description line, last. If you sell to two people who would never say the
same sentence, that is two avatars, not one — and they never blend.

**2. `core-avatars/<avatar>/language/`** — how they actually talk. Real
sentences from reviews, comments, tickets, surveys, forums. Verbatim, with
a source on every line. The point is not summary; it is that the ad can use
words your customer has already said. `rules.md` is the other half: the
registers to write in, and the words you may never use.

**3. `products/<product>.md`** — what the product *is*, described the way a
camera sees it. Colour, finish, the label text, the cap, the size. A model
that is not told what the packaging looks like will invent packaging, and
the frame comes back with a product that is not yours.

**4. `products/offer-bank.md`** — the actual offers, per avatar. Price,
what is included, the guarantee, the subscription terms.

**5. `core-avatars/objection-bank.md`** — the reasons people do not buy,
in their words. This is what the middle of every script answers.

**6. `identity-anchors.md`** — who and what the machine is allowed to name:
your founder, your ingredients, your certifications, your real results. If
it is not in here, it does not go in an ad.

**7. `variables/video.md`** — the map from a variable to a path. Leave it
alone unless you move a file; it is already wired.

## The rule that keeps output honest

**Nothing invented.** Every one of these files exists so the machine can be
specific without guessing. When a file is missing or thin, the machine says
so instead of filling the gap — a brief that admits it does not know your
packaging is useful; one that confidently describes the wrong packaging is
not.

## What "good" looks like

A brand folder is finished when someone who has never met your customer can
read `profile.md` and `language/`, write a line, and have you say *"yes, that
is exactly how they talk."* Until then, keep adding real sentences.

---

*Part of Open Source Outliers — daemn.co. MIT licensed. Your brand folder is
yours: nothing here phones home, and this template ships empty on purpose.*
