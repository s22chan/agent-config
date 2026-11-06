# One claim per list item in PR descriptions

## Observed incident

While drafting a pull request description from three commit messages, the agent wrote
list items that each joined three or four independent changes in one item, for
example:

> - `chore(ty): make ty pass on transformers 5.22.1`: the `ty` hook reported errors against
>   5.22.1, so any commit touching Python failed it. The 54 imports of the removed
>   `tokenization_utils` and `tokenization_utils_fast` modules now come from top-level
>   `transformers`. The 14 archimedes `Tokenizer = A | B` aliases and a few annotations use
>   `PreTrainedTokenizerBase`, because in 5.x `PreTrainedTokenizer` and
>   `PreTrainedTokenizerFast` are sibling classes. 52 now-unused ignores are removed
>   (`ty --fix`) and 131 rule suppressions are added on 127 lines for the errors the real
>   types expose, such as `AutoTokenizer.from_pretrained` being typed `... | None`.

The user said: "the bullet point is quite dense, make it more readable" and then "can we fix
the rules for this".

## Classification

Insufficient. The Communication rules ask for parallel bullets for multiple ideas and for
splitting independent claims within a sentence, but they sit under chat communication and
say nothing about what one list item may hold. The Git prose rules only cover line wrapping
for list items. A fresh session asked to quote its startup rules on how long a list item in
a PR description may be, or how to split one that covers several changes, quoted only the
line-wrap rule and said nothing covers splitting.

## Replay

Fresh `claude -p` sessions run from the repository, with
`--settings '{"disableAllHooks": true, "autoMemoryEnabled": false}'`, read-only tools,
prompt on stdin. The prompt gave the author's inputs: the three commit messages and a few
working notes on sizes and checks, and asked for the PR description only. Items are
markdown list items; a hard-wrapped item is joined first.

- Unedited rules, 3 samples: items over 45 words 2, 1, 1 (of 22, 18, 21 items); items with
  four or more sentences 1, 0, 1; mean words per item 20, 26, 23. The long items each
  joined three or four independent changes.
- Edited rule, 3 samples: items over 45 words 0, 0, 1 (of 29, 25, 25 items); items with
  four or more sentences 0, 0, 0; mean words per item 17, 18, 20. Remaining items of 30 to 40
  words were one claim stated in three short sentences, which the rule allows.
- Included case, a refactor with three parts and a behavior change (2 samples): 10 and 12
  list items; each part got its own sub-item with one claim.
- Excluded case, one change with one measured result and several figures (2 samples): 2 and
  0 list items; the result stayed as one table or paragraph and was not split into fragments.

Limits: the unedited rate is low (one to two long items per description), so three samples
per arm cannot separate a modest effect from chance. The first scoring rule, more than 45
words or more than two sentences, also flagged three-sentence single claims in the edited
arm, so the counts above use length and four or more sentences instead. A larger run needs
the owner's go-ahead.
