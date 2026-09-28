# Tests lane

Read and apply the
[verify-behavioral-tests workflow](../../../verify-behavioral-tests/shared.md)
as a filter over tests in scope. Find behavior a reader would think is protected
but that can regress while the test still passes.

When collaborator destination or threading is supported behavior, reject a
type- or module-wide patch as evidence if the shipped boundary accepts an
instance. Verify that the configured double is the instance reached through
that boundary.

For every candidate, return the owned contract; the exact test, change claim,
regression, or history that establishes it; the base and current safeguards;
why the proposed mutation violates that contract rather than an adjacent
implementation detail; and why a permanent detector is proportionate instead
of one-time verification. For every in-scope safety or correctness detector
over another shipped component's artifact, apply that workflow's
producer-derived positive-witness requirement. Do not let one candidate
mutation stand in for the remaining detectors.

Name the highest-consequence plausible surviving production mutation for root
verification after all lanes finish. Recommend `strengthen` or `delete`.
