# Godot Capture Integration

The first release does not ship a Godot addon. It provides deterministic command planning so teams can wire their own capture script:

```powershell
godot-visual-smoke plan visual-smoke.toml --project . --godot C:\Tools\Godot.exe
```

The planned command expects a helper script at:

```text
res://addons/visual_smoke/capture_scene.gd
```

A later release can include that helper once the command contract has been tested across Godot versions.
