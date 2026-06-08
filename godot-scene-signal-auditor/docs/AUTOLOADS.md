# Autoload Signal Usage

Flag configured autoload signal connections:

```powershell
godot-signal-audit . --autoload EventBus,SignalBus
```

This does not mean event buses are wrong. It makes coupling visible so large projects can review where global signal routes are used.
