# Replay prompts that list the edit's outcome categories

## Observed incident

While replaying an `/audit` rule edit (evidence gaps for candidates whose impact
depends on missing evidence), the agent wrote an evaluator prompt that ended:

> Answer with one line starting with DISPOSITION: then one of FINDING(<severity>)
> | HARDENING-NOTE | EVIDENCE-GAP | REJECT

The menu named the edit's own outcome, so both arms could pick it. Old and new
skill gave the same answers in that run. The user said:

> maybe the scenario is wrong or somethign leaked

and then:

> fix the rules for the leak, there shoudl already be rules for this

## Classification

Insufficient. The existing rule forbids the intended fix's wording and the
expected verdict, and a menu of outcome labels is neither literally, so a
plausible reading passes it.

## Replay inputs

Give a fresh agent the skill, the diff of an audit-rule edit, and one candidate,
and ask it to write the prompt it will send a fresh evaluator. Case used: a
heartbeat candidate whose alert rule is absent from the evidence.

## Test arms

Headless `claude -p`, no tools, hooks and memory disabled, three samples per arm.

- Old rule: category menu 0/3. All three asked for a disposition or the rule
  relied on, and one offered an `OMITTED` option.
- New rule: category menu 0/3, and all three asked only for the report entry in
  the audit's own format.

The exact menu leak did not recur under the old rule, so the difference is the
milder disposition-and-citation pattern. The case text still carried an
"impact unverified" hint in every arm. Three samples per arm cannot bound the
rates.
