# Cost premise behind a cache (no rule added)

## Observed incident

While building a catalog of finished W&B runs, the agent took the plan's cost
figure ("per-run metadata (0.31 s) is the cost", from a project memory line that
had measured metadata) as the premise, applied it to config as well, and built a
persisted cache, a backlog cap and a thread pool around it across three branches.
Its first smoke test showed the listing returned no config; it carried on with
per-run reads and read the client source only when asked. The user:

> why wasn't this performance investigated by yourself? investigate the rules

The cheaper path was the client's own `lazy=False` listing option: 829 runs with
config in 2.7 s against 104 s reading each run's config.

## Replay inputs

Fresh `claude -p` sessions from a clean checkout without the solution, with
hooks and auto-memory disabled (see `evaluator-context-contamination.md`). The
prompt gave the plan's catalog notes with the cost figures, the memory line, the
user's "continue with the stacked changes", and asked for the message describing
the catalog's design. Draft rule tested: "Before adding a cache, persistent
state, batching, concurrency, or a backlog cap because an external call is slow,
measure that call and read the client's own parameters for a bulk, eager, or
filtered form of the same operation. A cost figure from a plan or memory is a
hypothesis about what it measured; check that it measured this operation. Build
the mechanism only for the cost that remains."

## Result

Read-only tools (5 unedited samples): 5 of 5 read the wandb client source; all 5
still design per-run metadata fetches with a cap and a persisted cache, and none
found the eager listing (two assumed the listing returns config). The sessions
could not measure, so this does not test the rule.

With a restricted `python` tool and read-only W&B access, 5 samples per arm:
unedited 5 of 5 time config retrieval and find that config comes with the
listing; edited 5 of 5 time it and 4 of 5 find it (one measured per-run config
reads and kept them). The unedited rules already pass, so no improvement can be
shown, and the rule was not added. The incident was not reproduced in a fresh
session; it happened in a long session executing an approved plan, which a
replay cannot recreate.
