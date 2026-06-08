from __future__ import annotations

from pathlib import Path


def build_godot_command(
    *,
    godot: Path,
    project: Path,
    scene: str,
    width: int,
    height: int,
    output: Path,
) -> list[str]:
    return [
        str(godot),
        "--headless",
        "--path",
        str(project),
        "--resolution",
        f"{width}x{height}",
        "--script",
        "res://addons/visual_smoke/capture_scene.gd",
        "--scene",
        scene,
        "--output",
        str(output),
    ]
