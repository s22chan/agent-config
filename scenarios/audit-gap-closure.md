# Evidence gaps left open that the repository answers

## Observed incident

After an `/audit` of `s22chan/project-suffix-remaining-launchers` in
`/mnt/main0/home/steve.chan/review2`, the agent ran `/audit-fix`, decided each
numbered finding, and never read the report's "Evidence gaps" section. One gap
read: "I also did not verify callers that re-call `update_parameters(name=...)`
on the executor returned by `create_submitit_executor`." A reference trace of
that function (41 caller files) found `projects/glm_functional/ag_eval/
parity.py:249`, which overwrites the suffixed job name. The user asked:

> why wasn't the create_submitit_executor stuff flagged before?

and then

> why woudl that have been an evidence gap when it's clearly traceable?

Both the audit (it listed a traceable in-repo question as a gap) and the fix pass
(`fix-audit-findings` says "for each finding" and never mentions gaps) let it
stand.

## Replay inputs

Fresh `claude -p` sessions (default config, read-only tools, same model), the
workflow text pasted into the prompt, the audit excerpt (one finding and four
gaps), the live repo as cwd. Gaps: not-executed tests; Slurm `-J` quoting (needs
a login node, the control that must stay open); callers re-calling
`update_parameters(name=...)`; callers passing `job_name=None` to
`SLURMBackend.submit_array`. Arms differ only in the `fix-audit-findings` text.

## Result

Round 1 (the prompt asked for one line per evidence gap): every session,
edited or not, resolved the update_parameters and job_name gaps and left the
quoting gap open (6 of 6). The prompt forced the gap check, so the incident did
not recur.

Round 2 (the prompt asked only for the workflow's report, three sessions per
arm) was contaminated: auto-memory and the session-start notes from the working
session reached the sessions, and five of six cite an earlier note about
`parity.py`. Round 3 removed that: the worktree of the same commit as cwd,
`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `disableAllHooks`; a probe quoted the
notes back in the default config and answered "no" with the isolation on.

Round 3 (clean, three sessions per arm), counting three traceable gaps per
session (update_parameters callers, by-name consumers, `job_name=None`):

| Arm | Traced | Left unchecked | Found `parity.py` |
|---|---|---|---|
| Unedited | 0 of 9 | 9 of 9 | 0 of 3 |
| Edited | 7 of 9 (one more partly) | 1 of 9 | 1 of 3 |

The quoting gap stayed open in all six, as intended. Two edited sessions wrote
"resolved, no defect" for the update_parameters callers after reading the first
40 to 60 hits of a truncated search, so they missed `parity.py`; the rule gets
sessions to trace, not to trace completely. No session used the LSP (one did in
an earlier round, one per arm), so the tool sentence in the first draft stayed
out.

Round 4 (the same clean setup, tool calls captured as stream-json, three
sessions per arm): the current wording against the same wording plus "Take those
of a Python symbol from the ty LSP (`findReferences`, `incomingCalls`), not from
text search". No session in either arm called the LSP (0 of 6; they used 4 to 11
text searches each), although a direct request to a headless session returns 91
references in 43 files, so the tool works. `parity.py` was found in 2 of 3
sessions with the current wording and 1 of 3 with the LSP sentence, which is
noise at this size. The LSP sentence changed nothing measurable and is not
shipped. One session even wrote "I used a text search ..., not the ty LSP".

## Caveats

Three sessions per arm; the workflow was pasted, not loaded as a skill. The
matching `audit-change` amendment (do not record an in-repo traceable question
as a gap) was drafted and not replayed, so it is not shipped.

## Outcome

Added a "Close the evidence gaps" section to `fix-audit-findings`. The
`audit-change` side and a clause against reporting a truncated trace as resolved
are open.
