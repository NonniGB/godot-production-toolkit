# Tiny Architecture Project

This fixture has one deliberate module boundary violation: the UI script preloads
a gameplay script even though the policy only allows UI to depend on shared
code. It is also small enough to show the advisory high fan-in/fan-out and
possible unused script/resource sections in Markdown output. The data folder has
one referenced JSON file and one stale JSON file so the resource review has a
small, readable example.
The policy also shows `[ignore] paths` for generated folders; those patterns are
useful when code generators or imported addons would otherwise dominate owner
and hotspot summaries.

```powershell
godot-architecture-guard . --config architecture-guard.toml
godot-architecture-guard . --config architecture-guard.toml --format markdown --fail-on none
```
