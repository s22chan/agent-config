# History Rewriting

## Establish Scope and Safety

1. Use a target base named by the user or repository. Otherwise resolve the
   remote default branch from the configured upstream or remote HEAD; ask when
   no authoritative base can be determined.
2. Fetch when the target base or configured remote refs may be stale.
3. Record `<old-tip>` as the original `HEAD` and `<old-base>` as
   `git merge-base <old-tip> <target-base>`. Confirm the original tip is in the
   reflog; for a complex or conflict-prone rewrite, create a named backup ref.
4. Require a clean worktree and index unless the user explicitly includes
   current changes in the rewrite plan. Never hide unrelated work.
5. Check fetched remote refs for commits in the rewrite range and disclose that
   unconfigured or unfetched remotes cannot be detected. Never rewrite known
   shared history without explicit approval.
6. Read every commit with `git show`; preserve merge topology unless the user
   explicitly approves flattening it. Preserve authorship and every trailer.
7. Update the base with `git rebase <target-base>` or an equivalent cherry-pick
   reconstruction followed by a rebase. Never move `HEAD` with
   `git reset --soft <target-base>`; that can absorb the upstream delta into the
   next commit.

Before analyzing relationships among branches or commits, resolve every named
or context-implied target to `ref | tip SHA | tip subject | worktree`. Resolve
labels such as "overlay," "fix," or "refactor" to the concrete commit, symbols,
and diff they denote; do not silently substitute an adjacent change with a
similar description. When multiple plausible refs or changes exist, reconcile
them with the originating request and relevant history. Ask or report each
interpretation when the remaining ambiguity would change the conclusion.
Record that target ledger before drawing a topology conclusion; an unresolved
row cannot support a categorical recommendation.

## Remove Stale Worktrees

Treat a worktree directory and its branch ref as separate cleanup decisions.
Before removing either, enumerate registered worktrees, inspect the exact
worktree status and diff, and establish whether its commits were merged,
patch-equivalent, or superseded on the authoritative base. Preserve dirty
worktrees, requested reference branches, and unique or ambiguous work unless
the user explicitly directs otherwise.

On VAST-backed paths, recursive unlinking through `git worktree remove` can be
materially slower than renaming the directory. When the user authorized the
cleanup, the worktree is clean, and the worktree and `/mnt/main0/.vast_trash`
are on the same filesystem:

1. Choose an exact, collision-free destination directly under
   `/mnt/main0/.vast_trash`. The trash is temporary, not archival.
2. Move the worktree directory there, then verify that the original path is
   absent.
3. Run `git worktree prune --expire now --verbose` from a surviving worktree to
   remove the stale registration. If an interrupted `git worktree remove`
   already made the entry prunable, re-resolve the directory and registration
   state instead of retrying recursive removal.
4. Verify `git worktree list --porcelain` and a dry-run prune. Delete the local
   branch ref only after its independent retention audit permits it; do not
   infer permission to delete remote refs.

If the paths are on different filesystems, use the ordinary Git removal path;
`mv` may degrade into a recursive copy and provides no fast-path benefit.

## Review the Series

1. **Intent** — State in the opening body paragraph why each commit should land.
   Reject a goal that only renames its subject or summarizes its diff.
2. **Accuracy** — Describe only the diff each commit ships. Remove WIP, review,
   debugging, and same-branch history.
3. **Cohesion** — Keep one logical change per commit. Flag proposed squashes,
   splits, or reorders rather than silently changing boundaries.
4. **Convention** — Match repository subjects and preserve authorship and
   trailers.

### Choose Commit Ownership

After establishing the target base and sharing state, decide whether current
work belongs in an existing branch commit or has its own reviewer-visible goal.

- Fold a correction, completion, missing test, or removal of temporary surface
  into its owning unmerged review commit when leaving it separate would make
  that earlier commit inaccurate, incomplete, or needlessly transitional.
- Use a standalone commit when reviewers can accept or revert its behavior
  separately without leaving an earlier commit inaccurate or incomplete, or
  when the owning history is merged or otherwise outside the rewrite scope.
  File overlap and general cleanup do not establish ownership by themselves.
- If the user explicitly requires additive history or forbids rewriting,
  preserve that constraint after reporting the ownership tradeoff. Describe a
  resulting follow-up as a constrained boundary, not as independently
  reviewable when it is not.

Before previewing a rewrite, prepare `commit | goal | mechanism | evidence` for
every commit. The goal must justify the change without depending on the
mechanism column. Revise any row whose goal merely restates the subject or diff.

Before recommending a split or dependency, materialize or explicitly derive
each proposed commit or branch tree from its declared parent. For every affected
contract, classify behavior as inherited unchanged, introduced at that
boundary, deferred, or removed, then verify that the candidate tree is
internally coherent and testable. Evaluate transition cost from that candidate
tree rather than from a mechanical partition of the final diff. Do not claim a
compatibility layer, temporary implementation, or immediate rewrite unless the
candidate tree actually contains code absent from both the base and final
trees.

Audit the intermediate trees for review-only surface, not only the aggregate
base-to-tip diff. Trace symbols and tests touched by multiple commits, looking
for wrappers, fields, parameters, aliases, representations, assertions, or
tests that one commit introduces and a later commit removes, renames, retypes,
or rewrites. Also catch a commit that establishes a new source of truth but
leaves the superseded owner for a later commit to remove. When a construct is
absent from both the authoritative base and final tip, write its owning commit
in the final form unless the temporary state is required to keep that
intermediate tree independently coherent and testable. Mechanical patch
convenience or adaptation to an internal API that the same series replaces is
not sufficient justification. Record the concrete transition requirement for
every temporary construct that remains.

Report branch relationships along separate axes: runtime or semantic
prerequisites; source, API, or persisted-data coupling; textual conflict and
rebase cost; and recommended landing order. Do not turn "not a runtime
prerequisite" into "independent" when another axis remains material, and do not
turn integration convenience alone into a dependency.

Use branch-state verbs precisely. Distinguish a branch that exists locally, is
published to a remote, is selected as another review's base, or is merged into
the target branch. A stacked child needs its base ref locally to be constructed
and remotely published to support a remote review; the base does not need to be
merged before the child can be created, pushed, or reviewed. Before saying one
branch must precede another, name whether the constraint is ancestry,
publication, review order, or merge order. Describe a conflict-minimizing or
review-friendly order as a recommendation, never as a prerequisite.

## Split Review Branches

- Treat each requested independent branch as a separate PR candidate based
  directly on the target base. Translate the change onto the target base's
  paths and abstractions when necessary. Expected merge conflicts, overlapping
  or moved files, package layout, import paths, and easier patch application do
  not justify stacking branches.
- Apply the commit-ownership decision above before creating a correction or
  fixup branch. A separate branch must remain independently shippable from the
  target base, not merely make a sibling branch accurate or complete. Do not
  use a separate branch only to avoid an otherwise approved fold-back.
- Split by reviewer-visible behavior and ownership, not by original commit or
  file. File overlap does not establish a dependency, and one behavior may
  legitimately span production code, configuration, and tests.
- Do not equate every logical commit with a separate branch. Keep changes in
  one review branch when they share the authoritative owner, shipped entry
  point, and rollout contract, and accepting either change alone would leave
  that operational path incomplete or internally inconsistent. Use separate
  commits within the branch when their mechanisms remain independently
  reviewable. A likely merge conflict can prompt this ownership check, but is
  not sufficient evidence by itself.
- Keep a regression test with the production change it proves. Put test-only
  cleanup in separate branches grouped by owning entry point and rationale,
  such as hermeticity, redundant internal-contract assertions, or stronger
  end-to-end evidence. Revisit the test diff after splitting production and
  separate groups that a reviewer could accept or reject independently; do not
  leave an unrelated catch-all test-cleanup branch.
- Make every branch independently applicable and verifiable from its declared
  base. Tests and fixtures must not rely on helpers introduced only by a sibling
  branch; use narrow local scaffolding when that preserves independence. Base a
  test-only branch on a production commit only when the test requires behavior
  or files introduced by that commit.
- Name each branch for its own behavior. Do not add a personal or owner prefix
  unless the user or repository requires one, and do not configure the target
  base branch as its upstream.
- Before finalizing, audit branch-to-base mappings, run each branch's owning
  checks, and compose a temporary aggregate over the authoritative base. Compare
  that aggregate with the original change set and explain every difference.

Treat every non-base parent as a dependency claim. Stack only when the user
explicitly requests it or the child production behavior consumes a runtime
contract that does not exist on the target base. A refactor, file move, shared
test helper, documentation update, or anticipated conflict is not such a
contract when the behavior can be expressed against the target base. Examples,
demos, benchmarks, documentation, fixtures, and tests do not alone justify
ancestry between otherwise independent changes. Put explicitly requested
cross-branch integration coverage in a separate integration branch.

When the user disallows branch dependencies, treat that as an absolute topology
constraint: every review branch must contain only its own commits above the
target base. Adapt or duplicate the minimum local scaffolding needed to make
each branch build and test independently, and leave cross-branch conflicts for
later integration. Before reporting the split complete, verify that each pair
of sibling branches has the target base as its merge base and that each
``target..branch`` range contains only branch-owned commits.

When independently shippable PRs can land in either order, put the simplest one
first: prefer the smallest production surface, fewest runtime risks, and fewest
dependencies. Production dependencies, migrations, and fixes that restore
reliable test signal take precedence. Do not order branches solely to reduce
later rebase conflicts.

Keep evidence reviewer-actionable. Prefer a test path plus specific node and its
covered invariant. Omit mechanics recoverable from the diff, exhaustive edge-
case inventories, and lists of every test.

## Preview and Rewrite

Resolve ordinal references such as “first” to commit SHAs. Preview the resulting
order, boundaries, authorship, and trailer disposition. Show each proposed
message change as a fenced `diff` block and disclose shared-history risk. Obtain
explicit approval before changing history; approval does not authorize a push.

- Bind message files to commit SHAs during interactive rebase; do not depend on
  todo position.
- Preserve trailers when replacing a full message with
  `git commit --amend -F`.
- Record the original range's aggregate diff and changed paths. During
  reconstruction, stop if staged content contains unexplained upstream
  reversals or unrelated paths.
- If a conflict cannot be resolved from the intended patch and target-base
  behavior, stop with the rewrite state intact and obtain explicit approval
  before aborting it and returning to `<old-tip>`. Rerun owning checks after
  conflict resolution changes code.

## Verify

- Run `git range-diff <old-base>..<old-tip> <target-base>..HEAD` and explain
  every mapping. A message-only rewrite must contain no code diff.
- For a squash, split, reorder, or conflict resolution, compare aggregate old
  and new changes and account for every difference.
- Confirm final authorship, trailers, order, worktree state, and pushed status.
  Report message changes inline and list unresolved boundary decisions.
