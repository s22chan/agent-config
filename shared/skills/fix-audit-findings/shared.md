# Fix Audit Findings

Resolve the findings of a completed audit or review. A finding reports a
possible defect; it is not itself a requirement. Decide what each one needs
before editing, then edit.

## Establish the case

For each finding, before choosing a fix:

1. Name the producer that would trigger it, and read that code, or run a small
   read-only measurement on saved data, to see whether the case can occur and
   how often. A finding's own label, such as "exceptional but supported", is a
   claim to check, not evidence.
2. Reproduce a defect with a demonstrated trigger. Verify a claim about an
   external library or service from its source or a probe; when that is not
   possible, say it rests on the reviewer's account.

## Close the evidence gaps

For each evidence gap in the report, check whether the repository answers it,
such as the callers, consumers, or readers of a changed symbol. Resolve each gap
the repository answers, handle what the trace shows as a finding, and leave only
the gaps that need an external system or an execution you may not run, naming
what each one needs.

## Choose the response

- **Fix:** a case that occurs, or whose miss gives a wrong result or loses data.
  Add the proper change and a test that fails without it.
- **Cheapest covering change:** a case that is rare, unmeasured, or cannot be
  shown to occur. Let it raise, assert the documented invariant, log the skip, or
  state the measured size in a comment. Do not add a recovery branch, validator,
  or redesign for it, and name the cases the cheaper change leaves out.
- **Decline:** a finding the producer or the data shows cannot happen, or whose
  cost exceeds its effect. Record the evidence.

When a stale comment or doc is the only fault, correct it and leave the code.

## Report

Keep one line per finding: decision, the evidence behind it, and the change made.
List the cheaper and declined ones plainly so the user can overrule them. Follow
the repository's branch-size and commit rules for the edits.
