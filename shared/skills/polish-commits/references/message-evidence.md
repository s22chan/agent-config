# Commit Message Evidence

Use only the sections relevant to the committed change.

## Behavior and Compatibility

- For a bug fix, name the observable failure and connect the defect to that
  outcome through each material causal step. Use a plausible workflow when the
  impact would otherwise be abstract, without implying unsupported prevalence.
- Scope checkpoint and persistence claims by the formats actually exercised.
  Name sharded, distributed, cloud, and full-file paths separately and cite the
  strict outer-reader test that reaches each claimed format.
- Call a test a minimal reproduction only when it reaches supported behavior
  and fails on the faulty revision for the claimed reason. Otherwise label it
  regression coverage and state the narrower invariant it proves. Do not use
  plumbing assertions or duplicate the test as pseudocode in the message.
- When removing a workaround, environment override, compatibility shim,
  defensive guard, or documented accepted input shape, explain the supported
  scenario that required it and the replacement invariant that makes removal
  safe. Trace the current producer and consumer through the real path, and name
  the direct safety evidence in the message. If safety depends on repository
  call sites, stored artifacts, or sampled runtime data, state the inspected
  scope and do not generalize the claim to uninspected external callers or data.
- When claiming that an optimization or refactor preserves behavior, state the
  old and new observable behavior and the invariant, equality, or mapping that
  makes them equivalent. Include old and new quantities when the preserved or
  changed behavior is quantitative. Cover relevant zero, empty, and boundary
  cases.

## Ownership and Intent

- For ownership or isolation fixes, identify both sides of the boundary: the
  caller that does not own the resource and a current supported consumer that
  does. Trace the concrete interference; distinguish importing a dependency
  from creating the process-global, filesystem, or external state at risk.
- Before calling existing code wrong or changing a longstanding contract,
  reconstruct its intent from the introducing commit through the target branch.
  Inspect blame, the introducing message and diff, later semantic changes,
  owning tests, and branch ancestry. Separate original purpose, later attempted
  repurposing, effective shipped wiring, and experimental or unmerged fixes.
- Trace triggering events through wrappers, traps, child processes, and handlers
  to the final consumer. A downstream handler does not prove that the configured
  event reaches it.

## References and Results

- Cite a check as evidence only when its result applies to the committed patch.
  Run the owning check when practical; otherwise say it was not run.
- Tie every external reference to the exact claim it supports and deep-link the
  narrowest stable section. Omit related precedent that does not justify the
  committed design or evidence.
- Include operational comparison or external precedent only when it materially
  explains behavior, a decision, or a limitation introduced by the diff.
- When a matched study isolates the exact executed transformation, include its
  verified primary effect and baseline-to-treatment values at the result step
  defined in `SKILL.md`. Scope the result to the measured workload,
  environment, and comparison. Keep benchmark values out of the subject. Do
  not omit an available result in favor of naming the optimization.
- For an independent commit, use timings only from that commit's exact tree.
  An aggregate or adjacent-path benchmark may support an aggregate change, but
  not a sibling branch that ships only part of the measured implementation.
  When matched timing is unavailable, include an exact directly proven
  quantity such as request count or reserved capacity at the result step, and
  state that runtime impact was not isolated. Never infer a speedup from that
  quantity alone.
- Include workload incidence or an input distribution only when it explains how
  often the optimized path runs or why the effect has its size. Name the sampled
  artifact and distinguish observation from configuration-derived probability.
- Reconcile requested evidence against the final prose: primary outcome,
  baseline and treatment, incidence, behavioral invariant, limitations, and
  report or test references. Replace stale disclaimers instead of appending
  contradictory results.

## Visuals

Use the smallest visual that matches the evidence: a table for exact mappings,
a sequence diagram for established ordering, and a chart only for a measured
trend. Do not imply timing, pairing, or causality that the evidence did not
establish. Use Markdown tables when the repository's commit viewer renders
GitHub-flavored Markdown; otherwise use fixed-width layout only when necessary.
