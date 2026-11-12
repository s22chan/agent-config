# Connected explanations in docstrings

## Observed incident

The user said: "the docstring is not very human readable.  it's a string of loosely related statements" and later asked: "fix the rules for the docstring. also are any tests low value/signal?  we don't need a tautology".

The function docstring in commit `78d8c485827d99963ccd49c711b9106db24e7bcc`
was:

```python
"""Bind existing threads to allocated CPUs near the worker's CUDA device.

Shared CPU allocations are divided among visible participating GPUs. Task-bound
allocations retain their scheduler CPU share. CPU-only and non-Linux launches
are unchanged. Missing topology leaves placement unchanged with a warning.
Existing host allocations are not migrated.
"""
```

The paragraph collects allocation policy, skipped launches, errors, and memory
limits without explaining how the caller should relate them.

## Owner and boundary

Insufficient for routine authoring. The general Code prose rules required a
direct summary, plain sentences, and useful context, but did not require
paragraph cohesion. The polish-docs workflow already required connected
paragraphs; ordinary production authoring does not necessarily invoke it.

Update the docstring bullet in `instructions/common.md`. Require a caller-facing
explanation and a paragraph-by-paragraph check after drafting. Each explanatory
paragraph should develop one point through purpose, sequence, or cause.
Independent interface details can remain in reference sections. Do not duplicate
the rule in the prose-maintenance workflow or repository instructions.

## Authoring replay

Artifacts: `/mnt/main0/home/steve.chan/tmp/docstring-rule-20261108/`.
`instructions-a.md`, `instructions-b.md`, and `instructions-c.md` preserve the
original, first edit, and final edit. `inputs.json` gives the original authoring
notes; `placement.py`, `routing.py`, and `window.py` contain the source bodies.
`grading.md` fixes the criteria before the authoring arms.

Each fresh agent independently loaded its instruction snapshot, the same source
bodies and notes, and wrote three function docstrings. The prompt did not give
the user's criticism, a target answer, or grading categories. The original arm
was scored before launching the first edited arm. Each arm has one sample per
case:

| Case | Original failures | First edit failures | Final edit failures |
| --- | --- | --- | --- |
| GPU placement incident | 1/1 | 1/1 | 1/1 |
| Equivalent request-routing helper | 0/1 | 0/1 | 0/1 |
| Independent API reference sections | 0/1 | 0/1 | 0/1 |

The original incident replay puts timing, memory migration, and CPU sharing in
one paragraph. The first edit puts memory migration and backend failures in one
paragraph. The final edit groups timing and memory effects, but appends that
existing Torch threads are bound without relating that fact to the paragraph's
point. All three therefore fail the same fixed cohesion criterion. The routing
case uses different domain terms and separates selection, request lifetime, and
failure behavior. The reference case preserves argument units and return/error
contracts in Args, Returns, and Raises sections.

The final rule explicitly adds a drafting check. This small replay does not
demonstrate improved authoring behavior. Do not claim efficacy or keep tuning
against the same examples until a favorable sample appears.
