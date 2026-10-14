# Audit findings whose impact depends on evidence not collected

## Observed incident

`/audit` of `sid/comma-qos-chart` (HEAD `aa76404b`, base `origin/main`
`571f681d`) in `/mnt/main0/home/steve.chan/biohub-ai-infra` reported finding 3
as med, "impact unverified": the heartbeat seed in `nccl_comma.sh` runs for
tasks that never inject. The reviewers did not have the alert expression or the
reaper pin, so whether any alert fires was unknown. The user asked:

> 3. what's wrong with this?

The same audit reported finding 6 (low), whose only trigger was the user setting
their own `BIOHUB_COMMA_PATH` to a FIFO or huge file. The user replied:

> 6. isn't this very unlikely, the file size required for this has to be
> monstrous.

## Classification

Finding 3: insufficient. The old rules name evidence gaps only for missing
predecessor content, so a plausible run grades a candidate whose impact depends
on an absent consumer.

Finding 6: not reproduced. The old step 2 already allows labeling it optional
hardening, so it is a noise preference the skill does not state. A rule for it
was drafted, found to change nothing in the replay, and not added.

## Replay inputs

Give a fresh audit root only the skill and one candidate with its evidence.
Cases:

1. B: a pushgateway heartbeat for tasks that never inject, alert rule absent.
2. E: a new `job_id`-labelled metric, alert rule and cardinality limit absent.
3. C: a user override that repoints a shared symlink every user's loader reads,
   code and consumer quoted. A finding is expected.
4. D: a flag that slows only the user's own job. No finding is expected.

## Test arms

Setup: headless `claude -p`, no tools, hooks and memory disabled, skill text and
one candidate in the prompt, evaluator asked to write what the final report says
about the candidate without being given disposition categories. A first run that
listed the categories leaked the fix's vocabulary and is discarded.

- B: old not reported 2/2, new evidence gap 2/2.
- E: old graded low finding 2/2, new evidence gap 2/2.
- C: old finding 3/3, new finding 3/3. A thinner version with no quoted
  consumer was dropped by both arms and is discarded as a test defect.
- D: old not reported 2/2, new not reported 2/2.

These counts were run with the dropped self-inflicted-trigger paragraph in the
new arm; C and D did not separate it from the old skill. Two to three samples
per arm cannot bound the rates.
