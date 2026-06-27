# Tiny Runtime Regression

Use this path when scenario evidence and runtime telemetry need to explain a
performance or stability change.

## Source Inputs

- Scenario runs: [`godot-scenario-report-kit/examples/tiny-scenario-runs`](../../../godot-scenario-report-kit/examples/tiny-scenario-runs/README.md)
- Runtime telemetry: [`godot-runtime-telemetry-lab/examples/tiny-runtime-run`](../../../godot-runtime-telemetry-lab/examples/tiny-runtime-run/README.md)
- Dashboard evidence: [`godot-release-dashboard-kit/examples/tiny-release-evidence`](../../../godot-release-dashboard-kit/examples/tiny-release-evidence/README.md)
- Previous evidence: [`godot-release-dashboard-kit/examples/tiny-release-evidence-previous`](../../../godot-release-dashboard-kit/examples/tiny-release-evidence-previous/README.md)
- Sample reports: [`docs/assets/sample-reports`](../../../docs/assets/sample-reports/README.md)

## Commands

Run from the repository root after installing the local packages you need:

```powershell
godot-scenario-report compare godot-scenario-report-kit\examples\tiny-scenario-runs\baseline godot-scenario-report-kit\examples\tiny-scenario-runs\current --format markdown --output docs\assets\sample-reports\scenario-compare.md
godot-scenario-report flake compare godot-scenario-report-kit\examples\tiny-scenario-runs\baseline godot-scenario-report-kit\examples\tiny-scenario-runs\current godot-scenario-report-kit\examples\tiny-scenario-runs\repeat-run --format markdown --output docs\assets\sample-reports\scenario-flakes.md
godot-scenario-report manifest coverage godot-scenario-report-kit\examples\tiny-scenario-runs\scenario-manifest.json --results godot-scenario-report-kit\examples\tiny-scenario-runs\current --format html --output docs\assets\sample-reports\scenario-coverage.html
godot-telemetry-lab timeline godot-runtime-telemetry-lab\examples\tiny-runtime-run --budget-file godot-runtime-telemetry-lab\examples\tiny-runtime-run\android-high-budget.json --format html --output docs\assets\sample-reports\runtime-telemetry-timeline.html
godot-release-dashboard build godot-release-dashboard-kit\examples\tiny-release-evidence --previous-reports-dir godot-release-dashboard-kit\examples\tiny-release-evidence-previous --title "Tiny Runtime Regression" --output docs\assets\sample-reports\release-dashboard-demo.html
```

## Report Snapshots

- [`scenario-compare.md`](../../../docs/assets/sample-reports/scenario-compare.md)
- [`scenario-flakes.md`](../../../docs/assets/sample-reports/scenario-flakes.md)
- [`scenario-coverage.html`](../../../docs/assets/sample-reports/scenario-coverage.html)
- [`runtime-telemetry-timeline.html`](../../../docs/assets/sample-reports/runtime-telemetry-timeline.html)
- [`release-dashboard-demo.html`](../../../docs/assets/sample-reports/release-dashboard-demo.html)
- Timeline screenshot: [`runtime-telemetry-timeline.png`](../../../docs/assets/screenshots/runtime-telemetry-timeline.png)
- Scenario terminal capture: [`scenario-report-terminal.svg`](../../../docs/assets/screenshots/scenario-report-terminal.svg)
