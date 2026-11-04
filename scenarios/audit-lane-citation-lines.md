# Lane findings cite the line above the defect

## Observed case

A review lane given the lane rubric and the finding format reviewed a commit
that added `store.py` with two defects: a slice one item too long at line 15 and
an unguarded division at line 19. Both defects were found in every run, but the
cited lines were wrong in half the runs: `store.py:14` for line 15 and
`store.py:18` for line 19. The user asked: "fix the line numbers".

## Replay inputs

Fresh `claude -p` sessions (hooks and memory disabled, read-only tools), the
lane rubric and finding format pasted into the prompt, a throwaway repository
with the two-commit fixture. Every cited line was checked against the file.

## Arms

| Arm | Runs | Correct citations |
|---|---|---|
| Format unchanged | 3 | 3 of 6 |
| Added "read the cited lines, quote the code" | 3 | 0 of 6 |
| Added "take LINE from a numbered read, not hand counts or diff output" | 3 | 5 of 6 |

The shipped wording is the third arm. Cause of the early citations is not
established. Small samples; one fixture.
