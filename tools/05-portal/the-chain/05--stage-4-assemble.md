Here are the missions and scenes: {missions}
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

- `id`, `title` — from the missions' place name. `title` is the title
  card, in caps.
- `player` — who they are in here and what is in their pocket.
- `speakers` — every person who talks: `name` and a colour class.
- `theme.accent` — objective yellow unless the world has its own colour.
- `brand.name`, `brand.shopUrl` — from the variables above.
- `brand.product.name`, `.what` — from the product file, exactly. The
  label's name, and one line of what it is.
- `brand.product.says` — three short phrases from the quoted review
  phrases above, verbatim. Never a phrase that is not in that list.
- `brand.product.price`, `.priceNote` — from the offer file, only if it
  states them. Otherwise omit the fields.
- `context` — one entry per wheel key, with `say` mapping every value
  to how it reads in the stats on the passed screen.
- `items` — the product as a thing that can be picked up.
- `scenes` — one per scene: `plate` (`p-id.jpg`), `ratio: 16 / 9`,
  `mood` (a dark hex for when the picture is missing), `sound`.
- `map` — the radar: rooms as blocks and a spot per scene, 0..1.
- `missions` — one per mission, in order. Fields: `id`, `scene` (only
  when it changes), `heading` (0..1, where the view starts), `facing`
  (degrees, for the radar arrow), `clock`, `objective` (with `~y~…~s~`),
  `marker` (`x`, `y` as fractions of the plate, `label`, `kind`, `look`),
  `hotspots`, `lines`, `action`; and when the world would, `title`/`sub`/
  `tag` (first mission), `note`, `cash`, `stars`, `special`.
- `lines` — `{ who, t }`; `who: 'think'` is a thought. Optional on a
  line: `sfx`, `note`, `stars`, `cash`, `special`, `give`.
- `action` — `go` / `wheel` / `hold` / `get` / `scan` / `exit`, with the
  fields the template shows. The scan carries the lesson's copy.

Also produce `prompts.md`: the style block at the top, the references
table, then one prompt per plate and per look, named to match the file
names in the world file.

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
