# Baseline Workflow

Compare:

```powershell
godot-visual-smoke compare baselines\menu.png current\menu.png --diff diffs\menu.png
```

Approve:

```powershell
godot-visual-smoke approve current\menu.png baselines\menu.png
```

Review diffs before approving. A passing unit test only proves the image comparison logic, not that a UI change is desirable.
