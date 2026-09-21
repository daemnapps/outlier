#!/usr/bin/env python3
"""The simple email: the copy machine's words in one fixed shape, pictures
made by GPT, and — on --push — a DRAFT campaign in the brand's Klaviyo.

    python3 simple_email.py <run>  --brand <brand>            # pictures + the email
    python3 simple_email.py <run>  --brand <brand> --push     # ...and a Klaviyo draft
    python3 simple_email.py <run>  --brand <brand> --no-images   # layout only, no spend

Damon, 2026-09-19: "we're just going to focus on not doing fully design-based
email templates and just using what we had before as our baseline… the logo at
the top, headline for the email, an image that describes the headline with
relevance, the copy. If another image needs to go in there, towards the
bottom, it can. Maybe there's an offer… and then you just put a button in."

WHERE EACH PART COMES FROM
- the words: stage 8 of the email chain writes them into this shape, as a
  fenced `EMAIL` block (prompts/stage8-build-v2-damon.md)
- the look: `brands/<brand>/email/simple.json`, read off the brand's own last
  sent email — this engine names no brand, colour or font
- the pictures: GPT Image through the video machine's direct OpenAI door, the
  model named in its providers registry; the offer picture is made FROM the
  real product photo when the brand has one on file
- the send: a Klaviyo DRAFT. This tool has no send call and never will —
  scheduling is a person's act, in Klaviyo.

WHERE IT FILES (runs/README.md, 2026-09-17)
- the email and its record: runs/email-production/<brand>/<label>/deliverable/
- the pictures (media): Shared Assets/runs/email-production/<brand>/<label>/
"""
import argparse
import datetime
import html
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from paths import HERE, WORKSPACE, calendar_tool, component, lab_tool

# This folder's own email.py shadows Python's `email` package, which the
# picture door needs (urllib -> http.client -> email.parser). Nothing below
# imports from this folder again, so take it off the path.
sys.path = [p for p in sys.path if Path(p or ".").resolve() != HERE]
sys.path.insert(0, str(Path.home() / ".daemn"))
# The checks and the hold are the shared ones (components/quality-checks); the
# layout is asked of the element library (components/elements, template/email).
sys.path.insert(0, str(component("quality-checks")))
sys.path.insert(0, str(HERE / "machine"))
import quality_checks as Q                                  # noqa: E402
import email_elements as EE                                 # noqa: E402

MACHINE = "email-production"
LAYOUT = "simple"                       # the one email template (template/email in the element library)
DRIVE_RUNS = (Path.home() / "Library/CloudStorage/GoogleDrive-${DRIVE_ACCOUNT}"
              / "Shared drives/Shared Assets/runs")
KLAVIYO = "https://a.klaviyo.com/api"
REVISION = "2025-07-15"
# The picture model is the registry's; only the frame changes. The video
# machine's default is a tall 9:16 frame at its top quality — an email hero is
# wide, and a month of heroes at the top tier is spend nobody sees at 600px.
EMAIL_IMAGE = {"size": "1536x1024", "quality": "high"}


# --------------------------------------------------------------------- read

def the_email(run_dir):
    text = (run_dir / "stage8--blocks.md").read_text()
    m = re.search(r"```EMAIL\s*\n(.*?)```", text, re.S)
    if not m:
        sys.exit(f"{run_dir.name}: stage 8 wrote no EMAIL block — this run was built "
                 "in the old block layout. Rebuild it:  python3 email.py <source> … "
                 "--rerun-from stage8")
    try:
        return json.loads(m.group(1))
    except ValueError as e:
        sys.exit(f"{run_dir.name}: the EMAIL block is not valid JSON ({e})")


def look(brand):
    f = WORKSPACE / "brands" / brand / "email" / "simple.json"
    if not f.is_file():
        sys.exit(f"no brands/{brand}/email/simple.json — the brand's look for the "
                 "simple email is not on file yet")
    return json.loads(f.read_text())


def product_photo(brand, key):
    """The real product photo, when the brand keeps one — as a file per
    product under products/<key>/images/, or named by key in products/images/."""
    if not key:
        return None
    root = WORKSPACE / "brands" / brand / "products"
    pics = [p for p in (root / key / "images").glob("*")
            if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
    pics += [p for p in (root / "images").glob(f"{key}*")
             if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
    rank = ("packshot", "cutout", "-00", "hero")
    pics.sort(key=lambda p: next((i for i, r in enumerate(rank) if r in p.name), 9))
    return pics[0] if pics else None


# ----------------------------------------------------------------- pictures

def openai_door():
    f = lab_tool("ai-video-production", "machine", "direct_openai.py")
    spec = importlib.util.spec_from_file_location("direct_openai", f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    base = mod.cfg()
    mod.cfg = lambda: {**base, "params": {**(base.get("params") or {}), **EMAIL_IMAGE}}
    return mod


def make_pictures(email, brand, media_dir):
    door = openai_door()
    media_dir.mkdir(parents=True, exist_ok=True)
    made = {}
    jobs = [("hero", email.get("hero"), None)]
    offer_img = (email.get("offer") or {}).get("image")
    if offer_img:
        jobs.append(("offer", offer_img, product_photo(brand, offer_img.get("product"))))
    for name, spec, ref in jobs:
        if not spec or not spec.get("prompt"):
            continue
        out = media_dir / f"{name}.png"
        prompt = (spec["prompt"] + "\n\nA wide photograph for the top of an email. "
                  "No words, letters, numbers or logos anywhere in the image.")
        if ref:
            prompt += ("\n\nThe product in the reference image must appear exactly as "
                       "it is — same pack, same colours, same label. Do not redraw it.")
        print(f"  picture: {name}" + (f" (from {ref.name})" if ref else "") + " …")
        door.generate(prompt, [ref] if ref else [], out)
        made[name] = web_copy(out)
    return made


def web_copy(png):
    """The picture as the email carries it: 1200px wide (2x a 600px email),
    JPEG. A 3MB PNG at the top of an email is a slow first screen on a phone."""
    jpg = png.with_suffix(".jpg")
    if not jpg.is_file() or jpg.stat().st_mtime < png.stat().st_mtime:
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82",
                        "--resampleWidth", "1200", str(png), "--out", str(jpg)],
                       capture_output=True, check=True)
    return jpg


def inline(path):
    """A picture inside the preview itself, so the page opens anywhere."""
    import base64
    return "data:image/jpeg;base64," + base64.b64encode(Path(path).read_bytes()).decode()


# ------------------------------------------------------------------- render

def para(text):
    t = html.escape(text.strip())
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return t.replace("\n", "<br>")


def render(email, lk, pictures, logo_src):
    c, f = lk["colors"], lk["fonts"]
    body = f"font-family:{f['body']};font-size:{lk.get('body_size', 16)}px;line-height:1.5;color:{c['text']};"

    def img(src, alt):
        return (f'<tr><td style="padding:0 0 24px 0;"><img src="{src}" alt="{html.escape(alt or "")}" '
                f'width="600" style="display:block;width:100%;max-width:600px;height:auto;border:0;"></td></tr>')

    rows = [f'<tr><td align="center" style="padding:24px 0;"><a href="{lk["logo"].get("link", "#")}">'
            f'<img src="{logo_src}" alt="{html.escape(lk["logo"]["alt"])}" width="{lk["logo"]["width"]}" '
            f'style="display:block;width:{lk["logo"]["width"]}px;height:auto;border:0;"></a></td></tr>']
    rows.append(f'<tr><td style="padding:0 32px 20px 32px;font-family:{f["headline"]};'
                f'font-size:{lk.get("headline_size", 24)}px;line-height:1.15;color:{c["text"]};">'
                f'{para(email["headline"])}</td></tr>')
    if pictures.get("hero"):
        rows.append(img(pictures["hero"], email["hero"].get("alt")))
    copy = []
    if lk.get("greeting"):
        copy.append(f'<p style="margin:0 0 16px 0;">{lk["greeting"]}</p>')
    copy += [f'<p style="margin:0 0 16px 0;">{para(p)}</p>' for p in email.get("body", []) if p.strip()]
    rows.append(f'<tr><td style="padding:0 32px 8px 32px;{body}">{"".join(copy)}</td></tr>')
    offer = email.get("offer")
    if offer:
        if pictures.get("offer"):
            rows.append(img(pictures["offer"], (offer.get("image") or {}).get("alt")))
        rows.append(f'<tr><td style="padding:0 32px 8px 32px;{body}font-weight:600;">'
                    f'{para(offer["line"])}</td></tr>')
    b = email["button"]
    rows.append(f'<tr><td align="center" style="padding:16px 32px 32px 32px;">'
                f'<a href="{html.escape(b["link"])}" style="display:inline-block;background:{c["button"]};'
                f'color:{c["button_text"]};font-family:{f["body"]};font-size:16px;text-decoration:none;'
                f'padding:15px 28px;border-radius:{lk.get("button_radius", 4)}px;">{html.escape(b["label"])}</a></td></tr>')
    if lk.get("signoff"):
        rows.append(f'<tr><td style="padding:0 32px 32px 32px;{body}">'
                    + "<br>".join(html.escape(s) for s in lk["signoff"]) + "</td></tr>")
    foot = f"font-family:{f['body']};font-size:12px;line-height:1.6;color:{c['muted']};"
    rows.append(f'<tr><td align="center" style="padding:24px 32px;{foot}">'
                + (f"{html.escape(lk['tagline'])}<br><br>" if lk.get("tagline") else "")
                + 'No longer find value in our emails? <a href="{% unsubscribe_url %}" '
                  f'style="color:{c["muted"]};">Unsubscribe</a><br>'
                  "{{ organization.name }} · {{ organization.full_address }}</td></tr>")
    return (f'<!DOCTYPE html><html><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"></head>'
            f'<body style="margin:0;padding:0;background:{c["page"]};">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'style="background:{c["page"]};"><tr><td align="center" style="padding:24px 8px;">'
            f'<table role="presentation" width="600" cellpadding="0" cellspacing="0" '
            f'style="width:100%;max-width:600px;background:{c["card"]};">'
            + "".join(rows) + "</table></td></tr></table></body></html>\n")


# ---------------------------------------------------------------- the check

def finished_text(email, with_link=False):
    """The words a reader will see, in one string."""
    parts = [email.get("headline", ""), *email.get("body", []),
             (email.get("offer") or {}).get("line", ""),
             (email.get("button") or {}).get("label", "")]
    if with_link:
        parts.append((email.get("button") or {}).get("link", ""))
    return " ".join(parts)


def price_check(email, brand, run_dir):
    """EVERY PRICE IN THE EMAIL IS ONE THE BANK SELLS TODAY (2026-09-19).

    The first email through this tool sold two of a set at a real price for a
    size the store had switched off and then removed. The product file lists
    every size ever made; the offer bank lists only what is live. The writer
    took the number from the product file and then told us, in its own notes,
    it was "verbatim from the offer bank". A prompt saying "prices verbatim
    from the bank" is a request; this is the check. A price that is not in the
    send's own offer block does not reach Klaviyo.

    The check itself is the shared one (components/quality-checks, 2026-09-20,
    which was lifted from here); this finds the send's offer and its bank entry.
    """
    try:
        offer = json.loads((run_dir / "run.json").read_text()).get("assignment", {}).get("offer")
    except (OSError, ValueError):
        offer = None
    text = finished_text(email)
    if not Q.prices_in(text):
        return []
    if not offer or offer == "none":
        return Q.price_check(text, "", None)
    bank = (WORKSPACE / "brands" / brand / "offers" / "offer-bank.md").read_text()
    block = Q.offer_block(bank, offer)
    if not block:
        # an offer the bank does not hold sells no price at all — every price fails
        block = f"## {offer} — (not in the offer bank)"
    return Q.price_check(text, block, offer)


def delivery_problems(email, brand, run_dir):
    """Everything that holds an email back from Klaviyo: prices, the chain's
    own check step (8c — product facts, chopped thoughts, typos), unfilled
    notes. All three are the shared checks; the gate is `delivery`."""
    problems = price_check(email, brand, run_dir)
    chk = run_dir / "stage8c--check.md"
    if chk.is_file():
        problems += [p + " — look at stage8c--check.md" if "check step's answer" in p else p
                     for p in Q.read_check_block(chk.read_text())]
    else:
        problems.append("this email was never checked (no step 8c) — rerun it from stage8")
    # A hole the writer marked is honest in the working copy and a defect in
    # the finished email: the first rewrite with customer language shipped a
    # "[UNFILLED: the handoff…]" note inside the body (2026-09-19).
    problems += Q.unfilled_check(finished_text(email, with_link=True))
    # A PARTNER'S PRODUCT is checked against the partner's own roster entry
    # (2026-09-21): their real link is present, no link nobody put on the
    # roster, and no earnings claim on a traffic-only arrangement. The run
    # names the partner; the roster is the only thing that describes them.
    run = json.loads((run_dir / "run.json").read_text())
    key = (run.get("assignment") or {}).get("affiliate")
    if key:
        brand_root = WORKSPACE / "brands" / brand
        partner = Q.partner_on_file(brand_root, key)
        if not partner:
            problems.append(f"this send features partner `{key}`, who is not active on "
                            f"{brand}'s roster — nothing is invented in their place")
        else:
            problems += Q.partner_check(finished_text(email, with_link=True),
                                        partner, own_domains=own_domains(brand))
    return problems


def own_domains(brand):
    """Our own web addresses, read off the brand's own files — never typed here."""
    import re as _re
    out = set()
    for rel in ("email/machine.json", "email/simple.json"):
        f = WORKSPACE / "brands" / brand / rel
        if f.is_file():
            for u in _re.findall(r"https?://([^/\s\"']+)", f.read_text()):
                out.add(u.lower())
    return out


# ------------------------------------------------------------------ klaviyo

def kl_key(lk):
    import daemn_keys
    k = daemn_keys.key(lk.get("klaviyo_key") or "")
    if not k:
        sys.exit(f"no {lk.get('klaviyo_key')} in the Keychain — this brand's Klaviyo is not "
                 "connected, so the email is built but not pushed")
    return k


def kl(method, path, key, payload=None, form=None):
    cmd = ["curl", "-sS", "-g", "--max-time", "120", "-X", method,
           "-H", f"Authorization: Klaviyo-API-Key {key}", "-H", f"revision: {REVISION}",
           "-H", "accept: application/vnd.api+json"]
    if form:
        for k2, v in form.items():
            cmd += ["-F", f"{k2}={v}"]
    elif payload is not None:
        cmd += ["-H", "Content-Type: application/vnd.api+json", "-d", json.dumps(payload)]
    r = subprocess.run(cmd + [f"{KLAVIYO}/{path}"], capture_output=True, text=True)
    out = json.loads(r.stdout) if r.stdout.strip() else {}
    if "errors" in out:
        e = out["errors"][0]
        sys.exit(f"Klaviyo refused {path}: {e.get('status')} {e.get('detail', e)}"[:400])
    return out


def upload(key, path, name):
    out = kl("POST", "image-upload", key, form={"file": f"@{path}", "name": name})
    return out["data"]["attributes"]["image_url"]


def the_slot(brand, label):
    """The calendar's send this email was written for — its segment decides
    who the draft goes to. Never guessed: no slot, no push."""
    sid = re.sub(r"--.*$", "", label)
    sid = sid[len(brand) + 1:] if sid.startswith(brand + "-") else sid
    runs = calendar_tool("runs")
    for d in sorted(runs.glob("calendar-*"), reverse=True):
        try:
            if json.loads((d / "run.json").read_text()).get("brand") != brand:
                continue
            for s in json.loads((d / "slots.json").read_text()):
                if s.get("id") == sid:
                    return s
        except (OSError, ValueError):
            continue
    return None


def send_strategy(lk, slot):
    """The calendar's day, at the brand's send hour, in EACH RECIPIENT'S OWN
    time zone (Damon, 2026-09-19: "scheduling the emails for recipient time
    zone based off of our data"). The hour is the brand's, read from its
    simple.json with the evidence beside it. Setting the time is not
    scheduling: the draft carries it, and a person still presses Schedule."""
    st = lk.get("send_time") or {}
    if not st.get("local") or not slot.get("date"):
        sys.exit("no send time — add send_time.local to the brand's simple.json")
    # the API revision in use (2025-07-15) takes `datetime` + `options` on the
    # strategy itself; the older `options_static` shape is refused
    return {"method": "static",
            "datetime": f"{slot['date']}T{st['local']}:00+00:00",
            "options": {"is_local": bool(st.get("recipient_time_zone", True)),
                        "send_past_recipients_immediately": False}}


def push(email, lk, brand, label, pictures, pick, out_dir):
    key = kl_key(lk)
    slot = the_slot(brand, label)
    if not slot:
        sys.exit(f"no calendar send named {label} for {brand} — the audience comes from "
                 "the plan, never guessed")
    matrix = json.loads((WORKSPACE / "brands" / brand / "email/audience-matrix.json").read_text())
    ids = {s["name"]: s.get("id") for s in matrix["segments"]}
    names = slot.get("segments") or [slot["segment"]]
    seg = [ids.get(n) for n in names]
    if not all(seg):
        sys.exit(f"segment(s) {names} have no Klaviyo id in the audience matrix")

    cache = out_dir / "hosted.json"
    hosted = json.loads(cache.read_text()) if cache.is_file() else {}
    for n, p in pictures.items():
        if n not in hosted:
            hosted[n] = upload(key, p, f"{brand}-{label}-{n}")
    cache.write_text(json.dumps(hosted, indent=1) + "\n")
    logo = lk["logo"].get("url") or upload(key, WORKSPACE / "brands" / brand / lk["logo"]["file"],
                                           f"{brand}-logo")
    doc = render(email, lk, hosted, logo)
    (out_dir / "email.html").write_text(doc)

    subs = email.get("subjects") or []
    if pick >= len(subs):
        sys.exit(f"pick {pick} not in the subject set (0..{len(subs) - 1})")
    subject, preview = subs[pick]["subject"], subs[pick].get("preview", "")
    frm = lk.get("from") or {}
    if not frm.get("email"):
        sys.exit("no from-address in simple.json — fill it in before pushing")

    tpl = kl("POST", "templates", key, {"data": {"type": "template", "attributes": {
        "name": f"{brand} · {label} · simple", "editor_type": "CODE", "html": doc}}})
    camp = kl("POST", "campaigns", key, {"data": {"type": "campaign", "attributes": {
        "name": f"[DRAFT] {slot.get('date')} · {label} · {slot.get('type')}",
        "audiences": {"included": seg, "excluded": []},
        "send_strategy": send_strategy(lk, slot),
        "campaign-messages": {"data": [{"type": "campaign-message", "attributes": {
            "definition": {"channel": "email", "label": label, "content": {
                "subject": subject, "preview_text": preview,
                "from_email": frm["email"], "from_label": frm.get("label") or brand}}}}]}}}})
    camp_id = camp["data"]["id"]
    msg_id = camp["data"]["relationships"]["campaign-messages"]["data"][0]["id"]
    kl("POST", "campaign-message-assign-template", key, {"data": {
        "type": "campaign-message", "id": msg_id,
        "relationships": {"template": {"data": {"type": "template", "id": tpl["data"]["id"]}}}}})
    rec = {"campaign_id": camp_id, "template_id": tpl["data"]["id"], "subject": subject,
           "preview": preview, "segments": names, "send_date": slot.get("date"),
           "send_time": (lk.get("send_time") or {}).get("local"), "recipient_time_zone": True,
           "pushed_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "status": "DRAFT — schedule it in Klaviyo yourself"}
    (out_dir / "pushed.json").write_text(json.dumps(rec, indent=1) + "\n")
    return rec


# --------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("run_dir")
    ap.add_argument("--brand", required=True)
    ap.add_argument("--no-images", action="store_true", help="lay it out without making pictures")
    ap.add_argument("--push", action="store_true", help="create a Klaviyo DRAFT")
    ap.add_argument("--pick", type=int, default=0, help="subject pair (0 = the control)")
    a = ap.parse_args()
    run_dir = Path(a.run_dir).resolve()
    label = run_dir.name
    # THE ELEMENTS GATE: the layout is a real template, or nothing is built
    try:
        EE.layout(LAYOUT)
    except EE.Unknown as e:
        sys.exit(f"HELD at the elements gate — {e.args[0]}")
    email, lk = the_email(run_dir), look(a.brand)

    out_dir = WORKSPACE / "runs" / MACHINE / a.brand / label / "deliverable"
    media = DRIVE_RUNS / MACHINE / a.brand / label
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "email.json").write_text(json.dumps(email, indent=1, ensure_ascii=False) + "\n")

    pictures = {}
    if not a.no_images:
        have = {n: web_copy(media / f"{n}.png") for n in ("hero", "offer")
                if (media / f"{n}.png").is_file()}
        pictures = have or make_pictures(email, a.brand, media)
    if lk["logo"].get("url"):
        logo = lk["logo"]["url"]
    else:
        import base64
        lf = WORKSPACE / "brands" / a.brand / lk["logo"]["file"]
        logo = f"data:image/{lf.suffix.lstrip('.')};base64," + base64.b64encode(lf.read_bytes()).decode()
    preview = render(email, lk, {n: inline(p) for n, p in pictures.items()}, logo)
    (out_dir / "preview.html").write_text(preview)
    print(f"email: {out_dir / 'preview.html'}")
    # which elements this email was built from, kept in the run's own record
    rj = run_dir / "run.json"
    if rj.is_file():
        try:
            state = json.loads(rj.read_text())
            picked = dict(state.get("elements") or {})
            picked["template/email"] = {"id": LAYOUT, "from": "library"}
            if picked != state.get("elements"):
                state["elements"] = picked
                rj.write_text(json.dumps(state, indent=2) + "\n")
        except ValueError:
            pass
    # THE DELIVERY GATE. check.json is the shared, gate-keyed shape
    # ({"delivery": {"result", "problems"}}); the old {"prices": "FAIL"} shape
    # blamed prices for every kind of failure.
    cj = out_dir / "check.json"
    if cj.is_file():
        try:
            old = json.loads(cj.read_text())
        except ValueError:
            old = {}
        kept = {k: v for k, v in old.items() if k in {g[0] for g in Q.GATES}}
        if kept != old:
            cj.write_text(json.dumps(kept, indent=1, ensure_ascii=False) + "\n")
    try:
        Q.hold("delivery", delivery_problems(email, a.brand, run_dir), out_dir)
    except Q.Held as held:
        sys.exit("HELD — not sent to Klaviyo:\n  " + "\n  ".join(held.problems))
    if a.push:
        rec = push(email, lk, a.brand, label, pictures, a.pick, out_dir)
        print(f"Klaviyo DRAFT {rec['campaign_id']} · “{rec['subject']}” · "
              f"{', '.join(rec['segments'])} · set for {rec['send_date']} {rec['send_time']} "
              "recipient time — press Schedule in Klaviyo")


if __name__ == "__main__":
    main()
