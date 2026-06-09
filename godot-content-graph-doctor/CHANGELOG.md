# Changelog

## 0.1.2 - 2026-06-09

- Added changed-file impact reports with direct, downstream, and unmatched content files.
- Added `--changed-file` and `--changed-files` for pull request and release-check summaries.
- Included changed-file impact sections in text, Markdown, and JSON output.

## 0.1.1 - 2026-06-09

- Added built-in presets for items, recipes, quests, dialogue, levels, and content packs.
- Added `--preset` and `--list-presets` so common content graphs can run without a TOML config.
- Allowed config collections to override preset collections with the same name.

## 0.1.0 - 2026-06-09

- Initial content graph validator for JSON, CSV, and TOML collections.
- Added duplicate id, missing reference, unused content, and numeric outlier checks.
- Added text, JSON, Markdown, and Mermaid output.
