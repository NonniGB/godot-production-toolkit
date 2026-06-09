# Audio Asset Guide

Use the `audio-mobile` profile when reviewing sound effects, music, ambience, or
narration for mobile and download-size risk.

```powershell
godot-asset-doctor . --profile audio-mobile --format json --output reports\audio-assets.json
```

The scanner checks `.wav`, `.ogg`, and `.mp3` files. WAV files also report
duration, sample rate, and channel count when the header is readable.

## Practical Checks

- Keep WAV files for short effects where editability or low latency matters.
- Review large WAV files before shipping them in mobile or web builds.
- Use compression or streaming import settings for long music, ambience, and narration.
- Keep `.import` metadata committed so CI can confirm Godot has seen the assets.

## Useful Thresholds

```powershell
godot-asset-doctor . --profile audio-mobile --large-audio-mb 6 --max-audio-duration-seconds 90
```

Configure the same values in `.godot-asset-doctor.toml`:

```toml
profile = "audio-mobile"
large_audio_mb = 6
max_audio_duration_seconds = 90
```
