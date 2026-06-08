from __future__ import annotations

import os
from pathlib import Path

from .models import ApiItem
from .parser import parse_gdscript

DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".godot",
    ".venv",
    "__pycache__",
    "addons/cache",
    "build",
    "dist",
    "logs",
}


def scan_project(project: Path, excludes: list[str] | None = None) -> list[ApiItem]:
    root = project.resolve()
    ignored = set(DEFAULT_EXCLUDED_DIRS)
    ignored.update(excludes or [])
    items: list[ApiItem] = []

    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        dirs[:] = [
            directory
            for directory in dirs
            if directory not in ignored and (current_path / directory).relative_to(root).as_posix() not in ignored
        ]
        for filename in files:
            if not filename.endswith(".gd"):
                continue
            path = current_path / filename
            relative_path = path.relative_to(root)
            if relative_path.as_posix() in ignored:
                continue
            items.extend(parse_gdscript(relative_path, path.read_text(encoding="utf-8")))
    return sorted(items, key=lambda item: (item.path, item.line, item.kind, item.name))
