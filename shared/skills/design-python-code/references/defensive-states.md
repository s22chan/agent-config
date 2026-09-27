# Price Defensive States End to End

- Treat a configured artifact, service, or provider as part of the requested
  identity. If it is missing, fail at that boundary; do not silently substitute
  another source. Retain a fallback only when a current supported workflow
  explicitly defines the sources as interchangeable—an existing fallback,
  comment, or documentation claim alone is not evidence.
- Prefer one required supported path over an explicit/default/fallback state
  matrix. Do not add provenance flags or selection states solely to recover
  from a missing required artifact.
- Before retaining defensive behavior, name the current supported producer,
  consumer, or deployment that can reach the guarded state and the material
  outcome it prevents. Do not treat a synthetically constructible state as
  evidence that the workflow supports it.
- Justify each rejected state independently. A supported untyped or historical
  container does not justify validation for every value Python could place in
  it. Trace the exact field value to an authoritative writer, an observed
  artifact, or a documented external contract; otherwise do not add a branch
  solely for coercion, subclass, or manually corrupted-value cases, such as
  excluding `bool` only because it is an `int` subclass.
- For serialized-state migrations, enumerate the formats that real prior
  writers emitted and distinguish only those formats. Use an actual base
  fixture or inspected artifact when available. Do not turn migration of one
  supported legacy shape into a general schema validator for malformed,
  hand-edited, or hypothetical third-party state.
- Charge the guarded state for its entire causal bundle, not only the terminal
  check: alternate loading or construction, global registry and path handling,
  cleanup, validation branches, comments, and tests. If removing an unsupported
  state collapses that machinery, count all of it as defensive cost.
- Prefer the simple supported path when an excluded state would fail promptly
  and clearly. State a non-obvious invariant near its owner, but do not build
  recovery or nicer diagnostics for a condition the current workflow excludes.
- Use a cheap local assertion to guard a supported invariant when useful. Do
  not let that assertion justify machinery added only to make a hypothetical
  state detectable.
