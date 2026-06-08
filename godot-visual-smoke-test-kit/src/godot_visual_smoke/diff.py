from __future__ import annotations

from pathlib import Path

from PIL import Image

from .models import DiffResult


def compare_images(
    baseline: Path,
    current: Path,
    *,
    diff_path: Path | None = None,
    pixel_tolerance: int = 0,
    max_changed_percent: float = 0.0,
) -> DiffResult:
    with Image.open(baseline) as baseline_image, Image.open(current) as current_image:
        base = baseline_image.convert("RGBA")
        curr = current_image.convert("RGBA")
        if base.size != curr.size:
            width, height = curr.size
            total = width * height
            return DiffResult(
                str(baseline),
                str(current),
                width,
                height,
                total,
                total,
                100.0,
                255,
                False,
                reason=f"Image size differs: baseline {base.size}, current {curr.size}.",
            )

        width, height = base.size
        diff_image = Image.new("RGBA", base.size, (0, 0, 0, 0))
        changed = 0
        max_delta = 0
        for y in range(height):
            for x in range(width):
                base_pixel = base.getpixel((x, y))
                curr_pixel = curr.getpixel((x, y))
                delta = max(abs(base_pixel[index] - curr_pixel[index]) for index in range(4))
                max_delta = max(max_delta, delta)
                if delta > pixel_tolerance:
                    changed += 1
                    diff_image.putpixel((x, y), (255, 0, 0, 255))

        total = width * height
        changed_percent = round((changed / total) * 100, 4) if total else 0.0
        passed = changed_percent <= max_changed_percent
        if diff_path:
            diff_path.parent.mkdir(parents=True, exist_ok=True)
            diff_image.save(diff_path)
        return DiffResult(
            str(baseline),
            str(current),
            width,
            height,
            changed,
            total,
            changed_percent,
            max_delta,
            passed,
        )
