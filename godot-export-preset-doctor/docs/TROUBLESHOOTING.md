# Troubleshooting

## No Presets Found

Run the command from the Godot project root or pass the file directly:

```powershell
godot-export-doctor C:\Projects\MyGame\export_presets.cfg
```

## Credential False Positives

Use an environment-variable style value such as `$STORE_PASSWORD` or `${STORE_PASSWORD}`. Empty password fields are ignored.

## ABI Findings

If you configure `required_android_abis`, every listed ABI must be enabled. Without config, the tool only requires at least one enabled Android architecture.

## SARIF Upload

Use `--format sarif --output export-doctor.sarif`. The SARIF file is meant for code-scanning dashboards and CI artifacts.
