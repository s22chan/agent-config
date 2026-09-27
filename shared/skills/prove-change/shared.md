# Prove a Change

Compare the same decisive exercise on the authoritative base and current
change. Treat regression checks as supporting evidence, not as the behavioral
proof itself.

## Resolve the comparison

1. Use a base supplied by the user or repository. Otherwise resolve the target
   from the configured upstream or remote HEAD; ask when none is authoritative.
2. Inspect the complete merge-base diff and sanity-check its size and paths.
3. Identify the exact shipping artifact, entry point, runtime environment, and
   final observable effect. Stop plainly when that path cannot be exercised.
4. Choose a minimal input that makes the intended behavior and plausible
   competing explanations produce different results.

## Exercise both revisions

1. Capture base behavior without disturbing the current tree. Prefer a detached
   temporary worktree; account for path-sensitive behavior and shared external
   state.
2. For dynamically resolved runtimes, select source code explicitly for each
   arm and assert that loaded production modules originate under the intended
   revision root before exercising behavior. A checkout, working directory, or
   driver path is insufficient because an editable installation, shared
   environment, or search path can redirect imports.
3. Record the revision root, entry-point identity, dependency environment, and
   resolved production-module origins separately. Stop when the source origin
   for either arm cannot be established.
4. Run the identical exercise against the working change, including
   uncommitted changes when they are in scope.
5. Confirm the intended command, backend, kernel, configuration, or integration
   actually ran. A swallowed failure or adjacent path is not evidence.
6. Compare output, exit status, measurements, and final persistent state across
   the complete owning window.
7. Restore any temporary worktree and confirm the original worktree and index
   remain unchanged.

Before claiming two third-party paths are equivalent or divergent, inspect the
installed version's implementations and the runtime mode that reaches them. Do
not infer semantics from API names or generic library behavior.

Before claiming duplication or indirection was removed, inspect the final
executed path and verify that the old mechanism no longer remains elsewhere.

## Report evidence

Lead with the verdict and compact before/after observations. Separate proof of
the requested behavior from regression checks, scope every claim to what ran,
and list any contract that remains unverified.
