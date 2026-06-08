# Implementation Roadmap

This is a suite-level implementation plan. Each tool remains standalone and should be implemented in its own repository or folder first, then published separately.

## Phase 0: Shared Standards

- Create a reusable project template for Python CLI tools:
  - `pyproject.toml`
  - `src/<package_name>/`
  - `tests/`
  - `docs/`
  - `examples/`
  - `.github/workflows/ci.yml`
  - `README.md`
  - `LICENSE`
  - `CHANGELOG.md`
  - `CONTRIBUTING.md`
- Pick a standard CLI stack:
  - Python 3.11+
  - Typer or argparse for CLI
  - pytest for tests
  - Ruff for lint/format
  - MkDocs or plain Markdown docs
- Define a common output model:
  - `--format text|json|sarif`
  - `--config <path>`
  - non-zero exit codes for CI failures
  - deterministic fixture tests

## Phase 1: First Three Public Repos

1. `godot-asset-pipeline-doctor`
   - Build parser for image files and `.import` metadata.
   - Add pixel-art, alpha, texture size, and mobile-memory checks.
   - Ship one example Godot project.

2. `godot-export-preset-doctor`
   - Parse `export_presets.cfg`.
   - Detect credentials, missing icons, missing architectures, debug flags, and insecure release options.
   - Ship a GitHub Action example.

3. `gdscript-api-comment-coverage`
   - Parse `.gd` scripts for public classes, methods, signals, and exported properties.
   - Generate Markdown API index.
   - Enforce configurable coverage thresholds.

## Phase 2: Visible QA Tooling

4. `godot-visual-smoke-test-kit`
   - Add baseline capture runner.
   - Add pixel-diff summaries.
   - Add scene list config.
   - Add CI artifact guidance.

5. `godot-mobile-perf-doctor`
   - Start with static project/export checks.
   - Add optional Android `adb` measurement later.
   - Produce human-readable and JSON reports.

## Phase 3: Deeper Godot Audits

6. `godot-input-map-auditor`
   - Parse `[input]` actions from `project.godot`.
   - Detect missing keyboard/gamepad/touch mappings.
   - Generate input reference docs.

7. `godot-save-schema-guard`
   - Validate JSON save fixtures against schemas.
   - Generate migration tests.
   - Detect unsafe resource-save patterns when possible.

8. `godot-scene-signal-auditor`
   - Parse `.tscn` connections and GDScript signal declarations.
   - Report stale scene connections and risky autoload coupling.
   - Export Mermaid graphs.

## Phase 4: Distinctive Game-Design Tools

9. `godot-localization-qa-guard`
   - CSV/PO localization parser.
   - Missing-key, placeholder, encoding, and unchanged-string checks.
   - Godot import-readiness and release QA report.

10. `pixel-space-asset-toolkit`
   - Polish existing starfield/asteroid/background tools into one package.
   - Add deterministic previews.
   - Add Godot import examples.

## Release Discipline

For every tool:

- First release: `v0.1.0`, CLI only, fixtures, docs, one example project.
- Second release: `v0.2.0`, CI integration examples and JSON/SARIF output.
- Third release: `v0.3.0`, community-requested improvements and docs polish.

Do not start more than two implementation repos at once. Maintenance evidence matters more than repo count.
