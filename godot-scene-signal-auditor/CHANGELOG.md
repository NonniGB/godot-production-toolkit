# Changelog

## 0.1.4 - 2026-06-19

- Scene contracts can now require node group membership.
- Scene contracts can now require exported properties on node scripts.
- JSON scene/script output includes parsed node groups and exported script properties.

## 0.1.3 - 2026-06-16

- Added `--contract` support for JSON and TOML scene contracts.
- Contract checks cover required nodes, scene connections, script methods, and script signals.

## 0.1.2 - 2026-06-09

- Added report metadata and plain-language rule explanations to JSON and text output.

## 0.1.1 - 2026-06-09

- Ensured file output reports end with a trailing newline.

## 0.1.0 - 2026-06-08

- Added `.tscn` persistent connection parser.
- Added conservative GDScript signal, method, and connect-call parser.
- Added stale scene connection and autoload signal usage findings.
- Added text, JSON, and Mermaid graph output.
- Added CLI, tests, CI, docs, and a generic sample project.
