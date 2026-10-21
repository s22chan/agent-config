# Matching workflow not loaded before writing code or tests

## Observed incident

During a change that added Python helpers and tests, the agent never invoked
`design-python-code` or `verify-behavioral-tests`. The result had a hand-rolled
argument parser grown over several fixes and test files with redundant assertions
(the same wrapper asserted beside the function it wraps, rows that restate a
table). The user asked: "can we debug why the rule didn't load and if it needs to
be addressed." The skills were in the session's skill list, and a `common.md` rule
said to "Apply every workflow whose description matches the task", but a skill's
rules are not in context until it is invoked and the rule did not say when.

## Classification

Insufficient. The rule names the workflows but gives no moment to load them, so a
task that looks like plain code writing proceeds without them.

## Replay

Fresh `claude -p` sessions run from the repository with
`--settings '{"disableAllHooks": true, "autoMemoryEnabled": false}'`, tools Read,
Skill and Write, and a Write target for the output.

- Unedited rule, helper-writing prompt (two framings, 8 samples): 0 of 8 invoked a
  skill. Test-writing prompt, 4 samples: 0 of 4.
- Edited rule ("Before writing or changing code or tests, load each workflow whose
  description matches the task by invoking it; its rules are not in context until
  it is loaded."), helper-writing, 4 samples: 4 of 4 invoked `design-python-code`.
  Test-writing, 4 samples: 3 of 4 invoked `verify-behavioral-tests`.
- Excluded cases, 4 samples (a one-sentence question, and a one-word fix in a
  prose file): 0 of 4 invoked a skill.
- Effect of loading on the tests written (same function): the 3 samples that
  loaded the skill wrote 2 tests each, with one calling the wrapper; the sample
  that did not, and the 4 unedited samples, wrote 8 to 13 tests with 3 or 4 calling
  the wrapper.

Counts are small. Whether loading `design-python-code` changes a parser's shape was
not established: loop depth and prefix operations were similar with and without it
(4 samples each).
