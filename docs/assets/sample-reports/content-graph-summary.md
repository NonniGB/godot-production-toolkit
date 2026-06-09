# Godot Content Graph Doctor

- Collections: 2
- Records: 5
- Errors: 1
- Warnings: 1

| Collection | Records | Unique IDs | References |
|---|---:|---:|---:|
| items | 3 | 3 | 0 |
| recipes | 2 | 2 | 2 |

## Findings

| Severity | Rule | Target | Message |
|---|---|---|---|
| error | missing_reference | recipes.repair_kit | recipes.repair_kit references items.missing_gel, but that id does not exist. |
| warning | numeric_outlier | items.repair_kit | items.repair_kit has value=120, which is at least 8x the median 12. |
