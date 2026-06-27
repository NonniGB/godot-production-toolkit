# Changelog

## 0.1.13 - 2026-06-27

- Missing mobile UI metadata and visual-smoke plan paths now return concise
  usage errors with setup guidance before JSON parsing starts.

## 0.1.12 - 2026-06-27

- Added bounded stress-text previews to localization layout-risk JSON findings.
- Included layout-risk label details in overlay summaries so scripts can link marked controls back to the stress text that caused them.
- Overlay PNGs can now show a short stress-text preview inside larger marked controls.

## 0.1.11 - 2026-06-17

- Added `--layout-risk-report` to `overlays` so PNG previews can mark controls with localized stress-text overflow risks.
- Included localized layout-risk counts and findings in overlay JSON/text summaries.

## 0.1.10 - 2026-06-17

- Added `layout-risk` to join exported mobile UI metadata with localization stress-pack catalogs.
- Added `translation_key` metadata support for direct UI node to translation-key matching.
- Added JSON, Markdown, and text layout-risk reports for stress translation overflow review.

## 0.1.9 - 2026-06-16

- Added `thresholds.text_expansion_factor` for flagging labels that fit current copy but may overflow after localization expansion.
- Added `text_expansion_overflow_risk` to reports, rule metadata, and readiness matrix text/Markdown output.

## 0.1.8 - 2026-06-16

- Added schema and tool version metadata to mobile UI, matrix, overlay, and readiness reports.
- Added a rule catalog plus `rule_title` and `rule_help` fields to mobile UI findings.
- Included rule help in text and Markdown mobile UI reports.

## 0.1.7 - 2026-06-14

- Added grouped rule summaries to combined mobile readiness reports.
- Included repeated linked-report rule counts in JSON, Markdown, and text output.

## 0.1.6 - 2026-06-13

- Added `--screenshot-dir` to `overlays` for drawing safe-area and touch-target overlays on captured PNG screenshots.
- Included screenshot usage counts and source paths in overlay summaries.

## 0.1.5 - 2026-06-13

- Added top linked findings to combined mobile readiness reports.
- Included linked finding rules and locations in JSON, Markdown, and text output.

## 0.1.4 - 2026-06-11

- Added `readiness` command for combining mobile UI metadata with optional input, export, localization, mobile performance, and visual-smoke JSON reports.
- Added Markdown, JSON, and text output for cross-tool mobile readiness summaries.

## 0.1.3 - 2026-06-11

- Added `overlays` command for PNG safe-area, control-bound, and touch-target previews.
- Added visual-smoke viewport support to overlay generation.
- Documented overlay workflows for local review and CI artifacts.

## 0.1.2 - 2026-06-09

- Added `--visual-smoke-plan` for reusing viewport metadata from `godot-visual-smoke plan --format json`.

## 0.1.1 - 2026-06-09

- Added `matrix` command for screen-by-screen mobile UI readiness reports.
- Added per-screen status columns for safe area, touch targets, spacing, text fit, and viewport bounds.
- Updated documentation with a matrix workflow.

## 0.1.0 - 2026-06-09

- Initial mobile UI metadata checker.
- Added safe-area, touch-target, spacing, off-screen, duplicate-id, and text overflow checks.
- Added text, JSON, and Markdown reports.
