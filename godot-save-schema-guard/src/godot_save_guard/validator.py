from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .models import Finding


def validate_json(data: Any, schema: Mapping[str, Any], *, json_path: str = "$") -> list[Finding]:
    findings: list[Finding] = []
    expected_type = schema.get("type")
    if expected_type and not _matches_type(data, expected_type):
        if expected_type in {"integer", "number"} and isinstance(data, str) and _looks_numeric(data):
            findings.append(
                Finding(
                    "numeric_type_drift",
                    "error",
                    json_path,
                    f"Expected {expected_type} but found numeric string.",
                )
            )
        else:
            findings.append(
                Finding(
                    "type_mismatch",
                    "error",
                    json_path,
                    f"Expected {expected_type} but found {type(data).__name__}.",
                )
            )
        return findings

    if expected_type == "object" and isinstance(data, dict):
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        for name in required:
            if name not in data:
                findings.append(
                    Finding(
                        "missing_required_property",
                        "error",
                        f"{json_path}.{name}",
                        f"Missing required property '{name}'.",
                    )
                )
        if schema.get("additionalProperties") is False:
            for name in sorted(set(data) - set(properties)):
                findings.append(
                    Finding(
                        "unexpected_property",
                        "warning",
                        f"{json_path}.{name}",
                        f"Unexpected property '{name}'.",
                    )
                )
        for name, child_schema in properties.items():
            if name in data and isinstance(child_schema, Mapping):
                findings.extend(validate_json(data[name], child_schema, json_path=f"{json_path}.{name}"))

    if expected_type == "array" and isinstance(data, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, Mapping):
            for index, item in enumerate(data):
                findings.extend(validate_json(item, item_schema, json_path=f"{json_path}[{index}]"))

    return findings


def _matches_type(data: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(data, dict)
    if expected_type == "array":
        return isinstance(data, list)
    if expected_type == "string":
        return isinstance(data, str)
    if expected_type == "integer":
        return isinstance(data, int) and not isinstance(data, bool)
    if expected_type == "number":
        return isinstance(data, int | float) and not isinstance(data, bool)
    if expected_type == "boolean":
        return isinstance(data, bool)
    if expected_type == "null":
        return data is None
    return True


def _looks_numeric(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True
