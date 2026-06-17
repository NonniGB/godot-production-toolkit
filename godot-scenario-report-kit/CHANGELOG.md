# Changelog

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
