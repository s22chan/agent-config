# A test pins parts of a composed value it does not own

## Observed incident

For a change that suffixes Slurm job names with a cost project, the agent wrote
tests that compared whole names, such as `eval_opencell_s200 - Katamari`,
`ag_parity - ESM4`, `embed - ESMC` and `Embed - Shrimp`. The change only decides
the project. The user said:

> isn't the katamari job overasserting?  we don't care about the job name, only the project.  not sure if this is done in other tests

and asked for the tests to be fixed and for the rules to catch it.
`verify-behavioral-tests` already says to reject an assertion that a
contract-preserving refactor can make fail; renaming the dataset part of an eval
job fails the test above without changing attribution.

## Replay inputs

Fresh `claude -p` sessions (read-only tools, isolated: auto-memory and user hooks
off), the skill text pasted, a diff, a detached worktree of the commit before the
test existed. Four cases, each "write the test for this change": A the incident
(Katamari eval job naming); C an equivalent case without the incident's terms
(`eval_run_name` appends a team to a run name built from model, lr and seed); B a
control where the whole value is the contract (the queue controller looks jobs
up by exact suffixed name); D a control where a helper's own output format is the
contract (`join_run_name` switches to a double dash that `split_run_name`
parses). Scoring fixed beforehand: A and C over-assert if a test pins the part
the change does not decide (A: the dataset or step part of the name; C: the
model, lr and seed part, as a literal or a rebuilt format); B and D fail if a
test checks only the changed part.

The unedited arm ran first, and the edited arms only after it showed the
incident recurring.

## Result

- Unedited, A and C: 3 of 3 over-asserted in each (A compared the
  `eval_<dataset>_s<step>` part, C compared `esmc_lr0.001_s3-<team>` whole).
  Controls B and D: whole value or round-trip through the real parser, 4 of 4.
- A first bullet named the incident's own terms (project suffix of a job name,
  dataset or step in an eval job's name). It gave 0 of 3 on A in an earlier
  round, but the rule described the task, so that result is not evidence and the
  bullet was dropped.
- General bullet 1 ("assert that component alone, parsed out of the value; do not
  also pin the components other code owns"): A 3 of 3 over-asserted, C 1 of 3.
- General bullet 2, shipped ("scope each assertion to what the change decides ...
  a test that fails when an untouched part is renamed pins the wrong thing"):
  A 1 of 3, C 0 of 3. Controls B and D: 4 of 4 kept the whole value or the
  round-trip.

## Caveats

Three sessions per arm for A and C, two for the controls; the skill was pasted
into the prompt, not loaded as a skill; case C and D are synthetic diffs, not
repo code; scoring is by reading the outputs, and one A session that checked that
each dataset appears in exactly one name was counted as scoped because it did not
rebuild the naming format.

## Outcome

Added one bullet to the "Test text, visuals, and adapters by contract" section of
`verify-behavioral-tests`, with no job-name, project or dataset terms.
