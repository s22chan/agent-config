# Model Execution and Resume

- Before eliminating a repeated model execution, identify why each execution
  exists and every consumer of its values and autograd graph. Audit training and
  evaluation modes for RNG, mutable buffers, hooks, caches, counters, and
  collectives.
- Treat an optimization as model-specific when its correctness depends on the
  concrete model's modules, hooks, mutable buffers, autograd graph, or wrapper
  behavior rather than only on a framework-independent tensor contract. Exercise
  the deployed model class and checkpoint through the shipped entry point with
  its runtime mode, precision, device class, and an input that activates the
  changed branches and distinguishes the competing semantics. Compare old and
  new final outputs and observable state over the real run.
- Use a synthetic model, call-count assertion, or shape check only to pin routing
  after real-artifact proof. If the real artifact cannot run, report equivalence
  as unverified; if exact equivalence is not intended, state the semantic change.
- Classify resume as exact, no-replay, or approximate before implementing,
  testing, or documenting it. Exact resume reproduces the uninterrupted
  post-checkpoint sequence and state; no-replay may discard in-flight work but
  does not repeat completed work; approximate resume restores only a count or
  statistical position.
- Trace prefetched or queued data, worker and rank RNG, counters, rank-local
  state, world size, and checkpoint format. Compare a partially consumed buffer
  and an exact boundary with an uninterrupted reference before claiming exact
  resume.
- Enumerate every supported checkpoint format before claiming resume
  compatibility. Trace destination-state construction, metadata validation,
  deserialization, and component `load_state_dict()` in order. In particular,
  an additive nested field can make strict distributed-checkpoint loading fail
  before a loader or model compatibility branch is reachable; prove an older
  sharded artifact through the real reader as well as any full-checkpoint path.
- When rank-local inspection state and shared checkpoint state encode different
  ownership or counting semantics, make their representations distinguishable
  when practical. Test that the shared form omits local-only fields; identical
  key shapes can let an incorrect writer silently recreate the original bug.
- Before aggregating a shared cursor, identify which ranks own distinct trained
  data streams and which merely replicate, prefetch, or discard loader work.
  Select one authoritative contributor per trained stream and produce the same
  result on every checkpoint rank. Divide, average, or enforce divisibility only
  after proving the replica counters are required to be equal; a remainder can
  reveal that the ownership premise is wrong rather than invalid input.
- Before claiming that delayed signal handling or checkpointing exposes training
  progress, resolve the production save and evaluation schedule and trace the
  most recent completed durable checkpoint through the caller's exact operation
  order. Distinguish delayed termination from a durability gap: a completed
  regular save immediately before validation can protect all current progress
  even when signal handling waits until validation ends, while initial
  validation or non-coincident intervals may not.
- Before labeling a path "unprotected" or assigning severity, quantify the
  regression cost: completed updates or samples since the last durable state,
  validation or other work repeated after resume, the duration and frequency of
  the exposed window, and whether the outcome is corruption, lost progress,
  replay, delayed exit, or only redundant work. Estimate likelihood from
  observed event rates and exposure windows when evidence exists; otherwise
  state that it is unknown instead of implying that it is likely.
