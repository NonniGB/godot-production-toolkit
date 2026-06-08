# Generated API Index

Generate a Markdown index:

```powershell
gdscript-api-coverage . --write-docs docs\API_INDEX.md
```

The output is a table:

```markdown
| Kind | Name | Location | Documented |
|---|---|---:|:---:|
| class | Inventory | scripts/inventory.gd:2 | yes |
```

Commit the generated index if you want code reviews to show API changes.
