# Rule Reference

## Generic Rules

- `missing_export_presets`: no `export_presets.cfg` found.
- `missing_preset_name`: preset has no name.
- `missing_platform`: preset has no platform.
- `missing_export_path`: preset has no export path.

## Android Rules

- `android_package_id_missing`: `package/unique_name` is empty.
- `android_package_id_invalid`: package id is not dotted identifier text.
- `android_package_id_placeholder`: package id still looks like a placeholder.
- `android_version_missing`: `version/code` or `version/name` is missing.
- `android_abi_missing`: no Android architecture is enabled.
- `android_required_abi_missing`: configured required ABI is disabled.
- `android_launcher_icons_missing`: launcher icon options are absent or empty.

## Release And Security Rules

- `debug_option_enabled_in_release`: a release-like preset has a truthy debug option.
- `hardcoded_credential_value`: a password, token, or secret option has a literal value. Values matching configured `allowed_secret_patterns` are treated as known placeholders.
- `hardcoded_keystore_path`: a keystore-like option points to a local path.

Credential findings redact values in every report format.
