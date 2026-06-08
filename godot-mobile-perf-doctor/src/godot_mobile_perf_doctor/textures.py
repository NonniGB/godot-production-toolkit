from __future__ import annotations

import os
from pathlib import Path

from PIL import Image

from .models import TextureInfo, TextureSummary

EXCLUDED_DIRS = {".git", ".godot", ".venv", "__pycache__", "build", "dist", "logs"}


def scan_textures(root: Path, *, max_dimension: int = 2048) -> TextureSummary:
    total = 0
    total_mb = 0.0
    large: list[TextureInfo] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [directory for directory in dirs if directory not in EXCLUDED_DIRS]
        current_path = Path(current)
        for filename in files:
            if not filename.lower().endswith(".png"):
                continue
            path = current_path / filename
            try:
                with Image.open(path) as image:
                    width, height = image.size
            except OSError:
                continue
            total += 1
            info = TextureInfo(path=path, width=width, height=height)
            total_mb += info.rgba_mb
            if max(width, height) > max_dimension:
                large.append(info)
    return TextureSummary(
        total_textures=total,
        large_textures=large,
        total_estimated_rgba_mb=round(total_mb, 2),
    )
