# Texture Guidance

Run:

```powershell
godot-mobile-perf-doctor . --max-texture-dimension 2048
```

Large source textures can increase memory, upload time, and battery cost. For pixel-art games, oversized source art is often accidental.
