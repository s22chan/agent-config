---
name: design-diagnostic-visualizations
description: Design or review diagnostic plots, alert attachments, dashboards, heatmaps, and dense entity-by-metric visualizations where operators must identify causes, recurrence, severity, prevalence, timing, or missing data. Do not use for decorative graphics or ordinary UI styling.
---

# Design Diagnostic Visualizations

Optimize the visual for the decisions an operator must make, not merely for
compactness or visual polish.

## Preserve diagnostic dimensions

Before choosing an encoding, identify which questions the visual must answer:
entity identity, magnitude, prevalence, recurrence across metrics or time,
missingness, and event timing. Map every decision-relevant dimension to a
visual channel or an exact annotation.

For entity-by-metric data or repeated panels:

- Consider full entity rows, aggregate summaries, and compact per-entity
  glyphs or minimaps before choosing an aggregation level. These are design
  alternatives, not a requirement to show all three.
- Before aggregating, name which diagnostic dimensions would be lost. If a
  lost dimension affects the decision, preserve it with a compact residual
  encoding rather than assuming a count or average is sufficient.
- Keep entity identity stable across metrics and panels through consistent
  color, position, or shape. Use a separate channel for quantitative severity;
  do not make one color simultaneously mean entity identity and magnitude.
- Distinguish missing or insufficient data from a measured zero or a
  sub-threshold result.

## Compare representations

When asked for the best visual, or when the choice is materially uncertain,
evaluate at least two meaningfully different encodings against the operator's
questions. Include compact glyph encodings in that comparison when full rows
would be too dense.

Treat a new requirement that exposes information lost by the current
aggregation as a reason to reconsider the representation. Do not only add text
or another aggregate to a design whose information model is insufficient.

Use redundant text only when it adds useful precision, accessibility, or
sample-size context. If the value is reliably and quickly inferred from the
visual, let the data use the space instead.

## Preserve semantic provenance

Before implementing a visual that explains an existing detector, alert, or
classification, identify the authoritative producer for every plotted score,
threshold, eligibility gate, mask, and status. Reuse authoritative values or
the existing implementation; do not restate production semantics in the
renderer. When no supported access path exists, report the ownership gap.
Extract a narrow shared helper only when production changes are in scope.

Keep presentation-only transformations such as layout, ordering, annotation,
and color normalization local to the visual, but derive them from the
authoritative diagnostic values. Numerical agreement between duplicate
implementations proves only the current examples, not continued alignment.

During review, reconcile the semantic owner of each production-derived value.
For unexplained recomputation in presentation code, identify the supported
producer or schema change that could make it diverge and the resulting wrong
display or operator decision. Keep it open when duplicated knowledge can change
independently; otherwise classify consolidation as optional. Rendered examples
and parity checks alone do not prove continued alignment.

## Verify the delivered visual

- Render a representative supported case, using observed data when available,
  and a realistic maximum-density case. Label altered or synthetic inputs as
  such; do not present them as historical evidence.
- Inspect the exact artifact at its delivery size. Check labels, legends,
  missing-data marks, color meaning, and dense layouts rather than relying on
  plotting code or artist properties alone.
- Trace thresholds, normalization, selection, and timing through the shipped
  data path before writing interpretation instructions.
- Add concise interpretation guidance when a nonstandard encoding would not be
  self-evident to the intended operator.
