# ADB Mode

The first release parses a summary text file:

```powershell
godot-mobile-perf-doctor . --adb-summary adb-summary.txt
```

Expected shape:

```text
Device: Pixel 8
Android: 15
Total frames rendered: 120
Janky frames: 6 (5.0%)
```

Future releases can collect this directly through `adb`.
