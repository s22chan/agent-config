# Audit effort for low-risk changes

## Observed case

No observed incident. The user asked whether audit effort can be classified by
risk, with docs changes and renames as low risk, and then to expand the
classifiers. Before the change an unnamed-lane audit always ran the five default
lanes.

## Replay inputs

Fresh `claude -p` sessions (hooks and memory disabled, read-only tools) in
two-commit throwaway repositories, asked only which lanes they would run on
`HEAD` against `HEAD~1`. Nothing was dispatched.

## Arms

Safe cases (should narrow to `review`, plus `docs` for prose) and traps (must
keep the default five). Two runs per case unless noted.

| Case | Before | After |
|---|---|---|
| README sentence; docstring | 5 lanes (one README run 4) | `review`+`docs`, 4 of 4 |
| Rename, every reference updated | 5 lanes | `review` only 2 of 2, then 5 lanes once on a rerun |
| Whitespace-only JS reformat | 5 lanes | `review` only, 2 of 2 |
| Verbatim move | 5 lanes | `review` only once, 5 lanes once |
| Flag off by default | 5 lanes (1 usable run) | `review` only, 2 of 2 |
| Rename with a stale config reference | 5 lanes | 5 lanes |
| Code change plus README line | 5 lanes | 5 lanes |
| Python indentation move; move with edit; flag on by default | 5 lanes | 5 lanes |

Two baseline runs were discarded because the session reported no `audit-change`
skill and stopped. Cost of a real narrowed `/audit` run was not measured.
