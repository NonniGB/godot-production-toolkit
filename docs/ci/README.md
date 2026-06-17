# Copy-Paste CI Recipes

These files are example GitHub Actions workflows for Godot projects that use
Godot Production Toolkit packages. They live under `docs/ci`, so they are
documentation examples only. To use one, copy it into your game's
`.github/workflows/` directory and adjust the commented paths, secrets, and
artifact names for your project.

The examples assume a Godot 4 project at the repository root. If your game
lives in a subfolder, change `GODOT_PROJECT_DIR` and any report paths that point
at project-owned files.

## Recipes

- `android-export.yml`: checks Android export presets, builds an Android
  release export, and uploads the APK/AAB plus export reports.
- `html5-export.yml`: checks the Web export preset, builds an HTML5 export, and
  uploads the static web build.
- `mobile-ui-and-localization.yml`: runs touch-layout metadata checks,
  localization stress-pack output, and localization QA together.
- `runtime-telemetry-budget.yml`: turns project-owned runtime telemetry samples
  into budgeted Markdown, JSON, and HTML reports.
- `content-pack-validation.yml`: checks content graph data and pack/mod
  manifests before publishing content packs, DLC, or patches.
- `release-dashboard-artifact.yml`: collects existing report artifacts and builds
  one static dashboard HTML file.

## Before Copying

- Replace placeholder Godot export preset names with your preset names from
  `export_presets.cfg`.
- Replace placeholder metadata/report paths with files your project actually
  writes.
- Add required repository secrets before enabling signing or deploy steps.
- Keep generated reports under a stable directory such as `reports/` so they can
  be uploaded as workflow artifacts.
