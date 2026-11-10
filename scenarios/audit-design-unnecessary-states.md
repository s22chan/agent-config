# Audit design lane accepts states no producer reaches

## Observed incident

The user ran `/audit` on a single commit that added CPU placement for GPU
workers, then asked the agent to fix the findings. A later trim removed
several states from that commit. The user wrote:

> this audit didn't raise issues with the fact that many of the states were vacuous and unnecessary (see the current working changes for removing unnecessary rank==1 or gpu==1 count checks, etc).  can you triage the rules and see why they weren't flagged?

The audit's design lane returned three findings. Two asked for more ownership
or ordering guarantees, and one removed a duplicated device rule. It named no
state for removal. The tests lane asked for tests of the partial-overlap
pooling and the participating-GPU subsetting. It also wrote that the pooling
had no supported producer and asked whether it was "coverage or design churn".
The root rejected the pooling as a defect and kept only the test gap.

The states the trim removed or reduced: two placement modes chosen by a flag,
the skip for one visible GPU with several workers and the lone-worker call in
the single-device branch, the pooling keyed by peer tuples, and warn-and-skip
paths where the repository rule prefers raising.

## Classification

Replayed from the audit transcripts, not from a fresh run:

- Pricing rule not delivered: insufficient. The reference that says to name a
  producer for every guarded state, charge the state for its tests and
  machinery, and prefer one path is linked from the design workflow only for
  authors "before adding states". The audit packet gives reviewers the rubric
  and the workflow file and forbids other reads. None of five reviewers read
  it, and the design reviewer accepted a skip path as "handled in code and
  covered by" a test.
- Root skipped the removal step for the pooling: mostly unexecuted. Step 4 of
  the reconciliation says to reframe machinery that exists only for an
  unsupported condition as churn and prefer removal. The pooling also served
  the supported case, so the reference's "charge the whole bundle" sentence
  was the deciding rule, and it was not in the packet.
- Remedies that add states: candidate, unverified. A finding that survived
  asked for guaranteed replacement binding while the same reviewer listed
  whether that skip ever fires as an open question.
- Fix pass: the agent added an environment variable and tests for the
  starved and partial cases without invoking `grill-change`, which the common
  instructions require when several findings target one abstraction and the
  fixes add compensating state. Unexecuted guidance; no edit.

## Replay inputs

Fresh `claude -p` sessions with the `audit-reviewer-high` agent definition
(Opus, high effort), hooks and auto-memory disabled, read-only tools. Each got
the original design-lane packet text from the audit transcript and the same
saved evidence files for the audited commit.

- Baseline arm: the packet unchanged.
- Edited arm: the rubric text from the edited lane file, and the reference's
  absolute path listed next to the workflow path.

The baseline ran and was scored before the edited arm started. Scoring was
fixed first: a state counts as named only when the report says it should go,
has no current producer, or is observed by no consumer. Asking for more
handling or tests does not count.

## Test arms

Three sessions per arm. Each session read 10 to 15 files; the edited sessions
also read the reference.

| Check | Baseline | Edited |
|---|---|---|
| Read the reference | 0 | 3 |
| Report says a state has no current producer or consumer | 0 | 3 |
| Names the two placement modes | 0 | 1 |
| Names the one-visible-GPU skip | 0 | 1 |
| Names the partial-overlap pooling | 0 | 0 |
| Names the participating-GPU subsetting | 0 | 0 |
| Names warn-and-skip instead of raising | 0 or 1 | 2, plus 1 partial |

Baseline run 3 cited the repository's prefer-raising rule but proposed adding
replacement binding, so it is counted as a defect and not as a named state; it
is the 1 in "0 or 1". Edited run 2 said to raise or add a fallback and is the
partial. Two edited sessions also flagged a platform guard that no producer
reaches, which neither the audit nor the fix pass had noticed.

## Limits

Three sessions per arm cannot estimate how often the omission happens.
The edited arm produced more findings in one session (eleven against three or
four at baseline, including test-lane items), so noise may also rise.
Only the design lane was replayed. The packet-rule line, the tests lane, the
remedy-adds-state pull and the fix-pass guidance are untested, and the pooling
and subsetting states were still not named. Artifacts: the audit evidence in
`~/tmp/audit-ev-GGkpFK/` and the replay inputs, streams and scoring in
`~/tmp/replay-audit-design/`.
