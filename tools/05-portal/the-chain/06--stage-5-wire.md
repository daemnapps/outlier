Here is the world file: {world_file}
Where it will be hosted: {host}
The ad platform: {platform}
What the store can read on arrival: {store_capabilities}
Today is: {today}

Wire it, and say what to watch.

# GIVE BACK

```
## Where the ad points
⟨The exact URL of the portal, with the platform's click tags in the
query string so they pass through: utm_*, and the platform's click id.
The player carries anything starting with utm_, fbclid, ttclid, gclid,
ad_ or sc_ straight through to the exit link.⟩

## What the store receives
| field | values | what the store should do with it |
|---|---|---|
| portal | ⟨id⟩ | know they came through the world |
| ⟨each context key⟩ | ⟨values⟩ | ⟨pre-fill the quiz result / pick the landing variant / tag the profile⟩ |
| portal_s | seconds in the world | segment slow vs fast walkers |

⟨One paragraph: how the landing page uses these on arrival, given what
the store can read. If it can read nothing, say what the smallest change
is — usually a script that copies query fields into the cart attributes
or the email signup form.⟩

## Events
⟨The events the player emits — beat, choice, hotspot, hold,
lesson_slider, lesson_reached, lesson_dig, exit, restart — and where they
go: `window.dataLayer` for a tag manager, the `portal` DOM event, and the
optional `measure.endpoint`. Which of these the brand should wire this
week, and the one line of tag-manager config to do it.⟩

## The four numbers
⟨From `the-format.md`: reached the lesson, finished the slider, took it
with them, and store conversion with context vs without. For each: how
to compute it from the events above, and the number it needs to beat —
the quiz funnel's equivalent step, if the brand has one.⟩

## Before an ad points here
⟨A checklist: walked every branch with ?director=1; every image present;
the exit link tested on the real store; the product card's quotes checked
against real reviews; sound tested on iOS; hold tested on Android; the
page loads under three seconds on 4G.⟩
```

# THE RULES

**The player already does the carrying.** Do not invent parameters. What
it sends is what is in the world file's `context`, plus `portal` and
`portal_s`, plus the ad tags.

**No new tracking.** Nothing here adds a pixel, a cookie or a script the
brand did not already run. The events go to what the brand already has.

**Numbers need a comparison.** A rate with nothing to beat is not a
result. If the brand has no quiz funnel, the comparison is the plain
landing page's click-through at the same step.

---

## EXAMPLES ARE EXAMPLES

Platforms, stores and fields here are illustrative. Wire what is in front
of you.
