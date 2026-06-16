# Report Schemas

The toolkit reports are meant to be useful in scripts as well as in pull request
reviews. These schemas describe the stable top-level fields that automation can
depend on across the JSON reports checked into this repository.

The detailed payload differs by tool. For example, asset reports use `issues`,
export and input reports use `findings`, dashboard reports list cards and
artifacts, and telemetry reports include runtime samples or budget summaries.
The shared contract is intentionally smaller:

- a report identifies the tool or report kind;
- a report includes a `summary` object when it represents a diagnostic run;
- diagnostic rows use stable severity text such as `error`, `warning`, or
  `info`;
- new fields may be added without a breaking schema change;
- existing field meaning should not change without a schema version bump.

## Schema Files

| Schema | Use |
|---|---|
| [`tool-diagnostic-report-v1.schema.json`](tool-diagnostic-report-v1.schema.json) | General JSON report shape for command-line diagnostic tools. |
| [`finding-v1.schema.json`](finding-v1.schema.json) | Shared finding/issue row shape used by several reports. |

These are deliberately broad enough to cover current published examples while
still catching accidental removal of the fields most scripts need first.

## Compatibility Notes

Treat the schemas as top-level stability checks rather than complete product
specifications. Consumers should:

- read `tool`, `metadata.report_kind`, or both to choose tool-specific handling;
- tolerate unknown fields;
- treat missing optional sections as normal;
- pin to a tool version if a workflow depends on a package-specific nested
  payload.

The repository tests parse these schemas and check representative sample JSON
reports against the required top-level fields.
