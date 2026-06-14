from __future__ import annotations

from dataclasses import dataclass
import json
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


@dataclass(frozen=True)
class DirectoryComparison:
    baseline_dir: Path
    current_dir: Path
    diff_output_dir: Path
    total_files: int
    changed_files: int
    added_files: int
    removed_files: int
    unchanged_files: int
    different_pixels: int
    entries: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "baseline_dir": str(self.baseline_dir),
            "current_dir": str(self.current_dir),
            "diff_output_dir": str(self.diff_output_dir),
            "total_files": self.total_files,
            "changed_files": self.changed_files,
            "added_files": self.added_files,
            "removed_files": self.removed_files,
            "unchanged_files": self.unchanged_files,
            "different_pixels": self.different_pixels,
            "entries": self.entries,
        }


@dataclass(frozen=True)
class ManifestComparison:
    baseline_manifest: Path
    current_manifest: Path
    diff_output_dir: Path
    total_files: int
    changed_files: int
    added_files: int
    removed_files: int
    unchanged_files: int
    different_pixels: int
    manifest_changes: list[dict[str, Any]]
    entries: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "baseline_manifest": str(self.baseline_manifest),
            "current_manifest": str(self.current_manifest),
            "diff_output_dir": str(self.diff_output_dir),
            "total_files": self.total_files,
            "changed_files": self.changed_files,
            "added_files": self.added_files,
            "removed_files": self.removed_files,
            "unchanged_files": self.unchanged_files,
            "different_pixels": self.different_pixels,
            "manifest_changes": self.manifest_changes,
            "entries": self.entries,
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


def compare_manifests(
    baseline_manifest: Path,
    current_manifest: Path,
    diff_output_dir: Path,
    *,
    tolerance: int = 0,
) -> ManifestComparison:
    baseline_files, baseline_metadata = _manifest_png_files(baseline_manifest)
    current_files, current_metadata = _manifest_png_files(current_manifest)
    relative_paths = sorted(set(baseline_files) | set(current_files))
    entries: list[dict[str, Any]] = []
    diff_output_dir.mkdir(parents=True, exist_ok=True)

    for relative_path in relative_paths:
        baseline_path = baseline_files.get(relative_path)
        current_path = current_files.get(relative_path)
        diff_path = diff_output_dir / relative_path
        if baseline_path and current_path:
            comparison = compare_images(
                baseline_path,
                current_path,
                diff_path,
                tolerance=tolerance,
            )
            status = "changed" if comparison.different_pixels or comparison.size_mismatch else "unchanged"
            entries.append(
                {
                    "path": relative_path.as_posix(),
                    "status": status,
                    "diff": str(diff_path),
                    **comparison.as_dict(),
                }
            )
            continue
        source = baseline_path or current_path
        if source is None:
            continue
        different_pixels = _write_missing_diff(source, diff_path)
        entries.append(
            {
                "path": relative_path.as_posix(),
                "status": "removed" if baseline_path else "added",
                "baseline": str(baseline_path) if baseline_path else None,
                "current": str(current_path) if current_path else None,
                "diff": str(diff_path),
                "different_pixels": different_pixels,
            }
        )

    return ManifestComparison(
        baseline_manifest=baseline_manifest,
        current_manifest=current_manifest,
        diff_output_dir=diff_output_dir,
        total_files=len(entries),
        changed_files=sum(1 for entry in entries if entry["status"] == "changed"),
        added_files=sum(1 for entry in entries if entry["status"] == "added"),
        removed_files=sum(1 for entry in entries if entry["status"] == "removed"),
        unchanged_files=sum(1 for entry in entries if entry["status"] == "unchanged"),
        different_pixels=sum(int(entry["different_pixels"]) for entry in entries),
        manifest_changes=_manifest_changes(baseline_metadata, current_metadata),
        entries=entries,
    )


def compare_directories(
    baseline_dir: Path,
    current_dir: Path,
    diff_output_dir: Path,
    *,
    tolerance: int = 0,
) -> DirectoryComparison:
    baseline_files = _png_files(baseline_dir)
    current_files = _png_files(current_dir)
    relative_paths = sorted(set(baseline_files) | set(current_files))
    entries: list[dict[str, Any]] = []
    diff_output_dir.mkdir(parents=True, exist_ok=True)

    for relative_path in relative_paths:
        baseline_path = baseline_files.get(relative_path)
        current_path = current_files.get(relative_path)
        diff_path = diff_output_dir / relative_path
        if baseline_path and current_path:
            comparison = compare_images(
                baseline_path,
                current_path,
                diff_path,
                tolerance=tolerance,
            )
            status = "changed" if comparison.different_pixels or comparison.size_mismatch else "unchanged"
            entries.append(
                {
                    "path": relative_path.as_posix(),
                    "status": status,
                    "diff": str(diff_path),
                    **comparison.as_dict(),
                }
            )
            continue
        source = baseline_path or current_path
        if source is None:
            continue
        different_pixels = _write_missing_diff(source, diff_path)
        entries.append(
            {
                "path": relative_path.as_posix(),
                "status": "removed" if baseline_path else "added",
                "baseline": str(baseline_path) if baseline_path else None,
                "current": str(current_path) if current_path else None,
                "diff": str(diff_path),
                "different_pixels": different_pixels,
            }
        )

    return DirectoryComparison(
        baseline_dir=baseline_dir,
        current_dir=current_dir,
        diff_output_dir=diff_output_dir,
        total_files=len(entries),
        changed_files=sum(1 for entry in entries if entry["status"] == "changed"),
        added_files=sum(1 for entry in entries if entry["status"] == "added"),
        removed_files=sum(1 for entry in entries if entry["status"] == "removed"),
        unchanged_files=sum(1 for entry in entries if entry["status"] == "unchanged"),
        different_pixels=sum(int(entry["different_pixels"]) for entry in entries),
        entries=entries,
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


def _png_files(root: Path) -> dict[Path, Path]:
    return {path.relative_to(root): path for path in sorted(root.rglob("*.png")) if path.is_file()}


def _manifest_png_files(manifest_path: Path) -> tuple[dict[Path, Path], dict[str, Any]]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("asset manifest must be a JSON object.")
    root = manifest_path.parent
    files: dict[Path, Path] = {}
    for entry in data.get("tiles", []):
        if not isinstance(entry, dict) or not entry.get("file"):
            continue
        relative_path = Path(str(entry["file"]))
        path = root / relative_path
        if path.exists():
            files[relative_path] = path
    output = data.get("output")
    if isinstance(output, str) and output.lower().endswith(".png"):
        relative_path = Path(output).name
        path = root / relative_path
        if path.exists():
            files[relative_path] = path
    metadata = {key: value for key, value in data.items() if key not in {"tiles", "output"}}
    return files, metadata


def _manifest_changes(left: dict[str, Any], right: dict[str, Any]) -> list[dict[str, Any]]:
    changes = []
    for key in sorted(set(left) | set(right)):
        if left.get(key) != right.get(key):
            changes.append({"field": key, "baseline": left.get(key), "current": right.get(key)})
    return changes


def _write_missing_diff(source: Path, diff_output: Path) -> int:
    with Image.open(source) as raw:
        image = raw.convert("RGBA")
    diff = Image.new("RGBA", image.size, (8, 10, 18, 255))
    different = 0
    for y in range(image.height):
        for x in range(image.width):
            pixel = image.getpixel((x, y))
            if pixel[3] > 0:
                different += 1
                diff.putpixel((x, y), (255, 74, 92, 255))
    diff_output.parent.mkdir(parents=True, exist_ok=True)
    diff.save(diff_output)
    return different
