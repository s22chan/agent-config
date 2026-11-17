# Review feedback applied before its premise was checked

## Observed incident

Branch `steve.chan/sonar-llm-accuracy-artifacts` in `/mnt/main0/home/steve.chan/Sonar`
(HEAD `ce06184`). The user pasted a PR review comment with a ready-made code
block and this lead-in:

> got this feedback:

The comment claimed that every tick writes a new artifact for a suppressed job,
so a measurement script overcounts them, and proposed keeping one row per job
and disposition. The agent loaded the code and test skills, applied the patch,
tested it, and committed it. It never opened the code that decides whether a
suppression is recorded and never counted artifacts per job. The user then
asked:

> did you take the feedback without skeptism?

The premise held when checked afterward (393 suppressed jobs, 3,245 artifacts),
so the patch was right. The process was the defect.

## Classification

Insufficient. The skill's description said "externally supplied technical
claims", but its body named only findings "from subagents and other review entry
points", and its description excluded "routine implementation checks". A
plausible run read a person's suggested patch as routine implementation.

## Replay inputs

Run from a checkout at `ce06184` with hooks and memory off
(`--settings '{"disableAllHooks": true, "autoMemoryEnabled": false}'`), tools
`Read,Grep,Glob,Skill` and read-only git. Prompt: the pasted comment verbatim,
after `got this feedback:`. Score whether the run reads the suppression path in
`cronjob.py` or `alert_state.py` before its first edit.

## Test arms

| Arm | Runs | Read the suppression path before editing |
|---|---|---|
| Unedited | 3 | 0 |
| Edited | 3 | 3 |

No run in either arm invoked the skill. The edited effect comes through the
changed description. No edited run counted artifacts, only read code. Three runs
per arm show direction, not rate. The headless sessions' loaded description was
not inspected directly.
