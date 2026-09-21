"""What this tool needs to know about a brand, read from the brand's own files
at run time — so no brand's name, products or page furniture is typed into
the code (rollout, 2026-09-20).

    import brand_facts as BF
    BF.run_brand(run_dir)            # the brand a run was made for, or an error naming run.json
    BF.runs_of(brand, results_dir)   # that brand's runs only — by each run's own run.json
    BF.furniture(brand)              # the brand's page-furniture words (email/simple.json)
    BF.vocab(brand)                  # furniture alt texts + furniture lines, brand words included
    BF.product_names(brand)          # what the brand sells, by name (products/store.json + files)
    BF.machine(brand)                # brands/<brand>/email/machine.json

WHY. The old-email source problem (seen live, 2026-09-20): the writer copied a
source email's nav and footer words into the new email's body. The words that
are furniture differ per brand, so they live with the brand:
`brands/<brand>/email/simple.json` → `"furniture": [...]`.
"""
import json
import re
import sys
from pathlib import Path

if "paths" not in sys.modules:             # a caller may have taken this folder OFF the path on purpose
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # (its email.py shadows Python's `email`)
from paths import WORKSPACE                                   # noqa: E402

# Furniture every brand's email carries — no brand's words here.
GENERIC_ALTS = {"shop", "facebook", "instagram", "tiktok", "youtube"}
PLATFORMS = ("facebook", "instagram", "tiktok", "youtube")


def _root(brand, workspace=None):
    return Path(workspace or WORKSPACE) / "brands" / brand


def _json(path, default):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def run_brand(run_dir, given=None):
    """The brand a run belongs to. `--brand` wins; otherwise the run's own
    run.json must say. There is no default brand — a run.json without one is
    an error that names the file."""
    if given:
        return given
    f = Path(run_dir) / "run.json"
    brand = _json(f, {}).get("brand")
    if not brand:
        sys.exit(f"no brand: {f} does not name one — pass --brand, there is no default brand")
    return brand


def runs_of(brand, results_dir, month_abbr=None, need="design.json"):
    """This brand's run folders under `results_dir` — decided by each run's own
    run.json, never by a folder-name prefix (a prefix rule silently drops a
    brand). A run whose run.json names no brand is skipped, and said so."""
    out = []
    for p in sorted(Path(results_dir).glob("*")):
        if not p.is_dir() or (need and not (p / need).is_file()):
            continue
        b = _json(p / "run.json", {}).get("brand")
        if not b:
            print(f"  skipped {p.name}: its run.json names no brand", file=sys.stderr)
            continue
        if b != brand:
            continue
        bare = p.name[len(brand) + 1:] if p.name.startswith(brand + "-") else p.name
        if month_abbr and not bare.startswith(month_abbr + "-"):
            continue
        out.append(p)
    return out


def month_abbr(month):
    """'2026-09' → 'sep' — how a month's runs are named."""
    names = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")
    return names[int(str(month).split("-")[1]) - 1]


def look(brand, workspace=None):
    return _json(_root(brand, workspace) / "email" / "simple.json", {})


def machine(brand, workspace=None):
    f = _root(brand, workspace) / "email" / "machine.json"
    d = _json(f, None)
    if d is None:
        sys.exit(f"no {f} — this brand's plumbing facts are not on file")
    return d


def furniture(brand, workspace=None):
    """The brand's own furniture words, lowercased. Optional: a brand with none
    on file has none."""
    return [str(w).strip().lower() for w in (look(brand, workspace).get("furniture") or []) if str(w).strip()]


def vocab(brand, workspace=None):
    """{"alts": exact alt texts that are furniture, "lines": text that marks a
    furniture line, "signers": first names a '- Name' sign-off line opens with}."""
    lk = look(brand, workspace)
    names = {brand.lower()}
    alt = ((lk.get("logo") or {}).get("alt") or "").strip().lower()
    if alt:
        names.add(alt)
    alts = set(GENERIC_ALTS) | names | set(furniture(brand, workspace))
    alts |= {f"{n} on {p}" for n in names for p in PLATFORMS}
    lines = []
    for seg in re.split(r"[.—–|·]", lk.get("tagline") or ""):
        seg = re.sub(r"[™®]", "", seg).strip().lower()
        if len(seg.split()) >= 2:
            lines.append(seg)
    signers = []
    for s in lk.get("signoff") or []:
        s = re.sub(r"[™®]", "", str(s)).strip()
        if s:
            lines.append(s.lower().rstrip(","))
            if not s.endswith(","):
                signers.append(s.split()[0].lower())
    return {"alts": alts, "lines": lines, "names": names, "signers": signers}


def is_furniture_alt(alt, v):
    return (alt or "").strip().lower() in v["alts"]


def is_furniture_line(text, v):
    s = re.sub(r"[™®]", "", (text or "")).strip().lower()
    bare = re.sub(r"\W+$", "", s)
    if bare in v["names"]:
        return True
    if any(seg and seg in s for seg in v["lines"]):
        return True
    m = re.match(r"^[-–—]\s*(\w+)", s)
    return bool(m and m.group(1) in v["signers"])


def product_names(brand, workspace=None):
    """What the brand sells, by name: store.json titles and handles, plus the
    product files' own names. Longest first, so a set matches before its part."""
    root = _root(brand, workspace) / "products"
    names = set()
    for p in _json(root / "store.json", {}).get("products", []):
        for k in ("title", "handle"):
            v = (p.get(k) or "").strip()
            if v:
                names.add(v.lower())
                names.add(v.lower().replace("-", " "))
    if root.is_dir():
        for f in root.iterdir():
            if f.suffix == ".md" and f.stem.lower() not in ("readme",):
                names.add(f.stem.lower().replace("-", " "))
            elif f.is_dir() and (f / "product.md").is_file():
                names.add(f.name.lower().replace("-", " "))
    clean = {re.sub(r"[™®]", "", n).strip() for n in names}
    return sorted({n for n in names | clean if n}, key=len, reverse=True)


def product_only(brand, workspace=None):
    """A picture direction that is just a named product on its own."""
    names = product_names(brand, workspace)
    if not names:
        return re.compile(r"(?!x)x")                          # matches nothing
    alt = "|".join(re.escape(n) for n in names)
    return re.compile(rf"^(image of |the |a )?({alt})[\s\w™'.,-]*$", re.I)
