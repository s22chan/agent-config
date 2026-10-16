# Text search used for Python symbol lookups (hook added)

## Observed incident

Across a long working session the agent traced Python callers with `git grep`/`rg`
(counts of 45 and truncated 40 to 60 hit lists) although `CLAUDE.md` says to
prefer the ty LSP for definitions, references and call hierarchy. The grep count
of `create_submitit_executor` callers was off by four (same-named local
functions, a text mention) and its truncated lists led two replay sessions to
write "resolved, no defect" while `parity.py:249` overwrote the suffixed job
name. The user asked whether a hook would fix it, then pointed to
nesaminua/claude-code-lsp-enforcement-kit and said the LSP also gives definition
lookup.

## Design

`shared/hooks/lsp-first-guard.py`, a PreToolUse hook on `Grep|Glob|Bash`
(registered in `preferences/claude.json`). It denies a search whose pattern
reduces to a bare identifier (after stripping anchors, `\b`, `def `/`class `, a
trailing `(`) that has an underscore or an uppercase letter and that the repo
defines as a `def` or `class` one to eight times; a definition lookup points to
`workspaceSymbol`, a reference search to `findReferences`/`incomingCalls`.
Covered surfaces: Grep, Glob filenames, and Bash `grep`/`rg`/`ag`/`ack`/`git grep`.
Passes: literals, phrases, ALL_CAPS constants, names the repo does not define
(keyword arguments, library methods), non-Python globs/types/paths, and calls it
cannot parse. `LSP_FIRST_GUARD=off` disables it. Ideas taken from the kit
(secondhand, read through a page summarizer): symbol detection by name shape,
guarding Grep, Glob and Bash together, non-code carve-outs. Not taken: its
progressive read gate, its pre-delegation hook, its third-party code.
`tests/test_lsp_first_guard.py` runs the hook against a temporary git repo.

## Replay

Fresh `claude -p` sessions (read-only tools incl. LSP, the `fix-audit-findings`
workflow pasted, the audit excerpt, a detached worktree of the audited commit,
auto-memory off, tool calls captured as stream-json), three per arm.

- First hook run was invalid: `--setting-sources project` also dropped the astral
  plugin, so the session had no LSP tool (init tool list: Glob, Grep, Read) and
  two sessions said "the LSP tool, which I don't have here". Fixed by enabling
  `astral@astral-sh` through `--settings`.
- Hook off, current wording: 0 of 3 sessions called the LSP; with an added LSP
  sentence 0 of 3 (the only rounds with captured tool calls). In the earlier
  rounds, which kept only the final text, 2 of 18 sessions mentioned using it.
- Hook on: 3 of 3 sessions called the LSP (2, 4 and 6 LSP calls:
  `workspaceSymbol`, `findReferences`, `incomingCalls`), after 2, 4 and 6 hook
  denials of their `def` and symbol greps.
- Completeness: `parity.py` found in 1 of 3 hook sessions (2 of 3 hook-off
  current wording, 1 of 3 with the LSP sentence). The two others listed the
  callers with `findReferences` but did not read each caller's later
  `update_parameters`, and reported that as "not checked". In the earlier
  no-hook round 3, two of three sessions wrote "resolved, no defect" from a
  truncated search; none of the three hook sessions did.

## Caveats

Three sessions per arm. The hook arm ran under project-only settings plus the
astral plugin, the earlier arms under default sources with hooks disabled, so the
arms are not strictly matched. The hook fixes tool choice; it does not make the
trace of what each caller does complete.

## Outcome

Hook added to the sources and not activated: `~/agent-config/bootstrap.sh` links
it and writes the registration into `~/.claude/settings.json`.
