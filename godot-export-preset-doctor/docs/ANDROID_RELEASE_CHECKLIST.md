# Android Release Checklist

Run:

```powershell
godot-export-doctor . --platform Android
```

Review these areas before uploading a build:

- `package/unique_name` is a stable dotted package id.
- `version/code` is at least `1` and increases for each store upload.
- `version/name` is set for human-readable release tracking.
- At least one Android ABI is enabled. `arm64-v8a` is usually required for modern releases.
- Launcher icons are configured.
- Release-like presets do not enable debug export options.
- Keystore passwords come from environment variables or CI secrets, not committed text.

For CI, pin required ABIs with a CLI flag:

```powershell
godot-export-doctor . --platform Android --required-android-abi arm64-v8a --fail-on warning
```

Or keep the same rule in `.godot-export-doctor.toml`:

```toml
platform = "Android"
required_android_abis = ["arm64-v8a"]
fail_on = "warning"
```
