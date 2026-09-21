**Everything named in this prompt as an example is an example of a SHAPE, not
of content.** No brand, product, person, price or phrase in this file belongs in
your answer. Your answer's content comes only from the inputs below.

Here is the email — its words and its pictures, top to bottom: {source}

Furniture words the brand this run is for already has on file (they matter only
if this email is one of that brand's own): {furniture_words}

What the code already found before you, line by line: {code_findings}

Write an objective record of this email. **Observation only.** You are not
saying what would work better or what is weak. A later step turns this record
into the email's construct, and it needs a clean record to do it from.

**How to read the pictures.** A line like `[IMAGE alt=…] address` is a picture.
Its alt text is the words that are IN that picture — many emails carry their
whole message inside pictures, so an alt text can be a headline, body copy and
a button all at once. Read it as message when the picture is message.
`[LINK] … -> address` tells you where a picture or a line sends the reader.

**The code's list is a starting point, not a verdict.** It points at lines that
look like furniture or damage. Confirm each one or overrule it, and find what
it missed. A template tag in the footer (an unsubscribe tag, an address tag)
is furniture, not damage. A merge tag sitting where a reader would have seen
words — in the subject, the greeting, the body — is damage.

Your answer has FOUR labelled parts, under exactly these headings, in this
order. Nothing may sit in more than one of the first three.

# THE MESSAGE

What this one email says to its reader.

**THE ENVELOPE**

- From-name and the shape of the address
- **Subject line, quoted exactly.** Character count.
- **Preview text, quoted exactly.** If there is none, write `no preview text`.
- What the pair does together: whether the preview completes the subject,
  repeats it, or changes the subject entirely

**THE BLOCKS, IN ORDER**

Message blocks only, numbered `B1`, `B2`, … in the order they appear. For each:
the type (copy / image / button / review / product / divider / PS) and its
content **quoted, never paraphrased**. A picture block: what is in the frame,
what the words in it say (from its alt text), and what it is doing there.

Where a furniture item sits in the middle of the message, leave a one-line
marker in its place — `(furniture — see F2)` — so the order still reads true.

The opening line of body copy is quoted in full and called out.

**THE CTA CENSUS**

Message buttons and links only. Each one: what it says, where it falls, where
it goes. Then the count, and whether the first one comes before or after the
argument has been made.

**THE WEIGHT**

Roughly how much of the email is picture and how much is text, and whether the
words live inside the pictures or beside them.

**THE OFFER**

Where it appears, in what words, exactly. If there is no offer, write
`no offer`.

**THE PROOF**

Every specific: a number, a duration, a named person, a review, a study, a
before-and-after. Quoted. An unspecific claim is not proof and does not go here.

**VOICE MARKERS**

Sentence length and rhythm. Punctuation habits. The words this speaker reaches
for and the register they sit in. What this speaker never does.

**WHAT IT NEVER DOES**

What this email conspicuously avoids — a claim it could have made and did not,
a beat it skipped.

# PAGE FURNITURE

The frame every email from this sender arrives in, whatever the email is about:
the logo row, a navigation row, category or shop-by links, a standing brand
strip or slogan panel, a social-icon row, the footer, the unsubscribe line, the
postal address, legal lines, "view in browser".

The test: **would this part be identical in the sender's next email, on a
different subject?** If yes, it is furniture.

Numbered `F1`, `F2`, … in the order they appear. For each:

- **what it is** — logo row / navigation row / category links / standing brand
  strip / social row / footer / unsubscribe and address / legal / other
- **where it sits** — above the message, inside it (between which blocks), or
  below it
- **its words and alt texts, quoted exactly**

If the source has no furniture at all, write `no page furniture`.

When you cannot tell whether a part is message or furniture, put it under
furniture and say why in one line.

# SOURCE DEFECTS

Every place the source is broken rather than chosen: a dropped or doubled
character, a word cut off at the start or end of a line, a merge tag that shows
as code or came out empty where a reader would have seen words, a link with no
target, a typo, a sentence that stops mid-thought.

Numbered `D1`, `D2`, …. For each:

- **the defect, quoted exactly as it appears** — broken, not corrected
- **where it is** — subject line, preview text, which block, which furniture item
- **what kind** — dropped character / cut-off word / broken or empty merge tag /
  dead link / typo / export damage
- **what it was evidently meant to say**, only when that is plain from the
  source itself; otherwise `unclear`

Everywhere else in this record the source is still quoted exactly, but each
defective quote carries its marker (`[D1]`) right after it.

If you find none, write `no source defects found`.

# STRIP

The same two lists again, as data the code checks later steps against. One
fenced block, exactly this shape, valid JSON, nothing else under this heading:

```STRIP
{
 "furniture_words": ["every word or phrase that appears ONLY in furniture, quoted exactly as written"],
 "defects": [
  {"id": "D1", "quote": "the broken form, exactly as it appears", "meant": "what it was meant to say, or unclear"}
 ]
}
```

Use empty lists (`[]`) when there is no furniture or no defect. Be complete
rather than tidy: a furniture word left off this list is a word a later step is
free to carry.
