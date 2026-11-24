# Comments and docstrings that an outside reader cannot follow

## Observed incident

An agent added a field to a function and wrote a docstring and two comments
for it. The user read them and wrote:

> this comment is worded badly like the prior commit wording issue, # Rows two
> steps apart from a trainer that logs a step every ten. Twelve hours end at
> step 17,280; the next logged step, 17,290, crosses this eval, the next row
> does not. also this comment uses stuff like "row spacing" etc

and, after one rewrite, about another comment:

> this is very repetitive: The rows logged in this much time before the newest
> one give the usual time

The user preferred the rewritten version once the shorthand and repeated words
were gone. The existing code-prose rules asked for short ordinary sentences, a
docstring that starts with the operation's purpose, and existing prose left
alone unless the change makes it inaccurate.

## Classification

Insufficient for authoring: those rules can be met while using undefined local
names and repeating a term clause after clause. The review skill (`polish-docs`)
already covered comments and docstrings but defaulted to a reader fluent in the
stack, with no instruction to gloss names or cut repeated clauses.

## Replay inputs

Fresh `claude -p` sessions with `--settings '{"disableAllHooks": true,
"autoMemoryEnabled": false}' --allowedTools ""`, run from an empty directory.
The user message was "commit". Each session got the working notes and the code
with the prose left as placeholders, and wrote the three pieces. A probe
session confirmed the new rule loaded at startup.

## Arms and counts

Authoring rule merged into the docstring bullet, three runs per arm:

- With the old docstring and comment in the prompt, the old opening ("usual row
  spacing") and the old comment survived in 3 of 3 runs, with and without the
  rule. Existing text is treated as fixed.
- Written from scratch, the merged rule glossed "row" in 1 of 3 runs against 0
  of 3, with no clear change in the comment above the test constant. Not
  separable from chance.

Review route, three runs per arm: the `polish-docs` skill applied to the
disliked prose.

- Unedited skill: the revised docstring explained `log_interval` by example in
  3 of 3 runs and never stated what it is.
- With the reader default changed: 3 of 3 stated it ("the number of steps
  between logged rows", "the trainer logs one step every `log_interval`
  steps").
- The docstring opening that the user disliked ("usual row spacing") was kept
  in 6 of 6 runs, because it is existing prose outside the diff.

## Not established

- Three runs per arm. The review gloss difference (3 of 3 against 0 of 3) is
  the only one that is clear, and it is on one piece of prose.
- Every review run either invented an eval step number or corrected itself
  mid-output ("Wait: ..."), in both arms. The notes did not give that number,
  so this is a limit of the test input.
- Whether an agent will run the review step unprompted was not tested. The new
  rule only tells it to.
