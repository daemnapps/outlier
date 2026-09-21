# MASTER: Board Page Template

The one artifact every board page is cloned from. Build this ONCE per brand against the newest board, verify it renders, then clone it for every other board with find-and-replace (see `workflow-a`, step 6).

Written as a Design Component (`.dc.html`) via `dc_write`. Two parts: template and logic class.

---

## Template (`b_dc_html`)

```html
<helmet>
<meta name="design_doc_mode" content="canvas">
<link rel="stylesheet" href="boards/<SLUG>/fig-assets.css">
<link rel="stylesheet" href="fonts.css">
<style>
  body { margin: 0; background: <BOARD_BG>; }
  a { color: <ACCENT>; } a:hover { color: <CREAM>; }
</style>
</helmet>
<div style="font-family: '<SANS>', -apple-system, 'Helvetica Neue', Arial, sans-serif; color: <CREAM>; padding: 60px 80px 120px;">
  <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 48px;">
    <div style="font-size: 14px; letter-spacing: 0.12em; text-transform: uppercase; color: <ACCENT>;"><BRAND> email format bank</div>
    <div style="font-family: '<SERIF>', Georgia, serif; font-size: 56px; line-height: 1;"><BOARD TITLE></div>
    <div style="font-size: 18px; color: rgba(<CREAM_RGB>,0.6);">Approved emails, <WIDTH>px artboards, verbatim from Figma. Codes: <CODE>-xx.</div>
  </div>
  <div style="{{ cropStyle }}" data-screen-label="<BOARD TITLE> board" ref="{{ boardRef }}">
    <x-import component-from-global-scope="<GLOBAL>" from="./boards/<SLUG>/Components.bundle.js" style="{{ innerStyle }}" hint-size="100%,3000px"></x-import>
    <sc-for list="{{ badges }}" as="b" hint-placeholder-count="0">
      <div style="{{ b.style }}">{{ b.label }}</div>
    </sc-for>
  </div>
</div>
```

`cropStyle` / `innerStyle` / `badges` are the only holes — they are genuine runtime values (measured after the bundle mounts), which is the sanctioned use of a style hole.

---

## Logic class (`c_dc_js`)

```js
class Component extends DCLogic {
  state = { bbox: null, badges: [] };
  CODE = "<CODE>";

  componentDidMount() { this.tries = 0; this.timer = setInterval(() => this.scan(), 400); }
  componentWillUnmount() { clearInterval(this.timer); }

  // ---- placeholders for images that could not be recovered ----
  markPlaceholders(root) {
    const frames = this.emailFrames || [];
    Array.from(root.querySelectorAll("div")).forEach(d => {
      if (d.__ph || d.childElementCount || (d.textContent || "").trim()) return;
      const r = d.getBoundingClientRect();
      if (r.width < 90 || r.height < 90) return;
      const cs = getComputedStyle(d);
      if (cs.backgroundImage !== "none") return;
      const bc = cs.backgroundColor;
      if (bc !== "rgba(0, 0, 0, 0)" && bc !== "transparent") return;
      if (frames.length && !frames.some(f => f.contains(d))) return;
      d.__ph = true;
      d.style.background = "repeating-linear-gradient(45deg, rgba(<ACCENT_RGB>,0.07) 0 12px, rgba(<ACCENT_RGB>,0.15) 12px 24px)";
      d.style.boxShadow = "inset 0 0 0 2px rgba(<ACCENT_RGB>,0.55)";
      if (cs.position === "static") d.style.position = "relative";
      const tag = document.createElement("div");
      tag.textContent = "IMAGE " + Math.round(r.width) + "\u00d7" + Math.round(r.height);
      tag.style.cssText = "position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);background:rgba(<INK_RGB>,0.78);color:rgb(<ACCENT_RGB>);font:500 15px/1 '<SANS>',Arial,sans-serif;letter-spacing:0.08em;padding:8px 12px;white-space:nowrap;pointer-events:none;z-index:3;";
      d.appendChild(tag);
    });
  }

  // ---- restore images the extractor dropped (see workflow-c) ----
  applyPatch(root) {
    if (this.patched || !root) return;
    this.patched = true;
    fetch("boards/<SLUG>/patch.json").then(r => r.json()).then(pj => {
      const entries = pj.geo || [];
      if (!entries.length) return;
      const divs = Array.from(root.querySelectorAll("div"));
      const used = new Set();
      for (const e of entries) {
        const ms = divs.filter(d => {
          if (used.has(d)) return false;
          const r = d.getBoundingClientRect();
          return Math.abs(r.width - e.w) < 2 && Math.abs(r.height - e.h) < 2 && getComputedStyle(d).backgroundImage === "none";
        });
        const el = ms[e.nth || 0];
        if (el) { used.add(el); el.style.background = e.bg.split("./assets/").join("boards/<SLUG>/assets/"); }
      }
    }).catch(() => {}).finally(() => { setTimeout(() => this.markPlaceholders(root), 300); });
  }

  scan() {
    const root = this.board;
    if (root) {
      const nodes = Array.from(root.querySelectorAll("div"));
      // GEOMETRY + COMPUTED STYLE, never data-name, never a hardcoded width
      let frames = nodes.filter(n => {
        if (n.offsetWidth < 550 || n.offsetWidth > 820 || n.offsetHeight < 500 || n.offsetHeight > 6500) return false;
        const cs = getComputedStyle(n);
        return cs.overflow === "hidden" && cs.borderRadius !== "50%" && !cs.borderRadius.endsWith("%");
      });
      frames = frames.filter(f => !frames.some(g => g !== f && g.contains(f)));
      if (frames.length) {
        clearInterval(this.timer);
        this.emailFrames = frames;
        this.applyPatch(root);
        const base = root.getBoundingClientRect();
        const rects = frames.map(f => {
          const r = f.getBoundingClientRect();
          return { x: r.left - base.left, y: r.top - base.top, w: r.width, h: r.height };
        });
        rects.sort((a, b) => (a.y - b.y > 400 ? 1 : b.y - a.y > 400 ? -1 : a.x - b.x));
        const minX = Math.min(...rects.map(r => r.x)), minY = Math.min(...rects.map(r => r.y));
        const maxX = Math.max(...rects.map(r => r.x + r.w)), maxY = Math.max(...rects.map(r => r.y + r.h));
        const padTop = 180, pad = 100;
        const badges = rects.map((r, i) => ({
          label: this.CODE + "-" + String(i + 1).padStart(2, "0"),
          style: { position: "absolute", zIndex: 5, left: (r.x - (minX - pad)) + "px", top: (r.y - (minY - padTop) - 56) + "px", background: "rgb(<ACCENT_RGB>)", color: "rgb(<INK_RGB>)", fontWeight: 500, fontSize: "18px", padding: "10px 16px", letterSpacing: "0.04em", whiteSpace: "nowrap" }
        }));
        this.setState({ bbox: { x: minX - pad, y: minY - padTop, w: maxX - minX + 2 * pad, h: maxY - minY + padTop + pad }, badges });
        return;
      }
    }
    // fallback: never show dead space — crop to all sizable content
    if (++this.tries > 50) {
      clearInterval(this.timer);
      this.applyPatch(root);
      if (root) {
        const all = Array.from(root.querySelectorAll("div")).filter(n => n.offsetWidth > 100 && n.offsetHeight > 100);
        if (all.length) {
          const base = root.getBoundingClientRect();
          const rs = all.map(f => f.getBoundingClientRect());
          const minX = Math.min(...rs.map(r => r.left - base.left)), minY = Math.min(...rs.map(r => r.top - base.top));
          const maxX = Math.max(...rs.map(r => r.right - base.left)), maxY = Math.max(...rs.map(r => r.bottom - base.top));
          this.setState({ bbox: { x: minX - 100, y: minY - 100, w: maxX - minX + 200, h: maxY - minY + 200 }, badges: [] });
        }
      }
    }
  }

  renderVals() {
    const b = this.state.bbox;
    return {
      boardRef: el => { this.board = el; },
      badges: this.state.badges,
      cropStyle: b ? { position: "relative", overflow: "hidden", width: b.w + "px", height: b.h + "px" }
                   : { position: "relative", overflow: "hidden", width: "100%", height: "3000px" },
      innerStyle: b ? { position: "absolute", left: -b.x + "px", top: -b.y + "px" }
                    : { position: "absolute", left: "0px", top: "0px" }
    };
  }
}
```

---

## Substitution table (what the clone script replaces)

| Token | Source |
|---|---|
| `<SLUG>` | board dir name, e.g. `jan-2026` |
| `<GLOBAL>` | global name from that board's `Components.d.ts` |
| `<BOARD TITLE>` | human board name, e.g. `January 2026 - Campaign` |
| `<CODE>` | board code prefix, e.g. `JAN26` |
| `<WIDTH>` | artboard width observed in that board |
| brand tokens | `<INK>`, `<CREAM>`, `<ACCENT>`, `<SERIF>`, `<SANS>` from METADATA + stage-1 read |

Filenames cannot contain em dashes — use hyphens.
