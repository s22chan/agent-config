# Verify Technical Evidence

Exercise the exact artifact and path that ships. An adjacent configuration,
backend, cache, or wrapper is not proof.

Start with the cheapest direct exercise that makes competing explanations
produce different observable results. Treat source, documentation, comments,
error text, and configuration as hypotheses until the executed path confirms
them. Verify the exact command, value, kernel, backend, cache state, and
integration layer that ran; inspect sibling implementations and relevant prior
fixes when they may encode the established solution.

Trace values through the complete executed path before claiming semantics. An
intermediate operation is not evidence when later reassignment, masking,
normalization, or control flow can discard its result. Use a minimal input that
makes competing interpretations produce different observable results.

Treat findings and proposed remedies from subagents and other review entry
points as claims. Inspect the cited code, nearby rationale, owning tests, and
relevant prior fixes before relaying them. Route a finding that would remove or
replace established behavior, or contradict its stated rationale, through
the applicable grill workflow for history and evidence. When a concern recurs
in sibling implementations, enumerate those instances and inspect their
established fixes before judging one in isolation.

When a claim depends on whether a backend emits a metric, field, event, or
other optional capability, keep three contracts separate: what the producer
actually emits, what acquisition requests, and what downstream consumers can
decode or classify. A query or configuration entry proves only attempted
acquisition. Decoder, classifier, and replay support may intentionally accept a
superset for archived or cross-version data. Establish producer availability
from a discovery query or another authoritative observation for the exact
backend and selector. If that evidence is unavailable, report an evidence gap;
do not infer availability from historical requests or downstream support.

Before reporting why an observed result occurred, verify every causal premise
against the executed path. Code, configuration defaults, artifacts, and tests
establish possibilities until runtime evidence connects them to the result.
Verify a concrete illustrative example or label it hypothetical. Before quoting
prose as evidence, confirm that its subject and surrounding context support the
claim.

Construct verification inputs so every relevant branch or bin runs. Do not rely
on random coverage or comparisons that silently skip empty or NaN cases.

An exhaustive conclusion requires an exhaustive search. Enumerate candidate
mechanisms, do not truncate results, and account for indirect calls, unpacking,
dictionaries, `**kwargs`, and later-derived task lists or summaries. Recheck
exclusions when later changes touch an excluded area, and report which
mechanisms were covered.

Verify numerical and performance claims directly, scope them to the observed
artifact and conditions, and omit unverified figures.

For comparisons, inspect the null or no-op action and make sure the scored
alternatives differ in the intended dimension while remaining capable of a
nonzero result. When two estimates of the same quantity differ by roughly 3x or
more, audit units, denominators, filters, sampling, and aggregation before
calling either estimate robust.

When windows or samples overlap, report the effective independent count rather
than treating every row as independent. For a span of length `h`, a first-order
approximation is `n / h`; disclose any statistic that assumes independent
samples, and use a dependence-aware estimate such as HAC/Newey-West when the
claim depends on uncertainty rather than only the point estimate.

Before assigning severity from a capacity, cardinality, quota, or size limit,
derive the smallest supported input that reaches it through the shipped path.
Compare that threshold with upstream caps, including the values that determine
each item's encoded size or expansion. State likelihood separately from impact;
do not infer material likelihood from a raw count alone.

Scope environment-dependent claims to the verified version, artifact, test, or
issue. Preserve uncertainty when the evidence does not establish the boundary.
