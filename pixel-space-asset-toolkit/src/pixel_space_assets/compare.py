from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image


@dataclass(frozen=True)
class ImageComparison:
    baseline: Path
    current: Path
    width: int
    height: int
    different_pixels: int
    total_pixels: int
    percent_different: float
    size_mismatch: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "baseline": str(self.baseline),
            "current": str(self.current),
            "width": self.width,
            "height": self.height,
            "different_pixels": self.different_pixels,
            "total_pixels": self.total_pixels,
            "percent_different": self.percent_different,
            "size_mismatch": self.size_mismatch,
        }


def compare_images(
    baseline_path: Path,
    current_path: Path,
    diff_output: Path,
    *,
    tolerance: int = 0,
) -> ImageComparison:
    with Image.open(baseline_path) as baseline_raw, Image.open(current_path) as current_raw:
        baseline = baseline_raw.convert("RGBA")
        current = current_raw.convert("RGBA")

    width = max(baseline.width, current.width)
    height = max(baseline.height, current.height)
    baseline_canvas = _canvas(baseline, width, height)
    current_canvas = _canvas(current, width, height)
    diff = Image.new("RGBA", (width, height), (8, 10, 18, 255))

    different = 0
    for y in range(height):
        for x in range(width):
            before = baseline_canvas.getpixel((x, y))
            after = current_canvas.getpixel((x, y))
            if _pixel_distance(before, after) > tolerance:
                different += 1
                diff.putpixel((x, y), (255, 74, 92, 255))
            else:
                diff.putpixel((x, y), _muted_pixel(after))

    diff_output.parent.mkdir(parents=True, exist_ok=True)
    diff.save(diff_output)
    total = width * height
    return ImageComparison(
        baseline=baseline_path,
        current=current_path,
        width=width,
        height=height,
        different_pixels=different,
        total_pixels=total,
        percent_different=(different / total * 100.0) if total else 0.0,
        size_mismatch=baseline.size != current.size,
    )


def _canvas(image: Image.Image, width: int, height: int) -> Image.Image:
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas.alpha_composite(image, (0, 0))
    return canvas


def _pixel_distance(left: tuple[int, int, int, int], right: tuple[int, int, int, int]) -> int:
    return max(abs(left[index] - right[index]) for index in range(4))


def _muted_pixel(pixel: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    alpha = pixel[3]
    if alpha == 0:
        return (8, 10, 18, 255)
    tone = int((pixel[0] + pixel[1] + pixel[2]) / 3)
    muted = max(24, min(120, tone))
    return (muted, muted, muted, 255)
