# Plain words for labels coined during the work

## Observed incident

After a long analysis the agent told the user: "a Reef memory rule would be
faults alone, not the pair". The user replied: "can you speak with less jargon
so a Reef memory rule would be faults alone, not the pair. assumes a context, I
don't know what a pair of what" and then "fix the rules for this".

The reply used three kinds of unexplained shorthand from the agent's own working
notes: a label for a two-part rule ("the pair"), labels for groups of cases
("terminal", "recovered", "control"), and an abbreviation of a technical term
("faults" for "major page faults"). The user had seen none of them defined.

## Classification and owner

Insufficient. The existing Communication bullet in `instructions/claude.md.in`
forbade coining a name only "for a quantity made up during an analysis, such as a
ratio, share, or score". A rule, a group of cases, or an event is not a
quantity, and an abbreviation is not a code identifier, so a reply could satisfy
the bullet's plain wording and still reproduce the incident. The fix is a new
bullet next to it; the original bullet is unchanged.

## What reproduces the incident

Each arm was a fresh `claude -p` session run from an empty directory with
`--settings '{"disableAllHooks": true, "autoMemoryEnabled": false}'`, no tools,
and only the prompt. A probe first asked a session to quote what it was given at
startup about the topic; it quoted only the Communication rules and answered
"none" for the project, the clusters and the incident.

The incident needs labels that are already in the agent's context from earlier
work. When the prompt gave the agent's working notes with the shorthand the
author had (group labels, a rule label, a table of counts) and asked the user's
question, the unedited rules failed 3 of 3: every reply repeated a label from
the notes with no gloss. When the prompt gave the same facts without labels and
asked the agent to name the groups itself in code constants first, the unedited
rules passed 3 of 3 (and 1 of 1 in an earlier variant): the agent chose
descriptive names and wrote a plain reply. A prompt asking for "working notes"
was refused by the API as reasoning extraction, so the second shape asks for code
constants instead.

## Approaches tried (labels-in-context prompt, same question)

Scoring criteria were fixed before the first arm: a reply fails if it uses a
made-up label for a rule or group, or an abbreviated technical term, without
saying what it means in ordinary words. Replies without an unexplained label:

| Wording | Clean replies |
| --- | --- |
| Unedited rules | 0 of 3 |
| Forbid any invented name, require abbreviations written out | 1 of 3 |
| The same plus a reread-before-sending step | 1 of 3 |
| Describe a group, rule or event in full at first mention (kept) | 3 of 3 |

Three samples per arm cannot separate a modest effect from chance. The jump from
0 of 3 to 3 of 3 is the only large one and is the wording kept.

## The rule

The first time a reply mentions a group of cases, a rule, or an event from the
agent's own analysis, it describes it in full in that sentence, by what defines it
and not by the label used while working; a short reference is fine afterward; an
abbreviated technical term is written out in full once.

Nearby excluded case (one sample, final wording): notes using "median" and "95th
percentile". The reply used both without defining them, as the original bullet
permits.

## Open

The wording was tuned on one prompt shape with a single set of notes. A second
task with different labels, and a longer session where the labels come from tool
output rather than notes, have not been run.
