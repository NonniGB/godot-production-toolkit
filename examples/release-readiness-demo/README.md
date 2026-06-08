# Release Readiness Demo

This tiny Godot fixture intentionally contains common release risks so the toolkit can show useful output quickly.

Run from the repository root after installing the local packages:

```powershell
godot-project-doctor run examples\release-readiness-demo\godot-project-doctor.toml --format markdown --output docs\assets\sample-reports\release-readiness-summary.md
godot-project-doctor summarize docs\assets\sample-reports --format html --output docs\assets\sample-reports\release-readiness-summary.html
```

The fixture includes:

- Android export preset settings that are incomplete for release.
- Pixel-art import settings with mipmaps/filtering enabled.
- Input actions with incomplete touch/controller coverage.
- Mobile rendering settings that are not ideal for a small 2D project.

The project is synthetic and intentionally broken. It is safe to use in docs, examples, and CI demonstrations.
