# How creative marketers work with us — the SOP

You never install anything and never touch code. You work inside **Higgsfield
Supercomputer**, which reads our Google Drive and our tools directly. Briefs
come to you there; finished work goes back to Drive from there.

The walkthrough video and this page, together, are the whole onboarding:
**daemn.co/onboarding.html**.

---

## Once — set up (ten minutes)

1. **Get the brand folder link.** One Google Drive link from the owner —
   no invitation, no account to be added to; the folder opens for anyone
   with the link. A Higgsfield account of your own is enough (the owner's
   workspace only matters if you are using its credits).
2. **In Higgsfield Supercomputer → Connectors → Explore**, connect **Google
   Drive** and **GitHub**. Sign in to each when asked.
3. **Put the brand folder in your own Drive.** Open the link, then in Google
   Drive: right-click the folder → *Organize* → *Add shortcut* → into a
   folder you make in *My Drive*. Supercomputer can only see what is in your
   own Drive.
4. **New chat in Supercomputer → the `+` button → Connectors** — check Google
   Drive and GitHub are both ticked for that chat.
5. **Paste the Day-one prompt** (`prompts/01-day-one-v2-damon.md`) with the
   brand's name and the folder link filled in. It clones the tools, finds the brand folder, reads
   the queue and tells you what is open. When it ends with *"Set up for
   <brand> — N briefs open"*, you are done.

## Every session — the loop

1. **New chat → paste the Pull-briefs prompt** (`prompts/02-pull-briefs-v2-damon.md`)
   with the brand's name. Name a brief if you have one; otherwise it takes
   the newest open one.
2. **It syncs first** — pulls the tools for updates, reads the live queue —
   then claims the brief and downloads its package.
3. **It lays the brief out**: the scenes with their clips and voices (or the
   image drafts), the intended cut, what is locked, the known issues, the loop.
   Read it. Watch every clip.
4. **Review** — it walks the checklist with you: same person, same wardrobe,
   same product, slop, sound, words, anything odd. You get a table: KEEP /
   FIX AT CUT / REROLL. Then three to five ideas. **You decide** what gets
   rerolled and which ideas to take.
5. **The asks** — the extras the brief wants: scroll stoppers, headlines,
   variations, extra scenes, formats, styles. It makes them in Higgsfield
   from the same cast and product references. You approve each one.
6. **The edit** — for video, it packs everything into `<brief>--edit` with a
   cut sheet; you take that into Premiere or CapCut. For statics, the finals
   go into `<brief>--finals`.
7. **Deliver** — finished files to `briefs/delivered/<brief>/` on Drive,
   named `<brief>--<what>--v1`, with a `DELIVERED.md` saying what was made,
   what was rerolled, and what is still open. The queue updates itself from
   the folder within the hour.

## The queue

`briefs/QUEUE.md` in each brand folder on Drive. One row per brief: type,
status, who, bounty, due, package. It is rebuilt every hour from the folder —
**open** because the package is there, **claimed** because your claim file is
in `briefs/claims/`, **delivered** because your files are in
`briefs/delivered/<brief>/`. Nobody edits the table by hand; the owner sets
bounty and due dates.

## The rules that never move

- **Nothing invented.** Not a product detail, not a claim, not a person. If
  the brief does not say it, the answer is "not in the brief" — ask.
- **Every face and every product carries its reference.** A person or product
  generated without their reference is a reroll, not a delivery.
- **One ratio.** Everything is made and cut at 9:16, with faces, the product
  and every word inside the centred 4:5 crop — the middle 70% of the frame.
  Nothing is made at 4:5 or 1:1. A swipe that arrives 4:5 or 1:1 is rebuilt at
  9:16 the same way.
- **Never write into the source package.** Deliveries go to `delivered/`.
- **Sync first, every session.** A brief made from yesterday's tools or a
  stale queue is the one that gets sent back.
- **When a door fails — Drive, GitHub, Higgsfield — say which one, in one
  line.** Do not work around it silently.

## When it goes wrong

| what you see | what it means | what to do |
|---|---|---|
| "Something went wrong" opening the brand folder | Supercomputer picked the wrong folder or cached an old one | Paste the folder's Drive link directly into the chat |
| No credits / "no chats" | Wrong Higgsfield workspace, or the free credits are used | Switch workspace (top-left) and refresh, or ask the owner |
| It found the wrong `briefs` folder | Two folders share the name | Give it the path or the link; it must not guess |
| The queue shows a brief you already delivered as open | The files are not in `delivered/<brief>/` under that exact brief name | Check the folder name matches the queue's Brief column |
| "Pull my GitHub repository" says no updates but the SOP changed | The clone is stale | Say "clone https://github.com/daemnapps/prizm-labs again, fresh" |

## Coming next (not yet — do not wait for it)

- AI editing inside the tools: the cut made from the cut sheet without a
  timeline. Until it lands, the edit is yours in Premiere or CapCut.
- A brief-download skill in Higgsfield, so "pull briefs" is one word.
