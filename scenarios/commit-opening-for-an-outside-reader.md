# Commit opening that an outside reader cannot follow

## Observed incident

An agent committed a bug fix. Its message opened with a measurement and used
names from the code (a "stall detector", "rows", a config key, an "open-gap
rule") before saying what the component does. After the agent ran the commit
workflow's own verification, the user wrote:

> the explanation of the issue in teh commit is a bit nonsensical to someone
> with no context

The existing guidance asked for plain language, a goal before mechanics, and a
body that makes sense on the target branch. A message can meet all three and
still be unreadable to someone outside the component.

## Classification

Insufficient. Nothing required saying what the affected part does before naming
what failed, glossing a code-local name, or putting measurements after the
events they measure.

## Replay inputs

Fresh `claude -p` sessions with `--settings '{"disableAllHooks": true,
"autoMemoryEnabled": false}' --allowedTools ""`, run from an empty directory.
Each got the user message "commit", the skill text under test, the author's
working notes, and the staged diff, and wrote the commit message. A probe
session first confirmed that the startup context held none of the incident, its
fix, or earlier results. Cases: the original change; a routine version bump;
the same bump with the diff line that describes the component removed.

Scoring rubric, fixed before reading outputs: (R1) the opening says what the
system does before naming what failed, (R2) code-local terms are glossed, (R3)
measurements come after the sequence of events. For the bump cases: count
outputs holding a name that appears in no input, and outputs that describe the
component.

## Arms and counts

| Arm | Original change, openings passing | Bump, name in no input | Bare bump, describes component |
| --- | --- | --- | --- |
| Original rules | 0 of 3 | 0 of 6 | not run |
| First edit | 3 of 3 | 7 of 8 | 0 of 3 |
| Candidate A | 3 of 3 | 2 of 5 | 0 of 3 |
| Candidate B | 2 of 3 | 2 of 5 | 0 of 3 |
| Current (A with the review feedback) | 3 of 3 | 1 of 5 | 0 of 3 |

## What the extra probe showed

The stray name in the bump outputs ("CronCreate") is in no input. With the
three Cron tools removed from the session it still appeared in 4 of 8 runs
under the first edit and 2 of 5 under A. Sessions asked to quote context lines
containing that prefix gave two sentences from another tool's description. The
original rules produced no slip with the same word in context. So the slip
comes from the session's own context, appears when the agent describes the
component, and is not removed by wording alone. The current rules add a
name-check step before committing.

## Not established

- The sample sizes are 3 to 8 per arm, too small to separate 1 of 5 from 0 of 6.
- The tests use a tool-less session, so the name-check step was never run.
- A second change, to code comments and docstrings, showed no effect on
  existing prose and a weak one on new prose, and is not part of this commit.
