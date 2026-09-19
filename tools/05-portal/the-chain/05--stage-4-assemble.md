Here are the beats: {beats}
Here is the lesson: {lesson}
Here is the product: {product_file}
Here is the offer: {offer_file}
Real customer phrases about this product, quoted: {review_phrases}
The store page the exit should land on: {shop_url}
Today is: {today}

Write the world file.

The player reads one JavaScript object, `window.PORTAL_WORLD`. The
template is `worlds/_TEMPLATE/world.js` and the worked example is
`worlds/barbershop/world.js`. Produce a complete file in exactly that
shape, nothing else, so it can be saved as `world.js` and run.

# WHAT GOES WHERE

- `id`, `title`, `voice` — from the beats' place name and the person with
  authority.
- `theme.accent` — one colour that lives in the world. Name where it
  comes from in a comment.
- `brand.name`, `brand.shopUrl` — from the variables above.
- `brand.product.name`, `.what` — from the product file, exactly. The
  label's name, and one line of what it is.
- `brand.product.says` — three short phrases from the quoted review
  phrases above, verbatim. Never a phrase that is not in that list.
- `brand.product.price`, `.priceNote` — from the offer file, only if it
  states them. Otherwise omit the fields.
- `context` — one entry per choice key, with `say` mapping every value
  to how it reads on the chip at the door.
- `beats` — one per beat, in order. Fields: `id`, `time`, `eyebrow`,
  `image` (numbered `NN-id.jpg`), `sound`, `mood` (a dark hex that
  matches the picture, for when it is missing), `lines`, `hotspots`,
  `action`, and for the lesson beat `lesson`, and for the hand-over beat
  `showProduct: true`.
- `lines` — `{ s }` sense, `{ who, t }` spoken, `{ y }` thought, `{ n }`
  note. In the order they are read.
- `hotspots` — `x` and `y` as fractions of the frame, estimated from the
  picture sentence; the brand adjusts after generating.
- `action` — `tap` / `choice` / `hold` / `lesson` / `exit`, with the
  fields the template shows.

Also produce `prompts.md`: every beat's image prompt, numbered to match
its file name, with the anchor sentence at the top of the file and at the
end of every prompt.

# THE RULES

**Nothing new.** Every string in the file traces to the beats, the
lesson, the product file, the offer file or the quoted phrases. You are
transcribing into a shape, not writing.

**Valid.** It must parse. Straight quotes inside strings are escaped or
the string uses the other quote. Trailing commas are fine. No em dashes
in any string.

**No claims.** The product card says what the product is and quotes what
customers said. It does not say what it does unless the product file's
*What it does* says it, in which case that goes in `what`, in the
customer's words.

**The exit carries everything.** Do not build the exit URL by hand; the
player appends the context. `shopUrl` is the bare page.

---

## EXAMPLES ARE EXAMPLES

The barbershop file is a shape to match, not content to keep. Nothing
from it survives into a new world except the structure.
