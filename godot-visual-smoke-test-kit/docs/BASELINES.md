# Baseline Workflow

Compare:

```powershell
godot-visual-smoke compare baselines\menu.png current\menu.png --diff diffs\menu.png --format json --output visual-report.json
```

Upload or open the current screenshot, diff image, and JSON report before
deciding whether the change is expected. If the baseline or current screenshot
is missing, `compare` reports a normal finding that names the missing path.

Approve:

```powershell
godot-visual-smoke approve current\menu.png baselines\menu.png
```

Review diffs before approving. A passing unit test only proves the image comparison logic, not that a UI change is desirable.
