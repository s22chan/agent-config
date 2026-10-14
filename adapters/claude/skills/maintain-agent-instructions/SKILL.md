---
name: maintain-agent-instructions
description: Add, fix, or clarify agent rules, skills, commands, and operational configuration by locating the authoritative owner and validating the intended routing. Use for instruction or policy changes, not ordinary implementation configuration whose owner is already explicit.
---

# Maintain Agent Instructions

For Claude, an unqualified personal rule targets the personal `CLAUDE.md` or an
applicable personal skill. A subagent inherits the current session's startup
snapshot, so validate a loaded instruction or configuration change in a newly
created Claude session. Start one yourself with a headless `claude -p` run from
Bash: it is a new process that loads the edited files at startup, so no user
action is needed. Give each arm its own run with only the prompt the evaluation
allows, confirm from its output that it loaded the edited rule (or, for the
unedited arm, did not), and use `--allowedTools` to keep it read-only.

A new session still runs this machine's session-start hooks and loads its
auto-memory, which inject handoff and memory notes that can hold the incident,
its fix, or this evaluation's earlier results. Start every arm with
`--settings '{"disableAllHooks": true, "autoMemoryEnabled": false}'`; the rules
in `CLAUDE.md` still load. Put into the prompt any memory the author had. Before
the arms, run one probe that asks a session to quote what it was given at
startup about the topic, and continue only when it answers none.

@~/agent-config/shared/skills/maintain-agent-instructions/shared.md
