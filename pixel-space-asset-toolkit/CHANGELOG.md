# Changelog

## 0.1.4 - 2026-06-14

- Added `compare-manifest` for comparing generated PNG sets through asset manifests.
- Included manifest field drift alongside changed, added, removed, and unchanged PNG counts.

## 0.1.3 - 2026-06-12

- Added `compare-dir` command for comparing PNG sets while preserving relative paths.
- Added directory diff summaries for changed, added, removed, and unchanged files.

## 0.1.2 - 2026-06-12

- Added `compare` command for deterministic PNG comparison and diff-image output.
- Added JSON and text summaries for pixel comparison runs.
- Added tag-triggered PyPI publishing workflow support.

## 0.1.1 - 2026-06-09

- Validated positive numeric dimensions and counts before generating assets.

## 0.1.0 - 2026-06-08

- Added deterministic starfield generation.
- Added deterministic hex asteroid tile generation with manifests.
- Added flat background stripping.
- Added preview contact sheet generation.
- Added CLI, tests, CI, docs, and generic examples.
