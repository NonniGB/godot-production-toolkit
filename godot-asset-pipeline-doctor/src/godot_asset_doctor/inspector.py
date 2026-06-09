from __future__ import annotations

from pathlib import Path
import wave

from PIL import Image

from godot_asset_doctor.models import AudioInfo, PngInfo


def inspect_png(path: Path) -> PngInfo:
    """Inspect PNG dimensions, alpha, palette size, and transparent RGB contamination."""
    with Image.open(path) as image:
        original_mode = image.mode
        rgba = image.convert("RGBA")
        width, height = rgba.size
        if hasattr(rgba, "get_flattened_data"):
            pixels = list(rgba.get_flattened_data())
        else:
            pixels = list(rgba.getdata())

    transparent_count = 0
    contaminated_count = 0
    unique_colors: set[tuple[int, int, int, int]] = set()

    for red, green, blue, alpha in pixels:
        unique_colors.add((red, green, blue, alpha))
        if alpha == 0:
            transparent_count += 1
            if red != 0 or green != 0 or blue != 0:
                contaminated_count += 1

    edge_contaminated_count = _count_contaminated_edge_pixels(rgba_pixels=pixels, width=width, height=height)
    has_alpha = any(alpha < 255 for _, _, _, alpha in pixels)

    return PngInfo(
        path=path,
        width=width,
        height=height,
        mode=original_mode,
        has_alpha=has_alpha,
        palette_color_count=len(unique_colors),
        transparent_pixel_count=transparent_count,
        contaminated_transparent_pixel_count=contaminated_count,
        contaminated_transparent_edge_pixel_count=edge_contaminated_count,
        estimated_rgba_bytes=width * height * 4,
    )


def inspect_audio(path: Path) -> AudioInfo:
    """Inspect audio file size and basic WAV metadata without decoding samples."""
    suffix = path.suffix.lower().lstrip(".")
    file_size = path.stat().st_size
    if suffix == "wav":
        try:
            with wave.open(str(path), "rb") as handle:
                frame_count = handle.getnframes()
                sample_rate = handle.getframerate()
                channels = handle.getnchannels()
            duration = frame_count / sample_rate if sample_rate else None
            return AudioInfo(
                path=path,
                format="wav",
                file_size_bytes=file_size,
                duration_seconds=duration,
                sample_rate_hz=sample_rate,
                channels=channels,
            )
        except (EOFError, OSError, wave.Error):
            return AudioInfo(path=path, format="wav", file_size_bytes=file_size)
    return AudioInfo(path=path, format=suffix or "unknown", file_size_bytes=file_size)


def _count_contaminated_edge_pixels(
    rgba_pixels: list[tuple[int, int, int, int]], width: int, height: int
) -> int:
    count = 0
    for y in range(height):
        for x in range(width):
            if x not in (0, width - 1) and y not in (0, height - 1):
                continue
            red, green, blue, alpha = rgba_pixels[y * width + x]
            if alpha == 0 and (red != 0 or green != 0 or blue != 0):
                count += 1
    return count
