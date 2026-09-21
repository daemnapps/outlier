#!/usr/bin/env node
/* daemn premiere relay — the little post office between Claude and the Premiere panel.
   Claude POSTs a command here; the panel polls /next, runs it, POSTs /result.
   Localhost only, no auth, no deps. */

const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = 7878;
const HOST = "127.0.0.1";
const LOG = path.join(__dirname, "logs", "relay.log");

const queue = [];
const results = new Map();
const waiters = new Map();
let seq = 0;
let lastPanelSeen = 0;

function logline(s) {
  const line = new Date().toISOString() + " " + s + "\n";
  try { fs.appendFileSync(LOG, line); } catch (e) {}
}

function body(req) {
  return new Promise((resolve) => {
    let b = "";
    req.on("data", (c) => (b += c));
    req.on("end", () => {
      try { resolve(b ? JSON.parse(b) : {}); } catch (e) { resolve({ __bad: b }); }
    });
  });
}
function send(res, code, obj) {
  const s = JSON.stringify(obj);
  res.writeHead(code, {
    "Content-Type": "application/json",
    "Content-Length": Buffer.byteLength(s),
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type"
  });
  res.end(s);
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://x");
  const p = url.pathname;

  if (req.method === "OPTIONS") return send(res, 200, {});

  // --- panel side ---
  if (p === "/next" && req.method === "GET") {
    lastPanelSeen = Date.now();
    if (!queue.length) { res.writeHead(204); return res.end(); }
    const job = queue.shift();
    logline("DISPATCH " + job.id + " " + job.op);
    return send(res, 200, job);
  }

  if (p === "/result" && req.method === "POST") {
    lastPanelSeen = Date.now();
    const r = await body(req);
    results.set(r.id, r);
    logline("RESULT " + r.id + " ok=" + r.ok + (r.error ? " " + r.error : ""));
    const w = waiters.get(r.id);
    if (w) { waiters.delete(r.id); w(r); }
    return send(res, 200, { received: true });
  }

  // --- claude side ---
  if (p === "/submit" && req.method === "POST") {
    const b = await body(req);
    if (!b.op) return send(res, 400, { error: "need { op }" });
    const id = "j" + ++seq;
    const job = { id, op: b.op, args: b.args || {} };
    queue.push(job);
    logline("QUEUE " + id + " " + b.op);

    const timeoutMs = Number(b.timeout || 30000);
    const panelAlive = Date.now() - lastPanelSeen < 8000;
    if (!panelAlive && !b.force) {
      queue.pop();
      return send(res, 503, {
        error: "The daemn bridge panel is not running in Premiere Pro. " +
               "Open Premiere, then Window > Extensions > daemn bridge."
      });
    }
    const r = await new Promise((resolve) => {
      waiters.set(id, resolve);
      setTimeout(() => {
        if (waiters.has(id)) {
          waiters.delete(id);
          resolve({ id, ok: false, error: "Timed out after " + timeoutMs + "ms waiting for Premiere." });
        }
      }, timeoutMs);
    });
    return send(res, r.ok ? 200 : 500, r);
  }

  if (p === "/health") {
    return send(res, 200, {
      relay: "up",
      port: PORT,
      panelConnected: Date.now() - lastPanelSeen < 8000,
      lastPanelSeen: lastPanelSeen ? new Date(lastPanelSeen).toISOString() : null,
      queued: queue.length,
      served: seq
    });
  }

  send(res, 404, { error: "no such endpoint" });
});

server.on("error", (e) => {
  if (e.code === "EADDRINUSE") {
    console.error("relay already running on " + PORT);
    process.exit(0);
  }
  console.error(e);
  process.exit(1);
});

server.listen(PORT, HOST, () => {
  logline("RELAY UP on " + HOST + ":" + PORT);
  console.log("daemn premiere relay listening on http://" + HOST + ":" + PORT);
});
