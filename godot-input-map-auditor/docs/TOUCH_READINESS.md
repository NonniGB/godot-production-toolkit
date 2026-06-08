# Touch Readiness

For touch-first projects, run:

```powershell
godot-input-audit . --require touch
```

For projects that need both desktop and mobile coverage:

```powershell
godot-input-audit . --require keyboard,touch
```

Use this as an early signal, not as the only UX check. Some touch input is scene-specific and may not be represented in the project input map.
