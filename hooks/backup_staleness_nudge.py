#!/usr/bin/env python3
"""backup_staleness_nudge.py -- SessionStart nudge when your ~/.claude backup is stale.

Wire this into Claude Code's SessionStart hook (see SETUP.md). It checks whether
~/.claude (a git work tree backed by your PRIVATE config repo) has uncommitted
changes AND its last snapshot is older than a threshold; if so it prints a one-line
reminder to back up. Otherwise it prints nothing.

Design contract (this runs on EVERY session start):
  - FAIL-SAFE: any error (git missing, not a repo, timeout) prints nothing and
    exits 0. It must NEVER block or break session startup.
  - NO NAGGING: it stays silent when there is nothing to back up (a clean tree)
    or when the last snapshot is recent.

Config via environment variables (optional):
  CLAUDE_BACKUP_STALE_DAYS   integer, default 3
  CLAUDE_BACKUP_HINT         the command/phrase to suggest, default below
"""
import os
import subprocess
import sys
import time

CLAUDE_DIR = os.path.expanduser("~/.claude")
STALE_DAYS = int(os.environ.get("CLAUDE_BACKUP_STALE_DAYS", "3"))
BACKUP_HINT = os.environ.get(
    "CLAUDE_BACKUP_HINT",
    "run your backup skill (save ~/.claude to your private config repo)",
)


def _git(*args):
    return subprocess.run(
        ("git", "-C", CLAUDE_DIR) + args,
        capture_output=True, text=True, timeout=5,
    )


def nudge():
    """Return the reminder string, or None if no nudge is warranted."""
    r = _git("log", "-1", "--format=%ct")
    if r.returncode != 0 or not r.stdout.strip():
        return None  # ~/.claude is not a git work tree -> nothing to check
    days = int((time.time() - int(r.stdout.strip())) // 86400)
    st = _git("status", "--porcelain")
    dirty = bool(st.stdout.strip()) if st.returncode == 0 else False
    if dirty and days >= STALE_DAYS:
        return (
            f"[backup] ~/.claude has uncommitted changes and its last snapshot is "
            f"{days} day(s) old -> {BACKUP_HINT}"
        )
    return None


def main():
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        msg = nudge()
        if msg:
            print(msg)
    except Exception:
        return  # fail-safe: never break SessionStart


if __name__ == "__main__":
    main()
