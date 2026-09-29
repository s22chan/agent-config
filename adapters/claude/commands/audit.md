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
raise reviewer effort above high. Launch all reviewers together as foreground
agents in a single message and wait for every one to return, so their results
return to this isolated coordinator instead of the invoking session. Waiting
once keeps the coordinator's prompt cache from expiring between lanes. The command frontmatter starts a fresh Sonnet/high coordinator, while
each reviewer uses Opus/high. A model cannot observe its own effort, so do not
ask a reviewer to state its model or effort and do not act on such a statement.
After each reviewer stops, read its transcript
`~/.claude/projects/*/*/subagents/agent-<agentId>.jsonl` and stop if any
assistant entry has a `message.model` other than `claude-opus-5-5` or an
`effort` or `perTurnEffort` other than `high`; a missing field is unverified,
not a mismatch. Do not create a separate mapping agent.

The reviewers omit Bash, delegation, and write tools. The root materializes
large diffs, base snapshots, and checker output into disposable local evidence
files without returning their bodies into its own model context. Give each
reviewer the compact scope index, the exact lane rubric text, its referenced
workflow path, and only its lane-local evidence paths.

The coordinator's turn limit and prompt-cache cost both grow with every tool
call. When `S22CHAN_AUDIT_EVIDENCE_DIR` is set, keep every evidence file in that
directory and create no other; a headless run pre-approves writes only there,
and only by literal path, so read the value once with `printenv` and never
redirect to a shell variable. Otherwise create one disposable evidence directory. Prepare evidence in a few
batched calls: resolve the revision, base, and
worktree state together, discover instruction files together, and materialize
the diff, base snapshots, log, sizes, and digests in one deterministic script
that prints only paths, byte counts, and digests. Read named downstream files
in one call when their paths are already known. Do not read a materialized body
back into your own context; the reviewers read it.

Reviewers do not read the personal instruction files whole. In the same script,
extract per-lane excerpts of `~/agent-config/instructions/common.md` by `## `
heading into that lane's evidence files, fail if any named heading yields no
lines, and list each excerpt as lane-local evidence. Do not list `common.md` or
`~/.claude/CLAUDE.md` in the shared scope index; the latter governs the
invoking agent's communication, shell, and tool use, not review. Sections per
lane: `review` and `grill` take Code and Verification; `design` takes Code and
Code prose; `tests` takes Verification and Code; `docs` takes Code prose;
`commits` takes Git and review prose and Code prose. When the diff touches agent
instruction or configuration files, add Instruction and configuration changes
to every lane. Repository instruction files stay in the shared scope index.

Construct every reviewer prompt with these headings in this exact order:

1. `# Review contract`: the same literal instructions for every reviewer.
2. `# Audit scope`: the same scope-index path, revision, worktree state,
   applicable-instructions paths, and decision-inventory path in the same field
   order for every reviewer in this audit.
3. `# Lane`: the lane name, exact rubric text, and referenced workflow path.
4. `# Lane evidence`: only that lane's evidence paths and recorded byte count.

Keep the first two sections byte-identical across the audit. Omit timestamps,
random identifiers, and restatements of lane-specific data from them. Put all
lane- or shard-specific values in the final two sections so the reviewers share
the longest stable prompt prefix. This ordering controls representation only;
it does not change the evidence each reviewer receives.

Do not ask a reviewer to search for its rubric. Keep the root responsible for
scope resolution, final verification, and merging. Use each foreground agent's
final response as its result. Confirm that every reviewer has stopped before a
mutation probe.

A direct interactive `/audit` has no access to a hard dollar meter. For a
bounded non-interactive run, use `~/.claude/scripts/audit-change`, which applies
Claude CLI's `--max-budget-usd` limit before invoking this command.

Only when a surviving tests-lane finding requires a mutation, read
`~/.claude/commands/references/audit-mutation-probes.md` and follow its managed
`.claude/worktrees`, `EnterWorktree`, `ExitWorktree`, and cleanup procedure.

@~/agent-config/shared/skills/audit-change/shared.md
