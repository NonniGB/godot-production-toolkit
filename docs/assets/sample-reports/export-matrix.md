# Godot Export Matrix

- Presets: 2
- Platforms: 2
- Warnings: 1
- Errors: 0

| Preset | Platform | Runnable | Filter | Include | Exclude | Export path |
|---|---|---|---|---|---|---|
| Android Release | Android | False | all_resources | * |  |  |
| Desktop Debug | Windows Desktop | True | all_resources | res://debug/* |  | builds/desktop/game.exe |

## Findings

| Severity | Rule | Preset | Message |
|---|---|---|---|
| warning | `export_matrix_missing_platform` | Web | Expected platform 'Web' has no export preset. |
