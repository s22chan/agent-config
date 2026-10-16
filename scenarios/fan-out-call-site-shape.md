# Fan-out rollouts that copy a helper recipe to every call site (no rule change)

## Observed incident

The agent rolled a Slurm job-name suffix out to about 45 launchers in
`/mnt/main0/home/steve.chan/review2` (branch
`s22chan/project-suffix-remaining-launchers`). `format_job_name` had been a
private helper whose callers had already resolved and validated the project. It
was made public and kept trusting its argument, so each launcher wrote

    format_job_name(name, resolve_cost_project("<project>", ""))

and imported both helpers. The agent added launchers in scripted batches, ran
tests after each, and did not reread the aggregate diff. An audit flagged only
that the helper trusts its argument; the commit-series review checked commit
boundaries and messages. The user found it:

> but we are calling resolve project name everywhere and formatting the name for
> the executor

and then asked:

> why wasn't this suggested? check the rules

The existing rules (reread the finished diff for logic in two places, promote
call-site preconditions when extracting, one validated source of truth) covered
the outcome, but each acts after the work; none says to settle the call-site
shape before a many-site rollout begins.

## Replay inputs

Fresh sessions given only the rules and the pre-rollout state: `format_job_name`
as a private helper in `submit.py` and a request to suffix job names in about a
dozen launchers outside it. Cases: the incident; a different rollout without its
terms (adding a retry wrapper that each caller must configure and validate, in
ten modules); and a nearby case the rule must not change (ten launchers that
each pass a different project value and need nothing else).

## Test arms

Edited arm: five fresh `claude -p` sessions (default config, so the installed
rules include the new bullet; the probe quoted the bullet back), read-only
tools. Unedited arm: five subagents of the session that predates the edit (the
probe answered `none`). Sandbox: the 14 pre-rollout files; prompts asked for
"the exact change you would make", with no rule terms. Case A (12 launchers):
helper-owned, with sites passing only name and project, in 3 of 3 edited runs
(helper in `project_key.py`) and in 2 of 3 unedited runs (helper in
`submit.py`); the third unedited run wrote the literal suffix at each site with
no helper. Case C (the control, a partition change at 6 sites): direct edits and
no helper in 2 of 2 in each arm.

This one-shot replay does not show an effect. A "plan the whole rollout"
prompt already led the unedited arm to a helper in 2 of 3 runs, and three runs
per arm cannot separate 2/3 from 3/3.

Batch replay (the incident's conditions): the same 12 launchers in three turns
of four, each turn asking for only that batch with the whole table given in
turn 1, files edited in a writable copy of the sandbox. Edited arm: three
`claude -p` sessions resumed across the turns. Unedited arm: three subagents
continued with SendMessage. Final trees, scored by script: in all six runs,
12 of 12 launchers were changed, 10 carry a literal `<name> - <project>`
string at the site, the two "default" launchers call `resolve_cost_project`
inline, and no helper or new file was added. The incident recurred in 3 of 3
unedited runs and in 3 of 3 edited runs, so the rule had no measurable effect
under batching. A likely reason, not tested: "Do not expand into unrequested
scope" and the turn's "edit the four batch-1 launchers" outrank a shared
helper that the batch did not name.

Caveats: the arms differ in harness (subagent vs CLI); an isolated
`CLAUDE_CONFIG_DIR` could not authenticate, so a clean unedited CLI arm was
not possible; three runs per arm.

## Second round: strengthened rule

The bullet was extended with "the same literal format" and "A request for one
batch does not narrow this: the helper belongs to the first batch even when that
batch names only some of the sites, and it is not unrequested scope". A fresh
`claude -p` session quoted the new text back before the runs. Three batch runs
(same protocol, installed rules include the clause): in all three the trees
match the unedited baseline exactly (12 launchers changed, 10 literal suffixes,
2 inline `resolve_cost_project`, no helper). The control (a partition change at
six sites, two runs) again made direct edits with no helper.

## Outcome

No rule change. Neither wording changed the batch behavior (0 of 3 helper-owned
in each edited round and in the unedited baseline), while a one-shot prompt
already produced a helper in most runs. The rule was removed from
`instructions/common.md`. The failure is in the batch conditions, not in
missing guidance, so a rule is the wrong tool; a candidate mechanism is a
check before the first commit of a many-site change that greps the diff for a
repeated format (not tried). Runs: `~/tmp/fanout` (sandbox, prompts, scorer).
