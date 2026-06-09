from __future__ import annotations

import tomllib
from pathlib import Path

from .models import SafeArea, SceneSpec, SmokeConfig, Viewport


def load_config(path: Path, viewport_manifest: Path | None = None) -> SmokeConfig:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    settings = data.get("settings", {})
    manifest_path = viewport_manifest or _settings_manifest_path(path, settings)
    viewports = load_viewport_manifest(manifest_path) if manifest_path else {}
    viewports.update(_parse_viewports(data.get("viewports", {})))
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


def load_viewport_manifest(path: Path) -> dict[str, Viewport]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return _parse_viewports(data.get("viewports", {}))


def _parse_viewports(raw_viewports: object) -> dict[str, Viewport]:
    if not isinstance(raw_viewports, dict):
        return {}
    return {
        name: Viewport(
            name=name,
            width=int(values["width"]),
            height=int(values["height"]),
            safe_area=_parse_safe_area(values.get("safe_area", {})),
        )
        for name, values in raw_viewports.items()
    }


def _parse_safe_area(raw_safe_area: object) -> SafeArea:
    if not isinstance(raw_safe_area, dict):
        return SafeArea()
    return SafeArea(
        left=int(raw_safe_area.get("left", 0)),
        top=int(raw_safe_area.get("top", 0)),
        right=int(raw_safe_area.get("right", 0)),
        bottom=int(raw_safe_area.get("bottom", 0)),
    )


def _settings_manifest_path(config_path: Path, settings: object) -> Path | None:
    if not isinstance(settings, dict):
        return None
    manifest = settings.get("viewport_manifest")
    if not manifest:
        return None
    manifest_path = Path(str(manifest))
    return manifest_path if manifest_path.is_absolute() else config_path.parent / manifest_path
