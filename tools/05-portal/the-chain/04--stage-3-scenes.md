Here is the world bible: {world_bible}
Here is the lesson: {lesson}
Here is how they talk: {language_file}
The quiz questions the store currently asks, if any: {quiz_questions}
Today is: {today}

Cut the missions.

Eight to eleven missions, in the shape `the-format.md` gives (threshold,
wait, texture, turn, chair, mirror, lesson, hand-over, feeling, door).
Every mission is a place to stand (a scene), a marker to walk to, a few
lines of subtitle, and exactly one thing to do. It is played, not read:
the person drags to look around a wide plate, taps the marker, taps
through the lines, does the thing.

First list the scenes: the four to six places in the world a person
stands, each a wide 16:9 plate (the street outside, the waiting chairs,
the chair facing the mirror, the counter). Missions happen in scenes;
several missions can share one, turning to face something else.

# GIVE BACK

First the scenes:

```
## Scene · ⟨id⟩
**Plate.** ⟨One sentence: the wide 16:9 view from where the person stands,
who is in it, the light. First person. Which references it needs: the
room, which characters, the product.⟩
**Sound.** ⟨street / shop / chair / quiet⟩
```

Then each mission:

```
## ⟨N⟩ · ⟨mission id, one or two words⟩ · ⟨time on the world's clock⟩ · in ⟨scene⟩

**Objective.** ⟨Four words, the key noun marked ~y~like this~s~. What the
HUD says at the bottom.⟩

**Marker.** ⟨The thing to walk to or the person to talk to, and where it
is in the plate (left / centre / right). Talk markers are people.⟩

**Look.** ⟨One sentence: the 9:16 close-up the marker opens, first person.
Or none.⟩

**Lines.** ⟨subtitles, one tap each⟩
- think: ⟨a thought in their own head, one breath⟩
- ⟨Name⟩: ⟨a spoken line⟩

**HUD.** ⟨Optional: a notification (title + line), a wanted star, the
special meter filling, cash changing. Only when the world would.⟩

**Side things.** ⟨One to three objects or people from the bible's "objects
nobody explains", each a marker with one sentence. Or none.⟩

**The one thing to do.**
⟨go: ⟨button label⟩⟩
— or —
⟨wheel · key `⟨field⟩` · asked by ⟨Name⟩: "⟨the question⟩"
  - ⟨answer⟩ → `⟨value⟩` · reply: "⟨what the asker says back⟩"
  - …⟩
— or —
⟨hold: "⟨label⟩" · after: "⟨what happened while they held⟩"⟩
— or —
⟨get: the product⟩ / ⟨scan⟩ / ⟨exit: the stats rows⟩
```

Then, after the missions:

```
## The prompts
⟨The style block from WHICH-MODELS.md, then one prompt per plate and per
look, each naming its references ("the room in reference image 1, the
older man in reference image 2"). Ends: "no text, no HUD".⟩

## The radar
⟨The rooms of the place as a rough map: which scene sits where.⟩

## The fields
| key | the quiz question it replaces | values |
|---|---|---|
```

# THE RULES

**One action per mission.** Never two. If a mission needs two things it
is two missions.

**Every wheel is a question the funnel would have asked.** Map it. If
the store asks "how often do you shave?", a mission asks it as the barber
would, off the wheel. The exception is the texture mission, which asks
something that is pure world — one of those, and only one.

**Something to walk to, every time.** A mission with no marker is a
slideshow. The marker is a thing or a person in the plate.

**Replies reassure. They never sell.** After an honest answer the reply
is a reassurance connector from the language file. "No shame in that."
"I got you." Never a benefit.

**The turn is where the honest question lives.** The wheel about what
is actually wrong comes at the moment the world makes them self-conscious
— not before.

**The product is not named until the hand-over.** Not in a line, not in
a reply, not in a hotspot.

**Lines are short.** A thought: under twenty words. Spoken: something a
person says in one go. Two or three lines a mission, never six.

**Their words.** Every line passes the language file. No medical, no
marketing, no formal transitions, no em dashes.

**Prompts draw the product from its reference.** The real one, attached
as a reference image. Nothing else in a frame carries a logo.

---

## EXAMPLES ARE EXAMPLES

Barbers, capes and neck lines: illustrative. Missions come from the bible
in front of you.
