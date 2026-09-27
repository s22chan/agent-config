# Long-Form Audit Report

Render the already verified findings for a reader who has not opened the code.
Do not rerun lanes or expand the finding set merely to fill the format.

## Structure

1. **Header** — scope, base, commit count, lanes run, and findings that survived
   root verification.
2. **Verdict** — the state of the change and the cheapest check or decision that
   would materially change it.
3. **Scan table** — verified findings only, as
   `# | finding | impact | likelihood | fix`, ordered by operational
   consequence and action priority rather than lane, proof freshness, or arrival
   order.
4. **Full findings** — the highest-value findings, numbered to match the table.
5. **Minor** — one line each: `location — defect — cost`.
6. **Blocked** — `question | what it decides | where to look`.
7. **Coverage** — lanes with no findings, unresolved evidence gaps, and claims
   rejected during root verification.

## Full finding

```markdown
## N · <claim as a statement>

**<observable outcome in one sentence>**

**Trigger** — the supported input or event that produces it.

**Evidence and mechanism** *(provenance)*
<one executed step or relevant Git fact per line, annotated with file:line,
commit SHA, or range>

**Fix** — the smallest change that prevents the failure; give exact replacement
text when it is short.
```

## Reporting rules

- Keep impact and likelihood separate. Use `unknown` for likelihood when the
  evidence does not establish it, and name the check that would resolve it.
- State the violated rule or contract beside the violation.
- Lead with what a user, operator, or reviewer observes; explain code mechanics
  second.
- Mark whether each mechanism line comes from the reviewed repository, a
  dependency, or an external source.
- Let the scan row own impact, likelihood, and fix cost. Let the full finding own
  trigger, mechanism, and exact fix; do not repeat the same prose at both levels.
- Split a finding when its branches have materially different likelihood or
  impact.
- Keep a verified finding with unknown likelihood in action order rather than
  hiding it in the blocked section. A missing prerequisite that prevents the
  finding itself from being verified belongs in the verdict and blocked section,
  not the scan table.
