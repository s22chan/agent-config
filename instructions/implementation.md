- For every implementation request, before recommending an approach or editing
  code, inspect the project manifest and lockfile, the standard library, and
  nearby implementations for a supported dependency or shared local operation
  that already owns the required contract. For generic infrastructure or a
  standard protocol, also search the current external package ecosystem for a
  maintained implementation and verify its supported behavior and version
  compatibility from primary sources. Compare each candidate's exact behavior,
  lifecycle, dependency cost, and adaptation cost with a direct implementation.
  Reuse it when it fits; keep domain policy local when a generic dependency
  would leave the same policy or add more translation than it removes.
- Before writing production code, trace the shipped entry point, current
  consumers, sibling implementations, and import boundaries. Decide which
  module owns each policy, state transition, and external effect, and which
  dependency direction preserves that ownership. Put facts that must change
  together at that owner and make callers depend on narrow immediate
  collaborators. After editing, reread the complete path for duplicated policy,
  hidden state, and new cross-layer coupling.
