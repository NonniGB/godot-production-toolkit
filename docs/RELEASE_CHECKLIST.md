# Release Checklist

## Pre-release verification

Run:

```powershell
python verify_tool_manifests.py
python verify_release_alignment.py
python -m unittest discover -s tests -v
```

Run every affected package test suite from its package directory.

Check:

- Root `pyproject.toml` version matches the suite tag you intend to create.
- `python verify_release_alignment.py` passes before tagging.
- `PROJECT_OVERVIEW.md` reflects current status.
- `project-metadata.json` reflects current tool count and output formats.
- Root and per-tool changelogs mention user-facing changes.
- Private project references, personal data, and credentials are absent from public docs and examples.

## Tagging

Use semantic versioning. For example:

```powershell
git tag v0.1.2
git push origin main --tags
```

## Post-release notes

Record:

- Release URL.
- CI run URL.
- PyPI package URLs and publish workflow run URLs.
- Issues or pull requests that should influence follow-up fixes.
- Documentation gaps discovered after release.

Current package URLs:

- [`godot-asset-pipeline-doctor`](https://pypi.org/project/godot-asset-pipeline-doctor/)
- [`godot-export-preset-doctor`](https://pypi.org/project/godot-export-preset-doctor/)
- [`godot-mobile-perf-doctor`](https://pypi.org/project/godot-mobile-perf-doctor/)
- [`godot-input-map-auditor`](https://pypi.org/project/godot-input-map-auditor/)
- [`godot-localization-qa-guard`](https://pypi.org/project/godot-localization-qa-guard/)
- [`godot-save-schema-guard`](https://pypi.org/project/godot-save-schema-guard/)
- [`godot-scene-signal-auditor`](https://pypi.org/project/godot-scene-signal-auditor/)
- [`godot-visual-smoke-test-kit`](https://pypi.org/project/godot-visual-smoke-test-kit/)
- [`gdscript-api-comment-coverage`](https://pypi.org/project/gdscript-api-comment-coverage/)
- [`pixel-space-asset-toolkit`](https://pypi.org/project/pixel-space-asset-toolkit/)

## Package patch releases

Standalone package versions can move independently from the root suite version. When a tool changes:

- bump that tool's `pyproject.toml`, `__version__`, CLI `--version`, and changelog;
- update docs or examples that describe the changed behavior;
- run the affected package tests plus root release-alignment checks;
- publish the changed package to PyPI after `main` CI is green;
- verify PyPI shows the new package version.
