# W&B Research Report

Create reports from verified source data, not run names or prior prose. Use the
project's W&B environment when available; otherwise use
`uv run --with wandb-workspaces --with wandb`. Source the W&B environment file
inside the command process.

For report width, equations, Markdown tables, panel grids, or serialized block
layout, read [report layout and formatting](references/layout-and-formatting.md).

## Establish evidence

1. Identify the raw training runs, their IDs, job IDs, code/config differences, and intended hypothesis.
2. Classify each candidate run and figure as current evidence, superseded, or
   excluded. Exclude superseded evidence from current-result figures and
   headline comparisons. Retain concise supersession provenance when it is
   needed to explain a changed conclusion or audit a revision. Include a
   historical figure only when it is part of the research question and remains
   supported by an included source.
3. Read the raw run histories and summaries through the API. Verify every metric key and the required steps before reporting a value.
4. Inspect submitted scripts, archived source, and printed runtime config when the conclusion depends on an override. A run name, tag, or report label is not evidence that an override took effect.
5. Separate direct observations from interpretation. Label a mechanism as supported rather than proven unless the study isolates that mechanism.
6. Derive the research question and arm labels from the exact executed
   configuration difference. Treat shared settings as held constant; do not
   frame the comparison around a shared optimization or put its name in an arm
   label.
7. For a controlled intervention comparison, identify the cheapest available
   null action—such as retaining the existing default or skipping the
   component—and report its measured score. The null must isolate the
   intervention and be able to produce a nonzero score; a zero-by-construction
   baseline merely restates the metric. If the runs do not establish a
   meaningful null, disclose that limitation rather than implying one.
8. When a measurement differs by roughly 3x or more from a comparable existing
   estimate, audit its units, reference frame, aggregation, sampling window,
   and executed configuration before reporting it or using within-sample
   robustness checks. Resampling cannot detect a shared measurement error.
9. Treat overlapping forward windows as dependent observations. When reporting
   an inferential statistic for h-length windows, report an effective sample
   size based on span / h alongside the raw observation count; do not present
   the raw count as independent evidence. Treat HAC/Newey-West estimates as
   weak evidence when the selected lag approaches that effective sample size.

## Build or update the report

Prefer loading and updating an existing report with `Report.from_url`; do not create a duplicate report for a revision.

Select the exact runs in every panel grid. After saving, deserialize the report and verify that each runset has the intended selected IDs and that every panel uses the verified metric path. Do not rely on a plausible-looking metric name.

When a logical training arm is fragmented by preemption, do not imply that the raw W&B sessions form one continuous curve. Create a clearly named, tagged, analysis-only derived run only when a continuous chart is necessary. Merge raw history by trainer step, retain the source run IDs in config and report prose, and copy values without interpolation. Link both the derived series and the raw training runs. Never use a derived run's configuration as evidence of the training configuration.

Before handoff, verify that each requested source run contains the plotted metric at the claimed endpoint and that the derived run, if any, contains the merged endpoints.

## Write the research narrative

Use this order unless the user asks for another format:

1. **Abstract:** lead with the decision goal and intervention, then state the
   principal measured result and qualified conclusion. When the report concerns
   an optimization with a measured runtime result, include that primary
   performance figure in the abstract rather than leaving it to Results; state
   immediately if the measurement is a broader policy effect rather than an
   isolated attribution.
2. **Background and research question:** intended semantics and the falsifiable question.
3. **Methods:** arms, held-constant settings, data/replay protocol, checkpoints, and measurements.
4. **Results:** tables and panels with metric directions and exact comparison steps.
5. **Interpretation:** distinguish evidence from causal claims.
6. **Limitations and next experiment:** identify confounders, horizon/seed limits, and the intervention needed to resolve them.
7. **Reproducibility:** raw W&B runs, derived-series provenance, Slurm jobs, and relevant commits or scripts.

State what clipping, normalization, or other transformations act on.

## Final checks

- Verify report title, project, and URL by reading it back through the API.
- Confirm direct source values, derived-series endpoint values, selected IDs, and panel metric paths.
- Mark derived chart runs as analysis-only in their name, tags, and report text.
- Avoid claims that a short or single-seed comparison establishes a causal mechanism or a generally optimal training setting.
