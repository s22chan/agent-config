# Inject an external-effect collaborator instead of patching it in tests

## Trigger

While trimming a launcher helper, the agent kept hardware queries inside the
function and had tests patch five library calls. Asked whether the query could
be a default callback overridden in tests, it argued for a single patched
module function instead, because "the repo rules discourage parameters only
tests use". The user answered "to avoid the patching", then asked "can we
override the parameter that only tests use rule in my personal rules" and
checked whether it was "a repo rule that blocked it". No repo rule blocks it
(the worktree's AGENTS.md and .claude/rules files do not mention it). The
wording that pushed the agent came from personal files: common.md "Do not add
unused modes, flags, abstractions" and design-python-code "tests of an internal
helper are not consumers".

## What the agent did

Reasoned from those rules that a parameter only tests pass is unsupported, and
proposed patching one module-level function.

## What it should have done

Take the external-effect collaborator as a defaulted parameter, so the test
passes a fake and patches nothing.

## Test arms (fresh `claude -p`, hooks and memory off; probe quoted the edited bullet)

Prompt: write the function and its unit tests, tests run on CPU-only CI with no
GPU and no NVML. All arms invoked design-python-code and verify-behavioral-tests.

- Unedited, incident prompt: 0 of 3 added a parameter; 3 of 3 wrote a
  no-argument function and patched in the test.
- First edited wording, incident prompt: 3 of 3 injected callables, but each
  injected 3 to 4 (including an internal helper and the real affinity calls).
- Final wording (adds "when a test cannot run that effect for real" and "keep
  every other collaborator real"), incident prompt: 3 of 3 injected; one
  injected only the hardware reader, one injected two, one injected four.
- Final wording, equivalent case in another domain (HTTP status plus clock):
  injected the clock; the HTTP call was not injected.
- Final wording, nearby case where tests want intermediate values: added no
  parameter (1 of 1).

Not resolved: over-injection of internal helpers in 2 of 3 incident arms.
