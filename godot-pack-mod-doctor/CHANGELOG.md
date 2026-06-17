# Changelog

## 0.1.3 - 2026-06-17

- Added dependency shape checks for pack manifests, including missing and duplicate dependency IDs.
- `load-order` now reports duplicate pack IDs, missing dependency packs, and dependencies that appear after the packs that need them.
- Text and Markdown reports now include dependency counts for ordered pack reviews.

## 0.1.2 - 2026-06-16

- Added `manifest from-folder` for generating deterministic pack manifests
  from a folder of Godot resources.
- Added advisory checks for local paths, parent-directory paths, non-`res://`
  paths, case-only collisions, file types that need review, and development or
  private files.

## 0.1.1 - 2026-06-16

- Added `diff` for added, removed, and changed files between pack manifests.
- Added `load-order` for detecting undeclared resource override conflicts across ordered packs.

## 0.1.0 - 2026-06-16

- Initial pack/mod manifest checker.
- Added duplicate path, override policy, and base reference checks.
- Added JSON, Markdown, and text reports.
