# Changelog

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
