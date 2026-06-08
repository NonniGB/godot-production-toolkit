# Release Checklist

## Pre-release verification

Run:

```powershell
python verify_tool_manifests.py
python -m unittest discover -s tests -v
```

Run every affected package test suite from its package directory.

Check:

- `PROJECT_OVERVIEW.md` reflects current status.
- `project-metadata.json` reflects current tool count and output formats.
- Root and per-tool changelogs mention user-facing changes.
- Private project references, personal data, and credentials are absent from public docs and examples.

## Tagging

Use semantic versioning. For the first public release:

```powershell
git tag v0.1.0
git push origin main --tags
```

## Post-release notes

Record:

- Release URL.
- CI run URL.
- PyPI package URLs and publish workflow run URLs.
- Issues or pull requests that should influence follow-up fixes.
- Documentation gaps discovered after release.

Current `0.1.0` package URLs:

- [`godot-asset-pipeline-doctor`](https://pypi.org/project/godot-asset-pipeline-doctor/)
- [`godot-export-preset-doctor`](https://pypi.org/project/godot-export-preset-doctor/)
- [`godot-mobile-perf-doctor`](https://pypi.org/project/godot-mobile-perf-doctor/)
