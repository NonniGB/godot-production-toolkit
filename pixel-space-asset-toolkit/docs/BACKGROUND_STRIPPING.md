# Background Stripping

Remove a flat corner-color background:

```powershell
pixel-space-assets strip-background input.png --output cleaned.png --tolerance 4
```

The corner pixel is treated as the background color. This is useful for simple generated or exported sprites with a solid matte.
