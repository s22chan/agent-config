# Code prose in verdict and label words

## Observed incident

While finishing a new module, the agent wrote this module docstring:

> ``subprocess.Popen`` is wrapped once, so submitit, dask-jobqueue, the lance backends and
> launchers that call ``sbatch`` themselves are attributed without per-launcher code. The project
> comes from `resolve_cost_project`. A name that already carries an approved suffix is kept, so a
> launcher can pick its project explicitly. Scripts piped to ``sbatch`` on stdin, ``sbatch`` run
> from a shell, and processes that never import ``evolutionaryscale`` are not covered.

The user said: "the language is weird here" and then asked to fix the agent rules
for the language. The words that read oddly were verdict and label words
("attributed", "carries", "kept", "not covered") in place of what the code does.

## Classification

Insufficient. The plain-sentence and everyday-word rules sit under Communication
and read as scoped to explanations in chat; "Code prose" had no word-choice rule.
A fresh session asked to quote its startup rules on comment and docstring wording
quoted only the Code prose items and noted that the Communication wording rules
are scoped to chat.

## Replay

Fresh `claude -p` sessions run from the repository, with
`--settings '{"disableAllHooks": true, "autoMemoryEnabled": false}'`, read-only
tools. The prompt gave the author's inputs: a few lines of working notes on what
the patch does and what it leaves out, plus the module body without its
docstring, and asked for the module docstring only.

- Unedited rules, 4 samples: 4 of 4 used three or more stock terms from
  {attributed, covered, kept, idempotent, heuristic, "without changes", "left
  alone"} (5, 5, 3, 5 hits).
- Edited rule, 4 samples: 1 to 2 such terms each (2, 1, 2, 1 hits); no
  "attributed" or "idempotent".
- Included case, a retry helper docstring (2 samples): plain sentences, literal
  verbs, no verdict words.
- Excluded case, a function whose API contract names idempotence (2 samples): the
  contract term and RFC citation were kept in 1 of 2 and explained in plain words
  in the other.

Scoring was a word list, so it measures the stock terms and not overall quality;
the samples were read as well. Terms such as "kept" and "left alone" remained in
some edited samples.

Reverting `8085c79` (restoring the duplicate Communication rules, conflicts
resolved to the earlier side) with no new bullet, 4 samples: hits 2, 5, 3, 5, so
that commit is not the cause. With the revert and the new bullet, 4 samples:
hits 4, 2, 2, 2.
