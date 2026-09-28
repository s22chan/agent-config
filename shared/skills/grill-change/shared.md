# Grill a Change

Review as a skeptical staff engineer. Do not call a change ready while a
material failure mode or unsupported claim remains open.

## Establish scope and findings

1. Resolve the user- or repository-named base. Otherwise use the configured
   upstream or remote HEAD; ask when neither is authoritative. Fetch only when
   the task permits remote-ref updates, and disclose stale-ref limitations.
2. Inspect the complete merge-base diff. Recompute scope when the file count is
   implausible, and read affected implementations, callers, configuration,
   rationale, and owning tests.
3. For commit or branch topology decisions, also use the applicable
   commit-polishing workflow; this workflow owns behavioral risk, not ancestry
   or landing structure.
4. Track every finding with severity, owner, and one disposition: open,
   verified fixed, rejected with evidence, or explicitly approved deferral.
   Green checks do not close unresolved design or performance questions.

## Ground operational relevance

For each concern, establish this chain:

`supported consumer → real trigger or producer → executed path → observable
consequence → existing safeguards`.

- A constructible or mocked state proves implementation behavior, not that a
  supported workflow supplies it. Classify the trigger as normal execution,
  known operational event, exceptional failure, invalid configuration,
  unsupported operation, or hypothetical. Say when frequency is unknown.
- Inventory every new guard, fallback, coercion, and silent default as
  `branch → supported trigger → consequence`. Remove machinery with no
  supported trigger unless the user explicitly chooses optional hardening.
- Trace the consequence to wrong output, action, persistence, data loss, or
  outage. Credit warnings, conservative defaults, confirmation, retries, and
  containment that reduce realized impact.
- When the initiating operation already fails visibly, assess only the added
  harm from missing recovery or cleanup. Separate recovery from diagnostics:
  propagating an actionable exception is not recovery.
- Calibrate severity from likelihood and impact. A rare case may still be
  severe when catastrophic, irreversible, or security-sensitive; a synthetic,
  low-impact case is optional hardening, not a priority defect.
- Match remediation cost to residual severity. Do not add global discovery,
  synchronization, retries, caches, compatibility paths, or lifecycle state
  when a simpler boundary or existing containment addresses the supported case.

## Reframe clustered remedies

Before implementing a batch of review fixes, group findings by the authority
and invariant that own them. Trigger a combined design check when several
findings target one abstraction or their proposed remedies add compensating
branches, state, fallbacks, or post-processing.

Treat repeated audit/fix rounds that reopen adjacent defects as the same
trigger, even when each new finding appears local. Preserve verified
requirements, evidence, and acceptance criteria, but stop extending the
current patch shape and re-derive the design from the earliest informed owner.
Prefer that owner-level redesign unless the findings have independent owners
and the combined form would add more reachable states or coupling. Do not wait
for the user to ask explicitly to scrap the accumulated remedies.

Restate the supported contracts, producers, and consumers from the accumulated
evidence. Compare the smallest independent repairs with a redesign at the
earliest boundary that owns the variation. Ignore sunk implementation cost,
but price both options by reachable states, duplicated policy, new machinery,
failure modes, and verification burden.

Recommend the redesign when it removes multiple special cases without
weakening supported behavior. Otherwise keep independent fixes local; shared
location or similar symptoms alone do not justify a rewrite. State the chosen
design, its main tradeoff, and the decisive disadvantage of the strongest
alternative before editing. Preserve every finding's trigger, consequence,
and acceptance criterion through implementation and verification.

Keep one closure ledger across the redesign: map each surviving finding to its
owner, trigger, consequence, disposition, and decisive verification. After the
implementation, reconcile every row and exercise the shipped outcomes that
distinguish the old failures; use targeted mutations when a silent regression
could otherwise survive the owning tests.

## Recover established intent

Before removing or replacing a guard, workaround, synchronization, reset,
fallback, compatibility path, or apparently redundant operation:

1. Trace its current call path and nearby rationale.
2. Inspect exact-line blame, its introducing commit, and relevant later changes.
3. Identify the original failure, the invariant established, and the evidence
   that a later change makes it obsolete. A later mitigation alone is not proof;
   verify their combined behavior across the modes each governs.
4. If the origin is a merge or squash, inspect constituent change history and
   review context when available. Otherwise report intent as unverified rather
   than inferring it from the landing message.

Treat parser, matcher, regex, and decoder changes as input-boundary changes:

- For narrowing, establish why broader observed formats were accepted and test
  representative producer or client inputs before removing them.
- For widening, enumerate the new accepted space and its validating authority.
  Untrusted text may identify a candidate but must not define trusted services,
  namespaces, paths, or identifiers owned by configuration or an allowlist.
- Exercise the intended format and the nearest plausible non-target lookalikes.

## Validate claims and remedies

- Treat comments, docs, tests, and commit rationale describing a tradeoff,
  fallback, limitation, or rejected alternative as claims. Reconstruct the
  avoided failure, accepted cost, and supported scope, then verify the code.
  Accurate scoped rationale rejects a defect; stale or false rationale does not
  immunize one.
- Do not silently strengthen ambiguous documentation into a contract. Establish
  its repository meaning and consumers, or report the ambiguity and the
  consequence of each interpretation.
- Reproduce or trace the concern on the current tip and exact shipping
  configuration. Account for later fixes and reordered or spun-out work.
- Separate a valid finding from its proposed remedy. Price every remedy against
  the authoritative base, including machinery, state, recurring cost, failure
  modes, and tests. Treat diff-added machinery as removable, not sunk cost, and
  choose the smallest change that prevents the supported failure.
- Use dependency and sibling-implementation evidence already established for the
  same task, contract, and revision. Inspect further only when that evidence is
  absent, a dependency-search reopening condition applies, or the review
  identifies a specific unsupported behavior. Do not repeat candidate discovery
  merely because this workflow follows design or implementation. Prefer a
  dependency's supported lifecycle unless executed evidence shows it is
  insufficient.
- Select only adversarial dimensions reachable in the touched contract. Check
  untested branches, error paths, defaults, caller blast radius, and assumptions
  not enforced by types, validation, or contracts.
- Observe persistent state—accumulators, caches, counters, RNG, hooks, and
  similar state—across its complete reset or reporting window.
- Reject evidence from an adjacent backend, proxy, mock call count, or assertion
  derived from the implementation when it does not prove the shipped outcome.
  Require evidence before adding recurring hot-path or lifecycle cost.
- For remediation of an earlier finding, preserve its trigger, consequence, and
  acceptance criterion. Mark it fixed only when the root condition is absent,
  not merely when the proposed edit landed.

## Reach a verdict

Lead with the sharpest open concern and its observable consequence. Reconcile
every finding before sign-off. A deferral requires its reason, consequence, next
action, and explicit approval; otherwise keep it open. Summarize the evidence
that changed the verdict and ask only questions evidence cannot resolve.
