# Godot Release Dashboard Kit

`godot-release-dashboard-kit` builds a small static dashboard from JSON,
Markdown, and image artifacts produced by Godot Production Toolkit commands.

It is intentionally simple: point it at a reports folder and it writes a
self-contained HTML file suitable for a CI artifact or release checklist.
Report cards are grouped into practical workflows and keep their release
readiness state visible, so export, runtime evidence, mobile UI, content, and
other checks stay easier to scan in one page. Common toolkit reports also show
typed highlights such as frame p95, pack order, export preset counts, scenario
retry counts, exported file counts, and risk scores without making readers open
every JSON file first.

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

Fail a CI job when the input folder is empty or points at the wrong path:

```powershell
godot-release-dashboard build reports\release-evidence --require-reports --output reports\dashboard.html
```

Compare the current reports with a previous report folder:

```powershell
godot-release-dashboard build reports\current --previous-reports-dir reports\previous --title "Release Candidate Evidence" --description "Android export and runtime checks" --project "Demo Game" --output reports\dashboard.html
```

Include scenario run evidence in the same dashboard:

```powershell
godot-scenario-report bundle reports\scenarios --manifest scenario-manifest.json --telemetry reports\runtime-timeline.json --evidence log=reports\run.log --evidence junit=reports\junit.xml --format json --output reports\release-evidence\scenario-bundle.json
godot-scenario-report flake compare reports\retry-run --format json --output reports\release-evidence\scenario-flakes.json
godot-release-dashboard build reports\release-evidence --output reports\dashboard.html
```

## Inputs

The dashboard scans a folder recursively for `.json`, `.md`, `.png`, `.jpg`,
`.jpeg`, `.svg`, and `.webp` files. Toolkit JSON reports are summarized through
their `tool`, `kind`, and `summary` fields when available. If a JSON report
includes `command`, `commands`, `tool_version`, `schema_version`,
`generated_at`, `profile`, `risk`, `workflow`, or `category`, the dashboard
shows those fields as report metadata, reproduction commands, and grouping
labels. `workflow` and `category` can appear at the report top level, inside
`metadata`, or inside `summary`. When they are absent, the dashboard uses a
conservative fallback based on the tool name, report kind, and file path. Image
artifacts such as mobile UI overlays, screenshot diffs, pixel previews, and
visual smoke captures are embedded into the self-contained HTML output.
For common toolkit report shapes, dashboard cards include a small Highlights
section with typed values such as runtime sample counts, frame p95/max, pack
counts, pack load order, export preset counts, export file totals, asset counts,
and risk levels.

Exported-folder and exported-file-list JSON from `godot-export-preset-doctor`
is shown as export artifact evidence. The dashboard rolls up file counts, byte
totals, SHA-256 coverage, extension counts, private/signing findings,
development-file findings, and a compact file manifest so exported build
contents are easier to review next to the preset and runtime checks.

Scenario bundle JSON from `godot-scenario-report-kit` is shown as a release
evidence card with scenario pass/fail counts plus the nearby files a reviewer
should open next, such as logs, JUnit XML, runtime telemetry, profiler captures,
visual-smoke reports, or screenshots. The dashboard shows link metadata from the
bundle; it does not run the game or rewrite those evidence files. If the bundle
contains a compact telemetry summary, the dashboard also shows sample count,
frame p95, frame max, memory max, and budget spike counts.

Scenario flake comparison JSON from `godot-scenario-report-kit` is shown as a
separate runtime evidence card. It lists flaky scenario groups, retried scenario
runs, ordered attempt statuses, and final status values so a failed-then-passed
scenario is easier to distinguish from a fresh failure.

Visual smoke JSON from `godot-visual-smoke-test-kit` is shown as screenshot
review evidence. The dashboard summarizes captures, comparisons, changed
screenshots, pixel-change totals, linked screenshot or diff paths, and visual
findings. Scenario bundle cards also surface linked visual-smoke summaries when
the bundle references a visual report.

When `--previous-reports-dir` is supplied, the dashboard scans the previous
folder with the same report rules and adds a compact change section. The trend
section shows previous/current blocked, attention, and ready counts as static
readiness bars, followed by cards for added, removed, and changed reports with
status changes and error/warning deltas. The `--baseline` flag is accepted as a
shorter alias. HTML dashboards include local filter buttons for blocked,
attention, ready, and workflow-specific report groups, so a larger release page
can be narrowed without rerunning any command. The generated page also includes
keyboard focus states, a skip link, live filter status text, a no-JavaScript
note, and print styles for reviewers who save CI artifacts as PDF.

## Outputs

- `html`: self-contained static dashboard with release readiness metrics, local
  status/workflow filters, source report links, workflow-grouped report cards,
  scenario evidence sections, export artifact evidence sections, image
  previews, keyboard navigation affordances, and print-friendly report cards.
- `json`: summary for scripts or later dashboard tooling, including counts for
  `blocked`, `attention`, `ready`, workflow groups, scenario bundles, scenarios,
  linked scenario evidence, flaky scenarios, retried scenarios, export artifact
  reports, inspected export files, hashed files, export artifact finding groups,
  visual-smoke reports, visual captures, visual comparisons, and changed visual
  checks. Reports that include reproduction commands are counted in
  `summary.reports_with_commands`, and report cards can include `highlights`
  rows for typed summary values. Scenario-linked telemetry summaries are rolled
  up as sample, spike, warning, and error counts. When a previous folder is
  supplied, JSON output also includes `previous_summary`, `trends`,
  `trends.status_counts`, `trends.status_deltas`, and trend-related summary
  counts.
