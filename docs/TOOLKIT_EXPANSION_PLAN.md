# Toolkit Expansion Plan

## Purpose

Godot Production Toolkit is already useful as a set of narrow release checks:
assets, export presets, input maps, localization, save fixtures, scene signals,
visual smoke tests, mobile performance settings, API comments, and deterministic
pixel asset helpers.

The next opportunity is to make it more useful for larger Godot 4 projects that
are data-driven, simulation-heavy, mobile-aware, and maintained by small teams.
Those projects tend to fail in ways ordinary unit tests do not catch:

- content files reference missing ids or describe impossible production chains;
- runtime scenarios pass once but regress later without comparable evidence;
- mobile UI works on desktop but not on a portrait touch screen;
- GDScript autoloads and scenes accumulate implicit coupling;
- save migrations exist but are not proven against real fixtures;
- performance budgets are checked manually rather than tracked over time.

The public positioning should stay practical: this is a production-safety toolkit
for Godot projects, not a project-specific framework.

## Current Strengths

- **Clear standalone packages.** Each tool has its own CLI, tests, docs, examples,
  and PyPI package.
- **Good CI story.** JSON/SARIF/Markdown outputs make the tools useful locally,
  in GitHub Actions, and in scripts.
- **Strong release hygiene.** Version checks, changelogs, package publishing,
  and manifest verification are already in place.
- **Good mobile/pixel-art base.** Asset, input, export, and mobile perf checks
  already cover common Android and 2D production mistakes.
- **Script-friendly interfaces.** Most tools are noninteractive and machine-readable.

## Current Weaknesses

- **Data content integrity is under-covered.** The suite validates save fixtures,
  but it does not yet validate general game data graphs such as goods, recipes,
  ships, modules, factions, stations, maps, quests, or other referenced content.
- **Runtime evidence is not standardized.** Visual smoke checks exist, but there
  is no general way to validate, summarize, compare, or minimize scenario result
  files from a Godot project.
- **Mobile UI readiness is mostly indirect.** Input and project settings checks
  help, but there is no touch-target, safe-area, portrait layout, or UI screenshot
  readability report.
- **Architecture drift is only lightly covered.** Scene signal auditing catches
  some coupling, but autoload/module boundaries, signal ownership, and dependency
  direction are not first-class checks.
- **Asset metadata checks are shallow.** PNG/import checks are useful, but larger
  2D projects also need sprite manifest, atlas, anchor-point, scale, naming, and
  source/export consistency checks.
- **The umbrella CLI does not yet feel like a project cockpit.** It can run tools,
  but it could do more to recommend checks, compare reports, track trends, and
  produce a single release note for humans.

## Recommendation

Enhance the existing suite first, then add three or four new tools where a new
domain would otherwise make an existing package confusing.

Avoid creating a broad second repository for now. A single coherent toolkit with
deeper, more opinionated checks is more credible and easier to adopt than several
small repositories with overlapping scopes.

## Expansion Themes

### 1. Data Graph Safety

Create a new package: `godot-content-graph-doctor`.

Purpose: validate JSON/TOML/CSV/YAML game content as a graph of ids and references.

Useful checks:

- duplicate or empty ids;
- references to missing ids;
- unreachable content;
- unused content that is never referenced;
- invalid enum-like fields;
- numeric budget checks such as negative cost, zero volume, impossible capacity;
- production-chain checks for missing producers, missing consumers, circular-only
  dependencies, terminal dead ends, and goods that cannot enter the economy;
- schema inference reports that show field presence, observed types, and examples;
- impact report for a changed data file: which other files and checks are likely
  affected.

Why this should be a new tool:

Save fixtures are one specific data type. A content graph tool is broader and
should not be squeezed into `godot-save-schema-guard`.

Public value:

Any RPG, strategy game, sim, factory game, roguelike, trading game, or content-rich
Godot project can use this.

First milestone:

- Config file declaring collections, id fields, and reference fields.
- JSON report with missing-reference and duplicate-id findings.
- Markdown graph summary.
- Example fixture with goods, recipes, stations, and ships using neutral names.

### 2. Scenario Result Toolkit

Create a new package: `godot-scenario-report-kit`.

Purpose: standardize the outputs of project-owned runtime scenarios without
prescribing how the game launches.

Useful checks:

- validate scenario result JSON against a simple public schema;
- summarize pass/fail, assertions, timings, snapshots, warnings, and artifacts;
- compare two scenario result folders and show meaningful deltas;
- detect flaky scenarios from repeated runs;
- produce a Markdown/HTML scenario report for CI artifacts;
- minimize a failing scenario file when the project uses a compatible step format;
- generate a stable issue bundle with scenario config, report, redacted logs, and
  artifact links.

Why this should be a new tool:

Runtime scenario reporting is neither visual smoke testing nor static diagnostics.
It deserves its own package because it can become the bridge between Godot runtime
tests, CI artifacts, and machine-readable debugging.

Public value:

Godot projects often have custom smoke tests but inconsistent reporting. A small,
schema-based result toolkit would be useful even when every project keeps its own
runner.

First milestone:

- `validate-result`, `summarize`, and `compare` commands.
- JSON and Markdown outputs.
- Tiny synthetic scenario-result fixtures.
- GitHub Action artifact example.

### 3. Mobile UI Readiness

Expand existing tools before adding a new one.

Primary packages:

- `godot-input-map-auditor`
- `godot-mobile-perf-doctor`
- `godot-visual-smoke-test-kit`

Useful enhancements:

- input auditor: action taxonomy (`navigation`, `combat`, `menu`, `debug`) and
  required-device policies per action group;
- input auditor: generated touch-readiness matrix with missing gestures, missing
  controller alternatives, and duplicate conflicts;
- mobile perf doctor: portrait/landscape intent checks, stretch/safe-area warnings,
  viewport budget presets, and Android setting profiles;
- visual smoke kit: screenshot-set manifests for common device sizes, safe-area
  overlays, and layout drift reports;
- visual smoke kit: OCR-free text-density heuristics based on bounding boxes if a
  project supplies node rectangles or accessibility metadata.

Why not a new tool yet:

The existing packages already own input, mobile settings, and screenshots. The
first wins are extensions, not a separate `godot-mobile-ui-doctor`.

Public value:

Mobile Godot projects need concrete, repeatable checks that do not require a
developer to inspect every screen by hand.

First milestone:

- Input action groups and policy config.
- Visual smoke manifest with multiple viewports and per-viewport thresholds.
- Mobile perf profile presets: `portrait-2d`, `tablet-2d`, `low-memory-2d`.

### 4. GDScript Architecture Guard

Create a new package: `godot-gdscript-architecture-guard`.

Purpose: detect architecture drift in medium-to-large GDScript projects.

Useful checks:

- autoload dependency direction rules;
- forbidden imports or forbidden singleton access by path glob;
- max file size and max function size warnings;
- signal ownership rules;
- scene-to-autoload coupling report;
- public API surface report for selected folders;
- config-defined module boundaries with friendly explanations.

Why this should be a new tool:

`godot-scene-signal-auditor` should stay focused on scene signal wiring. Architecture
rules are broader and need a policy file.

Public value:

Godot projects often grow through autoloads and signals. A lightweight architecture
guard gives small teams some of the benefits of a larger engineering process.

First milestone:

- Policy TOML with modules, allowed dependencies, and forbidden patterns.
- JSON/Markdown reports.
- SARIF for forbidden dependency findings.
- Synthetic project showing clean and failing boundaries.

### 5. Save Migration Confidence

Enhance `godot-save-schema-guard`.

Useful enhancements:

- migration chains, not only single migration commands;
- roundtrip validation: old fixture -> migrate -> validate -> optional load probe;
- fixture coverage report by save version;
- redaction helper for sharing failing save snippets;
- compatibility matrix for supported save versions;
- deterministic output snapshots for CI review.

Why not a new tool:

This is the same domain as the existing package. Expanding it makes the current
tool more useful and easier to explain.

First milestone:

- `chain` subcommand with a TOML migration plan.
- Markdown compatibility matrix.
- Fixture version summary.

### 6. Asset Metadata And Sprite Production

Enhance `godot-asset-pipeline-doctor` and `pixel-space-asset-toolkit`.

Useful enhancements:

- sprite manifest validation: id, source path, runtime path, dimensions, tags;
- anchor-point validation for thrusters, sockets, weapon hardpoints, UI markers,
  or other project-defined attachment points;
- atlas consistency checks: cell sizes, padding, duplicate empty cells, unexpected
  transparency, naming drift;
- source/export consistency checks for generated assets;
- contact sheet diffing for reviewed asset batches;
- palette and contrast reports for pixel-art readability.

Why not a new tool yet:

The current asset and pixel packages already cover PNGs and deterministic assets.
Sprite metadata should extend that foundation first.

First milestone:

- Manifest schema and validator.
- Anchor bounds checks against PNG dimensions.
- Contact sheet generation from a manifest.

### 7. Release Evidence Cockpit

Enhance `godot-project-doctor`.

Useful enhancements:

- `doctor recommend`: inspect a project and suggest which standalone checks apply;
- `doctor collect`: run selected checks and produce one release evidence folder;
- `doctor compare`: compare two evidence folders and highlight new/regressed findings;
- `doctor trend`: summarize repeated report folders over time;
- `doctor issue-bundle`: create a redacted issue bundle for public bug reports;
- support package-installed tools as well as source-checkout tools.

Why not a new tool:

The umbrella CLI should become the user's main cockpit. These features make the
whole suite easier to use without diluting standalone packages.

First milestone:

- `recommend` command based on project files.
- `compare` command for two report directories.
- single Markdown report linking all generated artifacts.

## Priority Roadmap

### Phase 1: Deepen Existing Tools

Goal: make the current packages feel more useful before expanding the suite count.

Work:

1. Add input action groups and policy config to `godot-input-map-auditor`.
2. Add mobile profile presets and safe-area/stretch warnings to `godot-mobile-perf-doctor`.
3. Add visual smoke viewport manifests to `godot-visual-smoke-test-kit`.
4. Add save migration chains to `godot-save-schema-guard`.
5. Add sprite manifest and anchor validation to `godot-asset-pipeline-doctor`.
6. Add `recommend` and `compare` commands to `godot-project-doctor`.

Expected result:

The suite becomes more useful for mobile-first and data-heavy projects without
introducing a lot of new package maintenance.

### Phase 2: Add Content Graph Safety

Goal: cover the biggest current gap: data-driven content integrity.

Work:

1. Create `godot-content-graph-doctor`.
2. Support configurable collections and references.
3. Add graph reports, missing references, duplicate ids, unused content, and
   production-chain sanity checks.
4. Publish to PyPI once the first fixture and docs are complete.

Expected result:

The toolkit becomes relevant to simulation, RPG, strategy, factory, trading, and
content-heavy Godot projects, not only release engineering.

### Phase 3: Add Runtime Evidence Tools

Goal: make project-owned scenario and telemetry outputs easier to review and compare.

Work:

1. Create `godot-scenario-report-kit`.
2. Add result schema validation, summary, compare, flaky-run detection, and HTML reports.
3. Add examples that do not require a real Godot binary.
4. Integrate with `godot-project-doctor collect`.

Expected result:

The toolkit moves from static checks into repeatable runtime evidence without
trying to own every project's runner.

### Phase 4: Add Architecture Guard

Goal: help medium-to-large Godot codebases avoid autoload and signal coupling drift.

Work:

1. Create `godot-gdscript-architecture-guard`.
2. Add policy-based module boundaries.
3. Add signal ownership and singleton access checks.
4. Add SARIF output for dependency violations.
5. Integrate summary output with `godot-project-doctor`.

Expected result:

The toolkit becomes valuable during refactors, not only before releases.

## Suggested New Package Names

- `godot-content-graph-doctor`
- `godot-scenario-report-kit`
- `godot-gdscript-architecture-guard`

Potential later package, only if existing tool expansion becomes crowded:

- `godot-mobile-ui-doctor`

## Success Criteria

- A new user can install one package and get a useful report in under five minutes.
- Every new feature has a tiny synthetic fixture and at least one failing example.
- Every tool continues to support JSON output for scripts and Markdown/text for humans.
- The umbrella CLI can recommend checks without requiring project-specific setup.
- Public docs stay generic and do not mention private projects, paths, or proprietary data.
- The suite remains useful even when a project has its own runtime harness.

## Near-Term Build Sequence

1. `godot-project-doctor recommend` with project-file detection.
2. Input action group policies in `godot-input-map-auditor`.
3. Mobile profile presets in `godot-mobile-perf-doctor`.
4. Visual smoke viewport manifests in `godot-visual-smoke-test-kit`.
5. Sprite manifest and anchor checks in `godot-asset-pipeline-doctor`.
6. Save migration chains in `godot-save-schema-guard`.
7. First version of `godot-content-graph-doctor`.
8. Content graph production-chain checks.
9. First version of `godot-scenario-report-kit`.
10. First version of `godot-gdscript-architecture-guard`.

This sequence improves existing packages first, then adds the three genuinely
new domains with the strongest public utility.
