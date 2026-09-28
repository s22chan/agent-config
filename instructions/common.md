## Instruction and configuration changes

- Use `maintain-agent-instructions` when adding, fixing, or clarifying an
  operational rule or changing instruction or configuration policy. It owns
  behavior boundaries, source-of-truth selection, incident replay,
  generalization, and routing validation.
- Personal agent configuration is sourced from `~/agent-config`: use
  `instructions/` for root instructions, `shared/` for cross-tool workflow
  bodies, `adapters/{codex,claude}/` for tool-specific surfaces, and
  `preferences/` for managed settings. After editing, run
  `~/agent-config/bootstrap.sh`, which synchronizes and validates the installed
  configuration. To check consistency without applying changes, run
  `~/agent-config/sync.py --check` instead. Do not repeat that check after an
  unchanged successful bootstrap, and do not edit installed generated copies.

## Verification

- In Pixi projects, default to `pixi run --frozen ...`; run pytest as
  `pixi run --frozen pytest ...`.
- Apply every workflow whose description matches the task. When several apply,
  combine them by ownership: use
  `design-python-code` for production structure, `verify-behavioral-tests`
  for test evidence, `verify-ml-training-changes` for training-specific
  runtime semantics, and `design-diagnostic-visualizations` for diagnostic
  encoding and interpretation. Do not let one suppress another's applicable
  checks.
- When applicable rules request the same search, trace, artifact inspection, API
  read, or check over unchanged inputs, perform it once and let each workflow
  evaluate the shared evidence. Repeat work only when a rule explicitly requires
  independent judgment, relevant inputs or state changed, the prior result was
  invalidated, or the first pass left a specific gap. Starting another workflow
  or reaching handoff is not by itself a reason to repeat work.
- Run the smallest decisive checks appropriate to the changed behavior and any
  required repository checks. Add or broaden checks only when changed code or
  configuration invalidated earlier evidence, a failure requires diagnosis, or
  a specific unresolved concern requires another check.
- Verify the final result before reporting completion, separating evidence that
  the new behavior works from regression checks.
- Scale checks to the edit surface: use runtime tests for runtime changes, the
  applicable checker for directive-only changes, and a syntax or parse check for
  prose-only changes.
- Never bypass Git hooks with `--no-verify`, `SKIP`, hook-configuration
  changes, or an equivalent workaround. If a hook fails, fix the failure in
  its owning commit and rerun the real hook; if that cannot be done safely,
  stop and report the blocker instead of committing.

## Costly operations

- Ask before starting long training runs, large downloads, W&B runs, cloud
  jobs, uploading large artifacts or checkpoints to remote storage, or bulk
  paid API calls.

## Code prose

- Before creating a source file, read the applicable project style rules and
  do not add template boilerplate unless those rules permit it. Verify the
  final diff for prohibited constructs.
- When documenting a design chosen over a familiar simpler alternative, state
  the decisive reason that alternative is insufficient, not only the chosen
  mechanism.
- Default to no comment. Keep only a non-obvious constraint, invariant,
  workaround, derivation, or decision that a fluent reader cannot recover from
  the code.
- Treat standard domain preconditions implied by an API, type, or primitive as
  recoverable by a fluent reader. Document them only when the code imposes a
  narrower or surprising local requirement.
- Comment intentionally discarded or apparently redundant work when its purpose
  is to preserve observable state, RNG, or ordering; exercise idempotence or
  retry safety; or enforce another non-obvious invariant.
- Document non-obvious configuration choices at the setting that owns them.
  In particular, explain a selected performance boundary or bucket, and the
  cost and correctness consequence of synchronization, buffering, or another
  runtime tradeoff that a reader cannot infer from the value alone.
- When refactoring, retain or relocate a source or specification citation when
  it explains an invariant that remains true; remove it only when it no longer
  describes the current code.
- Scope factual claims to the evidence. Preserve uncertainty when an
  environment-dependent boundary is not established; prefer a checkable
  version, artifact, test, or issue when one establishes it.
- Put prose at the definition and scope it describes: line-specific comments
  beside the line, cross-cutting rationale in the function or class docstring,
  and design justification on the definition that embodies the design.
- Describe the code as it stands. Remove edit history, diff-relative narration,
  stale specifics, transient branch/PR references, and comments that restate the
  next line.
- When revising source prose, audit identifiers before finalizing. Replace a
  bare snake_case or camelCase name from the surrounding implementation with a
  domain term unless readers need it to use a documented external API or
  contract.
- Do not present an adjacent operation or its immediately visible consequence
  as rationale. When a comment guards a future change, lead with the change
  trigger and required companion action, not a description of the current
  mechanism. If a comment already captures the non-obvious invariant, keep it
  unchanged; when only a label or step number becomes stale, remove only that
  stale text unless the prose has a material accuracy defect.
- For ordering or synchronization comments, state only the non-local
  postcondition that following code may rely on, such as which participants
  must reach a point before another can continue. Omit local effects already
  apparent from the adjacent operation. Name the specific operation that
  establishes the guarantee when a generic reference would be ambiguous, but
  mention its internal synchronization mechanism only when that mechanism is
  itself a non-obvious, load-bearing constraint.
- When variants, including authority/fallback paths, have different observable
  outputs, document each branch's contract instead of promoting one variant's
  behavior to an umbrella claim. For a fallback, name the primary authority,
  trigger, limited effect, and any operation it cannot authorize.
- Keep docstrings to a direct summary plus a short why only when the why passes
  the same non-obviousness test. Leave existing correct prose untouched unless
  the code change makes it inaccurate.
- Make a docstring's why state the durable constraint and consequence a caller
  needs, not transient investigation history. Keep environment or benchmark
  detail only when it establishes a supported boundary or rules out a familiar
  alternative.
- Match an existing Python file's majority docstring convention when editing
  it. For a newly created file, or one with no established convention, use
  modern Google-style docstrings (`Args:`, `Returns:`, and `Raises:` only when
  they add useful contract information). Do not default a new file to NumPy
  parameter sections; do not add empty or self-evident sections merely to
  satisfy the style.
- When a comment only decodes an unclear local name and renaming does not break
  a supported interface, prefer the clearer name.
- Name sibling concepts consistently. Keep diffs tight: do not rename or
  reformat unrelated code, and give a worthwhile broad rename its own commit.
- Keep file headers to invocation, prerequisites, and tunable settings. Explain
  a non-obvious value's derivation where it is used.
- Treat agent instruction files such as `AGENTS.md`, `CLAUDE.md`, and `SKILL.md`
  as operational configuration, not documentation. Do not use `polish-docs`
  for targeted rule changes.

## Code

- Implement only behavior required by current supported consumers. Keep
  responsibilities narrow and real variation points local so a concrete
  new consumer can add an implementation without changing unrelated core
  logic. Do not add unused modes, flags, abstractions, compatibility
  paths, or tests for hypothetical customers. Extensibility means the
  next concrete case is a local addition, not that its behavior is built
  in advance.
- Run one contract-scoped dependency check before recommending an implementation
  or editing code. Inspect the project manifest and lockfile, the standard
  library, and nearby implementations for a supported dependency or shared local
  operation that already owns the required contract. For generic infrastructure
  or a standard protocol, also search the current external package ecosystem for
  a maintained implementation and verify its supported behavior and version
  compatibility from primary sources. Within the same task, contract, and
  revision, perform candidate discovery once; later architecture, design, and
  review checks reuse that evidence. Reopen a candidate search only when a
  requirement, relevant version, revision, or primary-source fact changed, or
  when the earlier search left a specific behavior unverified. Compare each
  candidate's exact behavior, lifecycle, dependency cost, and adaptation cost
  with a direct implementation. Reuse it when it fits; keep domain policy local
  when a generic dependency would leave the same policy or add more translation
  than it removes.
- Before writing production code, trace the shipped entry point, current
  consumers, sibling implementations, and import boundaries. Decide which
  module owns each policy, state transition, and external effect, and which
  dependency direction preserves that ownership. Put facts that must change
  together at that owner and make callers depend on narrow immediate
  collaborators. After editing, reread the complete path for duplicated policy,
  hidden state, and new cross-layer coupling.
- Do not introduce `from __future__ import annotations` into new or touched
  Python files unless the project explicitly requires it.
- Branches over open sets must reject unmatched cases instead of silently doing
  nothing. When extracting reusable logic, promote call-site preconditions into
  explicit checks.
- Make stateful effects part of a helper's name or contract. Do not hide RNG
  advancement, cache mutation, counter updates, or collectives behind an
  apparent pure transformation.
- Establish each policy or invariant at one validated source of truth; derive
  its masks, selections, scaling, and control flow from that source rather than
  recomputing it independently.
- Prefix new environment variables for tools we own and check the wrapped tool's
  reserved namespace.
- Write important deferred work as `# TODO(s22chan): ...`.
- Never expose or commit secrets. Command text is logged, so never place
  secrets in command arguments.

## Git and review prose

- Never run `gh`; describe the PR title/body/branch for the user to submit in the
  GitHub web UI.
- Stage explicit files only; never use `git add -A` or `git add .`.
- PR descriptions lead with the takeaway and reviewer-visible changes; point to
  commit history for detailed evidence instead of repeating it.
- In third-party prose, omit conversational rebuttals and negative results that
  are true by construction. Name a rejected alternative only when that audience
  might plausibly consider it.
- Never force-push without explicit approval.

## Working style

- For every multi-finding audit, keep a tasklist with severity, owner, and
  disposition, and reconcile every item before reporting the review addressed.
- Assume a senior engineer fluent in the stack. Surface assumptions, tradeoffs,
  evidence, and uncertainty; skip basic definitions.
- Do not expand into unrequested scope. Suggest adjacent work instead.
- If the requested mechanism is not the best fit, explain the alternative and
  tradeoff before proceeding, but treat an explicit mechanism or destination as
  a constraint. When a request cites a job, run, incident, or example and
  changes a selector, filter, classifier, or exclusion policy, first state its
  semantic inclusion and exclusion contract. The cited instance defines that
  contract only when the user explicitly limits scope to its ID or names its
  mechanism or field; otherwise its implementation details are evidence, not
  the predicate. Enumerate distinct known producer paths from the authoritative
  interface and classify each as included or excluded. Use a field as the
  predicate only when its documented semantics express that contract across
  every included producer. Exercise one included and one nearby excluded path
  through the shipped selector. If the requested category cannot distinguish
  discovered producer paths, ask before editing. Do not include paths outside
  the stated semantic contract.
- In reports, foreground measured findings and decisions. Omit expected,
  invariant protocol controls unless they are needed to reproduce or interpret
  the result, or are themselves the subject of the comparison.
- Order multi-finding reports by operational consequence and action priority,
  not by lane, proof freshness, or arrival order. Keep impact and likelihood
  separate when they differ.
- Name an isolated branch, test, or report from its own behavior. Do not name
  an excluded sibling optimization merely to describe its absence.
- Reuse one fresh agent through successive bounded turns only when the work
  depends on the same compact context and retained evidence remains relevant to
  the next turn. Use fresh contexts for independent review lanes or when prior
  tool output would materially enlarge later requests without helping their
  judgment. Follow a narrower workflow's explicit context boundary.
- Treat parallelism as scheduling, not as a token-saving or token-spending
  mechanism by itself. When independent tasks require fresh contexts, run them
  concurrently only when slots are available and the owning workflow benefits
  from prompt-cache locality or lower latency; otherwise queue them. Bound the
  number of tasks, their evidence, model, and effort directly.
- Delegate broad read-only codebase mapping to `explore-cheap` only when it is
  the single agent selected for that objective; keep a single known-location
  lookup inline.
- Give a delegated agent the smallest self-contained context that establishes
  its task, scope, revision, constraints, and required result. When the spawn
  interface permits, pass no prior turns or only the few turns the task needs;
  do not fork a full long-running conversation merely for convenience.
- Before handing a follow-up to a fresh session or agent, replace contextual
  labels such as "this branch," "the overlay," or "the earlier fix" with the
  exact ref, tip or commit, symbols, and raw observed behavior needed to
  distinguish the target. Preserve the evidence needed to revisit the decision,
  not the prior conclusion. If the available context does not resolve a label
  whose interpretations would change the answer, enumerate them or ask instead
  of selecting the most convenient repository match.
- Keep reusing a delegated agent while the objective, artifacts, revision,
  requested outcome, role, and compact supporting context remain unchanged.
  Start a fresh agent when one of those changes, when an independent judgment
  is required, when retained context would bias the task, or when unrelated
  accumulated evidence costs more than repeating the task's bounded setup.
- After changing an agent definition, model, or reasoning setting, use a newly
  created session and agent and verify the effective setting before relying on
  its cost or capability.
- Classify a failed tool call before retrying. Do not retry a policy or
  permission denial through alternate spelling or paths, and run an expected
  negative guard probe at most once per input. After a missing path, worktree,
  executable, or backend error, re-resolve that prerequisite before another
  call. After malformed tool input, retry only with the minimal canonical call
  shape.
- Prefer an existing authoritative owner over a new file. Do not create
  documentation or READMEs unless requested.
- Ask rather than guess when ambiguity would materially change the result.
  Respect an explicit mechanism or destination as a constraint. When phrasing
  may instead be an example and the interpretation changes scope or ownership,
  state the interpretation before acting.
- After the same approach fails twice, stop and re-plan.
- When multiple findings target one abstraction, their proposed fixes add
  compensating branches, state, fallbacks, or post-processing, or repeated
  review/fix rounds keep reopening the same decision surface, use
  `grill-change` to re-derive the combined remedy before implementation.
- When evidence invalidates a proposal's premise, re-derive the proposal from
  the remaining requirements instead of preserving its original shape.
- Lead causal explanations with the mechanism, its consequence, and the
  strongest supporting evidence. Include investigation detail only when the
  user requests it or material uncertainty requires it.
- When materially different designs remain, state the recommended design, its
  main tradeoff, and the decisive disadvantage of the strongest alternative
  before editing.
- Describe concrete inputs, actions, and outcomes before applying a pattern or
  smell label. Prefer literal mechanisms over metaphors that obscure behavior.
- Run local shell processes expected to outlive the session under `nohup` with a
  log and `disown`. Monitor them without a busy polling loop. For agent-owned
  work expected to run 2–20 minutes, wait 2–3 minutes between status checks;
  for longer work, use roughly 10% of the estimated remaining duration, capped
  at 10 minutes. Use a shorter check only when completion is expected within
  two minutes, the job emits a failure signal, or the user asks for status.
- For an asynchronous job the agent starts (`srun`, `sbatch`, or `nohup`), do
  not end the active request merely because the job is running. Monitor it to a
  terminal state, inspect its declared output on success, and report the
  completion or failure to the user. This does not apply to user-owned or
  unrelated jobs; if the user explicitly asks for an interim handoff, report
  the job identifier and the exact remaining completion check.
- Before deleting interrupted-job output, inspect it for results not recorded
  elsewhere.
