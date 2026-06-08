from __future__ import annotations

import tomllib
from pathlib import Path

from .models import SceneSpec, SmokeConfig, Viewport


def load_config(path: Path) -> SmokeConfig:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    settings = data.get("settings", {})
    viewports = {
        name: Viewport(name=name, width=int(values["width"]), height=int(values["height"]))
        for name, values in data.get("viewports", {}).items()
    }
    scenes = [
        SceneSpec(name=str(scene["name"]), path=str(scene["path"]), viewport=str(scene["viewport"]))
        for scene in data.get("scenes", [])
    ]
    return SmokeConfig(
        pixel_tolerance=int(settings.get("pixel_tolerance", 0)),
        max_changed_percent=float(settings.get("max_changed_percent", 0.0)),
        output_dir=str(settings.get("output_dir", "visual-smoke-output")),
        viewports=viewports,
        scenes=scenes,
    )
