# Verify Behavioral Tests

Make each permanent test fail on the supported behavior it protects, not merely
on the implementation used to produce it. For every assertion, name the
contract and observable regression it distinguishes; reject the assertion when
a contract-preserving refactor can make it fail.

## Ground the contract

- Start from an observed failure, explicit contract, or reachable current
  workflow with material impact. Name the production entry point and final
  observable outcome before closing a coverage, mutation, or review finding.
- Do not pin hypothetical callers, stricter future APIs, accidental default
  combinations, or failures that are loud, deterministic, cheap to diagnose,
  and easy to repair. Weigh permanent runtime, maintenance, and brittleness
  against recurrence and consequence; use a one-time check when that is enough.
- Fixtures, mocks, smoke runners, and feature-local harnesses are scaffolding,
  not products. Keep their self-tests only while building or debugging. Scope
  fixture data to its owning test or helper; lift it only when it expresses a
  shared behavioral premise or makes a substantial protocol example legible.
- When behavior or policy is removed, moved, or merged, state the old and new
  contract and inventory affected tests. Update the test at the new owner or
  delete obsolete negative tests. Invert one into an acceptance test only when
  acceptance is independently supported behavior.

## Exercise the shipped path

- Enter through the interface that exposes the behavior and assert its final
  result. A helper test may supplement but cannot replace shipped-path evidence.
- Keep every collaborator whose behavior determines the outcome real at the
  smallest practical integration layer. If an operational constraint requires
  a seam, replace only that seam and record what remains unproven.
- Mock calls, forwarded arguments, object identity, component properties, and
  construction counts are wiring unless a consumer observes them. They become
  valid adapter contracts when order, threading, destination, retries, required
  parameters, quota, measured performance budget, or side effects are the
  supported behavior; assert those through one ordered record.
- Let a public pure helper own a direct test only when its input/output contract
  is independently supported and caller state contributes nothing. Do not
  promote private helpers for test convenience.
- Verify import, process, initialization, deployment, and filesystem constraints
  at the boundary where they occur. Secondary runtime behavior is not a proxy.
- Prove each configuration is reachable through production defaults,
  preselection, multiplicity, and capabilities. Reachability alone is not
  support: reject requested-but-incapable combinations instead of pinning
  accidental inherited defaults.
- When a change moves a configuration default or authority, exercise every
  shipped producer and entry point that resolves it with the same deployment
  inputs, then compare the resolved values. Separate tests that assert different
  defaults are evidence of split authority unless an explicit supported variant
  makes the outcomes observably different.
- Use the real lightweight configuration when its defaults, validation, derived
  fields, or schema matter. Use a stand-in only when its named attributes are
  the complete collaborator contract.

For persistent state, exercise the complete lifecycle:

- Load older artifacts through the strict outer reader that ships, not only a
  component loader, and assert restored state rather than successful dispatch.
- Make local inspection state and shared persisted state distinguishable; verify
  that shared state omits local-only fields when their ownership differs.
- Compare complete sequences and final state across reset, iteration, save/load,
  and reporting windows. Include heterogeneous inputs and an adverse boundary.
- When durable state changes location or authority, seed the previously
  supported location and exercise the shipped transition. Prove that the new
  entry point preserves, migrates, or explicitly rejects that state; starting
  successfully with an empty replacement location does not prove preservation.

## Test text, visuals, and adapters by contract

- Classify output as human presentation, machine grammar, visual artifact, or
  external protocol before choosing an oracle.
- For human text, assert durable semantics and required data—action, identity,
  link, count, or safety qualifier—not whole sentences, punctuation, or spacing.
- When another shipped component parses generated text, pass real producer
  output through the real parser and assert extracted fields. Separate producer
  and handwritten parser fixtures can drift while both pass.
- For a detector consuming another component's artifacts, derive a positive
  witness from the real producer, preserving quoting, escaping, serialization,
  and wrappers, then exercise a nearby non-trigger. Handwritten positives are
  supplementary. Record the integration as unproven when the producer cannot
  run. This does not apply when independently supplied input is the contract.
- For generated queries or programs executed by an external engine, mocked
  result rows prove only downstream decoding. Exercise the generated artifact
  at the closest practical semantic boundary, or assert its load-bearing
  selectors, join and grouping keys, and cardinality. A mutation to any clause
  required for supported behavior must fail the owning test.
- For visual-only changes, prefer a stable artifact-level oracle. Otherwise use
  focused visual inspection; artist or renderer properties prove only wiring
  unless those properties are themselves consumed.
- Do not permanently pin client/session construction, cache hits, pooling, or
  multiplicity solely because fewer calls seem faster. Keep such a test only
  for a measured budget, quota, side effect, or changed supported outcome.

## Construct decisive cases

- Derive expected results independently from the implementation.
- For a configurable threshold, window, bucket, or limit, use at least two
  settings that produce different outputs for one purpose-built input. Test the
  boundary once at its predicate owner and configurability once at its consumer.
- Derive orchestration states from the production caller rather than enumerating
  private Boolean conjuncts. Report an ownership mismatch instead of expanding
  scope when moving the gate is not authorized.
- Make disputed transitions observable. Stateful doubles must reproduce the
  relevant reset, iteration, save, and load behavior.
- Materialize generators and aggregates before asserting. For keyed, windowed,
  partitioned, or distributed output, expose missing and unexpected members and
  the relevant key, window, or rank.
- Name tests for the behavior preserved. Add rationale only when the prevented
  failure is not evident and repository style permits it.

## Prove coverage

1. Map every headline behavior or correctness claim to one owning test that
   enters through the shipped path and asserts the final result.
2. Record material untested contracts; a broad green suite does not prove them.
3. For silent corruption of persistent state, numerical results, authorization,
   distributed ordering, production data, or skipped work claimed equivalent,
   use a targeted local mutation when proportionate. Invert the controlling
   gate, disable the transformation, corrupt selection or scaling, or suppress
   the state update; the owning test must fail for the intended reason.
4. Strengthen or remove tests whose relevant mutation survives. Do not mutate
   incidental details merely to raise a score.
5. Keep each behavior test in one owning location.

Mutation sensitivity does not expand the supported contract. When removing a
barrier or compatibility path has no observable effect on current consumers,
verify the supported end state and owning trace; do not invent a caller,
interleaving, or temporary-state observer merely to make restoration fail.
