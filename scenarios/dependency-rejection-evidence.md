# Evidence for rejecting a dependency

## Observed incident

The user asked: "how come we didn't use the gpu_affinity?" The agent cited
existing-thread rebinding and an old NVML dependency pin as reasons for a custom
implementation. The user then asked: "i mean the gpu_affinity limitations, do
they affect the async checkpointing binding problem as it is" and "fix the
rules". The agent had no isolated measurement showing that rebinding existing
threads contributed to the checkpoint improvement and had not tested the
dependency conflict. A thin adapter had not been evaluated.

The user also said: "maybe this utility is too old though, it hasn't been
updated in 3 years" and asked: "is the code there is still high quality".
Maintenance and compatibility costs remain relevant; the correction must not
turn reuse into an unconditional requirement.

## Classification and owner

The existing principle was clear but unexecuted: compare the candidate against
the current contract, inspect adaptation cost, and ground proposed changes in
observations. Keep that principle at its existing owner, the dependency-check
bullet in `instructions/common.md`. Make its comparison step concrete: record
the current consumer or verified maintenance/compatibility cost behind each
rejection reason, its evidence, and whether a thin adapter covers the gap.
Mark untested mismatches unresolved. Do not add a second general reuse rule or
claim that every inactive project must be used or rejected.

## Replay

Inputs and snapshots are in
`/mnt/main0/home/steve.chan/tmp/dependency-rule-20261108/`.
Fresh agents read `before.md` or `after.md` and identical `cases.md`, then wrote
implementation recommendations. The prompt provided raw contracts, source
facts, and evidence limits, without the user's criticism or expected answer.
The original arm was scored before editing.

The three cases cover the observed placement decision, a transfer utility whose
extra capabilities have no current caller, and a streaming service whose
documented memory limit rules out a whole-object package.

Original arm, one sample per case: zero failures. It recommended conditional
reuse with compatibility probes for placement, reuse for small synchronous
transfers, and a direct streaming implementation for the demonstrated memory
mismatch. The incident did not recur. The replay therefore cannot establish
improved behavior from the procedural clarification.

Edited arm, one sample per case: zero failures. It made the same three choices,
kept dependency compatibility unresolved, and did not attribute the measured
improvement to rebinding existing threads. These are boundary checks, not
evidence that the edit reduces the original failure rate.

Separate live inspection found the upstream tip was
`5d5e28b47967d87209a46edbd92af60f4d6b214b`, committed December 8, 2023, with
`pynvml==11.5.0` in its package metadata. Its per-device empty-affinity check
tests the outer list again rather than the current element. These observations
warrant compatibility and quality assessment; they do not demonstrate failure
in the checkpoint workload. The replay inputs did not include this later
inspection, so its output does not evaluate those maintenance concerns.
