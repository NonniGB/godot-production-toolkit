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

The tool redacts obvious credential values, but reports may still include preset names and local paths.
