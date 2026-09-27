# Integrate Upstream Refactors

Preserve upstream structure and reapply the branch's intended observable
behavior on top of it. Do not resolve a conflict by selecting one side wholesale.

## Establish state

Start with `git status`. Resolve a target base named by the user or repository;
otherwise use the configured upstream or remote HEAD and ask when neither is
authoritative.

### Rebase or merge in progress

1. List unmerged files with `git diff --name-only --diff-filter=U`.
2. Read both changes and relevant incoming file history before editing. During
   a rebase, remember that `ours` is upstream and `theirs` is the replayed
   commit.
3. Preserve the upstream structure and reapply the branch behavior. Stage only
   explicitly resolved files and continue.
4. Ask before aborting or choosing a non-obvious semantic resolution.

### Rebase or merge already complete

1. List files changed since the authoritative fork point.
2. Inspect each touched file's history with `git log [-p/-L] -- <file>` to find
   refactors that landed beneath the branch.

## Integrate and verify

- Replace compatibility re-exports with canonical imports.
- Update call sites for changed signatures and required arguments.
- Adopt a new shared abstraction instead of retaining a parallel hand-rolled
  implementation.
- Remove duplicated definitions and repair prose displaced by moves.
- Run checks capable of detecting faults in the touched surface. If conflict
  resolution changed code, verify the final executed path rather than relying
  only on a clean rebase.

Report what landed upstream, what was integrated, and any remaining conflict
between upstream intent and the branch behavior.
