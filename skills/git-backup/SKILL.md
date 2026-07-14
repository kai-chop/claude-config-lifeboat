---
name: git-backup
description: Full disaster-recovery backup of ~/.claude to a PRIVATE git repo, and non-destructive restore from it. Save triggers on "back up", "git backup", "snapshot my claude config", "DR backup". Restore triggers on "restore from git backup", "recover my claude config".
argument-hint: "[optional: extra commit message]"
user-invocable: true
---

Extra message: $ARGUMENTS

> Replace `<PRIVATE_BACKUP_REPO_URL>` below with your own private repo URL before use
> (e.g. `https://github.com/<you>/<your-claude-config>.git`). Keep it **private** —
> even with the whitelist, your config/memory is yours.

## Pick a mode first
- "back up / snapshot / DR backup" -> the **Save** steps below.
- "restore / recover" -> jump to the **Restore** section at the bottom.

## Goal
Snapshot the whole `~/.claude` (a git work tree whose `origin` is your PRIVATE
config repo) for full recovery after a machine failure. Take everything at once —
do not cherry-pick; the whitelist `.gitignore` already keeps secrets out.

## Save
1. **Show what will be included** (let the user see before committing):
   ```
   git -C ~/.claude status --short
   ```
2. **Stage all** (the whitelist `.gitignore` excludes secrets/sessions/caches/plugins,
   so `-A` is safe and "everything included" is correct for DR):
   ```
   git -C ~/.claude add -A
   ```
   - **Secret check before push:** confirm `git -C ~/.claude diff --cached --name-only`
     does NOT list `.credentials.json`, `history.jsonl`, `sessions/`, or `session-env/`.
     (The whitelist should already exclude them; this is a second line of defense.)
3. **Commit** (skip and report "no changes" if the tree is clean):
   ```
   git -C ~/.claude commit -m "chore(backup): ~/.claude snapshot YYYY-MM-DD <extra>"
   ```
4. **Push:**
   ```
   git -C ~/.claude push origin main
   ```
5. **Verify** (report the commit hash and that `## main...origin/main` shows no ahead/behind):
   ```
   git -C ~/.claude status -sb | head -1 && git -C ~/.claude log -1 --oneline
   ```

## Rules
- **No destructive git**: never `reset --hard` / `push --force` / `clean -f`. This backup
  is append-only (add -> commit -> push).
- If push is rejected as non-fast-forward, do NOT force. Stop and report; reconcile manually.
- This is a *nudge*-driven habit, not unattended automation — a human makes the final call
  (an unattended auto-push can publish a half-broken state; see README "3-layer discipline").

---

## Restore -- get your structure back on a dead / new machine

**Preconditions:**
- The repo is PRIVATE -> you must be authenticated to clone. Check `gh auth status`
  (logged in, token scope includes `repo`). If not, ask the USER to run `gh auth login`
  in a browser and stop. Never handle tokens for them; auth is per-machine and is
  intentionally NOT in the backup.
- Viewing the repo web page is not enough — restore is only via an authenticated `git clone`.
- `~/.claude` usually already has content -> you cannot clone directly into a non-empty dir.
  Use the non-destructive steps below.

**Steps (non-destructive, no destructive git):**
1. Auth check: `gh auth status` (if not logged in, ask the user to `gh auth login` and stop).
2. Clone somewhere else (do NOT touch `~/.claude`):
   ```
   git clone <PRIVATE_BACKUP_REPO_URL> ~/_claude-restore
   ```
3. Decide how to reconcile with any existing `~/.claude` (irreversible -> confirm with the user):
   - **New / near-empty machine** -> rename existing aside (`~/.claude` -> `~/.claude.bak-YYYYMMDD`),
     then move the clone into place. Most faithful (an exact copy of the repo).
   - **Keep existing, overlay** -> `cp -r ~/_claude-restore/. ~/.claude/` (existing untracked files remain).
4. **Re-resolve machine-specific values.** Old absolute paths (drive letters, usernames,
   install locations) are invalid on the new machine. Fix `settings.json` and anything under
   `**/memory/` that references old paths.
5. **Restart Claude Code** (settings / skills / hooks load at startup).
6. Cleanup: remove `~/_claude-restore` once verified (keep the `.bak` until the user confirms).

**Also needed after restore (excluded from backup by design):** `gh auth login`, plus any
local API keys / external tool setup. These are intentionally not tracked.
