**No example in this prompt is an answer.** Any id, name or phrase shown below
as an illustration of the SHAPE of a reply is a placeholder — never copy it
into your answer because it appeared here. Every id you write must be copied,
character for character, from the candidate lists you are handed further down.
An id that is not on its list is refused by the code that reads your reply, so
a guess is worse than saying nothing fits.

Here is the record of one email — its message and its defects. The sender's
page furniture was taken out before you, on purpose: {record}

Here are the candidate rows — the only ids that exist — one list per label:
{candidates}

Your job is to LABEL this email: say which library row it IS, on three lists.
You are not judging the email, not improving it, and not describing it again.
Label the SOURCE email as the record has it — nothing about any brand that
might later rebuild it.

The three labels:

1. `format/email` — the kind of send this is: what the email is FOR, read from
   what its message does to the reader from the first block to the last.
2. `template/email` — the build layout it arrives in: which parts it has and in
   what order, read from THE BLOCKS and THE WEIGHT. Furniture is not part of a
   layout's identity.
3. `framework/all` — the argument shape the words follow, read from the blocks
   in the order a reader meets them.

Rules, in order of importance:

- **One id per label, from that label's own list.** An id from the wrong list
  is a wrong answer.
- **Match on what the row says it IS** (its `what`), not on its name sounding
  close. Two rows can sound alike and describe different things.
- **When no row fits, say so.** Write `none-fits` as the id and give
  `proposed`: one line, in the form `new-id — Name — what it is in one
  sentence`, written brand-free and subject-free so it could describe any
  sender's email. A forced fit corrupts the library; `none-fits` grows it.
  Never bend a row to avoid writing `none-fits`.
- **`why` is evidence, not opinion.** One sentence that points at something
  the record actually holds — a block number, a quoted line, the weight — that
  makes this row the match. No brand, product or person names in `why` or in
  `proposed`: describe the function ("the sender's product", "the speaker").
- **A source defect is never evidence.** Do not match a row on a broken line.
- If the record does not contain enough to decide a label, that label is
  `none-fits` with `proposed` set to `undecidable — ` and what was missing.

# ELEMENT LABELS

Reply with ONE fenced block, tagged `ELEMENTS`, holding valid JSON with exactly
these three keys, and nothing before or after it:

```ELEMENTS
{
 "format/email":   {"id": "<an id from the format/email list, or none-fits>", "why": "<one sentence of evidence>", "proposed": null},
 "template/email": {"id": "<an id from the template/email list, or none-fits>", "why": "<one sentence of evidence>", "proposed": null},
 "framework/all":  {"id": "<an id from the framework/all list, or none-fits>", "why": "<one sentence of evidence>", "proposed": null}
}
```

`proposed` stays `null` unless the id is `none-fits`.
