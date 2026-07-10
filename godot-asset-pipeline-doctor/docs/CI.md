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
      - uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065
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
