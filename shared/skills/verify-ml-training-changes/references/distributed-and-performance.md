# Distributed and Performance Verification

- Exclude warm-up from every primary performance comparison and headline
  improvement. Use the same post-warm-up step boundary for every arm, chosen
  from the known startup lifecycle or a criterion fixed without reference to
  which arm is faster. Compilation, dataloader startup, cache population, and
  first-use initialization belong to a separate diagnostic result; never fold
  them into a steady-state throughput claim. If the run does not contain enough
  post-warm-up observations to support the requested comparison, call the
  result inconclusive instead of substituting full-loop or scheduler elapsed
  time. Report full-loop timing only when startup-inclusive operational latency
  is itself the stated research question.
- When deciding whether lookahead, worker prefetch, host buffering, device
  transfer, and distributed agreement are orthogonal, separate their functional
  roles from their scheduling and resource interactions. Trace each `next()`
  relative to worker-queue replenishment and GPU submission, identify where the
  batch resides, and quantify the configured queue depth plus any additional
  retained or discarded batches. Compare baseline and treatment timelines at
  the same training boundary: distinguish startup or epoch-boundary latency from
  recurring steady-state stalls, and do not count an earlier `next()` as wholly
  incremental when the baseline retrieves the same amount of data later. Bound
  the cost with extra produced batches and buffered bytes, then measure the
  baseline-relative critical-path delta by separating data-queue wait, full or
  residual agreement wait, and device-transfer wait. Report both typical and
  tail latency and the frequency of an empty producer queue. Exercise an empty
  or slow queue before claiming the mechanisms compose without delaying device
  work; a result measured with worker prefetch enabled establishes an
  incremental effect, not independence.
- Before adding a process group, collective, store, thread, or signal protocol,
  inventory existing rank-uniform collectives and host-observed synchronization
  points across data fetch, training, validation, and checkpointing. Include
  base paths and supported overrides; record each point's frequency, backend,
  device, participants, state boundary, and whether its synchronization cost is
  already paid. First test whether extending an existing payload provides the
  required agreement without adding another synchronization mechanism.
- Separate distributed agreement from the stateful action it authorizes. An
  existing synchronization point may safely propagate a decision even when
  checkpointing or mutation must happen later at an optimizer, cursor, or other
  state-consistent boundary. Trace work fetched, prefetched, accumulated, or
  queued between those points before choosing where to act.
- Test both sides of a performance optimization: expensive work is observably
  reduced, and downstream loss, gradients, metrics, FLOPs, counters, and other
  accounting reflect the work executed. Grouping alone does not prove padding
  reduction, and a zero loss does not prove its producer was skipped.
- Before adding telemetry, name the operational decision or reachable failure it
  diagnoses. Prefer one normalized signal comparable across world sizes and
  logging intervals. Keep raw numerator and denominator counters internal unless
  each enables an independent diagnosis. Avoid per-step host synchronization or
  disproportionate collectives for bookkeeping.
- Exercise divergent per-rank inputs through the real distributed entry point
  and assert completion or the same failure on every rank. Selection tests do
  not prove reducer or collective ordering.
- Consolidate related distributed cases within one process-group launch when
  isolation is unnecessary. Use the repository's slow-test marker when measured
  runtime exceeds its threshold; if none exists, report the measured runtime
  instead of inventing a marker. Choose timeouts from measured runtime with
  contention margin.

## Trace Distributed Ownership

- Translate runtime topology at the composition root into the narrow data
  contract it requires. Data producers may own stream identity, source class,
  ordering, sharding, and rank-uniform scheduling, but must not branch on model
  wrappers or parallel-axis names. Have them emit data facts or attestations;
  let the execution owner derive skip, full, compact, collective, or shape
  policy from those facts.
- For distributed counters, metrics, and checkpoint progress, determine each
  parallel axis's actual local inputs, partitioning, and reduction semantics.
  Do not infer that an axis is a replica, contributes once, or can share an
  ownership rule merely because it is non-DP, model-parallel, or shares an RNG
  seed. State the per-axis contribution rule and verify it with an input whose
  result differs for replication, sharding, and independent streams.
- Name and derive a seed for the stochastic process and synchronization domain
  it controls. When participants must share a schedule but not sampled data,
  derive the schedule from rank-invariant state and each data stream from its
  rank and worker identity. Verify that the scheduled decision agrees while
  rank-local samples differ.

## Name the Executed Transformation

Name an optimization for the work it actually changes. Call filtering examples
from a loss-only subpath "batch compaction" when the trunk still processes the
full batch; reserve "routing" for learned or branch-selecting dispatch. State
separately which work is skipped and which objective terms remain active.
