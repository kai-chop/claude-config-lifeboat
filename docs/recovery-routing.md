# Recovery routing — one decision tree, two routes

When a machine dies or you set up a new one, **triage the symptom first**, then take the
matching route. Your project repos and your `~/.claude` can be judged **independently**
(you may `pull` one and `clone` the other).

```
Symptom 1: Can the new machine boot and run from a restored full-disk image?
  |-- NO  (no image / corrupt / won't boot on new hardware)  ------------> Route B (clone)
  \-- YES  -> go to Symptom 2

Symptom 2: Does ~/.claude exist AND is it a healthy git work tree?
     check:  git -C ~/.claude rev-parse --is-inside-work-tree
             git -C ~/.claude log -1 --oneline
             git -C ~/.claude status
  |-- YES  (a recent-ish commit is HEAD, .git intact)  -----------------> Route A (pull)
  \-- NO   (missing / .git broken / cannot check out)  ------------------> Route B (clone)
```

When in doubt, prefer **Route B** — a clean clone always converges on the exact remote
state. The only thing Route A can salvage that Route B cannot is *local work newer than
the last push* that happens to survive on the restored disk.

---

## Route A — the disk survived (full-image restore): catch up with `pull`

Your `~/.claude` already exists but is **stale** (it is as old as the image) and carries
the **old machine's absolute paths**. Do not clone — catch up.

```bash
cd ~/.claude
git status        # <-- FIRST: is there local work newer than the last push? (only salvage chance)
git stash list    #     if you want to keep uncommitted work, `git stash push -u` before pulling
git fetch origin
git log --oneline HEAD..origin/main   # what you're about to catch up to
git pull --rebase origin main
```
Then **re-resolve machine-specific paths** (drive letters, usernames, install dirs) in
`settings.json` and anything under `**/memory/` that references old locations.

> Do the same `pull`-based catch-up for any project repos that also survived on the image.

## Route B — clean machine: rebuild with `clone`

No local state to catch up. Your recovery ceiling is exactly the last push.

```bash
# ~/.claude is usually non-empty on a fresh install -> clone aside, then reconcile
git clone <PRIVATE_BACKUP_REPO_URL> ~/_claude-restore
# then follow skills/git-backup/SKILL.md "Restore" (rename-aside or overlay) + restart Claude Code
```
There is **no local salvage** in Route B (there is no old disk) — that's expected. Everything
you had at the last push comes back; anything after it is gone.

### Keep the bootstrap OFF the machine (the part people forget)

Route B has a trap: on a **truly blank machine, the recovery instructions are not on the
machine either.** Your `RESTORE.md`, your backup skill, your handoff notes — they all live
*inside the very repos you haven't cloned yet*. Circular.

So the one thing that must survive **outside git and outside the machine** is a tiny
bootstrap card. Keep a one-screen note in your **password manager / a self-addressed email /
printed**, containing only:

- your private repo URL(s) (`~/.claude` backup, project repos) — URLs are not secrets,
- the 5 steps: install `git`/`gh` → `gh auth login` → clone backup into `~/.claude` (non-destructively)
  → restart your assistant → clone your project(s),
- one line of "what's restored / what isn't / recovery ceiling = last push".

Paste that card into a fresh assistant on the blank machine and it can drive the rest. Do **not**
store the card only inside the backup repo — that's the circular trap. Off-machine or it doesn't count.

---

## The catch that makes this worth writing down

The two routes look almost identical (both end in "get to the remote tip + re-resolve paths").
The **only** operational difference is Route A's very first `git status` — the one chance to
notice and rescue local work that never got pushed. Never skip it on a restored disk.

And before you trust *anything* the restored `~/.claude` tells you about "where you were,"
read **[startup-key.md](startup-key.md)** — a freshly-restored assistant will confidently
continue stale work unless you catch it up first.
