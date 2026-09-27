---
description: Multi-lane audit of a change — findings reported, primary worktree untouched
argument-hint: "[subset: review design grill tests docs commits] [--all-lanes] [--max-reviewers N] [--report] [target/base/full tracked tree]"
model: sonnet
effort: high
context: fork
agent: audit-coordinator
background: false
disable-model-invocation: true
---

Report-only audit.

<audit-arguments>$ARGUMENTS</audit-arguments>

# Claude adapter

Read and follow the shared audit workflow imported below. This command supplies
only Claude-specific argument handling, dispatch, and isolation mechanics.

Parse `audit-arguments` before inspecting the repository. An exact lane token
(`review`, `design`, `grill`, `tests`, `docs`, or `commits`) selects that lane;
when any lane token is present, the selected set is exactly the named lanes.
Only a bare invocation uses the default `review`, `design`, `grill`, `tests`,
and `docs` set. Select all six lanes with `--all-lanes`. Consume lane tokens,
`--all-lanes`, `--max-reviewers N`, and `--report` here; treat the remaining
text as scope, target, or base. Reject a missing, non-integer, or non-positive
reviewer limit, and reject a limit smaller than the selected lane count. Record
the selected lanes and reviewer limit in the scope index before dispatch. Reject
an effort override instead of interpreting it as scope; audit reviewer effort
is fixed at high. A full-tree request changes scope and does not select all
lanes.

Map shared workflows to these Claude skills and commands:

- `design-python-code` -> the `design-python-code` skill
- `grill-change` -> `/grill`
- `verify-behavioral-tests` -> the `verify-behavioral-tests` skill
- `polish-docs` -> `/polish-docs`
- `polish-commits` -> `/polish-commits`
- `verify-technical-evidence` -> the `verify-technical-evidence` skill

Create one fresh contained `audit-reviewer-high` agent per selected lane or
decision-owner shard. Never resume a reviewer for a different lane and never
raise reviewer effort above high. Run reviewers sequentially in the foreground
so their results return to this isolated coordinator instead of the invoking
session. The command frontmatter starts a fresh Sonnet/high coordinator, while
each reviewer uses Opus/high. Stop if a reviewer reports a substituted model or
effort. Do not create a separate mapping agent.

The reviewers omit Bash, delegation, and write tools. The root materializes
large diffs, base snapshots, and checker output into disposable local evidence
files without returning their bodies into its own model context. Give each
reviewer the compact scope index, the exact lane rubric text, its referenced
workflow path, and only its lane-local evidence paths. Do not ask a reviewer to
search for its rubric. Keep the root responsible for scope resolution, final
verification, and merging. Use each foreground agent's final response as its
result. Confirm that every reviewer has stopped before a mutation probe.

A direct interactive `/audit` has no access to a hard dollar meter. For a
bounded non-interactive run, use `~/.claude/scripts/audit-change`, which applies
Claude CLI's `--max-budget-usd` limit before invoking this command.

Only when a surviving tests-lane finding requires a mutation, read
`~/.claude/commands/references/audit-mutation-probes.md` and follow its managed
`.claude/worktrees`, `EnterWorktree`, `ExitWorktree`, and cleanup procedure.

@~/agent-config/shared/skills/audit-change/shared.md
