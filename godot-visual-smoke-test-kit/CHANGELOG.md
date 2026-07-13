# Changelog

## 0.1.3 - 2026-07-13

- `compare` now reports missing baseline or current screenshots as structured
  text/JSON findings with next-step guidance.
- Added missing-screenshot rule metadata for CI reports.
- Clarified the first compare-review-approve workflow in README and docs.

## 0.1.2 - 2026-06-09

- Added reusable viewport manifests for visual smoke planning.
- Included optional safe-area metadata in planned JSON output.
- Added report metadata and readable diff failure explanations to JSON and text output.

## 0.1.1 - 2026-06-09

- Added text and JSON approval status output for baseline updates.

## 0.1.0 - 2026-06-08

- Added `visual-smoke.toml` parser.
- Added PNG baseline/current diffing with pixel tolerance and diff image output.
- Added baseline approval helper.
- Added Godot capture command planning.
- Added CLI, tests, CI, docs, and generic config fixtures.
