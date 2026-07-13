# Troubleshooting

## Non-Deterministic Screenshots

Disable animation, random seeds, blinking cursors, clocks, and live telemetry in capture scenes.

## Font Differences

Use the same fonts in CI and local runs. Small font rendering changes can cause widespread pixel diffs.

## First Adoption

Run with a small tolerance and inspect diffs manually before setting CI to fail on changes.

## Missing Screenshots

If `compare` reports a missing baseline, review the current screenshot and run
`approve` only when it represents the expected UI. If it reports a missing
current screenshot, run the capture step first and upload the capture artifact
with the JSON report.
