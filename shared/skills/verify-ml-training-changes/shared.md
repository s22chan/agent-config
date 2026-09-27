# Verify ML Training Changes

Trace the exact shipped training path and report weaker evidence as unverified
rather than treating a synthetic proxy as runtime proof.

For repeated model execution, checkpoint compatibility, resume semantics,
cursor ownership, or checkpoint timing, read
[model execution and resume](references/model-execution-and-resume.md).

For prefetching, distributed agreement, performance accounting, telemetry, or
optimization naming, read
[distributed and performance verification](references/distributed-and-performance.md).

## Trace gradients and tensor effects

- For a gradient-routing claim, enumerate every tensor passed to the loss or
  manual backward, prove its `requires_grad` state and detach boundaries, and
  identify the reachable parameter sets. Backward through an intermediate does
  not prove reachability to a module whose input was detached.
- When manual backward bypasses outer loss policy, identify the constraint that
  motivated it. Consider representing the pending VJP through the ordinary loss
  path; for chunked memory reduction, `autograd.grad` plus a differentiable
  surrogate is one option. Compare gradient-buffer and graph costs before
  choosing that design.
- Before interpreting global gradient clipping, verify its shipped scope. Its
  multiplier scales the combined model gradient and can reduce one component's
  updates when another dominates the norm.
- When replacing an in-place tensor operation, preserve pre-write reads and
  audit every alias and caller that consumed the old side effect. Pass the
  transformed value explicitly to intentional post-write consumers.
- A green type checker does not prove runtime tensor, device, or dtype safety.
  Exercise the changed operations with representative runtime values.
- Test a final caller output with an adverse input where omitting or reordering
  the old mutation changes the result. An assertion that the helper leaves its
  input unchanged is only supplementary evidence.
- When selection, batching, or repetition changes cardinality, exercise a
  nontrivial multiplicity greater than one, a proper subset, and an empty
  selection where supported. Assert final ordering and shapes from independently
  derived expected values.

## Build representative training tests

- Construct the smallest purpose-built training configuration and set every
  field that can affect the assertion. Do not use a profile introduced by the
  current change as general test setup or snapshot its values unless that exact
  profile is the contract.
- Reuse a merge-base configuration only when it is part of the contract, and
  override relevant fields so unrelated default changes cannot alter the test.
- Make stateful loader, sampler, trainer, and checkpoint doubles reproduce the
  production reset, iteration, save, and load lifecycle relevant to the claim.
- For schedule-dependent checkpoint claims, exercise the top-level training
  orchestration with resolved intervals that distinguish coincident from
  non-coincident save and evaluation steps. Calling validation or checkpointing
  directly proves only that component's local ordering.
- Use lightweight test doubles only for narrow collaborator contracts that
  exactly match their declared attributes and behavior.
- Keep test- or experiment-only variation in fixtures and proxies. Do not widen
  production configuration unless a supported production consumer needs that
  state.
- Do not test incidental RNG consumption unless replay or sequence-level RNG
  equivalence is an explicit contract.
