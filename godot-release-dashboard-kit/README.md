# Godot Release Dashboard Kit

`godot-release-dashboard-kit` builds a small static dashboard from JSON,
Markdown, and image artifacts produced by Godot Production Toolkit commands.

It is intentionally simple: point it at a reports folder and it writes a
self-contained HTML file suitable for a CI artifact or release checklist.
Report cards are grouped into release readiness states so a project can quickly
spot blocked checks, warnings that need attention, and ready checks before a
release build goes out.

## Install

```powershell
python -m pip install godot-release-dashboard-kit
```

From a source checkout:

```powershell
python -m pip install -e .\godot-release-dashboard-kit
```

## Quick Start

```powershell
godot-release-dashboard build reports\godot-project-doctor --output reports\dashboard.html
```

Write a machine-readable dashboard summary:

```powershell
godot-release-dashboard build reports\godot-project-doctor --format json --output reports\dashboard.json
```

Include scenario run evidence in the same dashboard:

```powershell
godot-scenario-report bundle reports\scenarios --manifest scenario-manifest.json --telemetry reports\runtime-timeline.json --evidence log=reports\run.log --evidence junit=reports\junit.xml --format json --output reports\release-evidence\scenario-bundle.json
godot-release-dashboard build reports\release-evidence --output reports\dashboard.html
```

## Inputs

The dashboard scans a folder recursively for `.json`, `.md`, `.png`, `.jpg`,
`.jpeg`, `.svg`, and `.webp` files. Toolkit JSON reports are summarized through
their `tool`, `kind`, and `summary` fields when available. If a JSON report
includes `command`, `commands`, `tool_version`, `schema_version`,
`generated_at`, `profile`, or `risk`, the dashboard shows those fields as report
metadata and reproduction commands. Image artifacts such as mobile UI overlays,
screenshot diffs, pixel previews, and visual smoke captures are embedded into
the self-contained HTML output.

Scenario bundle JSON from `godot-scenario-report-kit` is shown as a release
evidence card with scenario pass/fail counts plus the nearby files a reviewer
should open next, such as logs, JUnit XML, runtime telemetry, profiler captures,
visual-smoke reports, or screenshots. The dashboard shows link metadata from the
bundle; it does not run the game or rewrite those evidence files. If the bundle
contains a compact telemetry summary, the dashboard also shows sample count,
frame p95, frame max, memory max, and budget spike counts.

## Outputs

- `html`: self-contained static dashboard with release readiness metrics, source
  report links, report cards, scenario evidence sections, and image previews.
- `json`: summary for scripts or later dashboard tooling, including counts for
  `blocked`, `attention`, `ready`, scenario bundles, scenarios, and linked
  scenario evidence. Reports that include reproduction commands are counted in
  `summary.reports_with_commands`. Scenario-linked telemetry summaries are
  rolled up as sample, spike, warning, and error counts.
