# The startup key — don't let a restored assistant trust its own stale state

## The trap

Many Claude Code setups have a `SessionStart` primer that says, in effect, *"read your
current-state notes and continue where you left off."* That is exactly right on a healthy
machine — and exactly **wrong** on a machine you just restored from an old image.

On a restored (or behind) machine:

1. The session primer fires and points the assistant at the **on-disk** "current state"
   (digests, ledgers, memory) — which is **as old as the image**.
2. The assistant, being helpful, confidently resumes *yesterday's* task from *yesterday's*
   understanding — before anyone has pulled the newer commits from your remote.
3. You now have a fresh assistant doing stale work, and it looks completely normal.

Nothing errors. That's what makes it dangerous.

## The fix — a human "startup key" (or a recovery-aware hook)

Because the primer itself can't tell "healthy" from "restored," the trigger to catch up has
to come from **outside** the stale state. The simplest reliable trigger is a one-line opener
the human pastes first:

```
This machine was just restored from an older image. Before trusting any on-disk
"current state", catch up to the remotes (pull my config repo and my project repos),
then read the recovery guide and report where I actually am and what may be lost.
```

That single message flips the order of operations: **catch up first, trust local state
second.** After the pull, the on-disk notes are current and the primer is safe to follow.

## Why not just automate it away?

You could make the primer "recovery-aware," but the detection is unreliable (a machine that
is merely a few commits behind looks the same as one restored from last week). The honest,
robust design is: keep the primer simple, and make the *human's first sentence* the switch.
It costs one line and it never misfires.

## Companion habit: keep the remote ahead of the disk

This trap only bites when the disk is behind the remote — i.e. exactly when your backups are
working. Pair this with the staleness nudge (see the repo README): the more reliably you push,
the more the restored disk is *behind*, the more the startup key matters. They're two halves
of the same discipline — **push often; catch up before you trust local state.**
