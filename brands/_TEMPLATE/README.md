# _TEMPLATE — the brand folder every brand copies

Ruled by Damon, 2026-08-30, during the naming pass. A new brand starts as a
copy of this tree; the brand-agnostic tools assume exactly these paths, for
every brand, no exceptions. If a folder earns a new home, it moves HERE and
in every brand in the same commit.

```
<brand>/
  README.md                          what this brand is; the folder test
  data-sources.md                    where every derived file's data comes from
  core-avatars/                      one folder per avatar; sub-avatars inside
    language-index.json / .md        the language bank's index
    objection-bank.md                what stops them — the avatars' objections
    <avatar>/profile.md              who they are
    <avatar>/language/**/*.json      their real sentences, by funnel stage
    <avatar>/sub-avatars/*.md
  calendar/
    moments.json                     cross-channel moments
  email/                             the email channel's record
    identity/sender.md               who emails come from
    audience-matrix.json             segment × avatar planning cells
    ledger · classified · learnings · performance · segments · sends/
  strategy/
    angles.json                      the one angle source; only Damon signs
    board.html + build_board.py      the judgment surface
  products/                          one profile per product, from the live feed
  offers/
    offer-bank.md                    the offers, split by avatar. IT IS HERE,
                                     not under products/ — this tree said
                                     products/ until 2026-09-19 while both live
                                     brands had offers/offer-bank.md, and seven
                                     config lines were repointed at the real one
  operations/                        the brand's own operating facts
    brand.json                       label, accounts, timezone, start month,
                                     rates (freight, payment, lead days)
    products.json                    every product and its SKUs, pack sizes,
                                     sets, costs, weights, production days
  existing-content/                  what the brand has already shipped or proven
    ads/  emails/  organic/
    landing-pages/                   the backbone of every page type we make:
      quiz/ · advertorials/ · listicles/ · offer pages (acquisition,
      pre-sell, retention) — one folder per page type
    angles.md                        receipted angles (staying here for now)
  variables/                         one variable map per surface (email.md, …)
  customer-service-documentation/    the CS playbook, .html + .md
  creators/                          the creator program: one folder per creator
  ai-cast/                           the brand's AI characters (CHARACTER-SPEC)
  hook-ledger.md                     {hook_ledger} — spent hooks never regenerate
  identity-anchors.md                {identity_anchors} — who chains may name
  position.md                        {position} — the line, the mechanism, the market
                                     stage, as labelled slots (2026-09-19); copy
                                     _TEMPLATE/position.md, fill every slot or write
                                     `open`; lint_position.py gates the shape; a brand
                                     without one refuses at the audience stage
```

**THIS TREE IS THE STANDARD, AND IT HAS DRIFTED FROM BOTH LIVE BRANDS BEFORE.**
`brands/<brand>/README.md` binds a structure change to land here and there in the
same commit, so a folder that exists in a brand and not here is a broken promise,
not a detail. Three were found on 2026-09-19 by comparing this file against the
two live trees: `offers/` (added above, and it was WRONG rather than missing —
`offer-bank.md` was filed under `products/`), `operations/` (added above, the
missed rider of MET-C24 (brand operations folder), ruled 2026-09-16 and built in
both brands the same day), and `meta/`, which is DELIBERATELY STILL ABSENT — it
is Damon's and undecided, and phase 2 rules it rather than this edit.

One thing this edit does NOT fix, so it is not lost: `brands/<brand>/` carries BOTH
`offers/offer-bank.md` and `commerce/offer-bank.md`. Two files with one name and
no ruling on which is the offer bank. That is brand content and a human's call,
and it belongs to the phase-2 consolidation.

Rules that travel with the tree: brand context is read-only to tools during a
run · every fact derived, never typed · one variable vocabulary across lanes ·
one avatar per piece.

## The four axes a brand runs on

Everything a brand makes is one point in four independent axes
(`components/naming/MODEL.md`), and each axis has exactly one home:

| Axis | Answers | Lives in | Seeded here? |
|---|---|---|---|
| **Avatar** | who is this for? | `core-avatars/<slug>/profile.md` | yes — shell + rules |
| **Angle** | what are we claiming? | `strategy/angles.json` | yes — shell + rules |
| **Channel** | where does it run? | **shared, not per brand** — `copy/bank/channel-map.json` | n/a |
| **Format** | how is it built? | 25 banks — `components/naming/registry.json` | partly: `offers/`, `email/` |

**An angle is channel-free and format-free.** The same claim runs as a paid
static, an organic video, an email and a landing page. A thing that only works
in one container is a format. This is checked, not merely asked for.

### `channels/` does not hold channels

Both live brands have a `channels/` folder and neither holds the channel
vocabulary — they hold creator contacts and rosters. The four channels
(paid-social, organic-social, email, owned-pages) are shared across brands and
live in the channel map. **The folder is named after the wrong thing**, which is
recorded here so a new brand does not copy the confusion.
