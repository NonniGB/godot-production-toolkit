# Troubleshooting

## Non-Deterministic Screenshots

Disable animation, random seeds, blinking cursors, clocks, and live telemetry in capture scenes.

## Font Differences

Use the same fonts in CI and local runs. Small font rendering changes can cause widespread pixel diffs.

## First Adoption

Run with a small tolerance and inspect diffs manually before setting CI to fail on changes.
