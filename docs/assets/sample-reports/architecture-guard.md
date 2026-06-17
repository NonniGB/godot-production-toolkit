# Godot GDScript Architecture Guard

- Scripts: 3
- Modules: 3
- Dependencies: 1
- Owner summaries: 3
- Hotspots: 2
- Possible unused scripts: 2
- Errors: 1
- Warnings: 0

| Severity | Rule | Path | Message | Suggestion |
|---|---|---|---|---|
| error | module_boundary_violation | scripts/ui/menu.gd | ui depends on gameplay, which is not allowed by policy. | Move shared code to an allowed module or update the policy if the dependency is intentional. |

## Module Ownership Summary

| Module | Scripts | In | Out | Autoload refs | Boundary violations | Autoload violations | Unmatched paths | Hotspots | Possible unused |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gameplay | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 0 |
| shared | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| ui | 1 | 0 | 1 | 1 | 1 | 0 | 0 | 1 | 1 |

## Dependency Hotspots

| Score | Path | Module | Incoming | Outgoing | Autoload refs |
|---:|---|---|---:|---:|---:|
| 3 | scripts/gameplay/inventory.gd | gameplay | 1 | 0 | 1 |
| 2 | scripts/ui/menu.gd | ui | 0 | 1 | 1 |

## Possible Unused Scripts

| Path | Module | Reason |
|---|---|---|
| scripts/shared/formatting.gd | shared | No res:// reference or class_name declaration was found. |
| scripts/ui/menu.gd | ui | No res:// reference or class_name declaration was found. |
