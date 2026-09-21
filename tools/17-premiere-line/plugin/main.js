/* daemn bridge — panel loop. Polls the local relay for work, runs it, posts the result back. */
const RELAY = "http://127.0.0.1:7878";
const IDLE_MS = 350;
const BACKOFF_MS = 2000;

const $ = (id) => document.getElementById(id);
let running = true;
let missCount = 0;
let doneCount = 0;

function stamp() {
  const d = new Date();
  return d.toTimeString().slice(0, 8);
}
function log(msg, cls) {
  const el = $("log");
  const line = document.createElement("div");
  if (cls) line.className = cls;
  line.textContent = stamp() + "  " + msg;
  el.appendChild(line);
  while (el.childNodes.length > 300) el.removeChild(el.firstChild);
  el.scrollTop = el.scrollHeight;
}
function setStatus(state, text, detail) {
  const dot = $("dot");
  dot.className = "dot" + (state === "on" ? " on" : state === "err" ? " err" : "");
  $("stext").textContent = text;
  if (detail !== undefined) $("detail").textContent = detail;
}

async function poll() {
  while (running) {
    let job = null;
    try {
      const r = await fetch(RELAY + "/next", { method: "GET" });
      if (r.status === 204) {
        if (missCount > 0) {
          missCount = 0;
          setStatus("on", "Connected", doneCount + " commands run");
        }
        await sleep(IDLE_MS);
        continue;
      }
      if (!r.ok) throw new Error("relay " + r.status);
      job = await r.json();
      missCount = 0;
    } catch (e) {
      missCount++;
      if (missCount === 1 || missCount % 20 === 0) {
        setStatus("err", "Waiting for daemn", "relay not answering on 7878");
      }
      await sleep(BACKOFF_MS);
      continue;
    }

    setStatus("on", "Connected", "running " + job.op);
    log("> " + job.op + (job.args && Object.keys(job.args).length
        ? " " + JSON.stringify(job.args).slice(0, 120) : ""));
    let payload;
    try {
      const data = await window.DaemnOps.run(job.op, job.args);
      payload = { id: job.id, ok: true, data };
      doneCount++;
      log("  ok " + JSON.stringify(data).slice(0, 160), "ok");
    } catch (err) {
      payload = { id: job.id, ok: false, error: String((err && err.message) || err) };
      log("  ERR " + payload.error, "bad");
    }
    try {
      await fetch(RELAY + "/result", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    } catch (e) {
      log("  could not return result: " + e, "bad");
    }
    setStatus("on", "Connected", doneCount + " commands run");
  }
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

$("reconnect").onclick = () => {
  missCount = 0;
  log("reconnecting...", "dim");
  setStatus("", "Reconnecting", "");
};
$("clear").onclick = () => { $("log").innerHTML = ""; };

setStatus("", "Starting", "relay " + RELAY);
log("daemn bridge ready — " + window.DaemnOps.list().length + " ops loaded", "dim");
log("ops: " + window.DaemnOps.list().join(" "), "dim");
poll();
