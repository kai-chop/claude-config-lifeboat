# claude-config-lifeboat

![License: MIT](https://img.shields.io/badge/license-MIT-green) ![For: Claude Code](https://img.shields.io/badge/for-Claude%20Code-blue) ![Backup: secret--safe](https://img.shields.io/badge/backup-secret--safe-brightgreen) ![Startup: fail--safe](https://img.shields.io/badge/hook-fail--safe-orange)

**A secret-safe disaster-recovery kit for your Claude Code `~/.claude` directory.**

Your `~/.claude` quietly accumulates the things that make your assistant *yours* — rules, skills, agents, commands, hooks, settings, and per-project memory. It lives on **one disk**. If that machine dies (hardware failure, OS reinstall, theft), that accumulated context is gone.

This kit is a small, opinionated way to:

1. **Back up `~/.claude` to a private git repo** — with a whitelist that guarantees secrets, sessions, and caches never leave your machine.
2. **Never forget to back up** — a fail-safe `SessionStart` hook nudges you when your snapshot is stale *and* you have unsaved changes (and stays silent otherwise).
3. **Recover correctly** — a symptom-triage that routes you to the right restore path, and a fix for a subtle trap where a freshly-restored machine trusts its own stale state.

> **Not novel — deliberately.** Plenty of people `git` their dotfiles. This is a clean, secret-safe packaging tuned for Claude Code specifically: the right whitelist, a repeatable save/restore skill, a nudge that won't nag or break startup, and a recovery playbook a *fresh* assistant can follow with zero prior context.

---

## Why a dedicated kit (and not just `git init ~/.claude`)

Three things a naive `git init` gets wrong:

- **Secrets leak.** `~/.claude` contains `.credentials.json`, session logs, and history. A blind `git add -A` publishes them. This kit ships a **whitelist `.gitignore`** (`exclude everything, then re-include only config assets`) so a mistake fails *closed*.
- **Backups rot silently.** A repo you forget to push is not a backup. The kit ships a **staleness nudge** that fires on session start — but only when there's something to save and it's been a while.
- **Recovery has a stale-state trap.** When you restore an old disk image, your assistant's session primer points at that image's *stale* "current state" and happily continues yesterday's work. The kit documents the **startup key** that catches you up to the remote *before* you trust local state.

---

## The 3-layer discipline (why backup is a *nudge*, not auto-push)

Guarantees get stronger as you push them down a layer:

| Layer | Mechanism | Strength |
|---|---|---|
| ① Deterministic guard | A hook/tool that *enforces* the behavior | Strongest — model-independent |
| ② Mechanical audit | A check that *detects and nudges* | Medium — you still decide |
| ③ Prose rule | "Remember to back up" in a doc | Weakest — breaks under load |

A **backup belongs at layer ②, not ①.** Unattended auto-push is tempting but wrong: it can publish a half-broken `~/.claude`, or run into a non-fast-forward and thrash. The safe ceiling is *"the machine never lets you forget; you make the final call."* That's what the nudge hook does.

---

## What's in the box

```
claude-config-lifeboat/
├── claude.gitignore                  # whitelist — drop into ~/.claude/.gitignore
├── skills/git-backup/SKILL.md        # repeatable save + non-destructive restore (Claude Code skill)
├── hooks/backup_staleness_nudge.py   # fail-safe SessionStart nudge (never breaks startup)
├── RESTORE.md                        # generic non-destructive restore guide
├── docs/recovery-routing.md          # symptom triage → Route A (pull) / Route B (clone)
├── docs/startup-key.md               # the stale-state trap and its fix
└── SETUP.md                          # wire it into your own ~/.claude + private repo
```

## Quickstart

See **[SETUP.md](SETUP.md)**. In short: create a **private** backup repo, drop in the whitelist, make `~/.claude` a git work tree, wire the nudge hook, and install the skill. First snapshot in ~5 minutes.

## Recovering a dead/new machine

See **[docs/recovery-routing.md](docs/recovery-routing.md)**. One decision tree, two routes:

- **Route A — the disk survived (full-image restore):** your `~/.claude` already exists but is *stale*. `git pull` to catch up; re-resolve machine-specific paths.
- **Route B — clean machine:** `git clone` your private repo into `~/.claude` (non-destructively). Nothing to salvage locally; your recovery ceiling is the last push.

## License

MIT — see [LICENSE](LICENSE). Adapt freely.
