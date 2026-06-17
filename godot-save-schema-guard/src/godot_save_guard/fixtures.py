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


def generate_fixture(
    schema: dict[str, Any],
    output_path: Path,
    *,
    include_optional: bool = False,
    overwrite: bool = False,
    overrides: list[str] | None = None,
) -> FixtureResult:
    """Write one deterministic JSON fixture from a small JSON Schema subset."""
    if output_path.exists() and not overwrite:
        return FixtureResult(
            output_path,
            [
                Finding(
                    "fixture_output_exists",
                    "error",
                    "$",
                    "Fixture output already exists. Use --overwrite after reviewing the target path.",
                )
            ],
        )

    fixture = _sample_for_schema(schema, include_optional=include_optional)
    findings: list[Finding] = []
    for override in overrides or []:
        finding = _apply_override(fixture, override)
        if finding:
            findings.append(finding)

    if not any(finding.severity == "error" for finding in findings):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        findings.append(
            Finding(
                "fixture_generated",
                "info",
                "$",
                f"Generated fixture from schema at {output_path}.",
            )
        )
    return FixtureResult(output_path, findings)


def _sample_for_schema(schema: dict[str, Any], *, include_optional: bool) -> Any:
    if "default" in schema:
        return schema["default"]
    if "const" in schema:
        return schema["const"]
    if isinstance(schema.get("enum"), list) and schema["enum"]:
        return schema["enum"][0]
    if isinstance(schema.get("examples"), list) and schema["examples"]:
        return schema["examples"][0]

    schema_type = schema.get("type")
    if isinstance(schema_type, list):
        schema_type = next((item for item in schema_type if item != "null"), schema_type[0] if schema_type else None)

    if schema_type == "object" or "properties" in schema:
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        selected = required | (set(properties.keys()) if include_optional else set())
        return {
            key: _sample_for_schema(value, include_optional=include_optional)
            for key, value in properties.items()
            if key in selected
        }
    if schema_type == "array":
        min_items = int(schema.get("minItems", 0) or 0)
        if min_items <= 0:
            return []
        item_schema = schema.get("items", {})
        return [_sample_for_schema(item_schema, include_optional=include_optional) for _ in range(min_items)]
    if schema_type == "integer":
        return int(schema.get("minimum", 0) or 0)
    if schema_type == "number":
        return float(schema.get("minimum", 0) or 0)
    if schema_type == "boolean":
        return False
    if schema_type == "null":
        return None
    return "example"


def _apply_override(fixture: Any, override: str) -> Finding | None:
    if "=" not in override:
        return Finding(
            "fixture_override_invalid",
            "error",
            "$",
            f"Override '{override}' must use dotted.path=json_value.",
        )
    raw_path, raw_value = override.split("=", 1)
    path = [segment for segment in raw_path.split(".") if segment]
    if not path:
        return Finding("fixture_override_invalid", "error", "$", "Override path cannot be empty.")
    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError:
        return Finding(
            "fixture_override_invalid",
            "error",
            "$",
            f"Override value for {raw_path} must be valid JSON.",
        )

    target = fixture
    for segment in path[:-1]:
        if not isinstance(target, dict):
            return Finding(
                "fixture_override_invalid",
                "error",
                "$",
                f"Cannot apply override {raw_path}: {segment} is not an object.",
            )
        target = target.setdefault(segment, {})
    if not isinstance(target, dict):
        return Finding(
            "fixture_override_invalid",
            "error",
            "$",
            f"Cannot apply override {raw_path}: parent is not an object.",
        )
    target[path[-1]] = value
    return None
