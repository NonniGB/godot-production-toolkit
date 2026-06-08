# CI Usage

## GitHub Actions

```yaml
name: Asset Checks

on:
  pull_request:
  push:

jobs:
  asset-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install godot-asset-pipeline-doctor
      - run: godot-asset-doctor . --profile pixel-2d --fail-on warning
```

## JSON Report

```powershell
godot-asset-doctor . --format json --output asset-report.json --fail-on warning
```

Keep JSON artifacts private if local paths reveal project or asset names you do not want to publish.

