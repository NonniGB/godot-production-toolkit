from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

from .models import AssertionResult, Finding, ScenarioResult


def load_results(path: Path) -> tuple[list[ScenarioResult], list[Finding]]:
    files = [path] if path.is_file() else [*sorted(path.glob("*.json")), *sorted(path.glob("*.xml"))]
    results: list[ScenarioResult] = []
    findings: list[Finding] = []
    for file_path in files:
        if file_path.suffix.lower() == ".xml":
            xml_results, xml_findings = _load_junit_results(file_path)
            results.extend(xml_results)
            findings.extend(xml_findings)
            continue
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


def _load_junit_results(path: Path) -> tuple[list[ScenarioResult], list[Finding]]:
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        return [], [
            Finding(
                rule_id="invalid_junit_xml",
                severity="error",
                source=str(path),
                message=f"Could not read scenario result JUnit XML: {exc}",
            )
        ]
    cases = list(root.iter("testcase"))
    return [_scenario_from_junit_case(case, path) for case in cases], []


def _scenario_from_junit_case(case: ET.Element, source: Path) -> ScenarioResult:
    name = _junit_case_name(case)
    failures = [child for child in case if _xml_local_name(child.tag) in {"failure", "error"}]
    skipped = any(_xml_local_name(child.tag) == "skipped" for child in case)
    status = "skipped" if skipped else "failed" if failures else "passed"
    assertions = [
        AssertionResult(
            name=_xml_local_name(failure.tag),
            status="failed",
            message=_junit_failure_message(failure),
        )
        for failure in failures
    ]
    return ScenarioResult(
        name=name,
        status=status,
        duration_ms=_junit_duration_ms(case),
        source=str(source),
        assertions=assertions,
        artifacts=[],
    )


def _junit_case_name(case: ET.Element) -> str:
    raw_name = str(case.attrib.get("name") or "unnamed")
    class_name = str(case.attrib.get("classname") or "").strip()
    if class_name and not raw_name.startswith(f"{class_name}."):
        return f"{class_name}.{raw_name}"
    return raw_name


def _junit_duration_ms(case: ET.Element) -> float:
    try:
        return float(case.attrib.get("time", 0) or 0) * 1000
    except ValueError:
        return 0.0


def _junit_failure_message(failure: ET.Element) -> str:
    message = str(failure.attrib.get("message") or "").strip()
    text = (failure.text or "").strip()
    if message and text:
        return f"{message} {text}"
    return message or text


def _xml_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


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
