# Design lane

Review ownership, reachable states, abstraction cost, and unnecessary
base-relative churn under the repository's language and design conventions.
When Python implementation or its owned configuration or interfaces are in
scope, read and apply the
[design-python-code workflow](../../../design-python-code/shared.md) in
review-only mode after reading repository instructions and established
conventions. Do not generalize its Python-specific rules to other languages.

Report runtime defects only with a concrete consequence for a current consumer.
Report diff-introduced churn only when the base comparison shows an avoidable
behavior difference, repeated work, reachable state, abstraction, or
maintenance obligation. This lane asks whether the current implementation has
the right ownership, reachable states, and abstraction cost.

Inspect test scaffolding changed to follow a new interface or ownership
boundary. When the diff mechanically changes identical construction,
injection, or mock wiring across cases, decide whether the nearest existing
helper can own the invariant part. Report a shared mutable double or avoidable
repeated changed wiring as a maintenance obligation; do not report distinct
scenario data, an explicit dependency repeated across independent harnesses,
or untouched inherited setup.
