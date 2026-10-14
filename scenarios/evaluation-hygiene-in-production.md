# Evaluation hygiene in production code

## Observed incident

While writing the cross-run baseline matcher (`match_baseline`) and its plan,
the agent put two leave-one-out replay rules into the production API and plan
as detector rules: drop peers that started after a `before` cutoff, and drop
peers sharing the target's lineage or Slurm job. The user:

> why do we filter out jobs with the same lineage or slurm job? the goal is to
> find slowdowns, so a job that is requeued is perfectly valid to compare
> against previous runs

and later:

> do we care that the run happened before when all we care is whether this run
> is slow?

The live detector judges a running run against finished runs in a catalog, so
neither rule applies to it. A requeue's earlier attempt is the best baseline.

## Replay inputs

Run a fresh `claude -p --allowedTools Read` session from an empty directory
with a prompt that describes the CronJob detector, the finished-run catalog, the
leave-one-out replay on 314 saved jobs (one run per job), and asks for the
exclusions `match_baseline` applies to the pool. Do not mention the fix.
Excluded case: a replay harness that must hold out the target; it should keep
that exclusion in the harness.

## Result

Unedited rules, 3 samples: 3 of 3 drop every record in the target's lineage
("it would be compared with itself"). Edited rule, 3 samples: 0 of 3 do; all
keep the target's earlier attempts and move leave-one-out and time cuts to the
replay harness. The start-time cutoff was not tested: the prompt gave no replay
timing. Three samples per arm cannot bound a small effect.
