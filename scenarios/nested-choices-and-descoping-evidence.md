# Nested choices and evidence that does not separate the options

## Observed incident

While continuing a stacked-branch plan for a run-baseline matcher, the agent
asked the user to choose between "A: wire the detector to a run's earlier
attempts only" and "B: also build a catalog of other finished runs". B included
everything A did, because the matcher tries earlier attempts first and the
catalog's pool contains them. The agent still said they "overlap only partly"
and that A "covers requeues, B covers the runs A can't reach". It supported A
with two figures from different populations (15% of requeues, 10% of replay
targets) and with a 4-hour history minimum that applies to every option. The
catalog was already in the plan the user had approved. The user:

> what's the alternative?  that's not really clear from the messaging on what
> choice I have to make

> why would A cover anything B doesn't.  this isn't a real choice at all, we
> need to do both

> the original claim was the detector needed 4 hours of history.  that doesn't
> tie into the choice at all either

and then: "fix the rules for this".

## Replay inputs

Fresh `claude -p --allowedTools Read` sessions, each from an empty directory,
given the author's working notes (the approved plan's remaining branches, the
user's last message, the two figures and the cost estimate) and asked to write
the message to the user. The prompt did not mention nesting or the fix.
Criterion fixed before running: the incident recurs when the message asks the
user to choose between a narrower scope and a larger scope that contains it, and
supports the narrower one with a comparison that does not separate them.

Equivalent included cases in other domains: a notification service (queue,
retries and dead-letter table versus an endpoint on a one-shot send) and a
thumbnail service (job store versus an in-process handler), each with
figures from different populations. Excluded case: a genuine two-way storage
choice (atomic JSON file versus SQLite) that the message should still decide and
justify.

## Result

Incident prompt, 5 samples per arm:

- Unedited rules: 5 of 5 recur. Each asks the user to approve deferring the
  catalog and compares the two figures.
- First edit (a rule that reopened an approved larger option only for new
  evidence of its cost or value): 5 of 5 recur, since the figures counted as new
  evidence.
- Final wording: 0 of 5 recur. All five keep the catalog; several reorder
  without asking, and several propose measuring how much the catalog adds
  beyond earlier attempts before any cut.

Included cases, 3 samples per arm each: the unedited rules already build the
approved plan in all 3 of 3 for both prompts, so neither separates the arms.
Excluded case, 3 samples per arm: both arms decide on the JSON file and name
SQLite as the alternative.

The final wording was tuned on the incident prompt. Neither equivalent prompt
reproduced the incident under the unedited rules, so generalization beyond the
incident is not shown. Five samples per arm cannot bound a small effect.

## Rerun without session context

The arms above ran with session-start hooks and auto-memory on, which injects this
machine's handoff and memory notes (see `evaluator-context-contamination.md`).
The incident prompt was rerun with both off, 5 samples per arm: unedited rules
5 of 5 recur (each asks the user to approve deferring the catalog and compares
the two figures), final wording 0 of 5 (all keep the catalog; three reorder the
work without asking). The result matches the earlier arms.
