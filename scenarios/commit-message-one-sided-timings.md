# Commit messages report a timing with no baseline

## Observed incident

The user asked the agent to commit audit fixes and fold them into the one
existing commit on a branch. The agent amended without loading the
commit-writing skill. Its drafts cited an earlier version of the same
commit as evidence, carried the old body forward, and reported a
host-to-device copy bandwidth measured in one configuration with a
disclaimer that no unbound comparison was run. The user responded:

> why are we reporting the bandwith witout a reference point

and, about a later draft:

> the new commit message has a lot of wordings but doesn't really explain everything in a organized fashion

The bandwidth figure showed that the copies ran. It said nothing about what
the change did, so it should have been left out and the verified placement
result kept.

## Classification

Three facets, replayed against the unedited skill:

- Not loading the skill: not reproduced. All three fresh sessions loaded it,
  so this was a lapse in the original session and no rule changed.
- Evidence from an earlier version of the same commit: clear rules exist
  ("remove same-branch history", "results only from the committed tree").
  The unedited samples followed them (0 of 2 messages kept the old
  evidence). One edited sample kept it; see the open gap below.
- A one-configuration timing reported with a disclaimer: insufficient. The
  skill's "exact directly proven quantity" clause for missing matched timing
  let a plausible execution include it.

## Replay inputs

Fresh `claude -p` sessions with hooks and auto-memory disabled, one clone per
session at the original pushed commit with the final fixes left uncommitted.
A startup probe asking each session to quote anything it was given about the
topic answered `none`. Each session received the user's words verbatim, "commit
these fixes and fold", plus working notes listing the fixes, the test counts,
and the probe results including the one-configuration bandwidth. It received
no preference, no expected structure and no corrected message. Sessions could
not run every commit command under the allowed-tools list, so the scored
artifact is the message each one wrote.

Cases:

1. The observed incident above. Run.
2. Equivalent case without its terms: a message reporting a 12 ms median
   latency after the change with no before-value. Not run.
3. Nearby case the rule must not block: a message reporting a request count
   falling from 400 to 1. Not run.

## Test arms

Unedited rule, 3 sessions. One described its message but wrote no file, so 2
messages were scored. Edited rule, 3 sessions, 3 messages scored.

| Check | Unedited | Edited |
|---|---|---|
| Loaded the skill | 3/3 | 3/3 |
| Reported the one-configuration bandwidth | 2/2 | 0/3 |
| Kept evidence from the earlier version | 0/2 | 1/3 |
| Lines over 72 columns | 0/2 | 0/3 |

The edited text reached the sessions through the installed skill's symlink to
the edited file. A separate fresh session that invoked the skill returned the
new sentence verbatim. The arm stream logs do not contain skill text.

## Open gap

One edited message kept a paragraph about a run on an earlier version of the
commit, as the original draft did. The skill's "preserve still-true claims
from the existing body" rule pulls against "results only from the committed
tree" when an old claim came from an earlier version of the same commit.
One sample in five scored messages does not separate this from chance, and no
rule changed for it.

## Limits

The unedited rate is 2 of 2 and the edited rate is 0 of 3, so the samples show
the edit removes the figure in this case and not how often it occurs. Only the
observed case ran; the included and excluded boundary cases are unverified.
The sparse clone lacked the `projects/` tree, which made one hook fail there
and appears in some sessions' check lists. Replay inputs, streams and
scoring: `~/tmp/replay-commitmsg/`.
