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

For generated sprite sets, compare two directories:

```powershell
pixel-space-assets compare-dir baseline\ferric generated\ferric --diff-output-dir reports\ferric_diffs --fail-on-diff --format json
```

Directory comparison preserves relative paths in the diff output and reports
changed, added, removed, and unchanged PNG files.

When a generator writes a manifest, compare through the manifests instead of
scanning every PNG in the folder:

```powershell
pixel-space-assets compare-manifest baseline\ferric\manifest.json generated\ferric\manifest.json --diff-output-dir reports\ferric_manifest_diffs --fail-on-diff --format json
```

Manifest comparison uses the files listed by each manifest and also reports
top-level manifest field changes such as seed, size, count, or material drift.
