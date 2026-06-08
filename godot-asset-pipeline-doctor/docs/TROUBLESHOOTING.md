# Troubleshooting

## The Tool Reports Missing `.import` Files

Open the project in Godot and let it import the assets. If the files still do not exist, check whether generated import metadata is ignored by your repository policy.

## Pixel-Art Assets Report Mipmaps

Disable mipmap generation for crisp 2D assets unless the asset is intentionally used across many sizes or in a 3D context.

## Transparent Edge RGB Warnings Look Surprising

Many image editors preserve RGB values under fully transparent pixels. This is normal, but it can create fringe artifacts. Use a cleanup tool or enable alpha-border fixing.

## Large Texture Warnings Are Too Noisy

Use the `default` profile locally and the `android-mobile` profile for release branches, or use `--fail-on error` so large texture warnings do not fail the build.

## Full Project Scans Are Too Slow

Scan the smallest useful project root, or add excludes for generated asset folders and vendor addons:

```powershell
godot-asset-doctor . --exclude "assets/generated/**" --exclude "addons/vendor/**"
```

The scanner already skips common artifact folders such as `docs`, `logs`, and `test-results`.
