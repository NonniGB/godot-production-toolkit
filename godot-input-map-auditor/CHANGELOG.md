# Changelog

## 0.1.3 - 2026-06-09

- Added optional TOML policy files for action groups and group-specific device requirements.
- Added group metadata to JSON reports and generated Markdown input references when a policy is active.
- Added report metadata and plain-language rule explanations to JSON, text, and SARIF output.

## 0.1.2 - 2026-06-09

- Accept case-insensitive required device family names.
- Ensure generated Markdown and GDScript files end with a trailing newline.

## 0.1.1 - 2026-06-09

- Validated required input device family names before auditing.

## 0.1.0 - 2026-06-08

- Added `[input]` parser for Godot `project.godot`.
- Added device-family classification for keyboard, mouse, gamepad, and touch events.
- Added missing required device and duplicate binding checks.
- Added Markdown input reference and GDScript constants generation.
- Added CLI, tests, CI, docs, and a generic sample project.
