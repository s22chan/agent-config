# Name a container of bare ints that stand for identifiers

## Trigger

A helper took and returned `set[int]` for the logical CPU numbers of each GPU.
The user asked: "what is cpus? the ints are not obvious to me what they
represent". Nothing in the signatures or docstrings said the ints were CPU
numbers. The personal rules already ask for "names that state domain meaning",
which `local_cpus` met, so the ints stayed unexplained.

## What the agent did

Used bare `set[int]` and `list[set[int]]` in signatures and returns. In an
earlier replay, 6 of 6 fresh authors given the same task did the same (no alias,
1 to 4 bare `set[int]` mentions each).

## What it should have done

Define one named alias with a comment saying what the values identify, and use
it in signatures and returns.

## Test arms (fresh `claude -p`, hooks and memory off; probe quoted the edited bullet)

- Unedited, incident prompt: 0 of 6 defined an alias.
- Edited, incident prompt: 3 of 3 defined an alias (one `TypeAlias` for a single
  id, two for the set).
- Edited, equivalent case with shard ids and reader ids: 1 of 1 defined
  `NewType`s for both.
- Edited, nearby case of a moving average over `list[float]`: 0 aliases (1 of 1
  left generic data alone).
