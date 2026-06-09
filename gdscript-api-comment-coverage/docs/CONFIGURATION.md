# Thresholds

Thresholds are passed as CLI flags:

```powershell
gdscript-api-coverage . --min-all 80 --min-public-func 90 --min-signal 100
```

Supported categories:

- `all`
- `class`
- `signal`
- `exported_property`
- `public_func`
- `constant`

Use `--fail-on none` to collect a report without failing CI.

When a threshold fails, text and JSON reports include a readable explanation for
the affected category. JSON also includes stable rule ids so scripts can track
the same threshold over time.
