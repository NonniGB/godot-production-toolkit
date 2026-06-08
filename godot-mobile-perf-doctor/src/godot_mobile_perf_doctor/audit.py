from __future__ import annotations

from typing import Any

from .models import Finding, TextureSummary


def audit_settings(settings: dict[str, Any], *, profile: str) -> list[Finding]:
    findings: list[Finding] = []
    renderer = str(settings.get("rendering/renderer/rendering_method", "")).lower()
    if renderer == "forward_plus":
        findings.append(
            Finding(
                "forward_plus_renderer_mobile_risk",
                "warning",
                "Forward+ renderer is expensive for many Android/mobile 2D projects; consider Mobile or Compatibility renderer after visual testing.",
            )
        )

    width = _int_setting(settings, "display/window/size/viewport_width")
    height = _int_setting(settings, "display/window/size/viewport_height")
    if width and height and width * height > 1920 * 1080:
        findings.append(
            Finding(
                "large_base_viewport",
                "warning",
                f"Base viewport {width}x{height} exceeds 1080p; profile '{profile}' may waste fill-rate on mobile.",
            )
        )

    stretch_mode = str(settings.get("display/window/stretch/mode", "")).lower()
    if stretch_mode in {"", "disabled"}:
        findings.append(
            Finding(
                "stretch_disabled",
                "warning",
                "Stretch mode is disabled or missing; mobile projects usually need explicit scaling behavior.",
            )
        )
    return findings


def texture_findings(summary: TextureSummary, *, max_dimension: int) -> list[Finding]:
    findings: list[Finding] = []
    for texture in summary.large_textures:
        findings.append(
            Finding(
                "large_texture_dimension",
                "warning",
                f"Texture {texture.path.as_posix()} is {texture.width}x{texture.height}, above max dimension {max_dimension}.",
                path=texture.path.as_posix(),
            )
        )
    return findings


def _int_setting(settings: dict[str, Any], key: str) -> int:
    value = settings.get(key)
    return value if isinstance(value, int) else 0
