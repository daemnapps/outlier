/* daemn bridge — operations against the Premiere Pro UXP API (26.3) */
const ppro = require("premierepro");

// ---------- helpers ----------
const tt = (s) => ppro.TickTime.createWithSeconds(Number(s) || 0);
const secs = (t) => { try { return t ? Number(t.seconds) : null; } catch (e) { return null; } };

async function P() {
  const p = await ppro.Project.getActiveProject();
  if (!p) throw new Error("No project open in Premiere.");
  return p;
}
async function S(project) {
  const s = await (project || await P()).getActiveSequence();
  if (!s) throw new Error("No sequence open. Open or create a sequence first.");
  return s;
}
// run a transaction: fn(compoundAction) is SYNCHRONOUS. Do all await work before calling.
function tx(project, label, fn) {
  let ok = false;
  project.lockedAccess(() => {
    ok = project.executeTransaction((ca) => { fn(ca); }, label || "daemn");
  });
  return ok;
}
function parseTrack(spec) {
  const m = String(spec || "V1").trim().toUpperCase().match(/^([VA])(\d+)$/);
  if (!m) throw new Error(`Bad track "${spec}". Use V1, V2, A1 ...`);
  return { kind: m[1], idx: parseInt(m[2], 10) - 1 };
}
async function getTrack(seq, spec) {
  const { kind, idx } = parseTrack(spec);
  const t = kind === "V" ? await seq.getVideoTrack(idx) : await seq.getAudioTrack(idx);
  if (!t) throw new Error(`Track ${spec} does not exist.`);
  return t;
}
async function clipsOn(seq, spec) {
  const t = await getTrack(seq, spec);
  return await t.getTrackItems(ppro.Constants.TrackItemType.CLIP, false);
}
async function getClip(seq, spec, index) {
  const items = await clipsOn(seq, spec);
  const i = Number(index) || 0;
  if (!items[i]) throw new Error(`No clip at ${spec} index ${i} (track has ${items.length}).`);
  return items[i];
}
async function itemName(it) {
  let name = "";
  try { name = it.name; } catch (e) {}
  if (!name) { try { name = await it.getName(); } catch (e) {} }
  return name;
}
async function flattenItems(folder, out, path) {
  out = out || []; path = path || "";
  const items = await folder.getItems();
  for (const it of items) {
    const name = await itemName(it);
    const rec = { name, path: path + "/" + name, isBin: false, mediaPath: null, ref: it };
    let asFolder = null;
    try { asFolder = ppro.FolderItem.cast(it); } catch (e) {}
    if (asFolder) {
      rec.isBin = true; out.push(rec);
      try { await flattenItems(asFolder, out, rec.path); } catch (e) {}
    } else {
      let clip = null;
      try { clip = ppro.ClipProjectItem.cast(it); } catch (e) {}
      if (clip) { try { rec.mediaPath = await clip.getMediaFilePath(); } catch (e) {} }
      out.push(rec);
    }
  }
  return out;
}
async function findProjectItem(project, needle) {
  const root = await project.getRootItem();
  const flat = await flattenItems(root);
  const clips = flat.filter((x) => !x.isBin);
  if (typeof needle === "number") {
    if (!clips[needle]) throw new Error(`No project item at index ${needle}.`);
    return clips[needle].ref;
  }
  const exact = clips.find((x) => x.name === needle);
  if (exact) return exact.ref;
  const loose = clips.find((x) => x.name && x.name.toLowerCase().includes(String(needle).toLowerCase()));
  if (!loose) throw new Error(`No project item matching "${needle}". Have: ${clips.map((f) => f.name).join(", ")}`);
  return loose.ref;
}
async function describeClip(c, i) {
  const o = { index: i };
  try { o.name = await c.getName(); } catch (e) {}
  try { o.start = secs(await c.getStartTime()); } catch (e) {}
  try { o.end = secs(await c.getEndTime()); } catch (e) {}
  try { o.inPoint = secs(await c.getInPoint()); } catch (e) {}
  try { o.outPoint = secs(await c.getOutPoint()); } catch (e) {}
  try { o.duration = secs(await c.getDuration()); } catch (e) {}
  try { o.disabled = await c.isDisabled(); } catch (e) {}
  try { o.speed = await c.getSpeed(); } catch (e) {}
  try {
    const chain = await c.getComponentChain();
    const fx = [];
    const n = chain.getComponentCount();
    for (let k = 0; k < n; k++) {
      const comp = chain.getComponentAtIndex(k);
      let dn = ""; try { dn = await comp.getDisplayName(); } catch (e) {}
      let mn = ""; try { mn = await comp.getMatchName(); } catch (e) {}
      fx.push({ index: k, name: dn, matchName: mn, params: comp.getParamCount() });
    }
    o.effects = fx;
  } catch (e) {}
  return o;
}

// Resolve an effect by index, display name, or matchName ("Motion", "Gaussian Blur", 2)
async function resolveComponentIndex(chain, spec) {
  if (typeof spec === "number") return spec;
  if (spec === undefined || spec === null) return 1;
  const n = chain.getComponentCount();
  const seen = [];
  for (let i = 0; i < n; i++) {
    const comp = chain.getComponentAtIndex(i);
    let dn = ""; try { dn = await comp.getDisplayName(); } catch (e) {}
    let mn = ""; try { mn = await comp.getMatchName(); } catch (e) {}
    seen.push(dn || mn);
    if (dn === spec || mn === spec) return i;
  }
  const low = String(spec).toLowerCase();
  const idx = seen.findIndex((x) => x && x.toLowerCase() === low);
  if (idx >= 0) return idx;
  const loose = seen.findIndex((x) => x && x.toLowerCase().includes(low));
  if (loose >= 0) return loose;
  throw new Error(`No effect "${spec}" on this clip. It has: ${seen.join(", ")}`);
}

// Resolve a param by index or display name ("Scale", "Opacity", 1). Sync — safe inside lockedAccess.
function resolveParamIndex(comp, spec) {
  if (typeof spec === "number") return spec;
  const n = comp.getParamCount();
  const names = [];
  for (let i = 0; i < n; i++) {
    let dn = "";
    try { dn = comp.getParam(i).displayName; } catch (e) {}
    names.push(dn);
    if (dn === spec) return i;
  }
  const low = String(spec).toLowerCase();
  let i = names.findIndex((x) => x && x.toLowerCase() === low);
  if (i >= 0) return i;
  i = names.findIndex((x) => x && x.toLowerCase().includes(low));
  if (i >= 0) return i;
  throw new Error(`No param "${spec}". This effect has: ${names.join(", ")}`);
}

// ---------- operations ----------
const OPS = {};

OPS.ping = async () => {
  const out = { connected: true, project: null, sequence: null };
  try {
    const p = await ppro.Project.getActiveProject();
    if (p) {
      out.project = p.name;
      try { out.path = p.path; } catch (e) {}
      const s = await p.getActiveSequence();
      if (s) out.sequence = s.name;
    }
  } catch (e) {}
  return out;
};

OPS.state = async () => {
  const p = await P();
  const out = { project: p.name, sequences: [], active: null };
  try { out.path = p.path; } catch (e) {}
  try { const seqs = await p.getSequences(); out.sequences = seqs.map((s) => s.name); } catch (e) {}
  let s = null;
  try { s = await p.getActiveSequence(); } catch (e) {}
  if (!s) return out;
  const a = { name: s.name, videoTracks: [], audioTracks: [] };
  try { a.end = secs(await s.getEndTime()); } catch (e) {}
  try { a.playhead = secs(await s.getPlayerPosition()); } catch (e) {}
  try { a.timebase = await s.getTimebase(); } catch (e) {}
  try { const fs = await s.getFrameSize(); a.frame = { w: fs.width, h: fs.height }; } catch (e) {}
  const vc = await s.getVideoTrackCount();
  const ac = await s.getAudioTrackCount();
  for (let i = 0; i < vc; i++) {
    const t = await s.getVideoTrack(i);
    const items = await t.getTrackItems(ppro.Constants.TrackItemType.CLIP, false);
    const clips = [];
    for (let j = 0; j < items.length; j++) clips.push(await describeClip(items[j], j));
    a.videoTracks.push({ track: "V" + (i + 1), clips });
  }
  for (let i = 0; i < ac; i++) {
    const t = await s.getAudioTrack(i);
    const items = await t.getTrackItems(ppro.Constants.TrackItemType.CLIP, false);
    const clips = [];
    for (let j = 0; j < items.length; j++) clips.push(await describeClip(items[j], j));
    a.audioTracks.push({ track: "A" + (i + 1), clips });
  }
  out.active = a;
  return out;
};

OPS.items = async () => {
  const p = await P();
  const root = await p.getRootItem();
  const flat = await flattenItems(root);
  return flat.map((x) => ({ name: x.name, path: x.path, isBin: x.isBin, mediaPath: x.mediaPath }));
};

OPS.import = async (a) => {
  const p = await P();
  const files = a.files || (a.file ? [a.file] : []);
  if (!files.length) throw new Error("import needs files: []");
  const ok = await p.importFiles(files, a.suppressUI !== false, null, !!a.asNumberedStills);
  return { imported: ok, files };
};

OPS["sequence.create"] = async (a) => {
  const p = await P();
  const s = a.presetPath
    ? await p.createSequenceWithPresetPath(a.name, a.presetPath)
    : await p.createSequence(a.name);
  return { created: !!s, name: a.name };
};

OPS["sequence.fromMedia"] = async (a) => {
  const p = await P();
  const names = a.items || [];
  const clips = [];
  for (const n of names) {
    const it = await findProjectItem(p, n);
    let c = null;
    try { c = ppro.ClipProjectItem.cast(it); } catch (e) {}
    if (c) clips.push(c);
  }
  const s = await p.createSequenceFromMedia(a.name, clips);
  return { created: !!s, name: a.name, from: names };
};

OPS["sequence.activate"] = async (a) => {
  const p = await P();
  const seqs = await p.getSequences();
  const s = seqs.find((x) => x.name === a.name) ||
            seqs.find((x) => x.name.toLowerCase().includes(String(a.name).toLowerCase()));
  if (!s) throw new Error(`No sequence "${a.name}". Have: ${seqs.map((x) => x.name).join(", ")}`);
  return { activated: await p.setActiveSequence(s), name: s.name };
};

OPS["sequence.playhead"] = async (a) => {
  const s = await S();
  if (a && a.at !== undefined) return { moved: await s.setPlayerPosition(tt(a.at)), at: Number(a.at) };
  return { at: secs(await s.getPlayerPosition()) };
};

// Read the sequence's in/out/zero points and true content end.
OPS["sequence.range"] = async () => {
  const s = await S();
  const out = {};
  try { out.zero = secs(await s.getZeroPoint()); } catch (e) {}
  try { out.in = secs(await s.getInPoint()); } catch (e) {}
  try { out.out = secs(await s.getOutPoint()); } catch (e) {}
  try { out.end = secs(await s.getEndTime()); } catch (e) {}
  let last = 0;
  const vc = await s.getVideoTrackCount();
  for (let i = 0; i < vc; i++) {
    const t = await s.getVideoTrack(i);
    const items = await t.getTrackItems(ppro.Constants.TrackItemType.CLIP, false);
    for (const c of items) {
      try { const e = secs(await c.getEndTime()); if (e > last) last = e; } catch (err) {}
    }
  }
  const ac = await s.getAudioTrackCount();
  for (let i = 0; i < ac; i++) {
    const t = await s.getAudioTrack(i);
    const items = await t.getTrackItems(ppro.Constants.TrackItemType.CLIP, false);
    for (const c of items) {
      try { const e = secs(await c.getEndTime()); if (e > last) last = e; } catch (err) {}
    }
  }
  out.lastClipEnds = last;
  out.emptyTail = (out.end || 0) - last;
  return out;
};

// Pull the in/out points back onto the actual footage (default: 0 -> last clip).
OPS["sequence.tidy"] = async (a) => {
  const p = await P();
  const s = await S(p);
  const r = await OPS["sequence.range"]();
  const inAt = a && a.in !== undefined ? Number(a.in) : 0;
  const outAt = a && a.out !== undefined ? Number(a.out) : r.lastClipEnds;
  const inT = tt(inAt), outT = tt(outAt);
  const ok = tx(p, "Reset sequence in/out", (ca) => {
    ca.addAction(s.createSetInPointAction(inT));
    ca.addAction(s.createSetOutPointAction(outT));
  });
  return { reset: ok, in: inAt, out: outAt, was: { in: r.in, out: r.out } };
};

OPS.place = async (a) => {
  const p = await P();
  const s = await S(p);
  const item = await findProjectItem(p, a.item);
  const ed = ppro.SequenceEditor.getEditor(s);
  const vt = a.videoTrack !== undefined ? parseTrack(a.videoTrack).idx : 0;
  const at = a.audioTrack !== undefined ? parseTrack(a.audioTrack).idx : 0;
  const time = tt(a.at || 0);
  const insert = (a.mode || "overwrite") === "insert";
  const ok = tx(p, insert ? "Insert clip" : "Overwrite clip", (ca) => {
    ca.addAction(insert
      ? ed.createInsertProjectItemAction(item, time, vt, at, a.limitShift !== false)
      : ed.createOverwriteItemAction(item, time, vt, at));
  });
  return { placed: ok, item: a.item, at: Number(a.at || 0), mode: insert ? "insert" : "overwrite" };
};

OPS.remove = async (a) => {
  const p = await P();
  const s = await S(p);
  const ed = ppro.SequenceEditor.getEditor(s);
  let sel;
  if (a.selected) {
    sel = await s.getSelection();
  } else {
    const clip = await getClip(s, a.track, a.index);
    sel = await s.getSelection();
    const existing = await sel.getTrackItems();
    for (const e of existing) sel.removeItem(e);
    sel.addItem(clip, true);
  }
  const ok = tx(p, "Remove clip", (ca) => {
    ca.addAction(ed.createRemoveItemsAction(sel, a.ripple !== false, ppro.Constants.MediaType.VIDEO));
  });
  return { removed: ok, ripple: a.ripple !== false };
};

OPS.trim = async (a) => {
  const p = await P();
  const s = await S(p);
  const c = await getClip(s, a.track, a.index);
  const acts = [];
  if (a.start !== undefined) acts.push(["start", tt(a.start)]);
  if (a.end !== undefined) acts.push(["end", tt(a.end)]);
  if (a.in !== undefined) acts.push(["in", tt(a.in)]);
  if (a.out !== undefined) acts.push(["out", tt(a.out)]);
  if (!acts.length) throw new Error("trim needs start/end/in/out");
  const ok = tx(p, "Trim clip", (ca) => {
    for (const pair of acts) {
      const k = pair[0], v = pair[1];
      if (k === "start") ca.addAction(c.createSetStartAction(v));
      if (k === "end") ca.addAction(c.createSetEndAction(v));
      if (k === "in") ca.addAction(c.createSetInPointAction(v));
      if (k === "out") ca.addAction(c.createSetOutPointAction(v));
    }
  });
  return { trimmed: ok, track: a.track, index: a.index };
};

OPS.move = async (a) => {
  const p = await P();
  const s = await S(p);
  const c = await getClip(s, a.track, a.index);
  const ok = tx(p, "Move clip", (ca) => ca.addAction(c.createMoveAction(tt(a.to))));
  return { moved: ok, to: Number(a.to) };
};

OPS.clone = async (a) => {
  const p = await P();
  const s = await S(p);
  const c = await getClip(s, a.track, a.index);
  const ed = ppro.SequenceEditor.getEditor(s);
  const ok = tx(p, "Clone clip", (ca) => {
    ca.addAction(ed.createCloneTrackItemAction(c, tt(a.offset || 0),
      a.videoOffset || 0, a.audioOffset || 0, a.alignToVideo !== false, !!a.insert));
  });
  return { cloned: ok };
};

OPS.disable = async (a) => {
  const p = await P();
  const s = await S(p);
  const c = await getClip(s, a.track, a.index);
  const ok = tx(p, "Toggle clip", (ca) => ca.addAction(c.createSetDisabledAction(a.disabled !== false)));
  return { ok, disabled: a.disabled !== false };
};

OPS.rename = async (a) => {
  const p = await P();
  const s = await S(p);
  const c = await getClip(s, a.track, a.index);
  const ok = tx(p, "Rename clip", (ca) => ca.addAction(c.createSetNameAction(a.name)));
  return { ok, name: a.name };
};

// ---- effects ----
OPS["effects.list"] = async (a) => {
  const names = await ppro.VideoFilterFactory.getMatchNames();
  let display = [];
  try { display = await ppro.VideoFilterFactory.getDisplayNames(); } catch (e) {}
  let out = names.map((m, i) => ({ matchName: m, name: display[i] || "" }));
  if (a && a.filter) {
    const f = String(a.filter).toLowerCase();
    out = out.filter((x) => x.matchName.toLowerCase().includes(f) || (x.name || "").toLowerCase().includes(f));
  }
  return { count: out.length, effects: out };
};

OPS["effect.add"] = async (a) => {
  const p = await P();
  const s = await S(p);
  const c = await getClip(s, a.track, a.index);
  const chain = await c.getComponentChain();
  const comp = await ppro.VideoFilterFactory.createComponent(a.matchName);
  if (!comp) throw new Error(`Unknown effect matchName "${a.matchName}".`);
  const at = a.at !== undefined ? a.at : chain.getComponentCount();
  const ok = tx(p, "Add effect", (ca) => ca.addAction(chain.createInsertComponentAction(comp, at)));
  return { added: ok, matchName: a.matchName, at };
};

OPS["effect.remove"] = async (a) => {
  const p = await P();
  const s = await S(p);
  const c = await getClip(s, a.track, a.index);
  const chain = await c.getComponentChain();
  const ci = await resolveComponentIndex(chain, a.effect !== undefined ? a.effect : a.componentIndex);
  let ok = false;
  p.lockedAccess(() => {
    const comp = chain.getComponentAtIndex(ci);
    ok = p.executeTransaction((ca) => ca.addAction(chain.createRemoveComponentAction(comp)), "Remove effect");
  });
  return { removed: ok, effect: ci };
};

OPS["effect.params"] = async (a) => {
  const p = await P();
  const s = await S(p);
  const c = await getClip(s, a.track, a.index);
  const chain = await c.getComponentChain();
  const ci = await resolveComponentIndex(chain, a.effect !== undefined ? a.effect : a.componentIndex);
  let comp = null, n = 0;
  p.lockedAccess(() => { comp = chain.getComponentAtIndex(ci); n = comp.getParamCount(); });
  const out = [];
  for (let i = 0; i < n; i++) {
    const rec = { index: i };
    let prm = null;
    p.lockedAccess(() => { prm = comp.getParam(i); });
    try { rec.name = prm.displayName; } catch (e) {}
    try { rec.timeVarying = prm.isTimeVarying(); } catch (e) {}
    try { const kf = await prm.getStartValue(); rec.value = kf && kf.value ? kf.value.value : null; } catch (e) {}
    out.push(rec);
  }
  let name = "";
  try { name = await comp.getDisplayName(); } catch (e) {}
  return { effect: name, componentIndex: ci, params: out };
};

OPS["effect.set"] = async (a) => {
  const p = await P();
  const s = await S(p);
  const c = await getClip(s, a.track, a.index);
  const chain = await c.getComponentChain();
  const ci = await resolveComponentIndex(chain, a.effect !== undefined ? a.effect : a.componentIndex);
  let ok = false, pname = a.param;
  p.lockedAccess(() => {
    const comp = chain.getComponentAtIndex(ci);
    const pi = resolveParamIndex(comp, a.param);
    pname = pi;
    const prm = comp.getParam(pi);
    p.executeTransaction((ca) => ca.addAction(prm.createSetTimeVaryingAction(false)), "Static param");
    const kf = prm.createKeyframe(a.value);
    ok = p.executeTransaction((ca) => ca.addAction(prm.createSetValueAction(kf, true)), "Set param");
  });
  return { set: ok, effect: ci, param: a.param, paramIndex: pname, value: a.value };
};

// keys: [{t: seconds, v: value, interp: "linear"|"hold"|"bezier"}]
OPS["effect.keys"] = async (a) => {
  const p = await P();
  const s = await S(p);
  const c = await getClip(s, a.track, a.index);
  const chain = await c.getComponentChain();
  const MODE = { linear: 0, hold: 4, bezier: 5, ease: 5 };
  const ci = await resolveComponentIndex(chain, a.effect !== undefined ? a.effect : a.componentIndex);
  let ok = false;
  p.lockedAccess(() => {
    const comp = chain.getComponentAtIndex(ci);
    const prm = comp.getParam(resolveParamIndex(comp, a.param));
    p.executeTransaction((ca) => ca.addAction(prm.createSetTimeVaryingAction(true)), "Enable keyframes");
    ok = p.executeTransaction((ca) => {
      for (const k of a.keys) {
        const kf = prm.createKeyframe(k.v);
        kf.position = tt(k.t);
        ca.addAction(prm.createAddKeyframeAction(kf));
      }
    }, "Add keyframes");
    for (const k of a.keys) {
      if (!k.interp) continue;
      const mode = MODE[String(k.interp).toLowerCase()];
      if (mode === undefined) continue;
      p.executeTransaction((ca) =>
        ca.addAction(prm.createSetInterpolationAtKeyframeAction(tt(k.t), mode)), "Interp");
    }
  });
  return { keyframed: ok, count: a.keys.length };
};

// ---- transitions ----
OPS["transitions.list"] = async (a) => {
  const names = await ppro.TransitionFactory.getVideoTransitionMatchNames();
  let out = names.map((m) => ({ matchName: m }));
  if (a && a.filter) out = out.filter((x) => x.matchName.toLowerCase().includes(String(a.filter).toLowerCase()));
  return { count: out.length, transitions: out };
};

OPS["transition.add"] = async (a) => {
  const p = await P();
  const s = await S(p);
  const c = await getClip(s, a.track, a.index);
  const trans = await ppro.TransitionFactory.createVideoTransition(a.matchName);
  if (!trans) throw new Error(`Unknown transition "${a.matchName}".`);
  const opts = ppro.AddTransitionOptions();
  const pos = (a.position || "end").toLowerCase();
  if (pos === "start") opts.setApplyToStart(true);
  if (a.duration !== undefined && opts.setDuration) { try { opts.setDuration(tt(a.duration)); } catch (e) {} }
  if (a.alignment !== undefined && opts.setTransitionAlignment) { try { opts.setTransitionAlignment(a.alignment); } catch (e) {} }
  const ok = tx(p, "Add transition", (ca) => ca.addAction(c.createAddVideoTransitionAction(trans, opts)));
  return { added: ok, matchName: a.matchName, position: pos };
};

OPS["transition.remove"] = async (a) => {
  const p = await P();
  const s = await S(p);
  const c = await getClip(s, a.track, a.index);
  const pos = (a.position || "end").toLowerCase() === "start"
    ? ppro.Constants.TransitionPosition.START
    : ppro.Constants.TransitionPosition.END;
  const ok = tx(p, "Remove transition", (ca) => ca.addAction(c.createRemoveVideoTransitionAction(pos)));
  return { removed: ok };
};

// ---- graphics / markers / export ----
OPS.mogrt = async (a) => {
  const p = await P();
  const s = await S(p);
  const ed = ppro.SequenceEditor.getEditor(s);
  let items = [];
  p.lockedAccess(() => {
    items = ed.insertMogrtFromPath(a.path, tt(a.at || 0),
      a.videoTrack !== undefined ? parseTrack(a.videoTrack).idx : 1,
      a.audioTrack !== undefined ? parseTrack(a.audioTrack).idx : 1);
  });
  return { inserted: items.length > 0, count: items.length };
};

OPS["mogrt.dir"] = async () => ({ path: await ppro.SequenceEditor.getInstalledMogrtPath() });

OPS["marker.add"] = async (a) => {
  const p = await P();
  const s = await S(p);
  const markers = await ppro.Markers.getMarkers(s);
  const ok = tx(p, "Add marker", (ca) =>
    ca.addAction(markers.createAddMarkerAction(a.name || "marker", a.type || "Comment",
      tt(a.at || 0), tt(a.duration || 0), a.comment || "")));
  return { added: ok, name: a.name, at: Number(a.at || 0) };
};

OPS.export = async (a) => {
  const p = await P();
  const s = await S(p);
  const em = ppro.EncoderManager.getManager();
  if (!em.isAMEInstalled) throw new Error("Adobe Media Encoder is not installed.");
  const type = (a.type || "queue").toLowerCase() === "immediate"
    ? ppro.Constants.ExportType.IMMEDIATELY
    : ppro.Constants.ExportType.QUEUE_IN_AME;
  const ok = await em.exportSequence(s, type, a.output, a.preset, a.full !== false);
  return { queued: ok, output: a.output, preset: a.preset };
};

OPS.save = async () => ({ saved: await (await P()).save() });

// ---- full-surface escape hatch ----
// Runs a snippet against the live API so any of the 428 methods is reachable
// even before it has a named op above. Local only; driven from this machine.
OPS.run = async (a) => {
  const fn = new Function("ppro", "P", "S", "tt", "secs", "tx", "getClip", "clipsOn",
    "findProjectItem", "describeClip", "parseTrack",
    '"use strict"; return (async () => { ' + a.code + " })();");
  const r = await fn(ppro, P, S, tt, secs, tx, getClip, clipsOn, findProjectItem, describeClip, parseTrack);
  return r === undefined ? { ok: true } : r;
};

// The words were already heard once, by Whisper, when the clip was indexed.
// Pushing them in beats re-transcribing in Premiere on every count: it is
// instant, it costs nothing, and the text is the same text the index searched,
// so what the editor reads on the timeline matches what the brief was built on.
OPS["transcript.push"] = async (a) => {
  const p = await P();
  const item = await findProjectItem(p, a.item);
  let clip = null;
  try { clip = ppro.ClipProjectItem.cast(item); } catch (e) {}
  if (!clip) throw new Error(`"${a.item}" is not a clip that can hold a transcript.`);
  const segs = ppro.Transcript.importFromJSON(
    typeof a.transcript === "string" ? a.transcript : JSON.stringify(a.transcript));
  const ok = tx(p, "Import transcript", (ca) =>
    ca.addAction(ppro.Transcript.createImportTextSegmentsAction(segs, clip)));
  return { pushed: ok, item: a.item };
};

OPS["transcript.has"] = async (a) => {
  const p = await P();
  const item = await findProjectItem(p, a.item);
  let clip = null;
  try { clip = ppro.ClipProjectItem.cast(item); } catch (e) {}
  if (!clip) return { item: a.item, transcript: false };
  return { item: a.item, transcript: !!ppro.Transcript.hasTranscript(clip) };
};

OPS.ops = async () => ({ ops: Object.keys(OPS).sort() });

window.DaemnOps = {
  list: () => Object.keys(OPS).sort(),
  run: async (op, args) => {
    const fn = OPS[op];
    if (!fn) throw new Error(`Unknown op "${op}". Known: ${Object.keys(OPS).sort().join(", ")}`);
    return await fn(args || {});
  }
};
