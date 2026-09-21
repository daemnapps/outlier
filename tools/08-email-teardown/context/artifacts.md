# Artifacts — email-teardown

One artifact per subject. Update it, never open a second one for the same
thing. Before publishing anything here, read this file.

**Damon's working copy is the LIVE page at `http://localhost:8786`** — launchd
serves it (`com.daemn.email-teardown-serve`) and a watcher rebuilds every
brand's page seconds after any prompt, board or census change
(`com.daemn.email-teardown-watch`), the video-board pattern. The artifact is
the shareable mirror; republish it when sharing matters.

**One page per brand** — `pages/<brand>.html`, generated, with `pages/index.html`
listing them. A second brand gets its own artifact registered as its own row
here; it never overwrites another brand's page.

| Brand | Artifact | Link | Mirror |
|---|---|---|---|
| <brand> | Tearing Down an Email | https://claude.ai/code/artifact/a63a2fb0-9bf7-41ea-be37-5ecab532d752 | `pages/<brand>.md` |

The page carries the lane's four stages with every prompt verbatim, the brand's
boards with their email counts, the formats found, and the honest state.
Republish over the same link after any prompt change or run.

**Never hand-edit `pages/*.html`** — it is generated. Change the prompts or the
README and rebuild:

```
python3 tools/build_page.py --brand <brand>
```
