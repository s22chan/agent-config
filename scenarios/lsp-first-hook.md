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

## Follow-up: shell parsing false positives and misses

Observed trigger. While the hook was live, it denied three Bash commands that
were not Python symbol searches, and the user asked "is the LSP rule worth the
false positives". The denied commands were a `grep -E "Passed|Failed|rror"`
filter on a commit's output with a `;` glued to the closing quote, a count
`n=$(git show REV:file | rg -c "name|other" )` with a space before the closing
parenthesis, and a Python heredoc whose body held example search commands.

Cause. `shlex.split` leaves `;` and `)` attached to the word before them, so
the filter was read as a search over a file path, and a command after a glued
`;` or inside `$(` was never recognised as a search at all. The guard also took
a redirection target for a search path and the body of a heredoc for commands.

What the guard did: denied the three commands above, and allowed
`n=$(rg -c symbol src)` and `echo x; rg symbol src` although both search
Python code. What it should do: allow a filter on another command's output
however it is punctuated, deny a symbol search wherever it sits in the line,
and ignore heredoc text and redirection targets.

Change. `shell_tokens` tokenizes with `shlex.shlex(punctuation_chars=True)` so
`;`, `|`, `(`, `)` and redirections are their own tokens, drops heredoc
bodies, treats a newline as a command end, and removes a file descriptor glued
to a redirection (`2>&1`). `.github` joins the non-code paths because the
replay showed `.github/workflows` denied.

Arms, with the same test file on both hooks. The old hook failed 5 of 11 tests
(four new, plus the `.github` case); the patched hook passes all 11, and the
seven original tests pass on it unchanged. Replay of 1,055 distinct commands
containing grep, rg, ag or ack from the last twelve sessions in one repository:
1,011 decisions unchanged, 7 deny to allow (all pipe filters or heredoc text),
37 allow to deny, which is 20 distinct commands: 19 symbol or definition
searches that the old parser had let through and the `.github/workflows` case
the path list now covers.

Caveats. The 20 new denials were judged from the matched segment and its
targets, not by running each search. The replay covers search-like commands
only, so it cannot show a change for other commands. The guard is still
lexical: a search built inside a variable or a script file is not seen.

## Outcome

Hook added to the sources and not activated: `~/agent-config/bootstrap.sh` links
it and writes the registration into `~/.claude/settings.json`.
