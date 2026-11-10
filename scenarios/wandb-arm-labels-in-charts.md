# Chart series labeled by arm, not raw run name

## Trigger

A W&B report compared training runs under three CPU-pinning settings. Its
charts and tables listed each run by its raw name (`ckpt-ab-p2GaLz-bound-esm4-2-refactor`,
`...-badpin-esm4-2-refactor`, `...-esm4-refactor-metrics`). The user wrote:
"the training runs are all named refactor/metrics, it's hard to tell which one we should compare to what in the charts"
and then "fix the rules for this".

## What the agent did

It selected the exact run IDs and verified metric paths, as the skill asks, and
colored runs by setting. The legend still showed raw run names, so a reader
could not tell which line was which setting.

## What it should have done

Label each series by the arm's name from the research question, and tell the
reader what each color means, without renaming the raw runs.

## Test arms (fresh `claude -p`, hooks and memory off, probe answered "none")

Prompt: the run table (ids, names, tags), the research question, and the
metrics, asking for the report-building code only.

- Unedited skill, incident inputs: 2 of 2 charted raw run names with no arm label.
- Edited skill, incident inputs: 2 of 2 used one run set per arm with an
  `${runsetName}` legend and arm-named run sets.
- Edited skill, same shape in another domain (three warmup schedules, runs
  named `sweep-...-run-NN`): 1 of 1 labeled by arm.
- Edited skill, runs already named by arm (`adamw-baseline` and similar): 1 of 1
  used the names as given and added no derived runs.

Not verified: that the `${runsetName}` legend template renders as intended in a
saved report.
