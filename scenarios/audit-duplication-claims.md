# Audit duplication claims

## Observed incident

The user requested `/audit` for `evolutionaryscale/utils/submit.py` and its
tests in `/mnt/main0/home/steve.chan/review2` at `d2ae4b22ca` on
`kp/evorun-suffix`. The design lane reported finding 10 as low severity:

> `submit.py:668` and `:724` — The fallback from run name to sbatch filename is
> written twice. The new `run_name or sbatch_dest.name` duplicates the older
> `run_name = sbatch_dest.name`.

The user asked where `run_name = sbatch_dest.name` was, then:

> doesn't that conditional do a lot of other processing

It does. The `if run_name:` block at lines 713-724 also asserts that
`logger.run_name=` is absent and appends `logger.run_name=<name>` to
training commands for non-array jobs, and its `else` prints the filename
notice. Computing the name once up front would make the test always true, so
unnamed jobs would gain `logger.run_name` and lose the notice. Only the
fallback expression overlaps, so the finding overstated the problem.

## Replay inputs

Give a fresh design-lane reviewer only the lane file, the repository rules, and
the diff of `submit.py` against `4d48a42595`. Cases:

1. The observed incident above.
2. Two copies of a validation helper call in sibling functions, where each
   function does the same work around the call. A finding is expected.
3. Two copies of a default expression in branches that run different side
   effects. Report only the expression, with that limit stated.

## Test arms

No arms run. The edit is unverified until replayed in a new session against the
unedited lane file.
