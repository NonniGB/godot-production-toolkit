# Preview Sheets

```powershell
pixel-space-assets preview generated\ferric --columns 8 --cell-size 64 --output generated\ferric_preview.png
```

Preview sheets make it easier to review generated tiles in pull requests and release notes.

## PNG Comparison

```powershell
pixel-space-assets compare baseline.png current.png --diff-output generated\diff.png --format json
```

The diff image uses red pixels for changes and muted grayscale pixels for areas
that stayed the same. Use `--tolerance` when tiny channel differences are
expected, and `--fail-on-diff` when a CI job should fail on any changed pixel.
