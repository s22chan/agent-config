# Report Layout and Formatting

## Width and Serialization

Use a wide report layout. Do not use W&B's narrow `readable` layout when it
compresses comparison tables or multi-panel evidence that readers must compare
together. Preserve an existing wider UI selection when updating a report rather
than assuming an API label maps to the same selection.

Verify the saved server model with
`Report.from_url(url, as_model=True).spec.width` and require a value other than
`readable`. Treat the locally deserialized width as untrusted when it disagrees
with the server model; do not rely on a local default to prove the saved layout.

## Equations and Tables

Use `LatexBlock` for displayed formulae and Markdown `$...$` only for short
inline notation. Keep each TeX expression as one string, or separate an
adjacent command and letter with whitespace or `{}`. Use KaTeX-safe commands
such as `\frac`, `\min`, `\lVert`, `\mathrm`, and `\qquad{}`. Avoid unsupported
commands such as `\mbox`.

Report Markdown tables do not provide supported cell-level shading. Use
explicit arm labels that match chart colors and bold the better value only when
the metric direction is stated. Put a column's unit on a second header line
with W&B's supported `<br>` break. Do not rely on other raw HTML or CSS for
table styling.

Keep tables narrow enough to scan without crowded headers or cells. Split a
table when long labels or roughly five columns make the rendered comparison
cramped. Pad Markdown source so pipes and columns align, use left alignment for
labels and right alignment for numeric values, and retain visible source-space
on both sides of each value. Read the saved Markdown blocks back and confirm
that padding and intended splits survived serialization.

## Panels and Block Order

Choose panel width from the visual comparison the reader must make. When panels
share an axis, prefer one chart while its series remain legible; otherwise put
them in one row with matched dimensions and bounds. Divide the 24-column grid
completely, such as two 12-column or three 8-column panels. Prefer fewer, wider
panels when labels or legends need room, and give unrelated plots a full row.
Read saved layouts back and verify every row consumes the intended width.

When prose and an equation are separate blocks, avoid relative references such
as “shown below” unless the blocks are adjacent in the saved report. Prefer a
self-contained sentence or move the equation beside the claim. Read back the
block sequence before handoff.
