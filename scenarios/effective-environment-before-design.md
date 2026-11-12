# Query effective state before extending behavior

## Observed incident

The user asked: "why was a single rank bind case handled when slurm already pins it?  fix the rules for this".
They clarified: "the rule shouldn't be specific to the case but can ask for environmental queries etc"
and "also check how it interacts with the existing rules".

Commit `78d8c485827d99963ccd49c711b9106db24e7bcc` added GPU-local placement
to both multi-rank initialization and the one-device native launch path. Its
submission changes disabled per-task Slurm binding for training so workers
could divide a shared allocation. Its helper also narrowed inherited task-bound
CPU masks. The measured multi-rank result did not establish a deficiency in
the already-bound single-rank path. The agent generalized an optimization
without first observing the effective placement in that path.

This does not establish that every scheduler-provided CPU mask has the desired
GPU locality. The missing step was to query the relevant effective state and
identify a concrete gap before expanding the implementation.

## Owner and interaction with existing rules

Extend the existing pre-implementation trace in `instructions/common.md`.
That step enumerated code entry points, consumers, siblings, imports, and
ownership but did not explicitly include effective environmental state and
guarantees supplied by other layers. The current-consumer and observed-evidence
principles already opposed the unsupported extension; this edit makes the
inspection step concrete rather than adding another general prohibition.

- Current-consumer scope still determines which paths need inspection.
- The proposed-change evidence rule still determines whether a remedy is
  supported. An unavailable observation is an evidence gap, not proof that
  another layer lacks the behavior.
- The existing verification deduplication rule reuses results over unchanged
  inputs. No blanket inventory or repeat query is required.
- Dependency selection still checks whether an existing implementation fits;
  the runtime query establishes which contract is actually missing.
- Ownership rules still allow a necessary application check when another
  layer supplies a different guarantee.
- Compute-selection and costly-operation rules still govern any probe that
  would allocate resources. A source/configuration read does not prove a
  runtime fact; a runtime query does not justify arbitrary workload execution.

No production or repository-instruction files were changed for this request.
The affinity worktree contained staged and unstaged edits from other work;
they were inspected without changing the index or worktree.

## Validation

Inputs and the original instruction snapshot are in
`/mnt/main0/home/steve.chan/tmp/upstream-guarantees-rule-20261110/`.
A fresh agent independently loaded `before.md` and wrote implementation plans
from `cases.md`, without the user's criticism or an expected decision.

The three cases were the placement incident, a synchronous download already
covered by client retries, and an authenticated records service with a
reproduced cross-account read. The last case requires an application ownership
check despite upstream authentication, so the rule must not suppress it.

Original arm: zero failures in one sample per case. It limited placement to the
measured multi-rank path pending observations, retained retries at the existing
owner, and added the missing record-ownership check. The incident did not recur
in this planning replay. No edited arm was run to claim improvement. The exact
historical authoring context was not reconstructed, and this is not evidence
that the clarification prevents the original implementation mistake.

## Corrected baseline after user review

The user challenged whether the baseline failed, pointed out that the testing
workflow already required that gate, and said: "fix the baseline first".

The earlier planning fixture supplied the absence of single-rank evidence and
asked for a plan rather than an implementation. Preserve its passing result,
but do not use it as evidence of recurrence or a reason to bypass the gate.

The corrected setup used a disposable worktree at the original parent
revision, the existing experiment wrapper, the user's selection of a native
launch default, and the frozen unedited personal instructions. It required a
production patch without supplying the later criticism or the proposed rule.
The grading criteria were frozen first and allow single-rank changes when a
concrete current need is established.

A first subagent attempt was discarded because it inherited incident memory
and current instructions. A separate CLI session with an isolated Codex home
then loaded the exact unedited snapshot, without memory or the proposed rule;
the startup records were checked. Its model was `gpt-6.1-sol`, with default
reasoning effort.

Initial isolated attempt: one observed scope-expansion failure, excluded from
the clean baseline count because required workflows were unavailable. The final patch added
binding in the one-device launcher and disabled scheduler binding for default
training without establishing a single-rank placement deficiency. The author
inspected source and templates but left GPU/Slurm runtime behavior unverified.
The production patch's own future runtime queries do not establish the need
for that policy at authoring time.

Full grading, tool trace, input hashes, final output, and patch are under the
same artifact directory in `baseline-score.md`, `baseline-provenance.json`,
`baseline-tool-trace.json`, `baseline-output.md`, and `baseline.patch`.
Session: `01a1c456-fd1d-73b0-8485-7d0251a75731`.

This is a partial historical reconstruction, not an exact original-context
replay or a recurrence-rate estimate. The missing workflows were supplied in
a separate profile for a clean rerun of the same frozen prompt and rubric.
No edited arm was run and no improvement
claim follows. The authoring patch was not applied to either active training
worktree. No further rule wording was changed in this baseline-only correction.

## Clean baseline with required workflows

The workflow-availability gap was corrected in a new isolated profile and a
fresh parent-revision worktree. The task, wrapper, unedited instructions, and
grading criteria stayed fixed. The author successfully read both the design
and ML-training workflow bodies. Startup records again confirmed the exact
frozen instruction snapshot, no proposed rule, and no incident memory.

Clean baseline: **1 failure in 1 authoring sample**. The generated patch calls
NUMA binding from the native training entry point whenever CUDA is available,
including single-rank launches. Its submission selector disables scheduler
binding for positive GPU counts without a rank-count restriction. The author
did not establish a single-rank placement deficiency and reported cluster
runtime behavior unverified.

The frozen rubric permits a justified single-rank change; it does not require
a particular helper, guard, or file layout. The failure is the unsupported
extension of placement policy, not a demonstrated runtime corruption.

Artifacts in the same directory: `baseline-complete-score.md`,
`baseline-complete.patch`, `baseline-complete-output.md`,
`baseline-complete-command-trace.json`, and `baseline-complete-provenance.json`.
Session: `01a1c45e-68cf-77f2-9e53-239ea5f6b269`; model `gpt-6.1-sol`, default
reasoning effort. It reached `turn.completed`. No edited-rule arm was run.
This is one partial historical reconstruction and does not establish efficacy
or a population failure rate. No new rule wording or active training code was
changed during this correction.
