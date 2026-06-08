# Automation Usage

Read `tool-manifest.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code behavior.

Automation-friendly generation examples:

```powershell
pixel-space-assets starfield --width 1080 --height 1920 --seed 42 --stars 900 --output generated/starfield.png --manifest generated/starfield.json --format json
pixel-space-assets asteroid-hex --material ferric --count 32 --size 64 --seed 7 --output generated/ferric --format json
```

Use fixed seeds and commit manifests if generated assets should be reproducible. Review generated assets before publishing if they were derived from private inputs.
