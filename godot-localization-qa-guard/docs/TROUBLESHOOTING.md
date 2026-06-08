# Troubleshooting

## CSV Header Error

Godot-style CSV files should begin with:

```csv
keys,en,fr
```

## Too Many Unused Keys

Only enable `--scan-scripts` and `--scan-scenes` when your project consistently uses key-like strings. Some keys are loaded dynamically and may need to be ignored in a future config file.

## Placeholder False Positives

The first release compares simple brace and percent placeholders. If your project uses a different formatting convention, run with `--fail-on error` so warnings do not block adoption.
