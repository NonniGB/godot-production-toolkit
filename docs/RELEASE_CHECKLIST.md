# Release Checklist

## Pre-release verification

Run:

```powershell
python verify_agent_interfaces.py
python -m unittest discover -s tests -v
```

Run every affected package test suite from its package directory.

Check:

- `AI_REVIEW_PACKAGE.md` reflects current status.
- `oss-review-evidence.json` reflects current tool count and output formats.
- Root and per-tool changelogs mention user-facing changes.
- Private-project references are absent from public docs and examples.

## Tagging

Use semantic versioning. For the first public release:

```powershell
git tag v0.1.0
git push origin main --tags
```

## Post-release evidence

Record:

- Release URL.
- CI run URL.
- PyPI package URLs when published.
- External issues, pull requests, or usage links.
- Community posts and responses.
