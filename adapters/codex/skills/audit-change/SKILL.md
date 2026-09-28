---
name: audit-change
description: Run a report-only audit of a branch, patch, or PR-sized change across code, design, history, test, documentation, and commit-series review lanes. Use for a comprehensive or lane-selective audit without fixes; do not use to implement findings or replace an ordinary single-purpose review.
---

# Codex adapter

Read and follow the [shared audit workflow](shared.md). This file supplies only
Codex-specific routing and isolation mechanics.

Run this skill only from a Sol session at `high` reasoning effort. Check
explicit session or runtime metadata when available. Stop only when that
metadata reports a different model or effort; inability to inspect the
initiating session is not a mismatch. Treat the user's confirmation that the
session is Sol/high as sufficient.

Map shared workflows to these Codex skills:

- `design-python-code` -> `$design-python-code`
- `grill-change` -> `$grill-change`
- `verify-behavioral-tests` -> `$verify-behavioral-tests`
- `polish-docs` -> `$polish-docs`
- `polish-commits` -> `$polish-commits`
- `verify-technical-evidence` -> `$verify-technical-evidence`

On invocation, hand the complete coordinator workflow to one fresh default
agent with `model: gpt-6-sol`, `fork_turns: none`, and `high` reasoning effort.
Give it the exact arguments, repository path, revision context, and this skill's
path. The initiating thread waits for and returns that coordinator's result. If
the delegation message identifies the current agent as the audit coordinator,
continue here and do not create another coordinator.

Create one fresh judgment agent per selected lane or decision-owner shard with
`model: gpt-5.6-sol`, `fork_turns: none`, and `high` reasoning effort. Never use
a higher reasoning effort for this workflow. Give each agent the compact scope
index and its lane-local evidence paths. Keep all dispatches within the shared
reviewer and evidence budgets. Construct every delegation with the same review
contract and shared scope first, in the same field order, followed by the lane
or shard identity, rubric, workflow paths, and lane-local evidence. Keep the
shared prefix byte-identical: exclude timestamps, random identifiers, and
lane-local values from it.

When more than one judgment agent is planned, dispatch the first agent in the
recorded allocation by itself and wait for its final result before dispatching
another. This completed request primes the common model prefix without consuming
an extra reviewer slot. Then dispatch the remaining independent agents in
parallel when collaboration slots permit and queue the rest. A single-agent
audit dispatches normally. Do not create a separate mapping or cache-priming
agent.

The root owns scope resolution, evidence materialization, final verification,
and merging. Keep every judgment agent read-only and tell it not to spawn
descendants. Use the live collaboration tree to verify liveness before a
mutation probe. Codex agents share the filesystem, so do not delegate mutation
probes or run them concurrently with reviewer turns.

For a tests-lane mutation, follow
[isolated mutation probes](references/mutation-probes.md). The local procedure
defines Codex's disposable worktree setup, execution, and cleanup.
