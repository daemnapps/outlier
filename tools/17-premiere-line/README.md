# The Premiere Line

Direct control of Adobe Premiere Pro from a session. Reads the live timeline,
places and trims clips, applies effects and keyframes, adds transitions, inserts
graphics, queues exports — on Damon's open project, as normal undoable edits.

**Artifact:** [The Premiere Line](https://claude.ai/code/artifact/b39daba5-a973-48f8-a904-072a0fc7ef33)
**Playbook:** `playbooks/premiere-editing.md`

## Shape

```
session ──▶ pp.js ──▶ relay 127.0.0.1:7878 ──▶ daemn bridge panel ──▶ Premiere
```

Everything is local. The relay starts itself on first command. The panel is a
UXP plugin installed at
`~/Library/Application Support/Adobe/UXP/Plugins/External/com.daemn.premiere.bridge_1.0.0`
and must be open in Premiere at **Window > Extensions > daemn bridge**.

## Files

| Path | What |
|---|---|
| `plugin/` | The UXP panel — `manifest.json`, `index.html`, `main.js` (poll loop), `ops.js` (31 ops) |
| `relay.js` | Local queue between session and panel |
| `pp.js` | The command door, and the recipe runner |
| `recipes/` | Named looks — Damon's custom effects and transitions |
| `install.sh` | Copies `plugin/` into Premiere's plugin folder |
| `api-26.3.json` | The whole API parsed: 118 types, 428 methods, 28 enums |
| `premierepro-26.3.d.ts` | Adobe's type definitions, the source of that map |
| `page-data.json` | Grouped capability data embedded in the artifact |

## Use

```bash
node pp.js state
node pp.js place '{"item":"hook_a.mp4","at":0,"videoTrack":"V1"}'
node pp.js effect.keys '{"track":"V1","index":0,"effect":"Motion","param":"Scale","keys":[{"t":0,"v":100},{"t":3,"v":112}]}'
node pp.js recipe punch-in '{"track":"V1","index":0}'
```

Times are seconds. Tracks are `V1`/`A1`. Clip `index` counts from 0 along the
track. Effects and params resolve by name.

## After editing the plugin

Re-copy it and restart Premiere — the app only scans for panels at launch:

```bash
./install.sh
```

## Versions

Built against Premiere Pro 26.3.2 (also installed: 25.6.6). The manifest allows
25.1.0 and up, so it loads in both.
