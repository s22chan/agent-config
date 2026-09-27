---
name: maintain-agent-instructions
description: Add, fix, or clarify agent rules, skills, commands, and operational configuration by locating the authoritative owner and validating the intended routing. Use for instruction or policy changes, not ordinary implementation configuration whose owner is already explicit.
---

# Maintain Agent Instructions

For Claude, an unqualified personal rule targets the personal `CLAUDE.md` or an
applicable personal skill. A subagent inherits the current session's startup
snapshot, so validate a loaded instruction or configuration change in a newly
created Claude session.

@~/agent-config/shared/skills/maintain-agent-instructions/shared.md
