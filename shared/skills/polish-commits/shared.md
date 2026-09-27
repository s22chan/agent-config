# Create and Polish Commits

Make each commit describe its final diff as if read fresh on the target branch.

## Choose the Workflow

- Before choosing the new-commit workflow, use the request context and diff to
  detect whether the work may correct, complete, supply missing tests for, or
  remove temporary surface from a commit already on the current branch. When
  it may, read [history rewriting](references/history-rewriting.md) before
  deciding the boundary; that reference owns target-base and sharing checks
  plus the fold-versus-additive decision. A request to "commit" authorizes
  creating a commit, not rewriting existing history.
- For a new commit, inspect the exact staged and unstaged changes, discover the
  repository's commit convention, author the message, commit only when the user
  requested it, and verify the resulting commit. Do not perform rewrite-only
  base, sharing, preview, or range-diff steps.
- For commit-series review, history cleanup, rebasing, or any rewrite, read
  [history rewriting](references/history-rewriting.md) before changing history.
- For a message that needs correctness evidence, performance results, ownership
  rationale, compatibility scope, external references, or a visual, read
  [message evidence](references/message-evidence.md) before drafting the body.

## Author Each Commit

- Follow explicit repository instructions, then inspect recent subjects for a
  clear local convention. Treat mixed or sparse examples as no convention.
  Otherwise use Conventional Commits, adding a scope only when the affected
  component has a stable, unambiguous name.
- Write a concise, imperative subject. Unless the repository requires another
  limit, keep every non-URL message line at 72 characters or fewer and wrap the
  body at 72 columns.
- Use plain, concrete language. Prefer short sentences and familiar words;
  keep technical terms only when they name the concept precisely.
- Before describing mechanics, state why the commit should exist in terms of
  the concrete benefit or avoided failure for a user, operator, reviewer, or
  maintainer. Name the observable outcome, supported contract, or maintenance
  consequence that matters downstream. A code action such as simplify, remove,
  consolidate, narrow, or replace is a mechanism, while a property such as
  strict, consistent, compatible, focused, or hermetic is only an invariant;
  neither is a goal unless the sentence explains what it enables or prevents.
- Anchor goal selection in the originating request and its causal hierarchy.
  When the requested outcome requires supporting ownership, path, rollout, or
  deployment changes, lead with the outcome and describe those prerequisites
  as mechanism or context. Do not promote a secondary migration to the goal
  because it touches more files or makes a convenient narrative.
- Use one causal order in the body: first state the concrete problem or goal
  and its consequence; then explain the shipped solution and why it addresses
  that problem; then report verified results and their scope; finally list the
  owning checks. Do not state a benchmark delta before the reader knows what
  change produced it. Include relevant preconditions, triggers, failures, and
  resulting invariants where they support that sequence. Remove draft,
  debugging, review, and same-branch history.
- When a change adapts supported behavior to a different or reduced capability
  set, state the overall adaptation strategy before low-level mechanics. Name
  material capability differences with their exact metric, API, event, or
  configuration identifiers when those identifiers define the contract. For
  each unavailable capability that affects observable behavior, distinguish an
  equivalent replacement, partial coverage through another signal, and
  explicit disablement when no reliable replacement exists. State what partial
  coverage retains without presenting it as equivalent. Omit query, join, and
  control-flow detail unless it is needed to explain correctness or the
  supported contract.
- When an incident, review, audit, failing check, or mutation result drove the
  change, preserve that verified trigger in the opening rationale. Name the
  concrete behavior that failed, passed unexpectedly, or survived testing and
  connect it to the operational consequence. Do not reduce the motivation to
  generic coverage, correctness, cleanup, or hardening, and omit reviewer or
  tool identity when it adds no causal evidence.
- Give refactors and test-only changes the same explicit goal. Name the
  supported behavior, ownership boundary, reliable signal, or maintenance
  obligation improved by the change; do not use cleanup itself as the reason.
- Scope every claim to verified behavior. Cite the owning behavioral test,
  benchmark, or other direct check that establishes it; otherwise identify the
  evidence as not run or the claim as unverified.
- At the result step for a performance, capacity, or resource change, give the
  strongest verified delta available, such as latency, throughput, request
  count, memory, or reserved capacity. State the baseline and treatment under
  matched conditions. Keep the subject focused on the concrete problem or
  user/operator outcome. Do not substitute the mechanism or an asymptotic
  claim for impact. When matched timing is unavailable, use an exact directly
  proven quantity and say that runtime impact is unmeasured; never attribute an
  aggregate benchmark to an independent commit that ships only part of it.
- For a user-visible format, grammar, rendered label, or interaction change,
  include a minimal concrete before/after example in the commit body when it
  makes the outcome clearer. When the commit changes multiple independently
  meaningful fields or placements, show each of those differences; one changed
  label is not a sufficient proxy. Derive the example from a verified test or
  artifact; do not invent an example merely to satisfy this rule.
- Every new commit needs a non-empty body. Prepare its subject, blank line, and
  body in a temporary message file; inspect that exact file, then create the
  commit with `git commit -F`. Do not use `git commit -m` as a shortcut, even
  when the subject seems self-explanatory.
- Treat the body as a reviewer index, not a design document. Unless the user or
  repository requires another format, use at most 250 words and three compact
  sections. Cite evidence from at most three owning tests.
## Verify

- Before drafting an amended commit message, inspect the complete candidate
  against its parent with `git diff --cached HEAD^`, including changed paths,
  rather than only the delta staged since the previous amendment. Make a
  behavior-to-message ledger for each independently observable final outcome:
  map it to a body sentence or record why it is immaterial. Preserve still-true
  claims from the existing body; revise or omit them only when the final
  candidate invalidates them or makes them immaterial. Fail verification on an
  unexplained omission.
- Before finalizing a commit or rewritten series, discover the repository's
  formatter and pre-commit entry point. Run every hook that applies to the
  changed files through that exact entry point (for example,
  `pixi run --frozen pre-commit run --files ...` in a Pixi repository). A
  direct linter invocation is not evidence that its formatter hook passed.
- If a hook rewrites files, inspect the patch, fold it into the commit that
  owns the affected code, and rerun the applicable hooks. For a rewritten
  series, do this after the final rebase or autosquash; do not leave a
  formatter-only tip commit merely to satisfy the hook.
- Inspect `git show --stat --oneline HEAD`, the full diff and message, authorship
  and trailers, and the final worktree and index state.
- Treat a missing commit body as failed verification. Inspect `git log -1
  --format=%B` and amend the commit before reporting it if no non-empty body
  follows the subject.
- For a bug fix with a verified error, fail verification if the message replaces
  the trigger or emitted failure with a generic reliability or correctness
  claim. Require the exact triggering scenario and observable error, including
  the exception type or message when known, before explaining the cause and fix.
- Fail verification when the opening body paragraph does not answer why the
  commit should land, or when it only restates the subject, edited symbols,
  implementation actions, desired properties, or compatibility boundaries.
  Require it to name a concrete downstream benefit or avoided failure and to
  remain meaningful before the reader knows how the diff implements it. Phrases
  such as "keep X strict" or "preserve X without breaking Y" fail unless they
  also explain why strictness or compatibility matters to a current consumer.
- Fail verification for a performance, capacity, or resource commit when a
  verified before/after result for the exact committed patch is omitted or
  disconnected from the solution that produced it, or when the claimed result
  comes from a candidate containing changes outside that commit. Fail when a
  quantitative result appears before the solution and causal link that explain
  it. Require the primary delta and its measurement scope before the check
  list. If only a direct non-timing quantity is proven, require that quantity
  instead of an inferred speedup.
- Compare the opening goal with the originating request. Fail verification when
  it foregrounds a prerequisite or secondary effect while omitting the primary
  requested outcome.
- For an adaptation to a different capability set, fail verification when the
  body only says that capabilities differ or that unsupported inputs are
  omitted. Require the observable disposition of each material difference:
  replacement, partial coverage with its limit, or explicit disablement.
- Fail verification for incident-, review-, audit-, check-, or mutation-driven
  work when the message omits the verified trigger that caused the change or
  the concrete failure mode it exposed. Test mechanics and implementation
  invariants do not substitute for that provenance.
- For a narrowed or removed compatibility behavior, fail verification unless
  the body identifies the current supported consumer, explains why that path
  is unaffected, and names the direct evidence and its scope. Do not accept
  labels such as unused, legacy, strict, or unsupported as proof by themselves.
- Inspect `git log -1 --format=%B` and fail verification if a non-URL line
  exceeds the selected limit, except for a required trailer that cannot comply.
- Inspect every edit made automatically by pre-commit hooks before accepting
  it. Formatting-only edits require rerunning the hook and inspecting the final
  patch; edits to executable behavior or configuration also require rerunning
  the owning checks against that final patch and fixing them in the owning
  commit.
