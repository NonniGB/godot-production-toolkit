from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Finding, FixtureResult
from .validator import validate_json


def validate_fixtures(path: Path, schema: dict[str, Any]) -> list[FixtureResult]:
    results: list[FixtureResult] = []
    files = [path] if path.is_file() else sorted(path.rglob("*.json"))
    for fixture in files:
        findings: list[Finding] = []
        try:
            data = json.loads(fixture.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            results.append(
                FixtureResult(
                    fixture,
                    [Finding("invalid_json", "error", "$", f"Invalid JSON: {exc.msg}.")],
                )
            )
            continue

        if isinstance(data, dict) and "version" not in data:
            findings.append(
                Finding(
                    "missing_version_field",
                    "error",
                    "$.version",
                    "Save fixture has no top-level version field.",
                )
            )
        findings.extend(validate_json(data, schema))
        results.append(FixtureResult(fixture, findings))
    return results
