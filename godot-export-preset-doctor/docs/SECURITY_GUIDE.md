# Security Guide

Godot export presets can contain signing-related paths and password fields. Avoid committing real secrets.

Prefer:

```text
keystore/release_password="$GODOT_ANDROID_KEYSTORE_PASSWORD"
```

Avoid:

```text
keystore/release_password="actual-password"
```

Also check `.gitignore` for local signing material:

```gitignore
*.keystore
*.jks
*.p12
```

The tool redacts obvious credential values, but reports may still include preset
names, local paths, exported file names, and artifact-relative paths. Review
exported-folder and exported-file-list reports before sharing them publicly.

## Placeholders

Some teams keep harmless placeholders in `export_presets.cfg` and inject the real values in CI. Configure these explicitly so the report stays useful:

```toml
allowed_secret_patterns = ["<.+>", "set-in-ci"]
```

Keep the patterns narrow. This option is for placeholders, not for allowing real secrets in source control.
