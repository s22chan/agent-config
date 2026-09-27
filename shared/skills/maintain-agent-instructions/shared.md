# Maintain Agent Instructions

Treat a requested rule change as a request for intended behavior, not
necessarily an edit to the file where the problem appeared.

## Select the owner

Before drafting wording, state the semantic behavior and its inclusion and
exclusion boundaries without relying on incident-specific terms. Inspect the
existing owners and update the narrowest source of truth:

- Put reusable workflow guidance in its skill.
- Put project-wide policy in the applicable project instruction file.
- Put tool-specific policy in that tool's configuration.
- Put implementation invariants with the code that enforces them.

For code-review guidance, put a repeated, consequential, non-obvious invariant
in the narrowest repository `AGENTS.md` that covers the affected code. State
the invariant and a safe implementation path, and exercise both a violation
and a valid counterexample. Keep formatting and other deterministic checks in
CI. Remove or narrow a review rule when it repeatedly produces noise or no
longer changes review outcomes.

Apply the same ownership check to configuration, documentation, tests, and
automation. Follow an explicitly required target when the user names one as a
constraint. Do not duplicate a rule in an adjacent artifact that only exposed
the problem.

Treat environment-managed or generated capability artifacts as read-only even
when filesystem permissions allow edits. Put durable overrides in tracked
user-owned configuration or skills, or change the upstream source when it is
explicitly in scope. Personal tracked skills and source repositories remain
editable.

Never edit repository-owned instruction files (`AGENTS.md`, `CLAUDE.md`,
`.claude/rules/`, or repository skills) unless the user explicitly names the
repository instruction target or requests project-wide policy. An unqualified
request to add a rule defaults to the applicable personal instruction file or
personal skill. Before editing an instruction file, state its owner and scope.

Before editing configuration, state the invariant, who selects its policy, who
derives its concrete values, and which values are independent or derived. When
multiple producers enumerate the same fields to preserve one invariant, put the
closed invariant at its owner and derive the fields instead of maintaining
parallel lists.

Before adding a repository, generator, synchronization layer, or shared source
to consolidate configuration, inventory the complete current overlap and every
consumer-specific adapter. Compare the resulting authorities, update steps,
generated artifacts, and verification surface with the direct layout. Add the
layer only when it materially reduces ongoing ownership or provides a separately
required capability; reassess that benefit after implementation and remove the
layer when the realized shared surface does not justify its machinery.

## Classify the incident

Inspect the exact incident and replay the closest existing instruction. Report
whether the guidance was:

- **Clear but unexecuted:** reproducing the incident requires skipping,
  narrowing, or failing to combine its plain requirements.
- **Insufficient or contradictory:** a plausible execution can satisfy its
  plain requirements and still reproduce the incident.
- **Absent:** no applicable instruction owner exists.

An explicit restatement or incident-derived example is not evidence that clear
guidance was insufficient. Amend an insufficient owner; create a new owner only
for absent guidance. When the incident cannot be inspected, report the proposal
as unverified instead of adding the rule.

## Validate the boundary

Do not predicate applicability on an incident-specific identifier, literal, or
wording unless it is a documented interface or contract. Exercise:

1. The observed incident.
2. A semantically equivalent included case without the incident's terms.
3. A nearby excluded case the rule must not block.

When correcting observed skill routing or decision behavior, run these cases in
a fresh session or agent that has loaded the edited instructions. For an edit to
an instruction or configuration artifact already loaded by the current session,
use a newly created session. A child or subagent qualifies only if it
independently loads the edited artifact; verify its effective content before
relying on the test. Give the evaluator the raw incident, the intended general
boundary, and the strongest observation for and against each classification.
Do not state the expected verdict or stipulate a disputed premise as fact;
require the evaluator to derive the classification from the edited rule. If
independent evaluation is unavailable or unauthorized, report the behavioral
fix as unverified. Ask instead of encoding a category that cannot distinguish
the known included and excluded cases.
