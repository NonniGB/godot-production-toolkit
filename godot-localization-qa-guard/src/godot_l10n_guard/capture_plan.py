from __future__ import annotations

import json
import re
from pathlib import Path

from . import __version__


def build_capture_plan(
    stress_manifest: dict[str, object],
    *,
    screens: list[str],
    viewports: list[str],
    output_dir: Path,
    include_source_locale: bool = False,
) -> dict[str, object]:
    screen_names = _clean_names(screens, "screen")
    viewport_names = _clean_names(viewports, "viewport")
    locales = _stress_locales(stress_manifest, include_source_locale=include_source_locale)

    captures: list[dict[str, object]] = []
    for screen in screen_names:
        for viewport in viewport_names:
            for locale in locales:
                captures.append(
                    {
                        "screen": screen,
                        "viewport": viewport,
                        "locale": locale["locale"],
                        "stress_variant": locale["stress_variant"],
                        "stress_catalog": locale.get("stress_catalog"),
                        "output_path": _capture_path(output_dir, screen, viewport, str(locale["locale"])),
                    }
                )

    return {
        "tool": "godot-localization-qa-guard",
        "metadata": {
            "schema_version": "1.0",
            "tool_version": __version__,
            "report_kind": "localization_capture_plan",
        },
        "summary": {
            "locales": len(locales),
            "screens": len(screen_names),
            "viewports": len(viewport_names),
            "captures": len(captures),
        },
        "source_language": stress_manifest.get("source_language"),
        "locales": locales,
        "screens": screen_names,
        "viewports": viewport_names,
        "captures": captures,
    }


def render_capture_plan(plan: dict[str, object], format_name: str) -> str:
    if format_name == "json":
        return json.dumps(plan, indent=2, sort_keys=True)

    summary = plan["summary"]
    captures = plan["captures"]
    if format_name == "markdown":
        lines = [
            "# Localization Capture Plan",
            "",
            f"Locales: {summary['locales']}",
            f"Screens: {summary['screens']}",
            f"Viewports: {summary['viewports']}",
            f"Captures: {summary['captures']}",
            "",
            "| Screen | Viewport | Locale | Stress variant | Output |",
            "|---|---|---|---|---|",
        ]
        for capture in captures:
            lines.append(
                "| {screen} | {viewport} | {locale} | {stress_variant} | {output_path} |".format(
                    **capture
                )
            )
        return "\n".join(lines)

    lines = [
        "Godot Localization Capture Plan",
        f"Locales: {summary['locales']}",
        f"Screens: {summary['screens']}",
        f"Viewports: {summary['viewports']}",
        f"Captures: {summary['captures']}",
    ]
    for capture in captures:
        lines.append(
            "- {screen} / {viewport} / {locale} ({stress_variant}) -> {output_path}".format(
                **capture
            )
        )
    return "\n".join(lines)


def _stress_locales(
    stress_manifest: dict[str, object],
    *,
    include_source_locale: bool,
) -> list[dict[str, object]]:
    locales: list[dict[str, object]] = []
    seen: set[str] = set()
    source_language = stress_manifest.get("source_language")
    if include_source_locale and isinstance(source_language, str) and source_language:
        locales.append(
            {
                "locale": source_language,
                "stress_variant": "source",
                "stress_catalog": None,
            }
        )
        seen.add(source_language)

    for output in stress_manifest.get("outputs", []):
        if not isinstance(output, dict):
            continue
        locale = output.get("locale")
        if not isinstance(locale, str) or not locale or locale in seen:
            continue
        locales.append(
            {
                "locale": locale,
                "stress_variant": output.get("variant") or "stress",
                "stress_catalog": output.get("path"),
                "strings": output.get("strings"),
            }
        )
        seen.add(locale)
    return locales


def _clean_names(values: list[str], label: str) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        name = value.strip()
        if not name or name in seen:
            continue
        cleaned.append(name)
        seen.add(name)
    if not cleaned:
        raise ValueError(f"at least one {label} is required")
    return cleaned


def _capture_path(output_dir: Path, screen: str, viewport: str, locale: str) -> str:
    return (output_dir / _safe_segment(screen) / _safe_segment(viewport) / f"{_safe_segment(locale)}.png").as_posix()


def _safe_segment(value: str) -> str:
    segment = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return segment.strip("._") or "unnamed"
