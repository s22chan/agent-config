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

The initiating thread is the audit root. It owns scope resolution, evidence
materialization, final verification, and merging as specified by the shared
workflow. Do not hand the complete audit to one long-lived child coordinator:
Codex may retain completed descendants against their parent's thread limit until
that parent exits, so queuing more reviewers under that parent can make required
fresh judgments impossible.

Before dispatch, derive one wave's judgment-agent capacity from the runtime's
thread limit and the live collaboration tree: subtract every currently occupied
slot, including the audit root and any ancestors, then reserve one more slot for
a disposable wave coordinator. When the planned judgments exceed that capacity,
partition them into the fewest waves that fit; do not reduce the selected lanes,
merge lane judgments, or count a predictable capacity shortfall as an evidence
gap.

For each wave, create one fresh default coordinator with `model: gpt-6.1-sol`,
`fork_turns: none`, and `high` reasoning effort. Give it the fixed scope index,
the assigned lane or shard delegations, this skill's path, and tell it to make
no judgments of its own. It dispatches all assigned fresh judgment agents
together, collects their final responses without merging them, returns those
raw results, and exits. Confirm that its subtree has left the live collaboration
tree before starting the next wave. Wave coordinators are scheduling machinery,
not judgment contexts, so they do not consume the shared reviewer budget.

If the runtime exposes no usable capacity for even one fresh judgment agent,
report that infrastructure blocker. Do not reuse a completed context or weaken
lane isolation to work around it.

Create one fresh judgment agent per selected lane or decision-owner shard with
`model: gpt-6.1-sol`, `fork_turns: none`, and `high` reasoning effort. Never use
a higher reasoning effort for this workflow. Give each agent the compact scope
index and its lane-local evidence paths. Keep all dispatches within the shared
reviewer and evidence budgets. Construct every delegation with the same review
contract and shared scope first, in the same field order, followed by the lane
or shard identity, rubric, workflow paths, and lane-local evidence. Keep the
shared prefix byte-identical: exclude timestamps, random identifiers, and
lane-local values from it.

Within each wave, dispatch all assigned judgment agents together. Do not run one
agent alone merely to prime the cache: every judgment agent already shares the
byte-identical prefix described above. A one-agent wave is valid only when the
derived capacity or remaining reviewer count is one. Do not create a separate
mapping agent.

Prepare evidence in a few batched calls, each running one deterministic script
that writes files and prints only paths, byte counts, and digests, and do not
read a materialized body back into the root context. Keep every judgment agent
read-only and tell it not to spawn descendants. Use the live collaboration tree
to verify liveness before a mutation probe. Codex agents share the filesystem,
so do not delegate mutation probes or run them concurrently with reviewer turns.

For a tests-lane mutation, follow
[isolated mutation probes](references/mutation-probes.md). The local procedure
defines Codex's disposable worktree setup, execution, and cleanup.
