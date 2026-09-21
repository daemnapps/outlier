"""Read both swipe pools WHERE THEY LIVE and hand back one record shape.

READ-ONLY. Nothing here writes to, moves, or reshapes either pool — the two
swipe folders stay exactly as their own tools write them (rollout rules 3, 4).

    swipe-paid/<advertiser>/blocks.json   competitor ads (the ad-library sweep)
    swipe-paid/<advertiser>/pages.json    the landing pages those ads go to
    swipe-paid/own/<account>/ads.json     ads we ran (rebuilt cache, not in git)
    swipe-paid/judgements.json            a person's calls, laid over the top
    swipe-organic/records/avatar-feeds/<feed>/items.json   organic posts, per feed
    swipe-organic/records/swipe-videos/<code>/format.json  the structure read of a pulled post
    swipe-organic/<name>/posts.json       a pulled set of one creator's / brand's posts

ONE RECORD
    id          swipe:<lane>:<where>:<ref> — the same id swipe-paid/corpus.py mints, so it joins swipe.db
    source      paid | organic | own          where we found it
    owner       competitor | own | creator    whose it is  (`--source competitor` matches this)
    kind        video | image | carousel | copy | page | email | unknown — read off the asset, never guessed
    route       which teardown it goes to (ROUTES); `unrouted` when the kind is unknown
    swiped_for  the brand it was swiped for, or `shared` when the pool does not say
    asset       where the asset is: url · file (repo path) · drive (Shared Assets path or link) · thumb
    format      the label its pool carries, or "" — NEVER filled in here
    structure   organic video only: the organic-structure read, or ""
    title       headline / caption, cut short
    pool        which pool file it came from (repo-relative)

`format` and `structure` are different elements (components/elements/CLAUDE.md):
a paid ad's `format` is checked against `format/<kind>`; what swipe-organic
calls a post's "format" is an organic STRUCTURE and is checked against
`structure/video`. They are kept apart here so neither list is asked the
other's question.
"""
import json
import re
from pathlib import Path

import paths as P

ROUTES = {"video": "video-teardown", "image": "image-teardown", "carousel": "image-teardown",
          "copy": "copy-teardown", "page": "page-teardown", "email": "email-teardown"}
UNROUTED = "unrouted"
KINDS = tuple(ROUTES)
SOURCES = ("paid", "organic", "own", "competitor")
SHARED = "shared"
# A pool writes these when nobody has labelled the swipe. All of them mean "empty".
EMPTY = {"", "unclassified", "unread", "unknown", "none", "unmeasured", "null"}
FORMAT_LIST = {"video": ("format", "video"), "image": ("format", "image"),
               "carousel": ("format", "carousel"), "copy": ("format", "copy"),
               "page": ("format", "page"), "email": ("format", "email")}
STRUCTURE_LIST = ("structure", "video")
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")
VIDEO_EXT = (".mp4", ".mov", ".webm")
NOT_ADVERTISERS = {"own", "organic", "refs", "capture", "context", "prompts", "teardown"}


def _slug(s):
    """The naming convention's slug (components/naming/names.py) — kept identical so ids join."""
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def _clean(v):
    v = "" if v is None else str(v).strip()
    return "" if v.lower() in EMPTY else v


def _load(f):
    try:
        return json.loads(Path(f).read_text())
    except (OSError, ValueError):
        return None


def _rel(f):
    try:
        return str(Path(f).relative_to(P.workspace()))
    except ValueError:
        return str(f)


def _cut(s, n=200):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def record(lane, where, ref, *, source, owner, kind, swiped_for, pool, title="",
           fmt="", structure="", url="", file="", drive="", thumb=""):
    kind = kind if kind in ROUTES else "unknown"
    return {"id": f"swipe:{lane}:{_slug(where)}:{ref}", "source": source, "owner": owner,
            "kind": kind, "route": ROUTES.get(kind, UNROUTED), "swiped_for": swiped_for or SHARED,
            "asset": {"url": url or "", "file": file or "", "drive": drive or "", "thumb": thumb or ""},
            "format": _clean(fmt), "structure": _clean(structure),
            "title": _cut(title), "pool": pool}


# ------------------------------------------------------------------ paid

def _accounts():
    """Which brand owns which ad account — read from brands/<brand>/meta/account.json."""
    out = {}
    for b in P.brands():
        d = _load(P.workspace() / "brands" / b / "meta" / "account.json") or {}
        if d.get("account_id"):
            out[str(d["account_id"])] = b
    return out


def read_paid():
    pool = P.paid_pool()
    judged = _load(pool / "judgements.json") or {}
    out = []
    for f in sorted(pool.glob("*/blocks.json")):
        adv = f.parent.name
        if adv in NOT_ADVERTISERS or adv.startswith(("_", ".")):
            continue
        doc = _load(f) or {}
        rel = _rel(f)
        drive_root = f"Shared Assets/swipe-paid/{adv}"
        for b in doc.get("blocks") or []:
            slug = b.get("slug") or ""
            stem = f"{b.get('nn')}_{slug}" if b.get("nn") else slug
            # the copy block itself is a copy swipe: one paragraph the advertiser locked
            if (b.get("primary_text") or b.get("headline")):
                out.append(record("paid", adv, f"block-{slug}", source="paid", owner="competitor",
                                  kind="copy", swiped_for=SHARED, pool=rel,
                                  title=b.get("headline") or b.get("primary_text"),
                                  url=b.get("landing_page"),
                                  file=f"{'/'.join(P.PAID_POOL)}/{adv}/blocks/{stem}.md"))
            for ad_id, m in (b.get("media") or {}).items():
                is_video = bool(m.get("video"))
                fields = m.get("fields") or {}
                kind = "carousel" if fields.get("media") == "carousel" else ("video" if is_video else "image")
                sub = f"video/{ad_id}.mp4" if is_video else f"photos/{ad_id}.jpg"
                r = record("paid", adv, ad_id, source="paid", owner="competitor", kind=kind,
                           swiped_for=SHARED, pool=rel, title=b.get("headline"),
                           fmt=fields.get("format"), url=m.get("video") or m.get("image"),
                           drive=f"{drive_root}/blocks/{slug}/{sub}", thumb=m.get("image"))
                call = ((judged.get(r["id"]) or {}).get("fields") or {}).get("format")
                if _clean(call):                            # a person's call wins
                    r["format"] = _clean(call)
                out.append(r)
        pages = _load(f.parent / "pages.json") or {}
        for slug, pg in pages.items() if isinstance(pages, dict) else []:
            out.append(record("paid", adv, f"page-{slug}", source="paid", owner="competitor",
                              kind="page", swiped_for=SHARED, pool=_rel(f.parent / "pages.json"),
                              title=slug, fmt=pg.get("type"), url=pg.get("url"),
                              file=f"{'/'.join(P.PAID_POOL)}/{adv}/_pages/{slug}.md",
                              drive=f"{drive_root}/_pages/{slug}"))
    return out


def read_own():
    pool = P.paid_pool() / "own"
    accounts = _accounts()
    out, seen = [], set()
    files = sorted(pool.glob("*/ads.json"), key=lambda f: (f.parent.name not in accounts, f.parent.name))
    for f in files:                                         # a real account first, so it wins a duplicate
        acct = f.parent.name
        doc = _load(f) or {}
        for ad in doc.get("ads") or []:
            if ad.get("id") in seen:
                continue
            seen.add(ad.get("id"))
            media = (ad.get("media") or "").lower()
            kind = {"video": "video", "static": "image", "image": "image", "carousel": "carousel"}.get(media, "unknown")
            out.append(record("own", acct, ad.get("id"), source="own", owner="own", kind=kind,
                              swiped_for=accounts.get(acct, SHARED), pool=_rel(f),
                              title=ad.get("name") or ad.get("title"),
                              fmt=(ad.get("fields") or {}).get("format") or ad.get("format"),
                              url=ad.get("permalink") or ad.get("preview") or ad.get("landing_page"),
                              thumb=ad.get("thumb")))
    return out


# --------------------------------------------------------------- organic

def _organic_kind(it, pulled):
    k = (it.get("kind") or "").lower()
    if k in ("video", "short", "reel"):
        return "video"
    if k in ("image", "photo"):
        return "image"
    if k in ("carousel", "slideshow", "sidecar"):
        return "carousel"
    url = (it.get("url") or "").lower()
    if it.get("id") in pulled or re.search(r"/(reel|reels|video|shorts)/|youtube\.com/watch|youtu\.be/", url):
        return "video"
    if "/photo/" in url:
        return "image"
    return "unknown"                                        # an instagram /p/ link does not say


def read_organic():
    pool = P.organic_pool()
    brands = set(P.brands())
    # a pulled post's structure read, keyed by its post code
    reads = {}
    for f in pool.glob("records/swipe-videos/*/format.json"):
        d = _load(f) or {}
        if _clean(d.get("format_id")):
            reads[f.parent.name] = d["format_id"]
    pulled = {p.name for p in (pool / "records" / "swipe-videos").glob("*") if p.is_dir()}
    out = []
    for f in sorted(pool.glob("records/avatar-feeds/*/items.json")):
        feed = f.parent.name
        owner_brand = feed.split("--")[0]
        doc = _load(f) or {}
        items = doc.get("items", doc) if isinstance(doc, dict) else {}
        for key, it in items.items():
            if not isinstance(it, dict):
                continue
            fit = it.get("brand_fit")
            swiped_for = owner_brand if owner_brand in brands else (fit if fit in brands else SHARED)
            kind = _organic_kind(it, pulled)
            structure = (it.get("sift") or {}).get("format") or reads.get(it.get("id"))
            out.append(record("organic", feed, key.replace(":", "-"), source="organic", owner="creator",
                              kind=kind, swiped_for=swiped_for, pool=_rel(f), title=it.get("caption"),
                              structure=structure if kind == "video" else "",
                              url=it.get("url"), thumb=it.get("cover"),
                              drive=(f"Shared Assets/swipe-organic/records/swipe-videos/{it.get('id')}/video.mp4"
                                     if it.get("id") in pulled else "")))
    for f in sorted(pool.glob("*/posts.json")):
        name = f.parent.name
        doc = _load(f) or {}
        named = doc.get("brand")
        for p in doc.get("posts") or []:
            fname = (p.get("file") or "").lower()
            url = (p.get("url") or "").lower()
            if (p.get("slides") or 0) > 1:
                kind = "carousel"
            elif fname.endswith(IMAGE_EXT):
                kind = "image"
            elif fname.endswith(VIDEO_EXT) or re.search(r"/(reel|reels|video|shorts)/", url):
                kind = "video"
            else:
                kind = "unknown"
            ref = p.get("id") or p.get("slug") or Path(p.get("file") or "post").stem
            stem = p.get("slug") or Path(p.get("file") or "").stem
            out.append(record("organic", name, ref, source="organic",
                              owner="own" if named in brands and p.get("creator") == named else "creator",
                              kind=kind, swiped_for=named if named in brands else SHARED, pool=_rel(f),
                              title=p.get("caption_full") or p.get("caption") or p.get("hashtags"),
                              fmt=p.get("format"), url=p.get("url"), drive=p.get("drive") or doc.get("drive_root"),
                              file=f"{'/'.join(P.ORGANIC_POOL)}/{name}/posts/{stem}.md" if stem else ""))
    return out


# ------------------------------------------------------------------- all

def found():
    """Is each pool there, and does it hold anything readable? For the inputs gate."""
    paid, org = P.paid_pool(), P.organic_pool()
    return {"paid": {"path": _rel(paid), "there": paid.is_dir(),
                     "files": len(list(paid.glob("*/blocks.json"))) if paid.is_dir() else 0},
            "own": {"path": _rel(paid / "own"), "there": (paid / "own").is_dir(),
                    "files": len(list(paid.glob("own/*/ads.json"))) if paid.is_dir() else 0},
            "organic": {"path": _rel(org), "there": org.is_dir(),
                        "files": (len(list(org.glob("records/avatar-feeds/*/items.json")))
                                  + len(list(org.glob("*/posts.json")))) if org.is_dir() else 0}}


def read_all():
    out, seen = [], set()
    for r in read_paid() + read_own() + read_organic():
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        out.append(r)
    return out


def matches(r, brand, source=None, kind=None):
    if r["swiped_for"] not in (brand, SHARED):
        return False
    if source and source not in (r["source"], r["owner"]):
        return False
    if kind and r["kind"] != kind:
        return False
    return True
