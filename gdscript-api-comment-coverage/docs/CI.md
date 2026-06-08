# CI Usage

```yaml
- name: Install API coverage tool
  run: python -m pip install gdscript-api-comment-coverage

- name: Check public API docs
  run: gdscript-api-coverage . --min-all 80 --min-public-func 80 --write-docs docs/API_INDEX.md
```

For early adoption, generate docs without failing:

```powershell
gdscript-api-coverage . --write-docs docs\API_INDEX.md --fail-on none
```
