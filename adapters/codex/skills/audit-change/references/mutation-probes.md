# Isolated Mutation Probes

Use this procedure only when a tests-lane claim depends on whether a plausible
production mutation survives its owning test. The primary worktree and all
delegated audit lanes remain read-only.

## Establish isolation

1. Wait for every audit subagent and descendant to finish, then confirm through
   the live collaboration tree that none remains active. A parent final response
   or its claim about a child is not a liveness check. Codex collaboration
   shares the filesystem and does not give this workflow a per-agent worktree
   isolation control, so the root agent owns and executes probes serially.
2. Before delegation and again before probe setup, record the primary
   worktree's `HEAD`, NUL-delimited porcelain status with all untracked paths,
   and a digest of the binary tracked diff from `HEAD`. A status snapshot alone
   cannot detect changed contents that retain the same status code. When an
   untracked or ignored path is part of the execution environment, digest its
   content too or disclose that exact-state verification does not cover it.
3. Create a collision-free temporary directory and add a detached Git worktree
   within it at the audited revision. Record the exact path. Do not create a
   branch, move a shared ref, or reuse a worktree belonging to another task.
4. If the audit includes tracked uncommitted changes, reproduce their combined
   `HEAD` diff in the probe worktree and verify that it matches the audited
   baseline. Keep excluded untracked files excluded rather than copying the
   surrounding checkout wholesale.
5. Resolve every cache, temporary, coverage, snapshot, build, and artifact
   destination before execution. Redirect supported destinations into the
   collision-free temporary parent. If any write may escape those disposable
   paths or reach external state, do not run the probe and report it as
   `unrun`.

If an available editing or execution tool cannot be scoped unambiguously to the
probe path, do not run the mutation. Report it as `unrun`; a command that might
resolve against the primary checkout is not an isolation mechanism.

## Exercise the probe

1. Reuse an existing project environment only when it does not write through
   absolute paths into the primary checkout. Run its interpreter with the probe
   worktree as the working directory; do not install or solve a replacement
   environment during the audit.
2. Before trusting the first result, verify that production modules and other
   path-sensitive artifacts resolve under the probe root. A checkout or working
   directory is insufficient when an editable install can redirect imports to
   the primary tree.
3. Capture the probe baseline, apply one mutation, and assert that the relevant
   source or artifact differs from that baseline before running the smallest
   owning test through its shipped entry point.
   Keep application, assertion, execution, and restoration in one guarded
   process whose cleanup runs on success, failure, and interruption.
4. Record the exact mutation, invocation, exit status, resolved source or
   artifact origin, and observable result. `confirmed` means the mutation
   loaded and the test still passed; `refuted` means the mutation loaded and
   the test failed for the intended behavior. Otherwise classify it as `unrun`
   or inconclusive rather than inferring a verdict.

## Restore and verify

Restore the mutation on every exit path and inspect the exact probe worktree
before removing it. If a tracked target still differs from the pre-mutation
baseline, record the failed restoration and invalidate that probe's evidence;
restore that target from the captured baseline instead of forcing past it.
Preserve only results not recorded elsewhere. Inspect unexpected untracked
artifacts; move disposable ones to the configured temporary trash and evidence
that must survive to an explicit durable destination, verifying each move.

Reverse any intentionally materialized audit working diff so the temporary
worktree is clean. Then remove only the exact worktree created for that probe,
without `--force`. If removal leaves a stale administrative entry, report its
exact path instead of running repository-wide worktree pruning. If the worktree
cannot be returned to a known clean state, leave it in place, report its
absolute path, and do not hide the failure with destructive cleanup. Do not use
a broad path, glob, unresolved variable, or a cleanup owned by another task.
Because probes run serially with one mutation at a time, scope a restoration
failure to its target and result rather than invalidating unrelated probes.

Finally, re-record the primary worktree's `HEAD`, porcelain status, and tracked
diff digest, plus the digests of any relevant untracked or ignored paths. If any
differs from the pre-audit snapshot, disclose the change and treat
execution-based claims from the overlapping interval as unverified until they
are rerun from a known clean state.
