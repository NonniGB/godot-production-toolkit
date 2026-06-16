from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import Finding, FixtureResult


@dataclass(frozen=True)
class RedactionOptions:
    paths: list[str]
    output_dir: Path
    replacement: str | None = None
    dry_run: bool = False
    overwrite: bool = False


def redact_fixtures(fixtures_path: Path, options: RedactionOptions) -> list[FixtureResult]:
    files = [fixtures_path] if fixtures_path.is_file() else sorted(fixtures_path.rglob("*.json"))
    results: list[FixtureResult] = []
    for fixture in files:
        findings = _redact_fixture(fixtures_path, fixture, options)
        results.append(FixtureResult(fixture, findings))
    return results


def _redact_fixture(fixtures_path: Path, fixture: Path, options: RedactionOptions) -> list[Finding]:
    findings: list[Finding] = []
    try:
        data = json.loads(fixture.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [Finding("invalid_json", "error", "$", f"Invalid JSON: {exc.msg}.")]

    redacted = deepcopy(data)
    total = 0
    for path in options.paths:
        matches = _find_matches(redacted, _parse_path(path))
        if not matches:
            findings.append(
                Finding(
                    "redaction_path_missing",
                    "warning",
                    _path_to_json_path(path),
                    f"Redaction path '{path}' was not found in this fixture.",
                )
            )
            continue
        for parent, key, json_path in matches:
            value = parent[key]
            if isinstance(value, (dict, list)):
                findings.append(
                    Finding(
                        "redaction_non_scalar_target",
                        "warning",
                        json_path,
                        f"Redaction path '{path}' points to an object or array and was not changed.",
                    )
                )
                continue
            total += 1
            if not options.dry_run:
                parent[key] = _replacement_for(value, options.replacement)

    output_path = _redacted_output_path(fixtures_path, fixture, options.output_dir)
    if options.dry_run:
        findings.append(Finding("redaction_planned", "info", "$", f"Would redact {total} value(s)."))
        return findings

    if output_path.exists() and not options.overwrite:
        findings.append(
            Finding(
                "redaction_output_exists",
                "error",
                "$",
                f"Output file already exists: {output_path.as_posix()}. Use --overwrite to replace it.",
            )
        )
        return findings

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(redacted, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    findings.append(
        Finding(
            "redaction_applied",
            "info",
            "$",
            f"Redacted {total} value(s) and wrote {output_path.as_posix()}.",
        )
    )
    return findings


def _find_matches(data: Any, parts: list[str], json_path: str = "$") -> list[tuple[Any, Any, str]]:
    if not parts:
        return []
    head, *tail = parts
    matches: list[tuple[Any, Any, str]] = []
    if isinstance(data, dict):
        keys = list(data.keys()) if head == "*" else [head]
        for key in keys:
            if key not in data:
                continue
            child_path = f"{json_path}.{key}"
            if tail:
                matches.extend(_find_matches(data[key], tail, child_path))
            else:
                matches.append((data, key, child_path))
    elif isinstance(data, list):
        indexes: list[int] = []
        if head == "*":
            indexes = list(range(len(data)))
        elif head.isdigit():
            indexes = [int(head)]
        for index in indexes:
            if not 0 <= index < len(data):
                continue
            child_path = f"{json_path}[{index}]"
            if tail:
                matches.extend(_find_matches(data[index], tail, child_path))
            else:
                matches.append((data, index, child_path))
    return matches


def _parse_path(path: str) -> list[str]:
    clean = path.removeprefix("$.").strip()
    return [part for part in clean.split(".") if part]


def _replacement_for(value: Any, configured: str | None) -> Any:
    if configured is not None:
        return configured
    if isinstance(value, bool):
        return False
    if isinstance(value, int | float) and not isinstance(value, bool):
        return 0
    if value is None:
        return None
    return "<redacted>"


def _redacted_output_path(fixtures_path: Path, fixture: Path, output_dir: Path) -> Path:
    if fixtures_path.is_file():
        return output_dir / fixture.name
    return output_dir / fixture.relative_to(fixtures_path)


def _path_to_json_path(path: str) -> str:
    clean = path.removeprefix("$.").strip()
    return "$" if not clean else "$." + clean
