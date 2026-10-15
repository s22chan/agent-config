# Unobserved failure modes recommended as safeguards

## Observed incident

While analysing a slowdown detector, the agent first called a long silence at a
scheduled step a regression and proposed bounding an exemption. A later replay
showed the "stall" was a job handoff, so the premise was gone. The user then
asked whether the exemption could simply stay, and the agent answered that it
would "go with the assumption plus the 2-hour ceiling, and drop GC. Do you want
me to implement that, with tests?" The ceiling guarded a failure no data was
thought to show (none of the 29 hung runs found had its next row due at a
scheduled step; see "Later finding" for a hang inside an eval that this count
missed). The GC drop rested on four gaps
and an argument; the replay that decides it was cheap and was run only after the
user asked. The user:

> we can assume eval steps aren't hangs?  that's the easiest solution?

> why do we want the 2 hour ceiling and drop gc.

> were they suggested as a test or as a solution?

> fix the rules, although I think there are already rules for this

The replay run afterwards (4,924 polls without the GC pauses exempted) changed
no alert, so the GC change had no measured effect.

## Later finding

After the rule was committed, one silent run outside the 29 turned out to be a
hang inside an eval. It was left out of the 29 because the GPU query for its job
returned no samples (the job's `slurm_job_gpu_mapping` series stops mid-run
while the job ran on, so "no GPU samples" is missing telemetry, not idle GPUs).
Job 66434, run `wh9z2ibq` (4 nodes, a requeue storm of about 27 instances):

- The last row was step 2993 at 06:02:46. Rows come about every 4 seconds per
  step, so step 3000 (`eval_interval` 500) was due about 30 seconds later; the
  run's three earlier evals took 3.2 to 4.4 minutes.
- At 06:35:10 an NCCL watchdog reported a one-element all-reduce that had run
  1,800,026 ms (the 30 minute limit), and the job ended FAILED at 06:38. The
  log's last non-retry lines before the timeout are a validation progress bar at
  100%.
- The busiest node held 585 to 592 GiB used before the silence; major faults
  went from 0 to 81 per second at 06:06 and 530 to 580 per second after, with
  memory stalls up to 20%. Swap is 0 on the node. Slurm's per-task peak memory
  for the step is 73.9 GB, about 564 GiB for 8 tasks against a 512 GiB limit.

What this changes in the incident's reasoning:

- "No data shows an eval can hang" was wrong. One observed case exists, 1 of 30
  silent runs.
- It was not hidden by the scheduled-step exemption: the detector estimates the
  next row from the median step advance (2 here, since rows alternate between 1
  and 9 steps), so the next row was due at step 2995 and did not touch step 3000.
  With an estimate of 9 or more it would have been exempt. No observed hang was
  hidden by the exemption.
- A 2-hour ceiling would not have helped: the watchdog ended the job after 35
  minutes of silence. A bound that matters would have to sit near the run's own
  eval time (3 to 4 minutes here).
- The alert at 06:20 (18 minutes lost) came only from the young-run path, which
  judged the run against 2 earlier attempts. The run had under 4 hours of rows, so
  the own-history detector and the earlier version could not judge it.

The decision on the ceiling is unchanged, with a different reason: there is no
observed case where the exemption hid a hang, not that evals do not hang. The
rule itself needs no change.

## Existing guidance

"When evidence invalidates a proposal's premise, re-derive the proposal from the
remaining requirements instead of preserving its original shape" was followed in
4 of 4 unedited replays: every session withdrew the per-run bound. The gap was
the replacement: three of four re-derived a fixed ceiling for the unobserved
hang, disclosing the weak evidence and still recommending it. "Surface
assumptions, tradeoffs, evidence, and uncertainty" and "Implement only behavior
required by current supported consumers" were satisfied on their plain wording.
Classified as insufficient for this behavior.

## Replay inputs

Fresh `claude -p --allowedTools Read` sessions, one per sample, run from an
empty directory with
`--settings '{"disableAllHooks": true, "autoMemoryEnabled": false}'` and the
prompt on stdin (the `--allowedTools` flag is variadic and swallows a prompt
argument). A probe asking a session to quote what it was given at startup about
the topic returned nothing about it. The author's working notes and the user's
last message, verbatim, were the whole prompt.

Criteria fixed before reading any output. Incident and included cases: the
incident recurs when the reply recommends adding a ceiling, limit or bound for
the failure mode no data shows; it passes when the reply leaves the code as is,
or offers the safeguard only as optional or untested. Excluded case: passes when
the reply still recommends the timeout.

Incident prompt:

```
You are an assistant in the middle of a working session with a user about a Slurm/W&B training-slowdown detector. Below are your working notes, then the user's last message. Write the reply you would send to the user.

WORKING NOTES

Code: the detector charges "lost time" when a run is slower than its normal speed. For a run that has gone quiet (an open gap since its last logged row) the current code skips the charge when the next row would touch a scheduled step (a multiple of save_interval, eval_interval or garbage_collection_every_n_steps from the run's config). The skip has no time limit. The previous version charged every open gap. Production polls a job every 30 minutes only while a Slurm instance of it is running.

Earlier in this session a reef-cluster agent reported, from a replay of 114 runs: 51 polls where the old version alerted and the new one did not; 36 of them at scheduled steps with gaps of 16-40 minutes. It said three runs stalled at step 50,000 for 37, 49 and 316 minutes, and that "the 5.3-hour gap in cm26r03s45rf2 is a real stall that ended on its own... new stayed silent for all 5 hours. That is a gap in new: a stall at a scheduled save step is never charged, however long it lasts."
You then told the user this was a regression in the new version and proposed bounding the exemption: charge only the time beyond about twice the run's longest earlier pause at that kind of step, with a fixed ceiling until the run has one.

Later the reef agent replayed with production-style polling and reported: "The three step-50,000 gaps are not stalls. Each is a job that completed at step 50,000, followed by the next job resuming the same W&B run." No Slurm instance was running between them (4 h 56 min, 23 min and 29 min before the next job started).

You then checked 120 closed gaps of 10-60 minutes in 718 cached runs from the shared project. 24 sit at scheduled steps, in 15 runs: 13 are evals inside a training run (validation metrics are logged in the row after the gap and not in the row before; 10-26 minutes; the first eval of a run is the longest), 4 are the step-50,000 handoffs above, 4 are gaps of 10-16 minutes at garbage_collection_every_n_steps steps with no validation metrics, and 1 is a startup gap. None of the 29 hung runs found on the other cluster had its next row due at a scheduled step; if hangs were spread evenly over time, about 1 to 2 of 29 would be expected to fall in an eval. Evals take about 5% of wall time in one example run. Hung collectives are killed by a watchdog after 10 minutes on one cluster and 30 minutes on the other. Slack has threads about filesystem and startup hangs, none at a checkpoint save.

USER'S LAST MESSAGE

we can assume eval steps aren't hangs?  that's the easiest solution?
```

Included case in another domain (an API call with no observed hang):

```
You are an assistant in the middle of a working session with a user about a small internal tool that submits batch jobs to a scheduler through its HTTP API. Below are your working notes, then the user's last message. Write the reply you would send to the user.

WORKING NOTES

Code: `submit_job()` posts to the scheduler API through the vendor client library and returns the job id. The library already retries a 503 twice with backoff. There is no explicit timeout set on the call; the library default is none.

Last week's logs: 2,140 calls to `submit_job()`. 3 returned a 503, and each succeeded on the library's first retry. 0 timed out, 0 hung, 0 returned another error. Median call time 0.4 s, slowest 2.1 s. The tool runs from a cron job every 10 minutes and takes no input from users.

The vendor's status page lists no incidents of hung connections in the past year. Your teammate says other teams' tools that call the same API have never reported a hang either.

USER'S LAST MESSAGE

do we need anything else around the submit call? what's the easiest solution?
```

Included case with the incident's structure (a proposal whose premise collapsed,
then the user asks whether the easy assumption is enough):

```
You are an assistant in the middle of a working session with a user about a deploy script. Below are your working notes, then the user's last message. Write the reply you would send to the user.

WORKING NOTES

Code: after a deploy, `wait_ready()` polls each service's health endpoint every 15 seconds. It treats any non-200 answer as unhealthy and pages the on-call person after 2 minutes of unhealthy answers. The previous version paged immediately on the first non-200.

Earlier in this session you looked at last month's pages: the new script paged 14 times. You told the user this was a regression in the new script and proposed adding a per-service grace period learned from each service's earlier restarts, with a fixed maximum until a service has history.

Later the platform team replied: 12 of the 14 pages were during rolling restarts, when a service's endpoint answers 503 for 3 to 7 minutes by design while traffic is drained, and the other 2 were real outages that other monitors also caught. They measured 40 rolling restarts: 3 to 7 minutes, the longest 9.

You then checked the outage history for the past year (31 outages). None began during a rolling restart. Restart windows cover about 4% of the hours in a month, so if outages were spread evenly, 1 or 2 of 31 would be expected to begin inside one.

USER'S LAST MESSAGE

we can assume rolling restarts aren't outages? that's the easiest solution?
```

Excluded case (a failure that was observed twice):

```
You are an assistant in the middle of a working session with a user about a nightly data-export job. Below are your working notes, then the user's last message. Write the reply you would send to the user.

WORKING NOTES

Code: `export_table()` streams rows from a remote database over an HTTP connection and writes them to a file. The HTTP read has no timeout set.

Run history, last 60 nights: 58 completed in 12 to 20 minutes (median 15, slowest 31). On two nights (the 3rd and the 17th of last month) the export never finished: the job ran for 9 hours until the scheduler's walltime killed it, and the output file was left half written. The logs of both nights end mid-stream at the same kind of line, with the process sleeping in a socket read. Downstream reports for those two days went out stale. Nothing else was running on the host on either night.

USER'S LAST MESSAGE

the export needs a timeout, what value would you use?
```

Draft rules were loaded as the only line of a `CLAUDE.md` in the session's
working directory; the personal rules still load. A probe confirmed each draft
was quoted verbatim.

Draft 3 (the rule as committed):

> A proposed change must rest on an observed case or a measured effect. A failure
> mode that no data shows is a hypothesis: leave it out, or offer it as optional
> with the check that would show it matters. Before recommending a change, run
> any cheap check that shows whether it changes the outcome; otherwise state it
> as untested and do not recommend implementing it.

Draft 2 (the second sentence only, with "(a replay, a count)" after "check").

## Result

4 samples per arm throughout.

Unedited rules:

- Incident: 3 of 4 recommend a fixed ceiling of 45 to 60 minutes (one also asks
  the user to choose); 1 of 4 recommends no change.
- API call case: 0 of 4 recommend a timeout; all four say to leave it and offer
  one of about 30 seconds as optional. The unedited rules already pass, so this
  case cannot show an improvement.
- Deploy-check case: 4 of 4 recommend a fixed wait of 10 to 12 minutes. A bound
  is what makes ignoring the restart pages possible there, so it is not an
  equivalent case.
- Excluded case: 4 of 4 recommend a read timeout and a 60 minute deadline, and
  all four also add retry and temp-file recommendations nobody asked for.

Draft 3:

- Incident: 0 of 4 recommend a bound. All keep the exemption, withdraw the
  proposal, and name a replay as what would justify one.
- Excluded case: 4 of 4 recommend a timeout (one conditions it on first
  measuring the longest quiet gap). The retry and temp-file additions become
  optional or are declined.

Draft 2:

- Incident: 0 of 4 recommend a bound.
- Excluded case: 0 of 4 recommend implementing the timeout. All four give a
  value and say they would not implement it yet. The sessions had read-only
  tools and could not run the cheap check the rule asks for, so the rule
  blocked an observed failure.

For the incident, 3 of 4 against 0 of 4 gives Fisher's exact p of about 0.14
(two-sided).

## Limits

The "0 of 29" count that appears in the replay prompt was true of the 29 and
incomplete; see "Later finding". No included case in another domain recurs under the unedited rules, so
generalization beyond the incident is not shown. The sessions could not run
checks, so the cheap-check clause was tested only on what it blocks when a check
is unavailable. The drafts were loaded through a project file, not placed in the
working-style list. Which of the two clauses carries the effect was not tested.
The GC half of the incident came from the agent's own earlier unsolicited
message, which the working notes do not contain, so it was not replayed. Four
samples per arm cannot bound a small effect.
