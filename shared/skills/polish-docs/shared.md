# Polish Docs

Make prose accurate, sparse, and understandable to a senior engineer seeing the
code fresh.

## Establish scope

- Use a user- or repository-named base. Otherwise resolve the configured
  upstream or remote HEAD; ask when no authoritative base exists. Review its
  merge-base diff with `HEAD`, plus uncommitted changes.
- Include Markdown, docstrings, comments, configuration prose, headers, and CLI
  help. Do not change logic, signatures, or behavior.
- Do not use this workflow for targeted `AGENTS.md`, `CLAUDE.md`,
  `.claude/rules/`, or `SKILL.md` edits. Those are operational configuration
  and belong to their authoritative owner.
- Treat prose outside the diff as base prose. Change it only when the branch
  makes it false or stale, or when the user explicitly broadens scope.
- Inspect deleted prose. Preserve correct comments and docstrings verbatim when
  code moves, and name the false or stale premise behind each deletion. Audit a
  rewritten claim independently: do not lose useful units, bounds,
  cardinalities, scope, citations, or measured costs merely because the new
  rationale reads better.

## Review in priority order

1. **Accuracy:** remove or qualify claims the source and evidence cannot verify.
2. **Ownership:** give each fact one canonical home across docs, source,
   configuration, tests, and commit prose.
3. **Structure:** make decisions, prerequisites, causes, contrasts, sequence,
   and consequences explicit.
4. **Sparseness:** remove mechanics recoverable from code and match the file's
   established markup, comment, and docstring conventions.

Choose the reader before editing; default to a senior engineer fluent in the
stack. Prefer a concrete subject, action, input, and observable result. Keep a
specialist term only when readers need it to operate an API or tool, reproduce a
procedure, or distinguish cases that plain language would merge. Preserve
literal identifiers, commands, metrics, and external fields.

Use length as a review trigger, not a target. Reconsider a sentence around 35
words, with three independent conditions, or mixing definition, consequence,
and exception. Split at decision boundaries; use a list for three or more
parallel requirements. Do not split coherent prose or count tables, commands,
interfaces, and citations.

Give an explanatory paragraph one main claim and connect supporting facts by
cause, contrast, sequence, prerequisite, or consequence. Move unrelated facts
to their owning section; do not conceal them with transition words. Reference
lists, tables, and procedures need no artificial narrative.

## Preserve decisions and authority

- For plans and proposals, keep the review path in the main flow: the decision,
  why it matters, what changes, ordering, and success criteria. Move supporting
  methods or history to a linked note only when reviewers do not need it to
  decide. Keep evidence conclusions, material limitations, safety constraints,
  prerequisites, ownership, and exit criteria with the decision.
- When capabilities gain operational authority independently, describe each
  capability's supported maturity, promotion evidence, permitted effects, and
  authority ceiling. Use only stages that change a real decision; do not force
  a maturity ladder onto a linear migration or one-step change.
- For inherited flags and sentinels, explain the concrete local state transition
  rather than repeating opaque upstream terminology.
- At a cross-layer contract, state the authoritative decision, valid proxy or
  attestation, failure the organization prevents, conservative fallback, and
  where changed assumptions are validated. Local lists or mappings should state
  only the invariant qualifying their members.

## Write source prose at its owner

- Lead a non-trivial symbol's docstring with the caller-visible goal or
  invariant: the cost avoided, failure prevented, or capability enabled. Use a
  direct contract summary for a simple accessor or transformation; omit a
  docstring that merely restates the signature.
- Document a non-obvious parameter by how the caller determines it: authority,
  units or cardinality, normalization, and coupled settings when relevant.
  Omit facts already clear from the type, name, default, and owning API.
- Before finalizing, ensure a senior engineer outside the immediate specialty
  can state each changed sentence's concrete input, action, and outcome without
  translating ornamental jargon.

## Apply and verify

Apply edits directly but leave them uncommitted unless the user requested a
commit or history rewrite. Run the cheapest syntax or parser check appropriate
to the touched files. Report corrected stale claims separately from wording
reductions, and list anything left unverifiable.
