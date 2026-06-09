# Tiny Architecture Project

This fixture has one deliberate module boundary violation: the UI script preloads
a gameplay script even though the policy only allows UI to depend on shared code.

```powershell
godot-architecture-guard . --config architecture-guard.toml
```

