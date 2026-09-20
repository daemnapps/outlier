/* ═══════════════════════════════════════════════════════════════
   PORTAL · GAME — the player, second cut.

   A first-person mission on a phone. You look around a wide plate,
   walk to the yellow marker, people talk to you in subtitles, you
   pick from a wheel, hold to do a thing, pick an item up, and the
   mission ends on the screen everybody knows. Every pick is a thing
   the store learns; the exit link carries it.

   Reads window.PORTAL_WORLD (see worlds/_TEMPLATE/world.js).
   No build, no framework, runs from file://.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  const W = window.PORTAL_WORLD;
  if (!W) { document.body.textContent = 'No world loaded.'; return; }
  const stage = document.getElementById('stage');
  const q = new URLSearchParams(location.search);
  const director = q.get('director') === '1';
  const HOSTED = window.PORTAL_IMAGES || {};

  /* ── state ─────────────────────────────────────────────────── */
  const S = { i: -1, ctx: {}, seen: new Set(), items: [], t0: Date.now(), sound: false, scanned: false, lines: 0, pan: 0, busy: false, special: 0 };
  const M = W.missions;

  /* ── helpers ───────────────────────────────────────────────── */
  const el = (t, c, h) => { const e = document.createElement(t); if (c) e.className = c; if (h != null) e.innerHTML = h; return e; };
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const src = img => img ? (W.base || '') + img : '';
  const alt = img => HOSTED[img] || '';
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const esc = s => String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  // objective markup: ~y~yellow~s~  ~g~green~s~  ~b~blue~s~
  const mark = s => esc(s).replace(/~y~/g, '<y>').replace(/~g~/g, '<g>').replace(/~b~/g, '<b>').replace(/~s~/g, '</y></g></b>');

  // prefer the local file; if it 404s, use the hosted copy once
  const loaded = {};
  function picture(img) {
    return new Promise(res => {
      if (!img) return res('');
      if (loaded[img]) return res(loaded[img]);
      const im = new Image(); let tried = false;
      im.onload = () => { loaded[img] = im.src; res(im.src); };
      im.onerror = () => { if (!tried && alt(img)) { tried = true; im.src = alt(img); } else res(''); };
      im.src = src(img);
    });
  }

  /* ── events out ────────────────────────────────────────────── */
  function emit(name, data) {
    const ev = Object.assign({ event: 'portal', portal: W.id, step: name, at: Math.round((Date.now() - S.t0) / 100) / 10 }, data || {});
    (window.dataLayer = window.dataLayer || []).push(ev);
    window.dispatchEvent(new CustomEvent('portal', { detail: ev }));
    if (W.measure && W.measure.endpoint && navigator.sendBeacon) {
      try { navigator.sendBeacon(W.measure.endpoint, new Blob([JSON.stringify(ev)], { type: 'application/json' })); } catch (e) {}
    }
  }

  /* ── exit link ─────────────────────────────────────────────── */
  function exitUrl() {
    let u; try { u = new URL(W.brand.shopUrl); } catch (e) { return '#'; }
    u.searchParams.set('portal', W.id);
    (W.context || []).forEach(c => { if (S.ctx[c.key] != null) u.searchParams.set(c.key, S.ctx[c.key]); });
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'ttclid', 'gclid'].forEach(k => { const v = q.get(k); if (v) u.searchParams.set(k, v); });
    return u.toString();
  }
  function said(key) { const c = (W.context || []).find(c => c.key === key); const v = S.ctx[key]; return c && c.say && c.say[v] ? c.say[v] : v; }

  /* ── build the stage ───────────────────────────────────────── */
  stage.innerHTML = '';
  const world = el('div', 'world');
  const bob = el('div', 'bob');
  const plateA = el('div', 'plate'), plateB = el('div', 'plate');
  bob.append(plateA, plateB); world.append(bob);
  const look = el('div', 'look');
  const edgeL = el('div', 'edge l'), edgeR = el('div', 'edge r');
  const vig = el('div', 'vig'), grain = el('div', 'grain');
  const lbxT = el('div', 'lbx t'), lbxB = el('div', 'lbx b');
  const hud = el('div', 'hud');
  const tr = el('div', 'tr');
  const cash = el('div', 'cash', esc((W.player && W.player.cash) || '$0'));
  const clock = el('div', 'clock');
  const stars = el('div', 'stars', '<b></b>★★★★★');
  tr.append(cash, clock, stars);
  const obj = el('div', 'obj');
  const subs = el('div', 'subs');
  const notes = el('div', 'notes');
  const radar = el('div', 'radar');
  const map = el('div', 'map'); radar.append(map);
  const bars = el('div', 'bars', '<i class="h" style="--v:1"></i><i class="a" style="--v:.8"></i><i class="s" style="--v:0"></i>');
  radar.append(bars);
  const br = el('div', 'br');
  const inv = el('div', 'inv');
  (W.items || []).forEach(it => { const s = el('div', 'slot', esc(it.short || it.name)); s.dataset.id = it.id; s.title = it.name; inv.append(s); });
  const sndBtn = el('button', 'ib', 'sound off'); sndBtn.type = 'button';
  br.append(inv, sndBtn);
  const go = el('button', 'go'); go.type = 'button';
  const hint = el('div', 'hint', 'drag to look around');
  hud.append(tr, obj, subs, notes, radar, br);
  const ov = el('div', 'ov');
  const dir = el('div', 'dir');
  stage.append(world, look, edgeL, edgeR, vig, grain, lbxT, lbxB, hud, hint, go, ov, dir);
  if (director) stage.classList.add('director');
  if (W.theme && W.theme.accent) stage.style.setProperty('--y', W.theme.accent);

  /* ── the plate: size, pan, markers ─────────────────────────── */
  let plate = plateA, other = plateB, ratio = 16 / 9, plateW = 0, stW = 0, stH = 0, markers = [];
  function size() {
    const r = stage.getBoundingClientRect(); stW = r.width; stH = r.height;
    plateW = Math.max(stW, stH * ratio);
    [plateA, plateB].forEach(p => { p.style.width = plateW + 'px'; });
    setPan(S.pan);
  }
  function setPan(x) {
    S.pan = clamp(x, 0, Math.max(0, plateW - stW));
    const tx = 'translate3d(' + (-S.pan) + 'px,0,0)';
    plate.style.transform = tx; plate.style.setProperty('--tx', tx);
    other.style.transform = tx;
    edges(); radarHeading();
  }
  function headingToPan(h) { return (plateW - stW) * clamp(h == null ? .5 : h, 0, 1); }
  function edges() {
    let l = false, r = false;
    markers.forEach(m => { if (m.done) return; const x = m.x * plateW - S.pan; if (x < 12) l = true; if (x > stW - 12) r = true; });
    edgeL.classList.toggle('on', l); edgeR.classList.toggle('on', r);
  }
  // drag to look
  let drag = null, lastMoved = false;   // no pointer capture: it would swallow the markers' clicks
  world.addEventListener('pointerdown', e => { if (S.busy) return; drag = { x: e.clientX, p: S.pan, moved: false }; });
  window.addEventListener('pointermove', e => { if (!drag) return; const dx = e.clientX - drag.x; if (Math.abs(dx) > 4) drag.moved = true; setPan(drag.p - dx); });
  const endDrag = e => { if (!drag) { if (lineResolve && e.target.closest && e.target.closest('.world,.look')) tapWorld(e); return; } lastMoved = drag.moved; drag = null; if (!lastMoved) tapWorld(e); };
  window.addEventListener('pointerup', endDrag); window.addEventListener('pointercancel', () => { drag = null; });
  // wheel / trackpad
  world.addEventListener('wheel', e => { if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) { setPan(S.pan + e.deltaX); e.preventDefault(); } }, { passive: false });
  // tilt to look (phones), only after a first touch so it never surprises
  let tiltBase = null;
  window.addEventListener('deviceorientation', e => { if (drag || S.busy || e.gamma == null) return; if (tiltBase == null) tiltBase = e.gamma; const d = e.gamma - tiltBase; if (Math.abs(d) > 3) setPan(S.pan + d * .6); }, true);
  window.addEventListener('resize', size);

  function clearMarkers() { markers.forEach(m => m.el.remove()); markers = []; }
  function addMarker(m) {
    const b = el('button', 'mk k-' + (m.kind || 'go') + (m.main ? ' main' : '')); b.type = 'button';
    b.innerHTML = '<i></i><b>' + esc(m.label || '') + '</b>';
    b.style.left = (m.x * 100) + '%'; b.style.top = (m.y * 100) + '%';
    plate.append(b);
    const rec = Object.assign({ el: b, done: false }, m);
    b.addEventListener('click', e => { e.stopPropagation(); if (S.busy || lastMoved) return; hit(rec); });
    markers.push(rec); edges(); return rec;
  }
  async function showPlate(scene, heading) {
    const sc = W.scenes[scene] || {};
    ratio = sc.ratio || 16 / 9;
    const url = await picture(sc.plate);
    other.classList.remove('on'); other.innerHTML = '';
    const t = other; other = plate; plate = t;
    bob.append(plate);                      // the live plate always sits on top
    plate.className = 'plate' + (url ? '' : ' fallback');
    plate.style.setProperty('--mood', sc.mood || '#4a3428');
    plate.style.backgroundImage = url ? 'url("' + url + '")' : '';
    size(); S.pan = headingToPan(heading); setPan(S.pan);
    plate.classList.add('on');
    sound.room(sc.sound);
    setTimeout(() => { other.classList.remove('on'); }, 800);
  }
  async function showLook(img, mood) {
    const url = await picture(img);
    look.className = 'look' + (url ? '' : ' fallback'); look.style.setProperty('--mood', mood || '#4a3428');
    look.style.backgroundImage = url ? 'url("' + url + '")' : '';
    look.classList.add('on');
  }
  function hideLook() { look.classList.remove('on'); }

  /* ── the radar ─────────────────────────────────────────────── */
  const RM = W.map || { rooms: [], spots: {} };
  function drawMap() {
    let s = '<svg viewBox="0 0 118 88" aria-hidden="true"><rect width="118" height="88" fill="#1b2530"/>';
    (RM.rooms || []).forEach(r => { s += '<rect x="' + r.x * 118 + '" y="' + r.y * 88 + '" width="' + r.w * 118 + '" height="' + r.h * 88 + '" rx="2" fill="' + (r.fill || '#2c3a48') + '" stroke="#3f5266" stroke-width="1"/>'; if (r.label) s += '<text x="' + (r.x + r.w / 2) * 118 + '" y="' + (r.y + r.h / 2) * 88 + '" fill="#8ea3b8" font-size="6" font-family="Barlow Condensed,sans-serif" text-anchor="middle" dominant-baseline="middle">' + esc(r.label) + '</text>'; });
    s += '<g id="rm-goal"><circle r="4" fill="#ffd23f"/><circle r="6.5" fill="none" stroke="#ffd23f" stroke-width="1" opacity=".6"><animate attributeName="r" values="5;9" dur="1.4s" repeatCount="indefinite"/><animate attributeName="opacity" values=".7;0" dur="1.4s" repeatCount="indefinite"/></circle></g>';
    s += '<g id="rm-you"><path d="M0 -6 L5 5 L0 2 L-5 5 Z" fill="#fff" stroke="#000" stroke-width=".8"/></g></svg>';
    map.innerHTML = s;
  }
  function radarPlace() {
    const m = M[S.i] || {}; const you = RM.spots[m.spot || m.scene] || { x: .5, y: .5 };
    const nx = M[S.i + 1]; const goal = nx ? RM.spots[nx.spot || nx.scene] : null;
    const y = map.querySelector('#rm-you'), g = map.querySelector('#rm-goal');
    if (y) y.dataset.pos = you.x * 118 + ',' + you.y * 88;
    if (g) { g.style.display = goal && (goal.x !== you.x || goal.y !== you.y) ? '' : 'none'; if (goal) g.setAttribute('transform', 'translate(' + goal.x * 118 + ',' + goal.y * 88 + ')'); }
    radarHeading();
  }
  function radarHeading() {
    const y = map.querySelector('#rm-you'); if (!y || !y.dataset.pos) return;
    const fov = 110, f = plateW > stW ? S.pan / (plateW - stW) : .5;
    const m = M[S.i] || {}; const base = (m.facing == null ? 0 : m.facing);
    y.setAttribute('transform', 'translate(' + y.dataset.pos + ') rotate(' + (base + (f - .5) * fov) + ')');
  }

  /* ── HUD bits ──────────────────────────────────────────────── */
  function setClock(t) { if (!t) return; const [h, m] = String(t).split(':'); clock.innerHTML = esc(h) + ':<b>' + esc(m) + '</b>'; }
  function setObjective(t) { if (!t) { obj.classList.remove('on'); return; } obj.innerHTML = mark(t); obj.classList.remove('on'); void obj.offsetWidth; obj.classList.add('on'); }
  function setCash(v) { if (!v) return; cash.textContent = v; cash.classList.remove('tick'); void cash.offsetWidth; cash.classList.add('tick'); sound.ping(880, .08); }
  function setStars(n) { stars.innerHTML = '<b>' + '★'.repeat(n || 0) + '</b>' + '★'.repeat(5 - (n || 0)); stars.classList.remove('flash'); if (n) { void stars.offsetWidth; stars.classList.add('flash'); sound.ping(220, .2); } }
  function setSpecial(v) { S.special = v; const s = bars.querySelector('.s'); s.style.setProperty('--v', v); s.classList.toggle('full', v >= 1); }
  function setHealth(v) { bars.querySelector('.h').style.setProperty('--v', v); }
  function note(title, text, ms) {
    const n = el('div', 'note', '<b>' + esc(title) + '</b>' + esc(text)); notes.append(n); sound.ping(1320, .05);
    setTimeout(() => { n.classList.add('out'); setTimeout(() => n.remove(), 400); }, ms || 4200);
  }
  function give(id) {
    const it = (W.items || []).find(i => i.id === id); if (!it || S.items.includes(id)) return;
    S.items.push(id); const s = inv.querySelector('[data-id="' + id + '"]'); if (s) s.classList.add('on');
    note('Picked up', it.name); sound.ping(660, .12); emit('pickup', { item: id });
  }
  function letterbox(on) { stage.classList.toggle('cut', !!on); }

  /* ── subtitles ─────────────────────────────────────────────── */
  const SP = W.speakers || {};
  let lineResolve = null;
  function tapWorld() { if (lineResolve) { const r = lineResolve; lineResolve = null; r(); } }
  function playLines(lines) {
    return lines.reduce((p, ln) => p.then(() => new Promise(res => {
      const sp = SP[ln.who] || { name: ln.who || '', cls: ln.who || '' };
      const isThought = ln.who === 'think' || !ln.who;
      subs.innerHTML = (isThought ? '<span class="think">' + esc(ln.t) + '</span>' : '<em class="' + esc(sp.cls || ln.who) + '">' + esc(sp.name) + '</em>' + esc(ln.t));
      subs.classList.add('on'); S.lines++;
      if (ln.note) note(ln.note.title, ln.note.text);
      if (ln.look) showLook(ln.look, ln.mood); else if (ln.look === null) hideLook();
      if (ln.cash) setCash(ln.cash); if (ln.stars != null) setStars(ln.stars); if (ln.special != null) setSpecial(ln.special); if (ln.give) give(ln.give);
      if (ln.sfx) sound.sfx(ln.sfx);
      const ms = ln.ms || Math.max(1600, 55 * ln.t.length);
      let done = false; const fin = () => { if (done) return; done = true; lineResolve = null; res(); };
      lineResolve = fin; setTimeout(fin, ms + 400);
    })), Promise.resolve()).then(() => { subs.classList.remove('on'); });
  }

  /* ── the go button ─────────────────────────────────────────── */
  function button(label, ghost) {
    return new Promise(res => {
      go.textContent = label || 'Continue'; go.classList.toggle('ghost', !!ghost); go.classList.add('on');
      go.onclick = () => { go.classList.remove('on'); go.onclick = null; res(); };
    });
  }

  /* ── overlays ──────────────────────────────────────────────── */
  function overlay(node) { ov.innerHTML = ''; ov.append(node); ov.classList.add('on'); S.busy = true; }
  function closeOverlay() { ov.classList.remove('on'); S.busy = false; setTimeout(() => { if (!ov.classList.contains('on')) ov.innerHTML = ''; }, 350); }

  function titleCard(m) {
    return new Promise(res => {
      const c = el('div', 'card', '<small>' + esc(m.sub || W.title || '') + '</small><h1>' + esc(m.title) + '</h1>' + (m.tag ? '<p>' + esc(m.tag) + '</p>' : ''));
      overlay(c); letterbox(true); sound.sting();
      setTimeout(() => { closeOverlay(); letterbox(false); res(); }, m.hold || 2600);
    });
  }

  function wheel(a) {
    return new Promise(res => {
      world.classList.add('slow');
      const w = el('div', 'wheel');
      w.innerHTML = '<div class="q">' + esc(a.q || '') + (a.hint ? '<small>' + esc(a.hint) + '</small>' : '') + '</div>';
      const n = a.options.length;
      a.options.forEach((o, i) => {
        const b = el('button', '', '<span>' + esc(o.t) + '</span>'); b.type = 'button';
        b.style.setProperty('--a', (360 / n * i) + 'deg');
        b.addEventListener('click', () => {
          b.classList.add('pick'); S.ctx[a.key] = o.v; emit('choice', { key: a.key, value: o.v });
          sound.ping(520, .08);
          setTimeout(() => { closeOverlay(); world.classList.remove('slow'); res(o); }, 380);
        });
        w.append(b);
      });
      overlay(w);
    });
  }

  function hold(a) {
    return new Promise(res => {
      const box = el('div', 'holdov', '<p>' + esc(a.label || 'Hold') + '</p>');
      const b = el('div', 'holdbtn', '<svg viewBox="0 0 36 36"><circle cx="18" cy="18" r="16" pathLength="100"/></svg><span>hold</span>');
      const after = el('div', 'after', esc(a.after || ''));
      box.append(b, after); overlay(box);
      let p = 0, timer = null, done = false;
      const tick = () => { p = Math.min(100, p + 2.2); b.style.setProperty('--p', p); if (a.sfx) sound.hum(p / 100); if (p >= 100 && !done) { done = true; clearInterval(timer); b.classList.add('done'); b.querySelector('span').textContent = 'done'; sound.hum(0); after.classList.add('on'); emit('hold', { id: a.id || 'hold' }); setTimeout(() => { closeOverlay(); res(); }, a.after ? 2200 : 500); } };
      const start = e => { e.preventDefault(); if (done) return; clearInterval(timer); timer = setInterval(tick, 40); };
      const stop = () => { if (done) return; clearInterval(timer); sound.hum(0); timer = setInterval(() => { p = Math.max(0, p - 3); b.style.setProperty('--p', p); if (p <= 0) clearInterval(timer); }, 40); };
      b.addEventListener('pointerdown', start); b.addEventListener('pointerup', stop); b.addEventListener('pointerleave', stop); b.addEventListener('pointercancel', stop);
    });
  }

  /* the scan: what a bump is, drawn, with a slider you control */
  function scan(a) {
    return new Promise(res => {
      const L = a.lesson || {};
      const box = el('div', 'scan');
      box.innerHTML = '<h3>' + esc(L.title || 'Scan') + '<span>zoom ×40</span></h3>' +
        '<svg class="cut" viewBox="0 0 360 200" aria-label="a hair under the skin">' +
        '<defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a5a3c"/><stop offset="1" stop-color="#5a3a26"/></linearGradient></defs>' +
        '<rect x="0" y="0" width="360" height="200" fill="#1a1512"/>' +
        '<path id="skin" d="M0 90 C 90 84, 150 96, 180 90 S 300 84, 360 90 L360 200 L0 200 Z" fill="url(#sk)"/>' +
        '<path d="M0 90 C 90 84, 150 96, 180 90 S 300 84, 360 90" fill="none" stroke="#c98b66" stroke-width="2"/>' +
        '<ellipse id="bump" cx="180" cy="88" rx="0" ry="0" fill="#c8453a" opacity=".9"/>' +
        '<ellipse id="mark" cx="180" cy="88" rx="0" ry="0" fill="#2a1710" opacity=".85"/>' +
        '<path id="canal" d="M180 92 C 178 120, 176 150, 174 175" fill="none" stroke="#3f2618" stroke-width="10" stroke-linecap="round"/>' +
        '<path id="hair" d="" fill="none" stroke="#111" stroke-width="3.2" stroke-linecap="round"/>' +
        '<g id="blade" opacity="0"><rect x="120" y="60" width="120" height="7" fill="#d8dde3" stroke="#6a7178"/><rect x="120" y="50" width="120" height="10" fill="#333"/></g>' +
        '</svg>' +
        '<p class="say"></p>' +
        '<div class="lab"><span>' + esc(L.low || 'leave some') + '</span><span>' + esc(L.high || 'skin close') + '</span></div>' +
        '<input type="range" min="0" max="100" value="' + (L.start || 20) + '" aria-label="how close">' +
        '<div class="row"><button type="button" class="btn dig">' + esc(L.dig || 'Dig at it') + '</button><button type="button" class="btn y fix">' + esc(L.fix || 'Put CRUSH on it') + '</button></div>' +
        '<div class="row"><button type="button" class="btn ok dead">' + esc(L.done || 'Got it') + '</button></div>';
      overlay(box);
      const hair = box.querySelector('#hair'), bump = box.querySelector('#bump'), markE = box.querySelector('#mark'), blade = box.querySelector('#blade'), say = box.querySelector('.say'), rng = box.querySelector('input'), ok = box.querySelector('.ok'), dig = box.querySelector('.dig'), fix = box.querySelector('.fix');
      let dug = false, fixed = false, curled = false;
      function draw(v) {
        const c = v / 100; // 0 = hair left above the skin, 1 = cut under the skin line
        blade.setAttribute('opacity', c > .05 ? String(Math.min(1, c * 1.4)) : '0');
        blade.setAttribute('transform', 'translate(0,' + (c * 34 - 4) + ')');
        if (c < .55) { // hair pokes out, curls a little
          const tip = 92 - (1 - c) * 46;
          hair.setAttribute('d', 'M174 175 C 176 150, 178 120, 180 92 C 181 ' + (tip + 14) + ', ' + (183 + (1 - c) * 8) + ' ' + (tip + 4) + ', ' + (186 + (1 - c) * 14) + ' ' + tip);
          bump.setAttribute('rx', '0'); bump.setAttribute('ry', '0'); curled = false;
          say.textContent = c < .25 ? (L.s0 || 'Left a little. The hair stays out where it belongs.') : (L.s1 || 'Closer. The tip sharpens and starts to bend.');
        } else { // cut below the surface: the tip curls back and goes into the skin
          const k = (c - .55) / .45;
          hair.setAttribute('d', 'M174 175 C 176 150, 178 120, 180 96 C 181 ' + (96 - 10 * k) + ', ' + (188 + 6 * k) + ' ' + (92 - 6 * k) + ', ' + (194 + 4 * k) + ' ' + (100 + 8 * k) + ' C ' + (196 + 2 * k) + ' ' + (108 + 10 * k) + ', 190 ' + (110 + 10 * k) + ', ' + (186 - 2 * k) + ' ' + (106 + 8 * k));
          bump.setAttribute('rx', String(10 + 22 * k)); bump.setAttribute('ry', String(4 + 12 * k)); bump.setAttribute('cx', '188'); curled = true;
          say.textContent = k < .5 ? (L.s2 || 'Under the skin now. The curl comes back on itself and pushes in.') : (L.s3 || 'That is the bump. Not dirt, not a pimple. A hair growing into you.');
        }
        if (curled) ok.classList.remove('dead');
      }
      rng.addEventListener('input', () => { if (fixed) return; draw(+rng.value); });
      dig.addEventListener('click', () => { if (!curled || fixed) { say.textContent = L.sNo || 'Nothing to dig at yet. Shave closer and watch.'; return; } dug = true; markE.setAttribute('cx', '188'); markE.setAttribute('rx', '30'); markE.setAttribute('ry', '13'); say.textContent = L.sDig || 'And now it is a dark mark that stays months after the bump is gone. That is the one you see in the mirror every day.'; emit('scan_dig'); });
      fix.addEventListener('click', () => { if (!curled) { say.textContent = L.sNo || 'Nothing to fix yet. Shave closer and watch.'; return; } fixed = true; let k = 1; const t = setInterval(() => { k -= .08; bump.setAttribute('rx', String(32 * Math.max(0, k))); bump.setAttribute('ry', String(16 * Math.max(0, k))); markE.setAttribute('rx', String(30 * Math.max(0, k))); markE.setAttribute('ry', String(13 * Math.max(0, k))); if (k <= 0) { clearInterval(t); hair.setAttribute('d', 'M174 175 C 176 150, 178 120, 180 92 C 181 80, 186 74, 192 66'); } }, 60); say.textContent = L.sFix || 'Soft enough the hair lets go and comes back out. Night after night the bump goes down and the mark fades with it.'; ok.classList.remove('dead'); emit('scan_fix'); });
      ok.addEventListener('click', () => { S.scanned = true; emit('scan_done', { dug, fixed }); closeOverlay(); res(); });
      draw(+rng.value);
    });
  }

  function passed(m) {
    const a = m.action || {};
    const mins = Math.max(1, Math.round((Date.now() - S.t0) / 60000));
    const P = W.brand.product || {};
    const rows = (a.stats || []).map(r => '<div><span>' + esc(r[0]) + '</span><b>' + esc(typeof r[1] === 'function' ? r[1](S) : r[1]) + '</b></div>').join('');
    const auto = '<div><span>Time in the shop</span><b>' + mins + ' min</b></div>' +
      '<div><span>Things you clocked</span><b>' + S.seen.size + '</b></div>' +
      '<div><span>Bump understood</span><b>' + (S.scanned ? 'yes' : 'skipped') + '</b></div>' +
      (W.context || []).filter(c => S.ctx[c.key] != null).map(c => '<div><span>' + esc(c.label) + '</span><b>' + esc(said(c.key)) + '</b></div>').join('');
    const box = el('div', 'passed');
    box.innerHTML = '<div class="band"><h1>' + esc(a.title || 'MISSION PASSED') + '</h1><div class="sub">' + esc(a.sub || 'respect +') + '</div></div>' +
      '<div class="stats">' + rows + auto + '</div>' +
      '<div class="reward"><small>' + esc(a.rewardLabel || 'reward') + '</small><h2>' + esc(P.name || '') + '</h2><p>' + esc(P.what || '') + '</p>' +
      (P.says || []).map(s => '<q>' + esc(s) + '</q>').join('') +
      '<a href="' + esc(exitUrl()) + '"' + (W.brand.newTab ? ' target="_blank" rel="noopener"' : '') + '>' + esc(a.cta || 'Cop it') + '</a>' +
      (P.price ? '<div class="cost">' + esc(P.price) + '</div>' : '') + '</div>';
    box.querySelector('a').addEventListener('click', () => emit('exit', { url: exitUrl(), ctx: S.ctx }));
    overlay(box); letterbox(true); stage.classList.add('passed'); sound.sting(true); emit('passed', { ctx: S.ctx, items: S.items });
    go.classList.remove('on'); obj.classList.remove('on');
  }

  /* ── missions ──────────────────────────────────────────────── */
  async function hit(m) {
    if (m.done) return;
    m.done = true; m.el.classList.add('done'); S.seen.add(m.id || m.label);
    sound.ping(1040, .06); edges();
    if (!m.main) {                          // a side thing: look, listen, carry on
      emit('hotspot', { id: m.id || m.label });
      if (m.look) showLook(m.look, m.mood);
      if (m.lines) { S.busy = true; await playLines(m.lines); S.busy = false; }
      else if (m.text) { S.busy = true; await playLines([{ who: m.who || 'think', t: m.text }]); S.busy = false; }
      if (m.look) hideLook();
      if (m.give) give(m.give);
      return;
    }
    // the objective marker: the mission continues
    if (m.resolve) { const r = m.resolve; m.resolve = null; r(); }
  }

  async function run(i) {
    if (i >= M.length) return;
    S.i = i; const m = M[i];
    clearMarkers(); hideLook(); S.busy = false; go.classList.remove('on');
    if (director) drawDirector();
    emit('mission', { id: m.id, n: i });
    if (m.scene) { world.classList.add('walk'); setTimeout(() => world.classList.remove('walk'), 900); sound.sfx('steps'); await showPlate(m.scene, m.heading); }
    setClock(m.clock); radarPlace();
    if (m.title) await titleCard(m);
    if (i === 0) { hint.classList.add('on'); }
    if (m.cash) setCash(m.cash); if (m.stars != null) setStars(m.stars); if (m.special != null) setSpecial(m.special); if (m.health != null) setHealth(m.health);
    if (m.note) note(m.note.title, m.note.text);
    setObjective(m.objective);
    (m.hotspots || []).forEach(h => addMarker(Object.assign({ kind: 'look' }, h)));
    if (m.marker) {
      const mk = addMarker(Object.assign({ kind: 'go', main: true }, m.marker));
      await new Promise(res => { mk.resolve = res; });
      S.busy = true;
      if (m.marker.look) await showLook(m.marker.look, m.marker.mood);
    } else { S.busy = true; }
    if (m.lines && m.lines.length) await playLines(m.lines);
    const a = m.action || { type: 'go' };
    if (a.objective) setObjective(a.objective);
    if (a.type === 'wheel') { const o = await wheel(a); if (o.say) { S.busy = true; await playLines([{ who: o.who || a.who || 'barber', t: o.say }]); } if (o.give) give(o.give); }
    else if (a.type === 'hold') { await hold(a); if (a.give) give(a.give); }
    else if (a.type === 'scan') { await scan(a); }
    else if (a.type === 'get') { give(a.item); await button(a.label || 'Keep it', false); }
    else if (a.type === 'exit') { passed(m); return; }
    if (a.type !== 'exit' && a.type !== 'get') { S.busy = false; await button(a.label || m.next || 'Next', a.ghost); }
    hideLook();
    run(i + 1);
  }

  /* ── director ──────────────────────────────────────────────── */
  function drawDirector() {
    dir.innerHTML = '<b>' + esc(W.title || W.id) + '</b> · mission ' + (S.i + 1) + '/' + M.length +
      '<div class="m">' + M.map((m, i) => '<i class="' + (i === S.i ? 'now' : i < S.i ? 'done' : '') + '" data-i="' + i + '">' + esc(m.id) + '</i>').join('') + '</div>' +
      'learned: ' + esc(JSON.stringify(S.ctx)) + '<br>items: ' + esc(S.items.join(', ') || 'none') + '<br>exit → <a href="' + esc(exitUrl()) + '">' + esc(exitUrl()) + '</a>';
    dir.querySelectorAll('.m i').forEach(n => n.addEventListener('click', () => { ov.classList.remove('on'); letterbox(false); stage.classList.remove('passed'); run(+n.dataset.i); }));
  }

  /* ── sound: made in the browser, nothing to download ───────── */
  const sound = (() => {
    let ac, master, bed, hum, humG;
    function ctx() { if (ac) return ac; ac = new (window.AudioContext || window.webkitAudioContext)(); master = ac.createGain(); master.gain.value = 0; master.connect(ac.destination); return ac; }
    function noise() { const b = ac.createBuffer(1, ac.sampleRate * 2, ac.sampleRate); const d = b.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; const s = ac.createBufferSource(); s.buffer = b; s.loop = true; return s; }
    function room(kind) {
      if (!S.sound) return; ctx();
      if (bed) { try { bed.stop(); } catch (e) {} bed = null; }
      const s = noise(); const f = ac.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = kind === 'street' ? 900 : 420; const g = ac.createGain(); g.gain.value = kind === 'street' ? .05 : .035;
      s.connect(f); f.connect(g); g.connect(master); s.start(); bed = s;
      if (kind === 'shop' || kind === 'chair') { const o = ac.createOscillator(); o.type = 'sawtooth'; o.frequency.value = 118; const lf = ac.createOscillator(); lf.frequency.value = 7; const lg = ac.createGain(); lg.gain.value = 6; lf.connect(lg); lg.connect(o.frequency); const og = ac.createGain(); og.gain.value = kind === 'chair' ? .05 : .018; const of = ac.createBiquadFilter(); of.type = 'lowpass'; of.frequency.value = 1400; o.connect(of); of.connect(og); og.connect(master); o.start(); lf.start(); const stop = bed; s.onended = () => { try { o.stop(); lf.stop(); } catch (e) {} }; }
    }
    function ping(f, len) { if (!S.sound) return; ctx(); const o = ac.createOscillator(); o.frequency.value = f; const g = ac.createGain(); g.gain.setValueAtTime(.12, ac.currentTime); g.gain.exponentialRampToValueAtTime(.001, ac.currentTime + (len || .1)); o.connect(g); g.connect(master); o.start(); o.stop(ac.currentTime + (len || .1) + .05); }
    function sting(big) { if (!S.sound) return; ctx(); [220, 277, 330, big ? 440 : 392].forEach((f, i) => setTimeout(() => ping(f, .5), i * 120)); }
    function sfx(k) { if (!S.sound) return; ctx(); if (k === 'bell') { ping(2200, .4); setTimeout(() => ping(2900, .5), 60); } if (k === 'steps') { [0, 380, 760].forEach(t => setTimeout(() => { const s = noise(); const f = ac.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = 180; const g = ac.createGain(); g.gain.setValueAtTime(.15, ac.currentTime); g.gain.exponentialRampToValueAtTime(.001, ac.currentTime + .12); s.connect(f); f.connect(g); g.connect(master); s.start(); s.stop(ac.currentTime + .15); }, t)); } if (k === 'clippers') { hum(1); setTimeout(() => hum(0), 900); } if (k === 'spray') { const s = noise(); const f = ac.createBiquadFilter(); f.type = 'highpass'; f.frequency.value = 3000; const g = ac.createGain(); g.gain.setValueAtTime(.08, ac.currentTime); g.gain.exponentialRampToValueAtTime(.001, ac.currentTime + .3); s.connect(f); f.connect(g); g.connect(master); s.start(); s.stop(ac.currentTime + .35); } }
    function humv(v) { if (!S.sound) return; ctx(); if (!hum) { hum = ac.createOscillator(); hum.type = 'sawtooth'; hum.frequency.value = 124; humG = ac.createGain(); humG.gain.value = 0; const f = ac.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 1600; hum.connect(f); f.connect(humG); humG.connect(master); hum.start(); } humG.gain.setTargetAtTime(v * .08, ac.currentTime, .05); }
    function toggle() { S.sound = !S.sound; sndBtn.textContent = S.sound ? 'sound on' : 'sound off'; sndBtn.classList.toggle('on', S.sound); if (S.sound) { ctx(); ac.resume(); master.gain.setTargetAtTime(1, ac.currentTime, .3); room((W.scenes[(M[S.i] || {}).scene] || {}).sound); } else if (master) { master.gain.setTargetAtTime(0, ac.currentTime, .2); } emit('sound', { on: S.sound }); }
    return { room, ping, sting, sfx, hum: humv, toggle };
  })();
  sndBtn.addEventListener('click', sound.toggle);

  /* ── go ────────────────────────────────────────────────────── */
  drawMap(); size();
  (M.slice(0, 3)).forEach(m => { const sc = W.scenes[m.scene]; if (sc) picture(sc.plate); if (m.marker && m.marker.look) picture(m.marker.look); });
  emit('open', { ref: document.referrer || '' });
  run(0);
})();
