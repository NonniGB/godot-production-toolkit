# Tiny Architecture Project

This fixture has one deliberate module boundary violation: the UI script preloads
a gameplay script even though the policy only allows UI to depend on shared
code. It is also small enough to show the advisory high fan-in/fan-out and
possible unused script sections in Markdown output.

```powershell
godot-architecture-guard . --config architecture-guard.toml
godot-architecture-guard . --config architecture-guard.toml --format markdown --fail-on none
```
