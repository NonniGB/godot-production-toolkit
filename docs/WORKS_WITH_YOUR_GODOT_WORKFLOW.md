# Works With Your Godot Workflow

Godot Production Toolkit is meant to sit beside the way you already build and
ship Godot projects. It is not a replacement editor, launcher, project
template, or runtime framework.

The tools are Python CLIs and a GitHub composite action. They inspect project
files, manifests, reports, screenshots, and exported evidence. They do not add a
required runtime dependency to your shipped game. If you use one of the tools in
CI or before a release, the result is a report, checklist, SARIF file, image
diff, dashboard, or other build artifact. Nothing from the toolkit needs to be
bundled into the player-facing build.

## Local CLI Use

Use local commands when you want quick feedback before committing, tagging, or
starting a release build.

Typical patterns:

```powershell
godot-export-doctor . --format markdown --output reports\export.md
godot-asset-doctor . --profile pixel-2d --format json --output reports\assets.json
godot-project-doctor doctor . --profile release
godot-project-doctor doctor . --profile release --write-plan
godot-project-doctor run --project . --checks assets,export,input --reports-dir reports\godot-project-doctor
```

This works best as a preflight layer:

- Run normal Godot unit tests, scene tests, and manual playtests as usual.
- Run the toolkit for checks that are easy to miss in review: export settings,
  import flags, input coverage, localization files, save fixtures, signal wiring,
  mobile UI metadata, and report packaging.
- Keep outputs in a `reports/` directory or your existing build evidence
  directory.

Most checks read files directly from the project folder. A few tools work from
artifacts that your own project or test harness already produced, such as
screenshots, scenario result JSON, runtime telemetry, or mobile UI rectangle
exports.

## GitHub Actions

The GitHub Action wraps the same idea for pull requests and release branches. It
does not require changing how the game is built. Put it before or after your
existing Godot export/test steps depending on what evidence you want it to
inspect.

```yaml
- uses: NonniGB/godot-production-toolkit/godot-ci-doctor-action@v0.1.2
  with:
    project: .
    checks: assets,export,input,localization,signals,mobile_perf
    reports-dir: reports/godot-project-doctor
```

Upload the reports directory as a workflow artifact if you want reviewers to
download the JSON, Markdown, HTML, SARIF, image diffs, or dashboards from the
run. The action is a CI step, not a game dependency.

## Pre-release Checklist

A practical release pass can be modest:

1. Run your normal Godot tests and any platform export smoke tests.
2. Run `godot-project-doctor doctor . --profile release --write-plan` for a
   checklist-style pass that can be kept with project docs.
3. Run focused tools for the release risk you are touching:
   `godot-export-doctor` for export presets, `godot-asset-doctor` for changed
   art, `godot-input-audit` for control changes, and `godot-l10n-guard` for
   localization.
4. If you have scenario, screenshot, telemetry, or mobile UI artifacts, summarize
   them with the artifact-oriented tools.
5. Save the reports with the build or attach them to the release workflow.

The toolkit should make review more repeatable. It should not add a large new
process to every small change.

## Artifact-only Usage

Several packages are useful even when they never open a Godot project directly:

- `godot-scenario-report-kit` summarizes JSON or JUnit XML outputs from your own
  scenario or test runner.
- `godot-runtime-telemetry-lab` adapts and compares runtime samples, budgets,
  and timelines that your project already emitted.
- `godot-visual-smoke-test-kit` compares screenshots and manages visual baselines.
- `godot-mobile-ui-doctor` checks exported UI rectangle metadata.
- `godot-release-dashboard-kit` turns existing reports and screenshots into a
  workflow-grouped static review page, with optional previous-run trends.

That makes the toolkit easy to add after the fact. A build can produce evidence
however it already does today; the toolkit can then inspect that evidence and
produce a clearer report.

## Does Godot Need To Be Installed?

For the CLI packages themselves, Python is the runtime. Godot is only needed
when your workflow needs Godot to generate the input evidence, run gameplay
tests, export builds, or capture screenshots. The table below describes whether
the package command requires the Godot executable in order to run.

| Package | Godot required to run the package? | Notes |
|---|---:|---|
| `godot-project-doctor` | No | Recommends package installs, runs and summarizes toolkit checks from a source checkout, and can write profile-based Markdown setup plans. It may inspect a Godot project directory, but the CLI itself does not launch Godot. |
| `godot-ci-doctor-action` | No | Runs in GitHub Actions around your existing workflow. It can consume the project files and reports you provide. |
| `godot-export-preset-doctor` | No | Reads `export_presets.cfg` and reports export-readiness issues. It does not perform the export. |
| `godot-asset-pipeline-doctor` | No | Reads PNG/audio files, `.import` files, and optional sprite manifests. |
| `godot-content-graph-doctor` | No | Reads content data files such as JSON, CSV, TOML, and related references. |
| `godot-gdscript-architecture-guard` | No | Statically reads GDScript files and optional architecture policy. |
| `godot-input-map-auditor` | No | Reads input map data from `project.godot` and related generated references. |
| `godot-localization-qa-guard` | No | Reads CSV, PO, POT, and project localization usage. |
| `godot-mobile-perf-doctor` | No | Statically reads project settings, import files, and mobile-relevant configuration. |
| `godot-mobile-ui-doctor` | No | Reads exported UI metadata such as `mobile-ui.json`. Your project may use Godot to produce that file, but the doctor reads the artifact. |
| `godot-pack-mod-doctor` | No | Reads pack, DLC, mod, or patch manifests. |
| `godot-release-dashboard-kit` | No | Builds workflow-grouped static HTML dashboards from existing toolkit reports and visual artifacts, with optional previous-run comparison cards. |
| `godot-runtime-telemetry-lab` | No | Reads telemetry files emitted by your own runtime or scenario runs, including normalized Godot `Performance` monitor CSV/JSON. |
| `godot-save-schema-guard` | No | Reads save fixtures, schemas, and migration command metadata; writes generated or migrated fixtures only when requested. |
| `godot-scenario-report-kit` | No | Reads scenario manifests, JSON results, JUnit XML, and result artifacts from your own test runner. |
| `godot-scene-signal-auditor` | No | Statically reads scenes, scripts, signal connections, and autoload usage. |
| `godot-visual-smoke-test-kit` | No for compare/report commands | Screenshot comparison and approval use existing PNGs. If you choose to generate fresh screenshots as part of the same workflow, that capture step can use your installed Godot executable. |
| `gdscript-api-comment-coverage` | No | Statically reads GDScript APIs and comments. |
| `pixel-space-asset-toolkit` | No | Generates, previews, and compares deterministic pixel-art assets with Python image tooling. |

## What Goes Into The Shipped Game?

Usually nothing.

A normal setup looks like this:

- Install one or more toolkit packages in a developer environment or CI runner.
- Point the command at a project directory or report artifact.
- Store the output under `reports/`, upload it from CI, or use it during review.
- Build and ship the Godot project the same way you already do.

The toolkit can help you decide whether a build is ready, but it does not have
to travel with the build.
