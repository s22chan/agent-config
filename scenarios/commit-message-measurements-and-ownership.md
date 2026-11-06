# Commit messages omit requested evidence and responsibility boundaries

## Observed incident

The user requested an optimized checkpoint design with clearer ownership and
said "yes you can run it, measure timing and memory usage", then "commit".
The agent committed a message with timing comparisons but no memory results.
It named several implementation changes without explaining the final division
of responsibility. The user responded:

> the commit message doesn't mention memory

> the commit message also doesn't tell the separation of concerns

The message should have reported the measured host RSS increase and unchanged
CUDA allocator peaks, scoped to their sampling methods. It should have named
the planner's tensor-assignment and metadata responsibilities, the stager's
buffers and copies, the writer's disk effects, the trainer's cadence and
publication, and the saver's remaining coordination.

The existing reconciliation rule should already have caught missing requested
evidence. However, "strongest verified delta" allowed a narrower reading of
result coverage, and the ownership reference addressed resource interference
without explicitly covering responsibilities redistributed by a refactor.

## Replay inputs

Two fresh agents per arm independently loaded frozen copies of the shared
commit-authoring rules and the message-evidence reference. They authored three
complete messages each. They received the same inputs in both arms, with no
prior conversation, corrected message, expected verdict, memory lookup or
access to the other arm's outputs. Loaded-rule SHA256 hashes were returned.
Operational Git actions were excluded because only message drafts were needed.
The original arm completed and was scored before the edited arm started.

- Observed case: the original user requests, actual four-file implementation
  diff, recent commit convention, test evidence and all original/final values
  from the saved comparison. The diff is based on parent
  `694c66eeb81923bb00ff07b4831bef7563f32ab9` and final tree
  `08b6039e84c77244077a71712805c9ec916dbd56` in `~/review-ckpt-optimized`.
  Whole-start medians were 255/158/611 versus 181/105/334 ms. Host RSS was
  35.26/36.07/148.65 versus 35.67/36.56/149.18 GiB; per-rank CUDA peaks were
  unchanged at 18.57/2.40/10.91 GiB. Inputs included sampling limitations.
- Equivalent included case: an archive exporter split planning, reusable
  scratch, compression/upload, refresh/publication and orchestration across
  owners. The user requested wall time and temporary-storage measurements.
  Time changed from 1200/8400 to 800/5700 ms; peak scratch increased from
  2.0/18.0 to 2.2/18.3 GiB. Inputs included tests and measurement scope.
- Nearby excluded case: correct `--output-dir` help from "Output file" to
  "Directory for generated files", verified through `--help`. No runtime or
  ownership changes and no measurements were supplied.

Full inputs, rule snapshots, hashes, author responses and scoring artifacts:
`~/tmp/commit-message-coverage-6ftdk2r6/`.

## Scoring

For the observed case, count messages reporting requested timing, host RSS and
CUDA values, and messages describing final responsibilities and coordination.
For the equivalent case, count messages reporting both wall time and scratch
values, and messages describing the new responsibilities and coordination.
For the excluded case, require a concise help correction without an invented
benchmark or architecture inventory. Score content, not exact wording.

## Results

The initial coarse scorer recorded 2/2 for both included cases and 2/2 for
the excluded case under each rule version. It did not detect the original
omission. These historical scores do not establish complete ownership coverage,
absence of regression or an improvement from the edit. Later independent
scoring found omitted or ambiguous boundaries in the original drafts.

The initial scoring accepted broad descriptions of responsibilities; it did
not require an explicit account of every affected owner. That scoring was too
generous for the reported ownership omission. The stricter replay below
separates each boundary.

The edit clarifies result coverage and ownership accounts in the existing
commit-writing skill. It adds no global instruction and requires no architecture
inventory for unrelated local edits. Bootstrap synchronization and validation
passed, installed Codex/Claude copies matched, and `git diff --check` passed.

## Raw-input replay

The user asked "find a better baseline before running both sides". A second
setup replaced the prepared measurement table with the chronological original
user requests, full implementation diff, saved comparison JSON and actual test
logs. It supplied neither the corrected message nor the expected ownership
account. The full input bundle, frozen rule variants, author responses and
per-boundary scores are in `~/tmp/commit-authoring-raw-baseline-nm5t7_fz/`.

Before outputs arrived, scoring required the planner's assignment/metadata,
the stager's buffers/copies, the writer's disk effects, the trainer's
cadence/publication, and the saver's coordination. Semantic equivalents count;
merely naming an executor does not establish its responsibility. Measurement
coverage allows a supported delta or unchanged result rather than requiring
exact formatting of every baseline value.

Both original samples completed and were scored before edited samples began.
They reported all requested measurement dimensions in 2/2 samples but neither
explained saver coordination. Full boundary coverage was 0/2. This reproduced
the ownership omission while leaving the memory omission unreproduced.

The first edited version explained coordination in 2/2 samples but full
boundary coverage in only 1/2: the other draft did not give the stager ownership
of buffers and copies. The phrase "materially moved" excluded responsibilities
that stayed with their existing owner but defined the other side of a changed
boundary. The revised rule includes those responsibilities while retaining the
exclusion for local changes that leave ownership unchanged. Its next two samples
reuse the same original baseline, inputs and predeclared scoring criteria.

The manual scorer recorded all five boundaries in both final revised samples
(2/2), and requested measurement coverage in 2/2. Its original/first-edit/revised
full-boundary counts were 0/2, 1/2 and 2/2. These are the original manual scores;
the calibrated blind review below qualifies the final count. Each arm used fresh authoring
sessions, verified rule hashes, identical raw inputs and the same rubric; the
original baseline was not rerun or modified between edited versions.

This is an exploratory authoring result, not an estimate of omission frequency.
The memory omission remains unreproduced. The earlier concise local-change
control passed under both original and first-edit rules; the final revision
retains that exclusion. Final bootstrap synchronization/validation passed and
installed copies matched the tested revised snapshots. No checkpoint code or
commit history was changed during these rule tests.

## Follow-up triage and calibrated checks

The user asked "triage and see test what can be fixed". The task list, exact
inputs, fixed rule snapshots, author responses, grading, hashes and correction
provenance are in `~/tmp/commit-test-triage-qt5vnkv2/`.

- Recurrence gate: the workflow already required it. The original controls were
  completed and scored before final-rule controls. No duplicate rule was added.
- Scoring: a grader was calibrated against the actual defective commit, a
  complete example, a semantic paraphrase, isolated missing-writer and
  missing-RSS examples, and a historically ambiguous draft. Its first pass
  exposed an ambiguous measurement label in the supposed complete fixtures.
  The fixtures were corrected to name public `start()` latency without changing
  the rubric. The corrected six-case corpus matched all declared overall
  outcomes: both complete examples passed, omissions were rejected, and the
  ambiguous draft remained nonpassing. This validates the local oracle, not
  instruction effectiveness or a population-level error rate.
- Input selection: the blind comparison exposed a hash-only block accidentally
  selected instead of one commit message. The selector was corrected to choose
  the checkpoint commit block, with source hash and block provenance. The
  invalid result was discarded. Only the changed input was regraded; the other
  five messages were byte-identical.
- Final-version controls: two fresh original and two fresh final-rule authors
  each wrote the equivalent included case and nearby excluded case. Both arms
  reported the archive timings and scratch increase with all five owners in
  2/2 samples. Both kept the help correction concise in 2/2. Loaded-rule hashes
  matched the actual original and final sources. This closes the missing
  final-version control check without claiming an improvement in passing cases.
- Causal attribution: inputs and grading changed together between the initial
  and raw setups. The record does not establish that summarization caused the
  initial test's problem. Working notes are permitted by the existing workflow.
- Remaining evidence: the memory omission was not reproduced in authoring.
  Rejecting the isolated missing-RSS example proves grader sensitivity, not that
  the new instruction reduces such omissions.

The calibrated blind review reused the saved checkpoint drafts without
rewriting them. Neither raw original draft established saver coordination.
One final-rule draft clearly described all five boundaries; the other left
saver coordination ambiguous. Thus final ownership coverage is **one confirmed
complete and one indeterminate**, qualifying the earlier manual 2/2 claim.
Both final drafts left the maximum-across-ranks reduction of CUDA peaks
implicit, so neither is confirmed complete under the full measurement-scope
rubric. These remaining ambiguities are recorded rather than scored as passes.

The rules themselves were unchanged during this follow-up. Only this evidence
record changed. The saved input hashes, final rule snapshots and installed
copies matched; `git diff --check` passed. The independent results remain small
exploratory samples, and do not establish reliable omission rates.
