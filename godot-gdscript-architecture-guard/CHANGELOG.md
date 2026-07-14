# Changelog

## 0.1.6 - 2026-07-14

- Added policy ignore paths so generated, vendor, or imported helper folders
  can be excluded from script scans, resource scans, owner summaries, hotspots,
  and possible-unused advice.
- JSON reports now include the active ignore patterns under `policy`.
- Documented ignore-path usage in the README and tiny architecture fixture.

## 0.1.5 - 2026-06-27

- Markdown reports now include a Mermaid module dependency graph when configured modules depend on each other.
- The CLI and JSON report version now read from the package version to keep release metadata aligned.

## 0.1.4 - 2026-06-19

- Added advisory possible-unused resource summaries for common Godot scene, resource, data, image, font, shader, and audio files.
- Text and Markdown reports now show possible unused resources beside existing script and hotspot sections.
- Updated the tiny architecture fixture with a referenced data file and a stale data file.

## 0.1.3 - 2026-06-17

- Added module ownership summaries for configured modules and unowned scripts.
- Markdown and text reports now show per-module script counts, dependency direction, autoload references, violations, hotspots, and possible-unused counts.
- JSON reports expose `owner_summaries` and an `owner_summaries` summary count for refactor review dashboards.

## 0.1.2 - 2026-06-17

- Added advisory high fan-in/fan-out file summaries to JSON, text, and Markdown reports.
- Added possible unused script summaries based on visible `res://` references and `class_name` declarations.
- Added warnings for configured module path patterns that match no GDScript files.

## 0.1.1 - 2026-06-15

- Added report metadata and rule explanations to JSON output.
- Added clearer rule descriptions to text, Markdown, and SARIF reports.

## 0.1.0 - 2026-06-09

- Initial GDScript architecture guard.
- Added module boundary checks, autoload access policy checks, unresolved resource dependency checks, and dependency graph output.
- Added JSON, Markdown, SARIF, and Mermaid output.
