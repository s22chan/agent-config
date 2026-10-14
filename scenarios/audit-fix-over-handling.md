# Audit fixes that handle cases nothing shows can happen (workflow added, no rule)

## Observed incident

After an audit of a W&B slowdown detector returned, the user told the agent to
"mask a task list and fix everything". The agent fixed most findings with full
handling. The user then said, mid-turn:

> a fix doesn't necessarily mean handling the error scenario if it an assert is
> less work and it's not a real scenario that's likely to happen or necessary to handle.
> tell me if any of the fixes falls in this category

and asked whether the agent rules would have produced the cheaper fixes without that
direction.

## Replay inputs

Fresh `claude -p` sessions with hooks and auto-memory disabled (probe answered
`none`), read-only, on a detached worktree of the code before the fixes. Inputs
were the audit finding text verbatim. Cases: four findings whose cheaper outcome
was taken (short in-place requeue, thinned peer read, null `historyKeys`,
swallowed metadata error), one transcript-renderer finding, and one real defect
(a hung run that cannot page) as a control.

## Result

- Prompt "reply with the exact change you would make", read-only, no Bash:
  cheaper outcome in 1 of 3 (requeue), 0 of 3 (peer read), 0 of 3 (null key),
  3 of 3 (log line), 0 of 3 (renderer); control fixed 3 of 3. The framing and the
  inability to check produced the over-handling.
- Draft rule "size a fix to the evidence" as a new bullet: 3, 0, 0, 3, 0 of 3.
  Clause added to the existing "Implement only behavior required..." bullet:
  3, 0, 0, 3, 2 of 3 (the renderer case, where sessions read the producer).
- Prompt "decide what to do about it" with read-only Bash and a pointer to saved
  data, unedited rules and the clause, 3 runs each: no code change in 3 of 3 for
  the requeue, peer-read and renderer findings in both arms; log line 3 of 3;
  null key 0 of 3 (all handled, plausibly a real case); control fixed 3 of 3. The
  clause had no measurable effect, so it was removed.

## Outcome

No rule change. Added the `fix-audit-findings` workflow (`/audit-fix`), which asks for
a decision per finding after checking the producer or measuring, in place of
"fix everything". Two fresh sessions run through `/audit-fix` on five findings:
fix for the hang and the swallowed error, comment only for the requeue and peer
read, decline for the null key.
