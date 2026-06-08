# Configuration

Create `.godot-export-doctor.toml` in the Godot project root:

```toml
format = "text"
fail_on = "warning"
platform = "Android"
required_android_abis = ["arm64-v8a"]
allowed_secret_patterns = ["<.+>", "CI_.+"]
```

CLI flags override config values:

```powershell
godot-export-doctor . --format json --output report.json --fail-on error
```

Fields:

- `format`: `text`, `json`, or `sarif`.
- `fail_on`: `warning`, `error`, or `none`.
- `platform`: optional platform filter, for example `Android`.
- `required_android_abis`: optional list of ABI option keys that must be enabled.
- `allowed_secret_patterns`: optional regular expressions for placeholder values that are safe to keep in `export_presets.cfg`.

Use `allowed_secret_patterns` for deliberate placeholders only:

```toml
allowed_secret_patterns = [
  "<.+>",
  "set-in-ci",
]
```

Do not use it to hide real passwords, tokens, signing keys, or local machine-specific secrets.
