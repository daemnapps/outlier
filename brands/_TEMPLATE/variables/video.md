# {{brand}} — video variables

**One map per brand, per surface.** The video machine reads ONLY this file to
find your brand's parts. Nothing brand-specific lives inside the machine.

**A run declares an avatar.** Everything avatar-shaped resolves through it,
and there is no default — a run that does not name an avatar is writing to
nobody.

| Variable | Resolves to |
|---|---|
| `{avatar}` | `core-avatars/<avatar>/profile.md` |
| `{language_bank}` | `core-avatars/<avatar>/language/rules.md` |
| `{product_file}` | `products/` |
| `{objection_bank}` | `core-avatars/objection-bank.md` |
| `{offer_file}` | `products/offer-bank.md` |
| `{identity_anchors}` | `identity-anchors.md` |

Leave this file alone unless you move something. If you do move a file,
change the path here and every tool follows.
