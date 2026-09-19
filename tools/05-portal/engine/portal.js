/* ═══════════════════════════════════════════════════════════════
   PORTAL — the player.

   Reads one object, window.PORTAL_WORLD (see ../worlds/), and plays it
   as a sequence of beats. Each beat is a picture, a few lines, and
   exactly one thing to do: tap, choose, hold, learn, or leave.

   Every choice is remembered as context and carried out through the
   exit link, so the store already knows the person by the time they
   arrive. That is the whole point: the world asks the quiz's questions
   without anyone noticing a quiz.

   No framework, no build, no server. Works from a file:// URL.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  const W = window.PORTAL_WORLD;
  if (!W) { document.body.textContent = 'No world loaded. Include a world.js before portal.js.'; return; }

  // ── state ──────────────────────────────────────────────────────
  const S = {
    i: -1,                       // current beat index
    ctx: {},                     // what the world has learned about you
    t0: Date.now(),              // when you walked in
    events: [],                  // everything that happened, in order
    sound: false,
    audio: null,
    timers: [],
  };
  const qs = new URLSearchParams(location.search);
  const director = qs.get('director') === '1';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── helpers ────────────────────────────────────────────────────
  const $ = (sel, root) => (root || document).querySelector(sel);
  const el = (tag, cls, html) => { const n = document.createElement(tag); if (cls) n.className = cls; if (html != null) n.innerHTML = html; return n; };
  const later = (fn, ms) => { const id = setTimeout(fn, reduced ? 0 : ms); S.timers.push(id); return id; };
  const clearTimers = () => { S.timers.forEach(clearTimeout); S.timers = []; };
  const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const vibrate = (p) => { try { navigator.vibrate && navigator.vibrate(p); } catch (e) { } };

  function emit(name, data) {
    const ev = { name, t: Math.round((Date.now() - S.t0) / 100) / 10, beat: W.beats[S.i] && W.beats[S.i].id, ...(data || {}) };
    S.events.push(ev);
    try { (window.dataLayer = window.dataLayer || []).push({ event: 'portal', portal: W.id, ...ev }); } catch (e) { }
    try { window.dispatchEvent(new CustomEvent('portal', { detail: ev })); } catch (e) { }
    if (W.measure && W.measure.endpoint) {
      try { navigator.sendBeacon(W.measure.endpoint, JSON.stringify({ portal: W.id, ...ev, ctx: S.ctx })); } catch (e) { }
    }
    if (director) renderDirector();
  }

  // ── the clock: how long you have been in the world ─────────────
  function parseTime(s) { // "10:40" (24h) -> minutes
    if (!s) return null; const m = /^(\d{1,2}):(\d{2})$/.exec(s); if (!m) return null; return (+m[1]) * 60 + (+m[2]);
  }
  function fmtTime(min) {
    let h = Math.floor(min / 60) % 24, m = min % 60; const ap = h >= 12 ? 'pm' : 'am'; h = h % 12 || 12;
    return h + ':' + String(m).padStart(2, '0') + ap;
  }
  function clockText(beat) {
    const t = parseTime(beat.time), t0 = parseTime(W.beats[0].time);
    if (t == null) return '';
    let s = fmtTime(t);
    if (t0 != null && t > t0) {
      const d = t - t0, h = Math.floor(d / 60), m = d % 60;
      s += ' · <b>' + (h ? h + 'h ' : '') + m + 'm in</b>';
    }
    return s;
  }

  // ── sound: synthesised, no files. Off until asked for. ─────────
  function audioOn() {
    if (S.audio) return S.audio;
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return null;
    const ac = new AC();
    const master = ac.createGain(); master.gain.value = 0; master.connect(ac.destination);
    // room tone: filtered noise
    const buf = ac.createBuffer(1, ac.sampleRate * 2, ac.sampleRate); const d = buf.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * 0.4;
    const noise = ac.createBufferSource(); noise.buffer = buf; noise.loop = true;
    const nf = ac.createBiquadFilter(); nf.type = 'lowpass'; nf.frequency.value = 600;
    const ng = ac.createGain(); ng.gain.value = 0.05; noise.connect(nf); nf.connect(ng); ng.connect(master); noise.start();
    // clippers: two detuned saws, hum at mains-ish pitch
    const o1 = ac.createOscillator(), o2 = ac.createOscillator(); o1.type = 'sawtooth'; o2.type = 'sawtooth';
    o1.frequency.value = 118; o2.frequency.value = 121;
    const cf = ac.createBiquadFilter(); cf.type = 'lowpass'; cf.frequency.value = 1400;
    const cg = ac.createGain(); cg.gain.value = 0; o1.connect(cf); o2.connect(cf); cf.connect(cg); cg.connect(master); o1.start(); o2.start();
    S.audio = { ac, master, ng, cg };
    return S.audio;
  }
  function setSoundScene(kind) {
    if (!S.audio) return; const { ac, ng, cg } = S.audio, t = ac.currentTime;
    const map = { street: [0.09, 0.0], shop: [0.06, 0.012], clippers: [0.05, 0.05], close: [0.03, 0.035], quiet: [0.03, 0.0] };
    const [n, c] = map[kind] || map.shop;
    ng.gain.setTargetAtTime(n, t, 0.6); cg.gain.setTargetAtTime(c, t, 0.4);
  }
  function toggleSound(btn) {
    S.sound = !S.sound;
    const a = audioOn(); if (!a) { S.sound = false; return; }
    if (a.ac.state === 'suspended') a.ac.resume();
    a.master.gain.setTargetAtTime(S.sound ? 1 : 0, a.ac.currentTime, 0.3);
    btn.classList.toggle('on', S.sound); btn.textContent = S.sound ? 'sound on' : 'sound';
    if (S.sound) setSoundScene((W.beats[S.i] || {}).sound);
    emit('sound', { on: S.sound });
  }

  // ── build the stage once ───────────────────────────────────────
  const stage = $('#stage');
  stage.innerHTML = '';
  const pics = [el('div', 'pic'), el('div', 'pic')]; let picN = 0;
  pics.forEach(p => stage.appendChild(p));
  stage.appendChild(el('div', 'grade')); stage.appendChild(el('div', 'grain'));
  const lesson = el('div', 'lesson'); stage.appendChild(lesson);
  const hsLayer = el('div'); stage.appendChild(hsLayer);
  const hscap = el('div', 'hscap'); stage.appendChild(hscap);
  const top = el('div', 'top'); stage.appendChild(top);
  const ticks = el('div', 'ticks'); top.appendChild(ticks);
  W.beats.forEach(() => ticks.appendChild(el('i')));
  const bar = el('div', 'bar'); top.appendChild(bar);
  const title = el('span', '', esc(W.title || W.id)); bar.appendChild(title);
  bar.appendChild(el('span', 'sp'));
  const clock = el('span', 'clock'); bar.appendChild(clock);
  const sndBtn = el('button', 'ib', 'sound'); sndBtn.type = 'button'; sndBtn.setAttribute('aria-label', 'toggle sound'); bar.appendChild(sndBtn);
  sndBtn.addEventListener('click', () => toggleSound(sndBtn));
  const sheet = el('div', 'sheet'); stage.appendChild(sheet);
  const live = el('div', 'sr'); live.setAttribute('aria-live', 'polite'); stage.appendChild(live);

  if (W.theme) {
    const r = document.documentElement.style;
    if (W.theme.accent) r.setProperty('--accent', W.theme.accent);
    if (W.theme.ink) r.setProperty('--ink', W.theme.ink);
    if (W.theme.paper) r.setProperty('--paper', W.theme.paper);
  }
  document.title = (W.title ? W.title + ' — ' : '') + (W.brand && W.brand.name ? W.brand.name : 'Portal');

  // tap the picture to reveal the rest of the lines at once
  stage.addEventListener('click', (e) => {
    if (e.target.closest('button,a,input,.hscap,.lesson')) return;
    hscap.classList.remove('on');
    revealAll();
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight' && director) go(S.i + 1); });

  // ── pictures ───────────────────────────────────────────────────
  const base = W.base || '';
  // a picture is a file next to the world (or a full URL). If the file is not
  // there, window.PORTAL_IMAGES can name a hosted copy to fall back to — that
  // is how a world plays before its frames have been pulled into the repo.
  function src(img) { return /^(https?:)?\/\//.test(img) ? img : base + img; }
  function alt(img) { const m = window.PORTAL_IMAGES || {}; return m[img] || null; }
  const preloaded = {};
  function preload(i) { const b = W.beats[i]; if (!b || !b.image || preloaded[b.image]) return; const im = new Image(); let tried = false; im.onerror = () => { if (!tried && alt(b.image)) { tried = true; im.src = alt(b.image); } }; im.src = src(b.image); preloaded[b.image] = im; }
  function showPic(beat) {
    const next = pics[(picN + 1) % 2], cur = pics[picN];
    next.className = 'pic'; next.style.backgroundImage = ''; next.style.removeProperty('--mood');
    if (beat.image) {
      next.style.backgroundImage = 'url("' + src(beat.image) + '")';
      const im = new Image(); let tried = false;
      im.onerror = () => {
        if (!tried && alt(beat.image)) { tried = true; next.style.backgroundImage = 'url("' + alt(beat.image) + '")'; im.src = alt(beat.image); return; }
        next.style.backgroundImage = ''; next.classList.add('fallback'); next.style.setProperty('--mood', beat.mood || '#3a2a22');
      };
      im.src = src(beat.image);
    } else { next.classList.add('fallback'); next.style.setProperty('--mood', beat.mood || '#3a2a22'); }
    requestAnimationFrame(() => { next.classList.add('on'); cur.classList.remove('on'); });
    picN = (picN + 1) % 2;
  }

  // ── lines ──────────────────────────────────────────────────────
  let pendingReveal = [];
  function revealAll() { pendingReveal.forEach(fn => fn()); pendingReveal = []; }
  function renderLines(beat, wrap) {
    const lines = el('div', 'lines'); wrap.appendChild(lines);
    let delay = 250;
    (beat.lines || []).forEach((L) => {
      let n;
      if (L.s != null) n = el('p', 'line sense', esc(L.s));
      else if (L.y != null) n = el('p', 'line you', esc(L.y));
      else if (L.n != null) n = el('p', 'line note', esc(L.n));
      else { n = el('p', 'line who', esc(L.t)); n.setAttribute('data-who', L.who || 'someone'); }
      lines.appendChild(n);
      const show = () => n.classList.add('on');
      later(show, delay); pendingReveal.push(show);
      delay += L.s != null ? 900 : 700;
    });
    return delay;
  }

  // ── hotspots ───────────────────────────────────────────────────
  function renderHotspots(beat) {
    hsLayer.innerHTML = ''; hscap.classList.remove('on');
    (beat.hotspots || []).forEach((h, k) => {
      const b = el('button', 'hs'); b.type = 'button'; b.style.left = (h.x * 100) + '%'; b.style.top = (h.y * 100) + '%';
      b.setAttribute('aria-label', h.label);
      b.addEventListener('click', (e) => {
        e.stopPropagation();
        hscap.innerHTML = '<b>' + esc(h.label) + '</b>' + esc(h.text);
        hscap.style.top = 'calc(' + Math.min(h.y * 100 + 6, 55) + '% )';
        hscap.classList.add('on'); b.classList.add('seen');
        emit('hotspot', { hotspot: h.label });
      });
      hsLayer.appendChild(b);
    });
  }

  // ── the one thing to do ────────────────────────────────────────
  function mainBtn(label, onclick, accent) {
    const b = el('button', 'btn main' + (accent ? ' accent' : ''), '<span>' + esc(label) + '</span><span class="arr">→</span>'); b.type = 'button';
    b.addEventListener('click', onclick); return b;
  }
  function continueBtn(beat, wrap, label) {
    const b = mainBtn(label || (beat.action && beat.action.next) || 'Next', () => go(S.i + 1));
    wrap.appendChild(b); later(() => b.classList.add('on'), 50); return b;
  }
  function replyLine(text, who, wrap) {
    const r = el('p', 'reply', esc(text)); r.setAttribute('data-who', who || (W.voice || 'the shop'));
    wrap.appendChild(r); later(() => r.classList.add('on'), 60); live.textContent = text;
  }

  function renderAction(beat, wrap, afterMs) {
    const A = beat.action || { type: 'tap', label: 'Next' };
    const act = el('div', 'act'); wrap.appendChild(act);
    const show = () => act.classList.add('on');
    later(show, afterMs); pendingReveal.push(show);

    if (A.type === 'tap') {
      // a product can sit in the world before the door, where it would really be
      if (beat.showProduct) act.appendChild(productCard(beat.product || (W.brand && W.brand.product) || {}));
      act.appendChild(mainBtn(A.label || 'Next', () => go(S.i + 1)));
    }

    else if (A.type === 'choice') {
      if (A.ask) act.appendChild(el('p', 'ask', esc(A.ask)));
      const btns = [];
      A.options.forEach((o) => {
        const b = el('button', 'btn', '<span>' + esc(o.label) + '</span><span class="arr">↳</span>'); b.type = 'button';
        b.addEventListener('click', () => {
          btns.forEach(x => { x.disabled = true; if (x !== b) x.style.display = 'none'; });
          b.classList.add('picked'); b.querySelector('.arr').textContent = '✓';
          S.ctx[A.key] = o.value != null ? o.value : o.label;
          emit('choice', { key: A.key, value: S.ctx[A.key] });
          if (o.reply) replyLine(o.reply, A.who, act);
          later(() => continueBtn(beat, act, A.next), o.reply ? 900 : 100);
        });
        btns.push(b); act.appendChild(b);
      });
    }

    else if (A.type === 'hold') {
      const ms = A.ms || 1200;
      const b = el('button', 'btn hold', '<div class="fill"></div><span>' + esc(A.label) + '</span><span class="arr">●</span>'); b.type = 'button';
      b.style.setProperty('--ms', ms + 'ms');
      let timer = null, done = false;
      const start = (e) => { if (done) return; e.preventDefault(); b.classList.add('holding'); timer = setTimeout(finish, ms); };
      const stop = () => { if (done || !timer) return; clearTimeout(timer); timer = null; b.classList.remove('holding'); };
      const finish = () => {
        done = true; b.classList.add('done'); b.classList.remove('holding'); b.disabled = true;
        vibrate(A.haptic || [40, 60, 120]);
        if (A.key) S.ctx[A.key] = A.value != null ? A.value : true;
        emit('hold', { label: A.label });
        if (A.reply) replyLine(A.reply, A.who, act);
        later(() => continueBtn(beat, act, A.next), A.reply ? 900 : 200);
      };
      b.addEventListener('pointerdown', start); b.addEventListener('pointerup', stop);
      b.addEventListener('pointerleave', stop); b.addEventListener('pointercancel', stop);
      b.addEventListener('keydown', (e) => { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); finish(); } });
      act.appendChild(b);
    }

    else if (A.type === 'lesson') {
      renderLesson(beat, act);
    }

    else if (A.type === 'exit') {
      renderExit(beat, act);
    }
  }

  // ── the lesson: shown, not told ────────────────────────────────
  // One drawn cutaway per lesson kind. "ingrown" is the built-in: a
  // curly hair, a razor, a slider for how close you shave, and the bump
  // that follows. Add another kind by adding another function here.
  const LESSONS = {
    ingrown(cfg, act, beat) {
      const skin = cfg.skin || '#7a5340', skin2 = cfg.skinDeep || '#5a3a2c', hair = cfg.hair || '#141010';
      const cut = el('div', 'cut');
      cut.innerHTML = `
      <svg viewBox="0 0 360 236" role="img" aria-label="${esc(cfg.alt || 'A cutaway of skin showing a hair being shaved and curling back under the skin')}">
        <defs>
          <linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${skin}"/><stop offset="1" stop-color="${skin2}"/></linearGradient>
          <radialGradient id="bump" cx=".5" cy=".7" r=".6"><stop offset="0" stop-color="#d14a3a" stop-opacity=".95"/><stop offset="1" stop-color="#d14a3a" stop-opacity="0"/></radialGradient>
          <radialGradient id="mark" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#2a1610" stop-opacity=".85"/><stop offset="1" stop-color="#2a1610" stop-opacity="0"/></radialGradient>
        </defs>
        <rect x="0" y="0" width="360" height="236" fill="#0d0b0a"/>
        <path id="surf" d="M0,140 C60,134 120,146 180,140 C240,134 300,146 360,140 L360,236 L0,236 Z" fill="url(#sk)"/>
        <ellipse id="bumpE" cx="196" cy="140" rx="0" ry="0" fill="url(#bump)"/>
        <ellipse id="markE" cx="196" cy="140" rx="0" ry="0" fill="url(#mark)"/>
        <path id="hairMain" d="" fill="none" stroke="${hair}" stroke-width="5" stroke-linecap="round"/>
        <path id="hairTip" d="" fill="none" stroke="${hair}" stroke-width="5" stroke-linecap="round"/>
        <g id="razor">
          <rect x="120" y="-10" width="140" height="8" rx="2" fill="#cfd3d8"/>
          <rect x="120" y="-2" width="140" height="2" fill="#f4f6f8"/>
          <rect x="248" y="-22" width="52" height="14" rx="3" fill="#8b8f95"/>
        </g>
        <text id="lab" x="14" y="26" font-family="IBM Plex Mono,monospace" font-size="10" letter-spacing="2" fill="#f6efe8" opacity=".85"></text>
      </svg>`;
      act.appendChild(cut);
      const slider = el('div', 'slider');
      slider.innerHTML = `<label><span>${esc(cfg.sliderLabel || 'How close you shave')}</span><b id="stage-lab"></b></label>
        <input type="range" min="0" max="100" value="0" step="1" aria-label="${esc(cfg.sliderLabel || 'How close you shave')}">`;
      cut.appendChild(slider);
      const svg = cut.querySelector('svg'), main = $('#hairMain', svg), tip = $('#hairTip', svg), razor = $('#razor', svg),
        bumpE = $('#bumpE', svg), markE = $('#markE', svg), lab = $('#lab', svg), stageLab = $('#stage-lab', slider), range = slider.querySelector('input');
      const labels = cfg.labels || ['coming out clean', 'cut at the skin', 'cut under the skin', 'curls back in', 'that’s the bump'];
      const surfY = 140, rootX = 160, rootY = 226;
      let reachedEnd = false;
      function draw(t) {
        // razor drops from hovering (y 96) to below the surface (y 158)
        const rz = 96 + t * 62; razor.setAttribute('transform', 'translate(0,' + rz + ')');
        // full hair: root → surface → curls right over the surface
        if (t < 0.5) {
          const h = 1 - t * 0.6; // slightly shorter as blade nears
          main.setAttribute('d', `M${rootX},${rootY} C${rootX + 6},190 ${rootX + 14},160 ${rootX + 18},${surfY} C${rootX + 24},${surfY - 26 * h} ${rootX + 48},${surfY - 46 * h} ${rootX + 62},${surfY - 40 * h}`);
          tip.setAttribute('d', ''); setBump(0); stage(0);
        } else if (t < 0.75) {
          main.setAttribute('d', `M${rootX},${rootY} C${rootX + 6},190 ${rootX + 14},160 ${rootX + 18},${surfY + 1}`);
          tip.setAttribute('d', ''); setBump(0); stage(1);
        } else {
          const u = (t - 0.75) / 0.25; // 0..1 regrowth under the skin
          const cutY = surfY + 14;
          main.setAttribute('d', `M${rootX},${rootY} C${rootX + 6},190 ${rootX + 14},165 ${rootX + 17},${cutY}`);
          // the tip regrows, hits the underside of the skin and curls back down
          const L = u; const ex = rootX + 17 + 26 * L, ey = cutY - 10 * L + 22 * L * L;
          tip.setAttribute('d', `M${rootX + 17},${cutY} C${rootX + 20},${cutY - 16 * L} ${rootX + 34},${cutY - 20 * L} ${ex},${ey}`);
          setBump(u); stage(u < 0.45 ? 2 : u < 0.95 ? 3 : 4);
          if (u >= 0.95 && !reachedEnd) { reachedEnd = true; onEnd(); }
        }
      }
      function setBump(u) { bumpE.setAttribute('rx', 30 * u); bumpE.setAttribute('ry', 14 * u); bumpE.setAttribute('cy', surfY - 4 * u); }
      function stage(k) { lab.textContent = (labels[k] || '').toUpperCase(); stageLab.textContent = labels[k] || ''; }
      range.addEventListener('input', () => { draw(range.value / 100); });
      range.addEventListener('change', () => emit('lesson_slider', { value: +range.value }));
      draw(0);

      let ended = false;
      function onEnd() {
        if (ended) return; ended = true; vibrate(30);
        emit('lesson_reached', { stage: 'bump' });
        const after = el('div', 'act on');
        if (cfg.dig) {
          const dl = el('p', 'reply', esc(cfg.dig.text)); dl.setAttribute('data-who', cfg.who || W.voice || 'the barber'); after.appendChild(dl); later(() => dl.classList.add('on'), 80);
          const db = el('button', 'btn', '<span>' + esc(cfg.dig.label || 'Dig at it') + '</span><span class="arr">↳</span>'); db.type = 'button';
          db.addEventListener('click', () => {
            db.disabled = true; db.classList.add('picked'); db.querySelector('.arr').textContent = '✓';
            markE.setAttribute('rx', 26); markE.setAttribute('ry', 11); markE.setAttribute('cy', surfY - 2);
            lab.textContent = (cfg.dig.result || 'now there’s a dark mark too').toUpperCase(); stageLab.textContent = cfg.dig.result || '';
            emit('lesson_dig', {});
            if (cfg.dig.reply) replyLine(cfg.dig.reply, cfg.who || W.voice, after);
            later(() => showSteps(), 700);
          });
          after.appendChild(db);
        } else later(() => showSteps(), 200);
        act.appendChild(after);
        function showSteps() {
          if (cfg.ask) { const q = el('p', 'ask', esc(cfg.ask)); after.appendChild(q); }
          const ul = el('ol', 'steps');
          (cfg.steps || []).forEach((s, k) => { const li = el('li', '', esc(s)); ul.appendChild(li); later(() => li.classList.add('on'), 200 + k * 380); });
          after.appendChild(ul);
          later(() => continueBtn(beat, after, (beat.action && beat.action.next) || 'Alright'), 300 + (cfg.steps || []).length * 380);
        }
      }
    }
  };
  function renderLesson(beat, act) {
    const cfg = beat.lesson || {}; const fn = LESSONS[cfg.kind || 'ingrown'];
    lesson.innerHTML = ''; lesson.classList.add('on');
    if (!fn) { act.appendChild(el('p', 'line note on', 'Unknown lesson kind: ' + esc(cfg.kind))); continueBtn(beat, act); return; }
    // the cutaway sits in the picture area; the slider and steps are its own
    const holder = el('div', 'act on'); lesson.appendChild(holder);
    fn(cfg, holder, beat);
    later(() => holder.querySelector('.cut') && holder.querySelector('.cut').classList.add('on'), 50);
  }

  // ── the exit: the product where it lives, and the door out ─────
  function contextParams() {
    const p = new URLSearchParams();
    p.set('portal', W.id);
    Object.keys(S.ctx).forEach(k => p.set(k, S.ctx[k]));
    p.set('portal_s', Math.round((Date.now() - S.t0) / 1000));
    // carry the ad click's own tags through untouched
    qs.forEach((v, k) => { if (/^(utm_|fbclid|ttclid|gclid|ad_|sc_)/.test(k)) p.set(k, v); });
    return p;
  }
  function exitUrl(url) {
    const u = url || (W.brand && W.brand.shopUrl) || '#'; if (u === '#') return u;
    const p = contextParams(); const joined = u + (u.includes('?') ? '&' : '?') + p.toString(); return joined;
  }
  function productCard(P) {
    const c = el('div', 'prod');
    const sw = el('div', 'sw'); if (P.image) sw.innerHTML = '<img alt="" src="' + esc(src(P.image)) + '">'; else sw.textContent = P.name || 'your product';
    c.appendChild(sw);
    const r = el('div');
    r.appendChild(el('h3', '', esc(P.name || '{PRODUCT}')));
    if (P.what) r.appendChild(el('p', 'what', esc(P.what)));
    if (P.says && P.says.length) { const ul = el('ul', 'says'); P.says.forEach(s => ul.appendChild(el('li', '', esc(s)))); r.appendChild(ul); }
    if (P.price) r.appendChild(el('div', 'price', '<b>' + esc(P.price) + '</b>' + (P.priceNote ? ' · ' + esc(P.priceNote) : '')));
    c.appendChild(r); return c;
  }
  function renderExit(beat, act) {
    const P = (beat.product) || (W.brand && W.brand.product) || {};
    if (beat.showProduct !== false) act.appendChild(productCard(P));
    // what the world learned, said back
    const chips = el('ul', 'you-chips');
    (W.context || []).forEach(c => { const v = S.ctx[c.key]; if (v == null) return; const o = (c.say || {})[v] || v; chips.appendChild(el('li', '', esc(c.label) + ': <b>' + esc(o) + '</b>')); });
    if (chips.children.length) act.appendChild(chips);
    const A = beat.action || {};
    const a = el('a', 'btn main accent', '<span>' + esc(A.label || 'Take it with you') + '</span><span class="arr">→</span>');
    a.href = exitUrl(A.url); if (W.brand && W.brand.newTab) { a.target = '_blank'; a.rel = 'noopener'; }
    a.addEventListener('click', () => { emit('exit', { url: a.href }); });
    act.appendChild(a);
    if (A.secondary) { const s = el('a', 'btn', '<span>' + esc(A.secondary.label) + '</span><span class="arr">→</span>'); s.href = exitUrl(A.secondary.url); s.addEventListener('click', () => emit('exit_secondary', { url: s.href })); act.appendChild(s); }
    const again = el('button', 'small', esc(A.again || 'Back to the door')); again.type = 'button'; again.addEventListener('click', () => { emit('restart', {}); S.ctx = {}; go(0); }); act.appendChild(again);
  }

  // ── render a beat ──────────────────────────────────────────────
  function go(i) {
    if (i < 0 || i >= W.beats.length) return;
    clearTimers(); pendingReveal = [];
    S.i = i; const beat = W.beats[i];
    lesson.classList.remove('on'); lesson.innerHTML = '';
    showPic(beat); preload(i + 1); preload(i + 2);
    [...ticks.children].forEach((t, k) => { t.className = k < i ? 'done' : k === i ? 'now' : ''; });
    clock.innerHTML = clockText(beat);
    renderHotspots(beat);
    if (S.sound) setSoundScene(beat.sound);
    sheet.innerHTML = '';
    if (beat.eyebrow) sheet.appendChild(el('p', 'eyebrow', esc(beat.eyebrow)));
    const after = renderLines(beat, sheet);
    renderAction(beat, sheet, after + 200);
    live.textContent = (beat.lines || []).map(L => L.s || L.y || L.t || L.n || '').join(' ');
    emit('beat', { index: i });
    if (director) renderDirector();
  }

  // ── director's view: the map, the context, the log ─────────────
  let dir, dirbtn;
  function renderDirector() {
    if (!dir) {
      dir = el('div', ''); dir.id = 'dir'; document.body.appendChild(dir);
      dirbtn = el('button', 'show', 'director'); dirbtn.id = 'dirbtn'; dirbtn.type = 'button'; document.body.appendChild(dirbtn);
      dirbtn.addEventListener('click', () => dir.classList.toggle('on'));
      dir.classList.add('on');
    }
    const map = W.beats.map((b, k) => '<span class="' + (k < S.i ? 'done' : k === S.i ? 'now' : '') + '">' + (k) + ' · ' + esc(b.id) + (b.action ? ' · ' + esc(b.action.type) : '') + '</span>').join('');
    dir.innerHTML = '<h4>Director · ' + esc(W.id) + ' · → to skip a beat</h4><div class="map">' + map + '</div>' +
      '<h4>What the world knows</h4><pre>' + esc(JSON.stringify(S.ctx)) + '</pre>' +
      '<h4>Exit link would be</h4><pre>' + esc(exitUrl()) + '</pre>' +
      '<h4>Events (' + S.events.length + ')</h4><pre>' + esc(S.events.slice(-14).map(e => e.t + 's  ' + e.name + '  ' + JSON.stringify(Object.assign({}, e, { name: undefined, t: undefined })).replace(/"(name|t)":[^,}]*,?/g, '')).join('\n')) + '</pre>';
  }

  // ── go ─────────────────────────────────────────────────────────
  window.PORTAL = { go, state: S, world: W, exitUrl, emit };
  go(0);
})();
