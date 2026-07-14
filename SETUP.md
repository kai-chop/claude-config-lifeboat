# SETUP — wire the lifeboat into your own machine

Prerequisites: `git`, the GitHub CLI (`gh`) or equivalent, Python 3, and Claude Code.

## 1. Create a PRIVATE backup repo
Keep it private — even with the whitelist, your rules/skills/memory are yours.
```bash
gh repo create <you>/<your-claude-config> --private
```

## 2. Install the whitelist and make ~/.claude a git work tree
```bash
cp claude.gitignore ~/.claude/.gitignore     # from this kit
cd ~/.claude
git init -b main
git remote add origin https://github.com/<you>/<your-claude-config>.git
```

## 3. VERIFY nothing sensitive is staged (do this before the first commit)
```bash
git add -A
git diff --cached --name-only | grep -iE 'credential|history\.jsonl|sessions/|session-env|\.bak$' \
  && echo "STOP: sensitive files staged — fix .gitignore" \
  || echo "OK: no secrets staged"
```
Only proceed if it prints `OK`.

## 4. First snapshot
```bash
git commit -m "chore(backup): initial ~/.claude snapshot"
git push -u origin main
```

## 5. Install the backup skill
```bash
mkdir -p ~/.claude/skills/git-backup
cp skills/git-backup/SKILL.md ~/.claude/skills/git-backup/SKILL.md
# then edit it and set <PRIVATE_BACKUP_REPO_URL> to your repo
```
Now you can say "back up" / "snapshot my claude config" and Claude runs the Save flow.

## 6. Install the staleness nudge (SessionStart hook)
```bash
mkdir -p ~/.claude/scripts
cp hooks/backup_staleness_nudge.py ~/.claude/scripts/backup_staleness_nudge.py
```
Add a SessionStart hook in `~/.claude/settings.json` (merge with any existing hooks):
```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [
        { "type": "command", "command": "python3 \"$HOME/.claude/scripts/backup_staleness_nudge.py\"" }
      ] }
    ]
  }
}
```
> On Windows, invoke it the way your other hooks do (e.g. `py -3 "%USERPROFILE%\\.claude\\scripts\\backup_staleness_nudge.py"`).
> The script is fail-safe: if anything goes wrong it prints nothing and exits 0, so it can never break startup.

Optional tuning via env vars: `CLAUDE_BACKUP_STALE_DAYS` (default 3), `CLAUDE_BACKUP_HINT`.

## 7. (Recommended) copy RESTORE.md into your repo
```bash
cp RESTORE.md ~/.claude/RESTORE.md
```
So a future *fresh* machine finds the restore steps inside the very thing it restores.

---

That's it. From now on: work normally; when you have unsaved config changes and it's been
a few days, the nudge reminds you; you say "back up"; done. To recover a machine, see
[docs/recovery-routing.md](docs/recovery-routing.md).
