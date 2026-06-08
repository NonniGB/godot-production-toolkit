from __future__ import annotations

import os
from pathlib import Path

from .gdscript_parser import parse_gdscript_signals
from .models import ParsedScene, ParsedScript
from .scene_parser import parse_scene

EXCLUDED_DIRS = {".git", ".godot", ".venv", "__pycache__", "build", "dist", "logs"}


def scan_project(root: Path, *, autoloads: set[str]) -> tuple[list[ParsedScene], dict[str, ParsedScript]]:
    root = root.resolve()
    scenes: list[ParsedScene] = []
    scripts: dict[str, ParsedScript] = {}
    for current, dirs, files in os.walk(root):
        dirs[:] = [directory for directory in dirs if directory not in EXCLUDED_DIRS]
        current_path = Path(current)
        for filename in files:
            path = current_path / filename
            relative = path.relative_to(root)
            if filename.endswith(".tscn"):
                scenes.append(parse_scene(relative, path.read_text(encoding="utf-8")))
            elif filename.endswith(".gd"):
                parsed = parse_gdscript_signals(relative, path.read_text(encoding="utf-8"), autoloads=autoloads)
                scripts[relative.as_posix()] = parsed
    return sorted(scenes, key=lambda scene: scene.path.as_posix()), scripts
