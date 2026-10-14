# Evaluator context contamination

## Observed incident

While testing a rule on fresh `claude -p` sessions, the agent gave each session
the author's notes and a read-only task. Four of five unedited-arm final
messages quoted this session's own measurements ("per-run 104 s, `lazy=False`
2.7 s, GraphQL 1.0 s") as "my earlier test". The sessions had loaded the
machine's session-start hook, which injects the handoff notes the current session
had just written. The user:

> fix the contamination problem in the agent-config

## Replay inputs

Fresh `claude -p --allowedTools Read` sessions from a clean checkout, each asked
what it was given at startup about the speed of fetching W&B run configs and to
answer exactly `none` if nothing.

## Result

Three samples with hooks and auto-memory on: 3 of 3 quote the handoff note with
the figures. Three with `disableAllHooks` only: 0 of 3 quote the figures, 3 of 3
still quote the memory index line. Four with `disableAllHooks` and
`autoMemoryEnabled: false` (two by setting, two by environment variable): 4 of 4
answer `none`. With those flags a session still quotes the edited rule from
`CLAUDE.md`, so the rules under test load. Earlier arms in this session (the
nested-choice rule) ran with hooks and memory on; their notes held no figures from
that test, but their absolute rates are not clean.
