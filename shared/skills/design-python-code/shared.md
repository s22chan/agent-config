# Design Python Code

Follow repository rules and established local conventions first. Optimize for
correct ownership and few reachable states; treat low coupling and high
cohesion as evidence, not targets that override behavior.

## Order the tradeoffs

Apply these priorities to each independently governed decision:

1. Preserve the observable contract and correctness of current supported
   consumers. Establish support from production or tooling callers or a
   documented external contract; tests of an internal helper are not consumers.
   A log, debug display, or test read does not justify configuration or profile
   state unless that output is itself an independently required contract;
   otherwise omit the read or derive its text at the presentation owner.
2. Put policy, mutable state, and effects at their informed owner, behind a
   narrow explicit boundary.
3. Choose the smallest direct design that serves those consumers. Minimize
   concepts and reachable states, not merely lines at one call site.
4. Centralize knowledge, policy, and state transitions that must change
   together. Do not merge coincidentally similar code.
5. Add substitution, composition, or another extensibility mechanism only for
   a current variation that the first four priorities cannot represent cleanly.

Before adding or retaining an abstraction, name the duplicated knowledge,
invariant, state transition, ownership boundary, or current variation it owns.
Price that value against call hops, types, validation, hidden state, tests, and
navigation cost.

## Design by decision owner

For a substantial change, inventory each decision's:

- authority and invariant;
- semantic inputs and observable output or effect;
- state lifetime;
- failure representation;
- supported producers and consumers.

Group decisions only when the same authority and invariant govern them; a file
or class boundary is not evidence. Apply the ordered priorities to each owner,
then reread the complete path for duplicated policy, hidden state transitions,
broad dependencies, and abstractions without a current purpose. Report one
mechanism and consequence rather than separate principle violations.

## Keep policy, state, and effects at their owner

- Keep activation gating at the caller that owns execution policy. Do not pass
  an enabled Boolean to a single-caller helper when false only means it is not
  called. Name retained flags for the semantic behavior they control.
- Translate raw flags and capabilities once into named semantic states. Derive
  later selections and masks from that source instead of rebuilding Boolean
  expressions at each consumer.
- Validate absent, partial, and complete metadata states before decoding values.
  Keep coverage, shape validation, and policy selection as distinct decisions.
- When coupled flags or optional arguments encode meaningful policy states,
  use a narrow validated plan. Keep a caller-local variable when the state has
  no independent contract and does not cross a boundary.
- When a layer owns an ordered stateful transaction but its caller owns one
  policy inside it, inject the narrow semantic operation. Do not make callers
  reconstruct the transaction or pass a broad owner or context object.
- Before plumbing caller policy inward because a nested component performs an
  effect first, determine whether it can return the pending effect for the
  established owner to perform. Keep inward policy only when returning it has a
  verified correctness or resource cost.
- Make effects visible in names and contracts. Do not hide RNG advancement,
  cache mutation, counters, persistence, or collectives behind an apparently
  pure transformation.
- Keep state at its real lifetime. Before storing a constructor input or local
  value on `self`, identify the supported later reader. Store a derived value
  instead of both it and its inputs, and derive redundant fields from one
  authoritative state.
- Treat mutable containers as owned state: copy at the boundary when mutation
  must not propagate, and avoid shallow copies when nested values remain shared.

## Model reachable configurations

- Enumerate states reached by actual producers and consumers. Distinguish a
  request, a required capability, and an independently supported disablement.
- Reject requested-but-incapable combinations unless a current workflow defines
  fallback semantics. Remove derivable fields and replace mutually exclusive
  Booleans with one typed state when that reduces meaningful combinations.
- Validate a configuration at its construction boundary. Verify every retained
  variant through a producer-to-consumer outcome that differs from another.
- When changing a default or configuration authority, inventory every shipped
  producer and entry point that can resolve it. Classify each old source as
  preserved, migrated, or removed. The same deployment inputs must resolve to
  the same concrete configuration across wrappers, libraries, CLIs, and offline
  tools unless a current supported variant owns the difference explicitly; an
  undocumented fallback is another reachable state, not compatibility for free.
- When variants require different fields, prefer narrow concrete types behind
  a small shared contract over one superset with inactive fields.
- For fallback, serialized state, legacy payloads, or defensive validation,
  read [defensive states](references/defensive-states.md) before adding states.

## Choose boundaries and helper placement

- Pass narrow semantic values or records rather than broad owners, contexts, or
  data clumps. Centralize a record only when its fields share an owner and
  lifetime.
- Keep direct code, a local variable, or a caller-local function for a
  single-use mechanic without independent semantics. Extract a helper when it
  has multiple callers, owns an independent contract or state, implements a
  supported protocol, or must be independently importable or picklable.
- Choose branches, tables, or dispatch from the variation's shape. A data-driven
  or open set may need keyed dispatch; a fixed branch count alone decides
  nothing.
- Use inheritance when a subtype must remain substitutable or implement a
  supported hook. Prefer composition for an independent lifecycle or mutable
  state, not merely to relocate methods.
- Keep orchestration focused on policy and control flow. Extract substantial
  selection or transformation with its own contract, but keep observable
  stateful ordering visible in the transaction that owns it.
- Place symbols in reader execution order when runtime lookup permits: public
  owner, supported subordinate operations or types, then private mechanics.
  Do not rearrange established code solely for aesthetics.
- After a substantial module change, read it top-down from the shipped entry
  point. Split responsibilities only when they have independent reasons to
  change; moving helpers alone does not create cohesion.
- Name non-obvious tolerances, thresholds, timeouts, and performance boundaries;
  document their measured or derived basis when it is not evident.

## Handle specialized state deliberately

- Treat a cache as persistent state with an invalidation contract. Require a
  current repeated cost and a result valid for the cache lifetime; do not cache
  hypothetical failures or duplicate an underlying cache.
- Name random streams for the stochastic process and participants they
  coordinate. Share only decisions that require agreement and derive unrelated
  streams independently.
- Use `maybe_*` only when work can truly be skipped; never for work that
  advances RNG, mutates state, or participates in a collective.
- Expose one absence representation when `None` and an empty container mean the
  same thing. Preserve distinct empty states only when a consumer observes the
  distinction.
- Use typing supported by the declared Python version and checker. Prefer
  `Self` for concrete-self returns and `type(self)` for construction. Inspect
  protocols, bases, subclasses, and overloads after signature changes; a green
  checker does not prove interface coverage.
- Let required private or undocumented dependencies fail at their boundary;
  use direct access or schema validation instead of silently inventing defaults.

## Final check

Verify the shipped entry point and current consumers, not only extracted
helpers. Confirm that the final design has one authority for each invariant,
no unintended persistent or aliased state, only supported configuration states,
and no abstraction whose cost is justified solely by hypothetical reuse. When
several entry points expose one configuration decision, compare their resolved
values under the same deployment inputs rather than validating each in
isolation.
