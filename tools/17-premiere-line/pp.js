#!/usr/bin/env node
/* pp — the command door into Premiere.
   Usage:  node pp.js <op> '<json args>'
           node pp.js state
           node pp.js place '{"item":"hook_a.mp4","at":0,"videoTrack":"V1"}'
           node pp.js recipe punch-in '{"track":"V1","index":0}'
   Starts the relay if it is not already up. */

const http = require("http");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const RELAY = { host: "127.0.0.1", port: 7878 };
const HERE = __dirname;

function req(pathname, method, payload, timeout) {
  return new Promise((resolve, reject) => {
    const data = payload ? JSON.stringify(payload) : null;
    const r = http.request({
      host: RELAY.host, port: RELAY.port, path: pathname, method,
      headers: data ? { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(data) } : {}
    }, (res) => {
      let b = "";
      res.on("data", (c) => (b += c));
      res.on("end", () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(b || "{}") }); }
        catch (e) { resolve({ status: res.statusCode, body: { raw: b } }); }
      });
    });
    r.on("error", reject);
    if (timeout) r.setTimeout(timeout, () => { r.destroy(new Error("relay timeout")); });
    if (data) r.write(data);
    r.end();
  });
}

async function relayUp() {
  try { const r = await req("/health", "GET", null, 1500); return r.body; }
  catch (e) { return null; }
}

async function ensureRelay() {
  let h = await relayUp();
  if (h) return h;
  const out = fs.openSync(path.join(HERE, "logs", "relay.out"), "a");
  const child = spawn(process.execPath, [path.join(HERE, "relay.js")], {
    detached: true, stdio: ["ignore", out, out]
  });
  child.unref();
  for (let i = 0; i < 30; i++) {
    await new Promise((r) => setTimeout(r, 200));
    h = await relayUp();
    if (h) return h;
  }
  throw new Error("Could not start the relay.");
}

function loadRecipe(name) {
  const f = path.join(HERE, "recipes", name.replace(/\.json$/, "") + ".json");
  if (!fs.existsSync(f)) {
    const have = fs.readdirSync(path.join(HERE, "recipes")).filter((x) => x.endsWith(".json"))
      .map((x) => x.replace(/\.json$/, ""));
    throw new Error(`No recipe "${name}". Have: ${have.join(", ") || "(none yet)"}`);
  }
  return JSON.parse(fs.readFileSync(f, "utf8"));
}

// substitute {{track}} {{index}} {{dur}} etc. into a recipe's steps
function fill(obj, vars) {
  if (typeof obj === "string") {
    const whole = obj.match(/^\{\{(\w+)\}\}$/);
    if (whole) return vars[whole[1]] !== undefined ? vars[whole[1]] : obj;
    return obj.replace(/\{\{(\w+)\}\}/g, (m, k) => (vars[k] !== undefined ? vars[k] : m));
  }
  if (Array.isArray(obj)) return obj.map((x) => fill(x, vars));
  if (obj && typeof obj === "object") {
    const o = {};
    for (const k in obj) o[k] = fill(obj[k], vars);
    return o;
  }
  return obj;
}

async function submit(op, args, timeout) {
  const r = await req("/submit", "POST", { op, args, timeout: timeout || 60000 }, (timeout || 60000) + 5000);
  if (r.status !== 200) {
    const msg = (r.body && r.body.error) || JSON.stringify(r.body);
    throw new Error(msg);
  }
  return r.body.data;
}

(async () => {
  const [, , op, ...rest] = process.argv;
  if (!op || op === "--help") {
    console.log("pp <op> '<json>'   |   pp recipe <name> '<json vars>'");
    console.log("pp build <project folder>   — lay a whole cut on the timeline");
    console.log("pp captions <project folder> — push the indexed words onto those clips");
    console.log("pp health");
    process.exit(0);
  }

  if (op === "health") {
    const h = await ensureRelay();
    console.log(JSON.stringify(h, null, 2));
    return;
  }

  await ensureRelay();

  // build a whole cut from a project folder the footage index wrote
  if (op === "build") {
    const dir = rest[0];
    if (!dir) throw new Error("build needs a project folder");
    const seqFile = path.join(dir, "sequence.json");
    if (!fs.existsSync(seqFile)) throw new Error("no sequence.json in " + dir);
    const seq = JSON.parse(fs.readFileSync(seqFile, "utf8"));
    const clips = seq.clips || [];
    if (!clips.length) throw new Error("that project has no scenes");

    const files = clips.map((c) => path.resolve(dir, c.file));
    const missing = files.filter((f) => !fs.existsSync(f));
    if (missing.length) throw new Error("missing scene files:\n  " + missing.join("\n  "));

    const steps = [];
    // Import first, then let Premiere build the sequence from the opening clip
    // so frame size, rate and audio match the footage instead of a guessed preset.
    steps.push(["import", { files }]);
    const name = seq.name || path.basename(dir);
    steps.push(["sequence.fromMedia", { name, items: [path.basename(files[0])] }]);
    steps.push(["sequence.activate", { name }]);
    // fromMedia already lays the opening clip down; the rest go after it, each
    // at the position the brief gave it.
    for (let i = 1; i < clips.length; i++) {
      steps.push(["place", {
        item: path.basename(files[i]),
        at: clips[i].start_on_timeline,
        videoTrack: "V1", audioTrack: "A1", mode: "overwrite",
      }]);
    }
    for (const c of clips) {
      if (!c.marker) continue;
      steps.push(["marker.add", {
        name: String(c.n).padStart(2, "0") + " · " + c.marker.slice(0, 60),
        at: c.start_on_timeline, comment: c.marker,
      }]);
    }

    const done = [];
    for (const pair of steps) {
      process.stderr.write("  " + pair[0] + " " + (pair[1].item || pair[1].name || "") + "\n");
      done.push({ op: pair[0], out: await submit(pair[0], pair[1], 120000) });
    }
    console.log(JSON.stringify({
      built: name, scenes: clips.length, runtime: seq.clips.reduce((a, c) => a + c.duration, 0),
      captions: fs.existsSync(path.join(dir, "captions.srt")) ? path.join(dir, "captions.srt") : null,
      steps: done.length,
    }, null, 2));
    return;
  }

  // Push the words we already have onto every clip in a built project, so the
  // Captions panel has a transcript to make captions from without Premiere
  // listening to the footage again.
  if (op === "captions") {
    const dir = rest[0];
    if (!dir) throw new Error("captions needs a project folder");
    const rec = JSON.parse(fs.readFileSync(path.join(dir, "project.json"), "utf8"));
    const seq = JSON.parse(fs.readFileSync(path.join(dir, "sequence.json"), "utf8"));
    const done = [];
    for (const c of seq.clips || []) {
      const sc = (rec.scenes || []).find((x) => x.n === c.n) || {};
      const words = (sc.spoken || "").trim();
      if (!words) { done.push({ n: c.n, skipped: "nothing spoken" }); continue; }
      const item = path.basename(c.file);
      // One segment per scene, timed to the cut. Premiere re-splits into
      // caption lines itself; what it must not do is guess the words.
      const payload = { segments: [{ start: 0, end: c.duration, text: words,
                                     speakerId: sc.creator || "speaker" }] };
      try {
        done.push({ n: c.n, item, out: await submit("transcript.push",
          { item, transcript: payload }, 120000) });
      } catch (e) { done.push({ n: c.n, item, error: e.message }); }
    }
    console.log(JSON.stringify({ project: rec.name, clips: done.length, done }, null, 2));
    return;
  }

  if (op === "recipe") {
    const name = rest[0];
    const vars = rest[1] ? JSON.parse(rest[1]) : {};
    const rec = loadRecipe(name);
    const merged = Object.assign({}, rec.defaults || {}, vars);
    const results = [];
    for (const step of rec.steps) {
      const filled = fill(step, merged);
      const stepOp = filled.op;
      delete filled.op;
      const out = await submit(stepOp, filled);
      results.push({ op: stepOp, out });
    }
    console.log(JSON.stringify({ recipe: name, applied: results.length, results }, null, 2));
    return;
  }

  const args = rest[0] ? JSON.parse(rest[0]) : {};
  const out = await submit(op, args);
  console.log(JSON.stringify(out, null, 2));
})().catch((e) => {
  console.error("ERROR: " + e.message);
  process.exit(1);
});
