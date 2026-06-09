from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import AssertionResult, Finding, ScenarioResult


def load_results(path: Path) -> tuple[list[ScenarioResult], list[Finding]]:
    files = [path] if path.is_file() else sorted(path.glob("*.json"))
    results: list[ScenarioResult] = []
    findings: list[Finding] = []
    for file_path in files:
        try:
            raw = json.loads(file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(
                Finding(
                    rule_id="invalid_json",
                    severity="error",
                    source=str(file_path),
                    message=f"Could not read scenario result JSON: {exc}",
                )
            )
            continue
        for item in _scenario_items(raw):
            result = _scenario_from_raw(item, file_path, findings)
            if result:
                results.append(result)
    return results, findings


def _scenario_items(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict):
        for key in ("scenarios", "runs", "results"):
            value = raw.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [raw]
    return []


def _scenario_from_raw(raw: dict[str, Any], source: Path, findings: list[Finding]) -> ScenarioResult | None:
    name = str(raw.get("scenario") or raw.get("name") or "").strip()
    status = str(raw.get("status") or "").strip().lower()
    if not name:
        findings.append(
            Finding(
                rule_id="missing_scenario_name",
                severity="error",
                source=str(source),
                message="Scenario result is missing a scenario/name field.",
            )
        )
        return None
    if status not in {"passed", "failed", "skipped", "warning"}:
        findings.append(
            Finding(
                rule_id="invalid_status",
                severity="error",
                scenario=name,
                source=str(source),
                message=f"{name} has unsupported status {status!r}.",
            )
        )
        status = "failed"
    assertions = [
        AssertionResult(
            name=str(item.get("name", "assertion")),
            status=str(item.get("status", "")).lower(),
            message=str(item.get("message", "")),
        )
        for item in raw.get("assertions", [])
        if isinstance(item, dict)
    ]
    artifacts = [str(item) for item in raw.get("artifacts", [])]
    return ScenarioResult(
        name=name,
        status=status,
        duration_ms=float(raw.get("duration_ms", raw.get("duration", 0)) or 0),
        source=str(source),
        assertions=assertions,
        artifacts=artifacts,
    )

