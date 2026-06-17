# Changelog

## 0.1.8 - 2026-06-18

- Scenario bundles now summarize linked visual smoke JSON reports with capture,
  comparison, changed-comparison, warning, and error counts.
- Markdown and HTML bundle reports show compact visual evidence metrics beside
  telemetry summaries and linked evidence tables.
- Added a tiny visual-smoke fixture and tests for release review bundles that
  include screenshot comparison evidence.

## 0.1.7 - 2026-06-17

- `flake compare` now groups repeated attempts of the same scenario inside a
  run folder or result file.
- JSON, text, Markdown, and HTML reports include retried scenario counts,
  attempt totals, ordered statuses, and the final status for each retry group.
- Added a tiny retry fixture and tests for runners that retry failed scenarios
  before producing a final pass/fail result.

## 0.1.6 - 2026-06-17

- `summarize`, `compare`, `manifest`, `flake`, and `bundle` now read JUnit XML
  result files directly alongside the existing JSON scenario result shape.
- JUnit `<testcase>` rows become scenarios, `time` values are converted to
  milliseconds, and `<failure>`, `<error>`, and `<skipped>` children map to the
  existing scenario/assertion status model.
- Added rule help and tests for malformed JUnit XML input.

## 0.1.5 - 2026-06-17

- Scenario bundles now summarize linked JSON runtime telemetry reports with samples, scenarios, frame p95, frame max, memory max, spike, warning, and error counts.
- Markdown and HTML bundle reports show compact telemetry metrics without copying raw telemetry samples into the bundle.
- Raw JSON sample files passed through `--telemetry` now get a small summary when possible.

## 0.1.4 - 2026-06-17

- Added repeatable `--evidence KIND=PATH` links for scenario bundles, so run logs, JUnit XML, profiler captures, crash reports, or other review files can be listed beside scenario results.
- Markdown and HTML bundle reports now include linked evidence and scenario artifact tables.
- Bundle evidence reports include metadata only; linked file contents are not copied, parsed, summarized, or embedded.

## 0.1.3 - 2026-06-16

- Added `bundle` reports that collect scenario results, listed artifacts, and optional manifest, telemetry, and visual evidence links.
- Added bundle findings for missing scenario artifacts and missing linked evidence paths.

## 0.1.2 - 2026-06-16

- Added `manifest check` for scenario manifests, expected artifacts, and optional result alignment.
- Added `manifest coverage` for tag, critical-flow, and platform coverage policy.
- Added `flake compare` to identify scenarios whose status changes across repeated runs.
- Extended the tiny fixture with a scenario manifest and repeat-run example.

## 0.1.1 - 2026-06-15

- Added report schema and tool version metadata.
- Added rule titles and short remediation help to JSON, text, Markdown, and HTML output.
- Added tests covering rule-help output for scenario findings.

## 0.1.0 - 2026-06-09

- Initial scenario evidence validator and summarizer.
- Added baseline comparison for new failures and duration regressions.
- Added text, JSON, Markdown, and HTML reports.
