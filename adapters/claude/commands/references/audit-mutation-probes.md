## Probe isolation

A mutation probe provides direct evidence when a finding depends on whether a
plausible production change survives its owning test. Run it when the following
isolation can be established; otherwise report it as UNRUN. Never probe in the
primary worktree or while an audit agent remains active.

Before dispatching sources, record the primary worktree's `HEAD`, NUL-delimited
porcelain status with all untracked paths, and a digest of its binary tracked
diff from `HEAD`. When an untracked or ignored path participates in execution,
digest its contents too or disclose that exact-state verification excludes it.
A status snapshot alone cannot detect changed contents that retain the same
status code.

After every source and descendant stops, the root owns probe setup, execution,
and cleanup:

1. Resolve a collision-free path under the repository's
   `.claude/worktrees/` directory and verify with `git check-ignore` that the
   path is ignored. If that managed location would change primary-worktree
   status, report the probe as UNRUN. Create one detached Git worktree there at
   the exact audited tip. Do not use Agent `isolation: "worktree"`: its
   configured base can differ from the audited tip and a fresh base may update
   a remote reference. Do not create a branch or fetch.
2. If tracked uncommitted changes are in scope, materialize their captured
   binary diff in the probe worktree and verify that the resulting baseline
   matches the scope handed to every source. Keep excluded untracked files
   excluded.
3. Use `EnterWorktree` to enter that worktree only after the live agent listing
   is empty; an ordinary `cd` does not persist across tool calls. Run deferred
   tests and checkers there. For each mutation, apply, assert, execute, and
   restore in one guarded script whose cleanup runs on success, failure, and
   interruption. Run one mutation at a time and verify the tree returns to its
   pre-mutation baseline before the next.
4. Before execution, resolve every cache, temporary, coverage, snapshot, build,
   and artifact destination and redirect supported destinations into the
   disposable managed-worktree area. The probe must not write the common Git
   directory, shared refs or configuration, the primary checkout, another
   agent's paths, user caches, or external state. If any write may escape, mark
   the probe UNRUN. Reuse an existing project environment only when those
   conditions hold; do not solve or install a replacement environment.
5. Before trusting the first result, shadow the package or artifact under audit
   with a marked decoy and confirm that execution resolves under the probe root.
   An editable install that redirects to the primary tree can otherwise invert
   every "mutation survived" verdict.
6. Record the exact mutation, invocation, exit status, source origin, and
   observable result. CONFIRMED means the mutation loaded and the test still
   passed; REFUTED means it loaded and the test failed for the intended
   behavior. Anything else is UNRUN or inconclusive.

Before teardown, inspect the exact probe worktree. A tracked target that differs
from the captured baseline means restoration failed: record that failure and
invalidate that probe rather than forcing past it. Preserve only results not
recorded elsewhere. Inspect unexpected untracked artifacts; move disposable
ones to the configured temporary trash and evidence that must survive to an
explicit durable destination, verifying each move.

Reverse any materialized working diff so the temporary worktree is clean, use
`ExitWorktree`, then remove that exact worktree without `--force`. If it cannot
be returned to the known clean state, leave it in place, report its absolute
path, and do not hide the failure with destructive cleanup.

Finally, re-record the primary worktree's `HEAD`, porcelain status, tracked-diff
digest, and any relevant untracked or ignored digests. If any differs from the
pre-audit snapshot, disclose the change and treat execution-based claims from
the overlapping interval as unverified until rerun from a known state.
