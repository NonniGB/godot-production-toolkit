from __future__ import annotations

import csv
import json
from pathlib import Path

from . import __version__
from .models import CsvTable, PoCatalog, TranslationEntry
from .pseudo import PLACEHOLDER_RE, pseudo_localize

Catalog = CsvTable | PoCatalog

VARIANT_LOCALES = {
    "pseudo": "qps-ploc",
    "long": "qps-long",
    "compact": "qps-compact",
    "rtl": "qps-rtl",
}


def write_stress_pack(
    catalogs: list[Catalog],
    output_dir: Path,
    *,
    source_language: str,
    variants: list[str],
    pseudo_expansion: float = 0.3,
    long_multiplier: float = 1.8,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    entries = _unique_entries(catalogs)
    variant_outputs: list[dict[str, object]] = []

    for variant in variants:
        locale = VARIANT_LOCALES[variant]
        output_path = output_dir / f"{variant}.csv"
        _write_variant_csv(
            entries,
            output_path,
            variant=variant,
            locale=locale,
            source_language=source_language,
            pseudo_expansion=pseudo_expansion,
            long_multiplier=long_multiplier,
        )
        variant_outputs.append(
            {
                "variant": variant,
                "locale": locale,
                "path": str(output_path),
                "strings": len(entries),
            }
        )

    manifest = {
        "tool": "godot-localization-qa-guard",
        "metadata": {
            "schema_version": "1.0",
            "tool_version": __version__,
            "report_kind": "localization_stress_pack",
        },
        "summary": {
            "catalogs": len(catalogs),
            "strings": len(entries),
            "variants": len(variant_outputs),
        },
        "source_language": source_language,
        "catalogs": [catalog.path for catalog in catalogs],
        "outputs": variant_outputs,
    }
    manifest_path = output_dir / "stress-pack-manifest.json"
    manifest["manifest_path"] = str(manifest_path)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def render_stress_report(manifest: dict[str, object], format_name: str) -> str:
    if format_name == "json":
        return json.dumps(manifest, indent=2, sort_keys=True)
    outputs = manifest["outputs"]
    summary = manifest["summary"]
    if format_name == "markdown":
        lines = [
            "# Localization Stress Pack",
            "",
            f"Catalogs scanned: {summary['catalogs']}",
            f"Strings found: {summary['strings']}",
            "",
            "| Variant | Locale | Strings | File |",
            "|---|---|---:|---|",
        ]
        for output in outputs:
            lines.append(
                f"| {output['variant']} | {output['locale']} | {output['strings']} | {output['path']} |"
            )
        lines.append("")
        lines.append(f"Manifest: {manifest['manifest_path']}")
        return "\n".join(lines)

    lines = [
        "Godot Localization Stress Pack",
        f"Catalogs scanned: {summary['catalogs']}",
        f"Strings found: {summary['strings']}",
    ]
    for output in outputs:
        lines.append(
            f"- {output['variant']} ({output['locale']}): {output['strings']} string(s) -> {output['path']}"
        )
    lines.append(f"Manifest: {manifest['manifest_path']}")
    return "\n".join(lines)


def _write_variant_csv(
    entries: list[TranslationEntry],
    output_path: Path,
    *,
    variant: str,
    locale: str,
    source_language: str,
    pseudo_expansion: float,
    long_multiplier: float,
) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["keys", source_language, locale])
        for entry in entries:
            source_text = entry.translations.get(source_language) or entry.source
            writer.writerow(
                [
                    entry.key,
                    source_text,
                    _variant_text(
                        source_text,
                        variant=variant,
                        pseudo_expansion=pseudo_expansion,
                        long_multiplier=long_multiplier,
                    ),
                ]
            )


def _variant_text(text: str, *, variant: str, pseudo_expansion: float, long_multiplier: float) -> str:
    if variant == "pseudo":
        return pseudo_localize(text, expansion=pseudo_expansion)
    if variant == "long":
        return _long_text(text, long_multiplier)
    if variant == "compact":
        return _compact_text(text)
    if variant == "rtl":
        return _rtl_text(text)
    raise ValueError(f"unsupported stress variant: {variant}")


def _long_text(text: str, multiplier: float) -> str:
    if not text:
        return text
    target_length = max(len(text), int(len(text) * multiplier))
    padding = " " + ("~" * max(1, target_length - len(text) - 1))
    return f"{text}{padding}"


def _compact_text(text: str) -> str:
    if not text:
        return text
    pieces: list[str] = []
    for part in PLACEHOLDER_RE.split(text):
        if not part:
            continue
        if PLACEHOLDER_RE.fullmatch(part):
            pieces.append(part)
        else:
            pieces.append(_compact_literal(part))
    compact = "".join(pieces).strip()
    return compact or text


def _compact_literal(text: str) -> str:
    words = text.split()
    if not words:
        return text[: max(1, min(4, len(text)))]
    compact_words = []
    for word in words:
        if len(word) <= 3:
            compact_words.append(word)
        else:
            compact_words.append(word[:3])
    return " ".join(compact_words)


def _rtl_text(text: str) -> str:
    if not text:
        return text
    return "\u202b" + text + "\u202c"


def _unique_entries(catalogs: list[Catalog]) -> list[TranslationEntry]:
    entries: list[TranslationEntry] = []
    seen: set[str] = set()
    for catalog in catalogs:
        for entry in catalog.entries:
            if entry.key in seen:
                continue
            seen.add(entry.key)
            entries.append(entry)
    return entries
