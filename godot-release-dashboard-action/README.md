# Godot Release Dashboard Action

This composite action builds a static dashboard from existing Godot Production
Toolkit reports and uploads it as a GitHub Actions artifact. Use it after jobs
that already wrote JSON, Markdown, HTML, SVG, or PNG reports.

## Usage

```yaml
name: Release evidence dashboard

on:
  workflow_dispatch:
  pull_request:

jobs:
  dashboard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download toolkit reports
        uses: actions/download-artifact@v4
        with:
          pattern: "*-reports"
          path: reports/release-evidence
          merge-multiple: true

      - uses: NonniGB/godot-production-toolkit/godot-release-dashboard-action@main
        with:
          reports-dir: reports/release-evidence
          dashboard-dir: reports/release-dashboard
          dashboard-title: Godot Release Evidence
          artifact-name: release-dashboard
```

For long-lived production workflows, pin the action to a tag or commit once you
have tested it in your project.

## Local Reproduction

Run the same dashboard command locally before pushing:

```powershell
python -m pip install godot-release-dashboard-kit
godot-release-dashboard build reports/release-evidence --title "Godot Release Evidence" --output reports/release-dashboard/index.html
godot-release-dashboard build reports/release-evidence --title "Godot Release Evidence" --format json --output reports/release-dashboard/dashboard.json
```

Add `--previous-reports-dir reports/previous-release-evidence` when you want the
dashboard to include readiness trend cards.

## Inputs

- `reports-dir`: folder containing report files from earlier jobs.
- `dashboard-dir`: folder where `index.html` and `dashboard.json` are written.
- `dashboard-title`: title shown in the generated dashboard.
- `dashboard-description`: optional description under the title.
- `project`: optional project name in dashboard metadata.
- `previous-reports-dir`: optional folder used for trend cards.
- `artifact-name`: uploaded artifact name.
- `upload-artifact`: set to `false` to skip the upload step.
- `python-version`: Python version for package installation.
- `tool-packages`: package install list, normally `godot-release-dashboard-kit`.
- `extra-args`: optional extra arguments passed to both dashboard builds.

## Outputs

- `dashboard-html`: path to the generated HTML dashboard.
- `dashboard-json`: path to the generated JSON dashboard summary.

## Artifacts

By default, the action uploads the dashboard directory as `release-dashboard`.
That folder contains:

- `index.html`: a static dashboard for reviewers.
- `dashboard.json`: a machine-readable summary for follow-up jobs.

The action does not run Godot and does not collect reports by itself. It only
builds the dashboard from files your workflow has already generated or
downloaded.
