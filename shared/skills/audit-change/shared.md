# Audit Change

Inspect the change and report verified findings without changing the primary
worktree, implementing a proposed fix, or mutating external state.

## Select scope and lanes

Recognize six lanes: `review`, `design`, `grill`, `tests`, `docs`, and `commits`.
By default run `review`, `design`, `grill`, `tests`, and `docs`. Run `commits`
only when the user names it or requests `all lanes`; commit-series review is
useful only when history narrative is in scope, and its remedies can require
separate authorization to rewrite history. When the user names lanes, run only
those lanes. Treat a request for the full setup, tracked tree, or current state
as scope, not as `all lanes`. Treat other supplied text as the target, base, or
scope. A request for a report or long form changes only the rendering; read
[report format](references/report-format.md) only then.

Resolve scope once and give every lane or decision-owner shard the same revision
and diff boundary. A shard narrows the judgment focus, not the audited change:

1. When the user explicitly requests the full setup, tracked tree, snapshot,
   or current state, inspect the full tracked tree at the resolved revision;
   no comparison base is required. State whether ignored or untracked paths
   are excluded.
2. Otherwise use a target or base named by the user or repository.
3. Otherwise use the configured upstream or remote HEAD. Ask only when no
   authoritative base can be resolved.
4. Inspect the complete merge-base diff. Include uncommitted changes only when
   the target is the current worktree or the user explicitly includes them;
   otherwise list the current worktree as outside the named revision's scope.
5. Name each identifiable untracked path excluded from the audit. When the
   available evidence gives only a count or description, report that without
   inventing a path.

Keep change scope separate from evidence scope. The diff remains fixed, but
inspect explicitly named or repository-established downstream callers,
configurations, and operational workflows even when they live outside the
target repository when they are needed to establish reachability, likelihood,
or impact. A source location supplied later identifies where to inspect the
change; it does not silently discard caller context supplied earlier.

Resolve supported prerequisites and transition ordering separately from the
diff boundary. When the user explicitly guarantees that the audited behavior
runs only after a named or generated predecessor, accept that order as a scope
premise, inspect the predecessor producer and resulting artifact, state, or
configuration, and judge only executions reachable afterward. Apply this to
deployments, migrations, generated artifacts, and other staged transitions. Do
not require compatibility with an intermediate version or state that cannot
receive the audited change. Do not infer this guarantee from intent, a
future-tense comment, or automation that merely opens an independently
executable change. Without an explicit guarantee, or when either change can run
independently, audit compatibility with the current base and report a concrete
ordering failure when one exists. If the predecessor does not exist yet, verify
how its contents are derived and state that execution against the final result
remains unverified.

No lane may use a predicted call site as a finding's trigger. When a consumer
is quotable in the diff, base, or a resolved successor included in the evidence
packet, quote it; otherwise ground the finding in the audited code's behavior
or its stated claims.

For a comparative audit, track base-relative provenance separately from
operational severity. Classify each candidate as introduced by the diff,
changed from the base, retained from the base, or outside the diff. Use the
actual base implementation to decide whether an abstraction, validation,
state, repeated computation, compatibility difference, or cleanup is required
by the change. Do not describe a retained oddity or an unchanged adjacent file
as refactor churn unless the change makes its consequence worse or makes a new
claim that it contradicts.

## Protect the primary worktree

Leave the primary worktree exactly as found. In it, do not edit files, apply
fixes, fetch, stage, commit, amend, stash, restore, switch or create branches,
rebase, rewrite history, or post comments. Use read-only Git operations and
disclose when a possibly stale ref limits the audit.

Outside an isolated mutation probe, an existing test or checker may run only
when its result is necessary to decide a finding and it is a routine local
operation that does not mutate in-scope or external state, require GPU or Slurm
resources, start a W&B or network-backed integration, or incur material cost.
Treat unknown cache, build, coverage, snapshot, or artifact behavior as a
possible write. Run it in an isolated probe only after proving that every write
is confined to disposable probe-local paths and that it cannot mutate external
state; otherwise report it as unrun with the evidence gap and the authorization
or environment needed to close it.

When a selected workflow says to edit, fix, commit, or rewrite, convert that
action into a finding. For a short prose or commit-message correction, include
exact replacement text only when every claim in it is verified.

## Judge the selected lanes

Each reviewer reads only its matching file under `references/lanes/`: `review`,
`design`, `grill`, `tests`, `docs`, or `commits`. Do not preload the other lane
files. Give each lane a fresh reviewer context so it applies its rubric directly
to raw evidence without inheriting another lane's conclusions. Do not suppress a
concern merely because another lane may also find it. During the merge, combine
findings with the same root cause into one finding and preserve both source
tags.

## Prepare and dispatch evidence

- Use at most six fresh judgment contexts for the entire audit by default,
  including lane reviewers, decision-owner shards, and independent passes over
  root-derived candidates. A follow-up that only restates an existing result
  does not consume another slot. Accept `--max-reviewers N` only as an explicit
  user override, consume it as workflow configuration, and record the resulting
  limit and planned allocation in the scope index before dispatch. Reject a
  limit smaller than the number of selected lanes before preparing evidence.
- Allocate at least one slot to every selected lane before considering shards.
  A shard replaces its lane's unsharded reviewer; it does not automatically add
  another reviewer. Never dispatch beyond the recorded limit. When the limit
  prevents a separate shard or verification pass, narrow the packet or retain
  an evidence gap instead of silently exceeding the budget.
- Limit each reviewer's materialized evidence packet to 98,304 bytes, including
  excerpts, diffs, snapshots, and checker output. Record the packet's byte
  count. Repository instructions, the lane rubric, and its referenced workflow
  are outside this packet limit. Give reviewers exact packet paths and tell
  them not to search or read additional repository content; they return a
  specific evidence request when the packet cannot support a verdict. Split by
  decision owner within the reviewer limit rather than sending an oversized
  packet.
- Keep scope resolution, final verification, and merging with the root agent.
- Before dispatch, record the primary worktree revision and state. Keep every
  reviewer read-only and do not let it start descendants.
- Build a compact shared scope index before judgment: the resolved revision and
  worktree state, changed or selected paths, applicable instructions, and the
  locations and digests of raw evidence. Materialize large diffs, base
  snapshots, and checker output with deterministic commands into disposable
  local files without returning their bodies into the root model's context.
  Separate observed values from interpretations. Do not put suspected findings
  or another lane's conclusions in the index.
- Before dispatch, record a decision inventory with one row
  per observable output or effect: its authority and invariant, semantic inputs,
  consumer, state lifetime, and failure representation. A shared record, module,
  or configuration object does not establish one governing decision.
- When the root has resolved a relevant successor as evidence, include its
  relevant code in the index by ref or evidence-file path. A consumer in a
  successor is evidence for deciding a claim, not an extension of the audited
  scope. When backend capability is in scope, include available discovery
  results for the exact backend and selector; do not substitute historical
  query text or downstream consumer support.
- Start one fresh high-effort judgment reviewer per selected lane, tied to the
  resolved revision and given no prior conversation. Never raise an audit
  reviewer above high effort. Put the exact lane rubric in its prompt rather
  than asking it to discover the file. Give it the compact scope index, exact
  paths for any referenced workflow, and a lane-local evidence packet
  containing only the current and base code, supported producer, consumer or
  downstream configuration, and owning tests needed for that lane. Prefer
  evidence-file paths over repeating large bodies in prompts.
- When one lane would still accumulate a large context across independently
  governed decisions, derive the smallest non-overlapping decision-owner
  shards from observable effects and their invariant owners. Give each shard a
  fresh high-effort reviewer context. Keep each decision with the inputs,
  consequence, and consumer that determine it. Do not create shards from
  suspected findings or incident literals, and do not split design into
  individual principles.
- Dispatch independent lane or shard reviewers promptly and run them in
  parallel when collaboration slots permit; queue the rest. Parallel scheduling
  does not relax the evidence boundary or make one lane's conclusions input to
  another lane.
- Require each reviewer to state once which audited revision and working-tree
  state its result covers. Reject or rerun a result whose scope identity differs
  from the resolved scope.
- Use the client's task-status interface and final responses as the lane
  results. Do not infer completion or findings from notification timing or an
  intermediate transcript. Remove disposable evidence files after all
  verification that depends on them is complete.

## Collect lane results

Apply the global failed-tool policy. In this report-only workflow, a second
failure in the same class is an evidence gap unless a materially different
method remains.

Each lane returns one finding per line. A location may be `path:LINE`, a commit
SHA, or a commit range, whichever owns the evidence:

```text
location — [high|med|low] — one-sentence defect — concrete trigger, then observable consequence
```

If a lane finds nothing, it says so explicitly.

Return no more than 20 findings from one judgment context, ordered by severity
and action priority, without investigation narration. If more findings survive,
return the top 20 and one final line stating how many additional findings were
omitted, or that the exact count is unknown. The merged report follows the same
20-finding limit and preserves that omission notice.

If a lane's final response contains only narration or has neither formatted
findings nor an explicit no-findings result, ask that same agent to restate the
result it already derived without new investigation or tool calls. Do not
convert an incomplete response into “no findings.”

Before probing or reconciling a tests-lane candidate, require its owned
contract, contract source, base/current safeguard comparison,
mutation-to-contract link, and permanent-detector justification. When a lane
omits a field, ask it to restate its existing result; when authorized evidence
cannot establish a field, keep an unverified evidence gap and do not invent a
disposition or comparative label. Do not infer a field from the current
implementation or from the fact that a mutation changes output. A mutation
result can verify only the sensitivity link; it cannot fill another field.
Reject permanent coverage when direct inspection or a one-time check proves a
simple port and no observed regression, prior owning safeguard, recurrence
risk, non-obvious invariant, or disproportionate consequence justifies keeping
an oracle.

After all lanes finish, the root confirms a tests-lane mutation only when the
client-specific isolation procedure permits it. A mutation probe is throwaway
evidence, not a proposed fix. Classify each candidate as `confirmed`,
`refuted`, or `unrun` with the reason. Re-check the primary worktree after all
probe work and invalidate execution evidence from any interval in which its
recorded revision or state changed.

## Verify and merge

Treat every lane result as a claim:

Only a candidate returned by a selected lane, or a root-derived candidate sent
through the required independent judgment pass, enters this reconciliation.
Prior resolved objections, user-confirmed premises, and curiosities from the
conversation are evidence context, not new candidates. Reopen one only when the
audited change alters its premise or a lane supplies contradictory evidence;
reconfirming an established decision is not an audit contribution.

For a candidate that depends on a missing prerequisite or different transition
order, enumerate reachable executions under the resolved premise before grading
its trigger. For any hypothetical trigger, identify a current supported producer
or lifecycle event before grading it. Reject a finding when its trigger
violates an explicitly guaranteed precondition and has no current supported
producer, or requires an unsupported manual departure that the normal workflow
prevents. Also reject an unsupported hypothetical path when its attempted use
fails immediately with an actionable error before changing durable or external
state and recovery is cheap. Do not retain these as hypothetical compatibility
concerns. These filters do not apply when a normal supported producer reaches
the trigger, the failure is silent, recovery is material, or the candidate can
cause data loss, irreversible effects, or a security boundary violation.
Preserve an evidence gap when promised predecessor content cannot yet be
inspected or derived.

For a candidate that adds or removes a backend capability, apply the
verify-technical-evidence workflow and trace producer availability,
acquisition, and downstream decoding or classification separately. A base query proves that the
backend was asked for a value, not that it emitted one; downstream support may
be retained solely for archived or cross-version inputs. Reject an availability
regression that lacks authoritative producer evidence for the exact backend and
selector. If the audit cannot obtain that evidence, record an evidence gap
instead of filling it from code shape or compatibility tests.

1. Open the cited code or Git evidence and re-derive the trigger, relevant path
   or history, safeguard, and observable consequence. Inspect nearby rationale
   and owning tests when they apply.
2. Identify the current supported producer or lifecycle event for every
   runtime-defect candidate and classify its likelihood from repository or
   operational evidence. Do not treat a state as operationally likely merely
   because a raw API can construct it. When no current producer establishes the
   trigger, reject the candidate or label it hypothetical optional hardening; it
   must not affect sign-off as a current-workflow defect. Retain an unsupported
   candidate under the serious-consequence exceptions above only with its low or
   unknown likelihood explicit; do not describe it as a current-workflow defect.
3. Independently evaluate base-relative churn. A candidate may survive without
   an operational trigger when the diff itself adds unnecessary machinery or
   diverges from an explicit behavior-preservation constraint. Require exact
   base evidence and name the added cost: changed accepted input or failure
   mode, repeated work, extra reachable state, redundant abstraction, dead
   mechanism, or ongoing maintenance obligation. Do not promote an inherited
   oddity, optional cleanup, or absent speculative feature on this basis. Do
   not reject an exact behavior difference merely because its observed impact
   is low; record it as low-severity churn when preservation is in scope.
   When a diff only forwards an existing owner's contract through a new
   wrapper, classify the forwarded semantics at that owner. The route does not
   independently introduce every syntactically constructible parameter
   combination as state or churn. Require the wrapper to interpret, default,
   validate, or branch on the values differently; a supported new producer to
   reach a previously unreachable harmful combination; or a concrete contract
   or maintenance obligation owned by the wrapper. If the new producer uses an
   existing valid combination and the forwarding is required for that use,
   treat unsupported combinations as retained optional hardening.
4. Before closing a hypothetical as rejected, check whether it exposed a
   smaller valid design action. If a diff-added guard, branch, wrapper, field,
   state, validation, or test exists only for that unsupported condition,
   reframe the added maintenance surface as churn and prefer removing it over
   asserting or testing the hypothetical. If the condition instead reflects a
   closed invariant owned by a touched type or boundary and a supported
   producer can violate it, prefer encoding the invariant structurally; use a
   cheap owner-level validation or assertion only when structure cannot express
   it and violation would otherwise propagate. Do not add an assertion merely
   to make an unsupported state fail sooner or to justify retaining machinery.
5. Drop or correct claims that do not survive. Apply the grill-change workflow
   when a surviving claim would remove or replace established behavior or
   contradict its stated rationale.
6. Deduplicate equivalent findings across lanes, keeping the version with the
   clearest reachable trigger and consequence while preserving source tags.
7. Track each candidate by severity, owner, and disposition: open, verified,
   rejected with evidence, or unverified evidence gap. A check forbidden by the
   audit remains an evidence gap for a separate authorized workflow; do not ask
   for approval and run it inside the audit. Reconcile every candidate before
   reporting the audit complete.
8. Record `reported / survived / unique / verification contributions` for each
   lane. A finding is unique only when no other lane reported the same root
   cause. A verification contribution means the lane supplied execution,
   history, or contract evidence that changed a finding's disposition,
   likelihood, impact, or severity even when the root cause was duplicated. Use
   these counts to expose repeated low-yield lanes; do not treat duplication as
   an additional finding.

The root is not exempt from this pass and does not perform it on its own work.
A finding you derived yourself is not a lane result, so nothing above triggers
the pass. Send it to a fresh high-effort judgment reviewer with the compact
scope index and lane-local evidence, framed as a claim to attack, and require a
verdict grading every link of its chain `verified`, `arithmetic`,
`inference-only`, or `false`. Present disputed premises as questions, not facts,
and include the strongest contrary observation already in scope; otherwise the
pass merely inherits the root's framing. Re-deriving your own hypothesis
returns confirmation; the graded chain is what exposes a link you assumed
rather than checked. A chain containing an `inference-only` or ungraded link
cannot be reported as high. Required for the finding you would lead with.

## Report

By default, lead with the finding worth acting on first, then return the merged
one-line list ordered by operational consequence and action priority. Keep
impact and likelihood separate, and do not let lane, proof freshness, or arrival
order determine priority. Tag each finding with its source lanes. Close with
evidence gaps, each lane's `reported / survived / unique / verification
contributions` counts, lanes that returned nothing, and claims rejected during
verification.

The rejected-claims section covers actual audit candidates whose rejection is
needed to explain scope or sign-off. Omit checks that only reconfirm an
established premise and rejected candidates whose disposition adds no material
boundary. Never investigate a settled decision solely to populate this section.

State whether each reported finding is exercised by a current workflow, an
exceptional but supported event, or only a broader API contract, and keep its
likelihood separate from impact. A high-impact hypothetical must not inherit a
high-severity or blocking disposition from impact alone.

For comparative audits, also label every finding `introduced`, `changed`, or
`retained` relative to the resolved base. Keep verified unnecessary churn in
the merged findings even when it is not a current-workflow defect, and state
the concrete base-relative cost. Keep inherited or outside-diff observations
out of the finding list unless the change worsens them; list them briefly as
rejected scope claims when another review supplied them.

For a requested long-form report, use
[report format](references/report-format.md) after the same verification and
deduplication pass. The report changes presentation, not the finding set or
evidence bar.
