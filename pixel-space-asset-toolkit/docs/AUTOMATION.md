# Script And CI Usage

Read `tool-manifest.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code behavior.

Script-friendly generation examples:

```powershell
pixel-space-assets starfield --width 1080 --height 1920 --seed 42 --stars 900 --output generated/starfield.png --manifest generated/starfield.json --format json
pixel-space-assets asteroid-hex --material ferric --count 32 --size 64 --seed 7 --output generated/ferric --format json
pixel-space-assets compare-manifest baseline/ferric/manifest.json generated/ferric/manifest.json --diff-output-dir reports/ferric-manifest-diffs --fail-on-diff --format json
```

Use fixed seeds and commit manifests if generated assets should be reproducible.
Manifest comparison is useful when CI should catch seed or generator-parameter
drift as well as changed PNG pixels. Review generated assets before publishing
if they were derived from private inputs.
