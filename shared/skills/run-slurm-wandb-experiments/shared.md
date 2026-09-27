# Run Slurm and W&B Experiments

Preserve the exact source, configuration, run identity, and scheduler
provenance for every logical experiment arm. For standalone GPU verification,
preserve the exact test, runner, source revision, resource request, and result.

Before generating or submitting an evorun job, or choosing transient checkpoint
storage, read [the evorun environment](references/evorun-environment.md).

## Choose the workflow

- For a standalone GPU correctness test, skip study identity, W&B, checkpoint,
  and paired-study steps. Inspect the repository's test-selection defaults and
  GPU decorator, include any required marker explicitly, and derive visible
  devices and Slurm tasks from the decorator's actual launch policy rather than
  the logical rank count alone. Inspect the final submission script and exact
  test command before submitting.
- For a training experiment or study arm, follow every applicable section below.

## Establish study identity

1. Locate the project's existing experiment ledger. If none exists, obtain a
   user-approved location before submitting rather than inventing one silently.
2. Assign every experiment or A/B submission a unique, descriptive Slurm job
   name and W&B run name. Include the same study-and-arm identifier in both.
3. Add structured W&B tags for the study identifier, arm, and experiment
   purpose.
4. Give every fresh W&B trajectory a new run ID. Reuse an ID only to continue
   the same logical arm after requeue or preemption.
5. Assign a stable explicit W&B run ID to a checkpoint-resumable arm and set
   `resume="allow"` on every allocation. Do not rely on resume-by-name.
6. When Slurm may automatically requeue a W&B-backed job, verify before the
   long run that creating and then resuming the same run ID accepts the exact
   resolved configuration serialization. Include enums, omitted defaults, and
   empty containers in that check; semantic equality in the application config
   does not prove W&B will accept the resumed payload. Preserve rejection of
   substantive configuration drift rather than enabling unrestricted value
   changes to make the probe pass.
7. Record job names, run names, tags, run IDs, Slurm job IDs, and scheduler
   dependencies in the experiment ledger.

## Resolve the exact launch profile

1. Treat a configuration module and its executable entry point as separate
   identities. Resolve the callable or subcommand that the user named (for
   example, `main`, `baseline`, or `debug`), the settings record it selects,
   and the resource request it submits. Do not substitute a sibling helper
   because its name, comments, or model family appears similar.
2. When the named entry point launches multiple settings and the user has not
   selected one, present the concrete variants and obtain their choice before
   allocating resources.
3. Derive GPU count from the executed submission path and derive device
   microbatch, global batch, and gradient accumulation from the resolved
   runtime configuration and world size. Treat comments and historical run
   descriptions as cross-checks; report conflicts, and do not let stale prose
   override executable values.
4. When the user asks for the same or exact configuration, build through the
   same settings record and builder path. Before submission, diff the fully
   resolved submitted configuration against that native launch profile and
   enumerate every difference. Only explicitly requested changes and run
   identity metadata may differ; logging cadence, evaluation, validation,
   checkpointing, loader, model, optimizer, and batching changes require
   separate approval.

## Choose hardware

Before choosing `l40-reserved` or `h100-reserved`, resolve the exact job
configuration, per-rank resource demand, and claim the run must support.
Inspect the current scheduler and node inventory; do not infer device memory,
topology, or fabric from the partition label alone.

1. Determine memory fit from peak per-device use at the resolved world size,
   precision, microbatch, sequence length, and sharding policy. Prefer a
   measurement from the same configuration, GPU class, and software stack.
   Otherwise form a conservative bound that includes parameters, gradients,
   optimizer and master state, activations, communication and sharding buffers,
   compiler and kernel workspaces, CUDA context and non-framework allocations,
   allocator fragmentation, and transient checkpoint, first-step, and
   evaluation peaks that the run will exercise. Aggregate model size and
   steady-state use are not sufficient; multiple GPUs do not pool memory unless
   the executed strategy shards the relevant state.
2. Treat a GPU class as fitting only when the peak leaves at least 10% of its
   verified device memory free, unless the owning workload has a validated
   tighter margin. When no representative measurement exists but the
   conservative bound fits the L40 with that margin, use an authorized bounded
   `l40-reserved` probe that reaches every applicable peak phase. Record peak
   framework-reserved memory and minimum device free memory. Use
   `h100-reserved` when the bound exceeds L40 capacity or the probe violates
   the margin; an OOM alone is not a useful probe result unless the failing
   phase and exact configuration are preserved.
3. Require H100 when the executed path or claim depends on a capability,
   topology, or fabric unavailable on the L40. Verify the actual code and
   backend capability gate and current Slurm node features rather than relying
   on model-family prose. Generic correctness does not require H100 merely
   because production uses it.
4. Measure absolute throughput, latency, power, or peak-memory numbers on the
   GPU class they are meant to characterize. Any result presented as an H100
   number or H100-specific capability result must run on `h100-reserved` and
   record the exact GPU model and memory, driver and CUDA stack, topology, and
   resolved workload configuration. Run relative comparison arms on the same
   GPU class and topology unless hardware is the experimental variable.

For a short generic smoke, correctness, or integration run, request the
least-scarce class and smallest allocation that exercises the required backend
and topology; prefer `l40-reserved` when the criteria above permit it. Do not
choose H100 merely to reduce queue time. Require explicit user approval unless
verified memory fit, required hardware support, or the measurement contract
makes H100 necessary.

## Verify the submitted artifact

1. Pass `logger.run_name` explicitly when a shell or profiler wraps the
   trainer. Do not assume `evorun --run-name` rewrites a nested training
   command.
2. Inspect the generated submission script and printed runtime configuration
   before treating names, groups, tags, or arm overrides as verified.

## Run paired studies

1. Reuse a historical control only when the study design explicitly permits it
   and the ledger verifies compatible model and profile, checkpoint, data order
   and seed, GPU topology, microbatch and global batch, precision, relevant
   source and software, and measurement environment and timing protocol. Record
   that compatibility decision and the source run's provenance.
2. For isolated causal or performance attribution, default to a fresh paired
   control unless the protocol predeclares why historical-control equivalence
   is sufficient.
3. Store transient or paired-replay checkpoints in the environment's designated
   local scratch storage. Do not upload them to remote storage unless the user
   explicitly requests durable retention.
4. Disable data-order and performance transformations such as shape bucketing
   in both arms unless they are the experimental variable.
5. Submit a verified sequential arm with an `afterok` dependency on its
   predecessor instead of waiting to submit it after the predecessor finishes.
6. Inspect every arm's generated script and record the dependency in the
   experiment ledger.

## Monitor and recover

- Do not tight-poll Slurm with `squeue`, `sacct`, or similar scheduler queries.
- For an automatically requeued job, inspect every allocation record rather
  than only the latest aggregate state. Distinguish the original interruption
  from a failure in the resumed allocation, and verify whether either attempt
  reached training or wrote a usable checkpoint.
- Treat an interactive launch and a shell-tool wait as submission, not a
  completion callback. Capture the job ID and durable output path, and report
  pending or running work honestly.
- Use a runner or generated script that records the executed command's exit
  status and emits the known completion marker only after the command ends. The
  marker must preserve that status so a completed failure cannot look successful.
- During an active turn, poll the durable log for a known completion marker at
  roughly 5% of requested walltime, bounded between 30 seconds and 10 minutes.
  Then inspect the scheduler and final log once to verify completion. Do not
  promise an automatic update after the turn ends.
- When an `afterok` prerequisite reaches a terminal non-success state, treat
  `DependencyNeverSatisfied` as a failed study chain rather than an active
  queued arm. Report it immediately, and cancel or replace the dependent job
  only when the current request authorizes that scheduler mutation.
