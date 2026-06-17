from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .loader import load_results
from .models import Finding, ScenarioResult
from .reports import _report


def manifest_check(manifest_path: Path, results_path: Path | None = None) -> dict[str, Any]:
    manifest, findings = _load_manifest(manifest_path)
    entries = _entries(manifest)
    findings.extend(_manifest_findings(entries, manifest_path))
    coverage_summary = _coverage_summary(entries, manifest)
    findings.extend(_coverage_findings(coverage_summary, manifest_path))
    results: list[ScenarioResult] = []
    if results_path is not None:
        results, result_findings = load_results(results_path)
        findings.extend(result_findings)
        findings.extend(_result_alignment_findings(entries, results, results_path))
        findings.extend(_expected_artifact_findings(entries, results_path))
    scenarios = [_entry_as_result(entry, manifest_path) for entry in entries]
    report = _report("manifest_check", scenarios, findings)
    report["manifest"] = str(manifest_path)
    if results_path is not None:
        report["results"] = str(results_path)
        report["result_scenarios"] = [result.to_dict() for result in results]
    report["coverage"] = coverage_summary
    return report


def coverage(manifest_path: Path, results_path: Path | None = None) -> dict[str, Any]:
    report = manifest_check(manifest_path, results_path)
    report["kind"] = "coverage"
    return report


def flake_compare(paths: list[Path]) -> dict[str, Any]:
    findings: list[Finding] = []
    runs: list[dict[str, Any]] = []
    by_scenario: dict[str, list[dict[str, Any]]] = {}
    retry_groups: list[dict[str, Any]] = []
    for path in paths:
        results, result_findings = load_results(path)
        findings.extend(result_findings)
        run = {"path": str(path), "scenarios": len(results)}
        runs.append(run)
        by_run_scenario: dict[str, list[dict[str, Any]]] = {}
        for result in results:
            observation = {"status": result.status, "duration_ms": result.duration_ms, "source": result.source}
            by_scenario.setdefault(result.name, []).append(observation)
            by_run_scenario.setdefault(result.name, []).append(observation)
        run_retries = 0
        for name, observations in sorted(by_run_scenario.items()):
            if len(observations) <= 1:
                continue
            run_retries += 1
            retry_groups.append(
                {
                    "scenario": name,
                    "run": str(path),
                    "attempts": len(observations),
                    "statuses": _unique_in_order(str(item["status"]) for item in observations),
                    "final_status": str(observations[-1]["status"]),
                    "observations": observations,
                }
            )
        run["retried_scenarios"] = run_retries
    flake_groups: list[dict[str, Any]] = []
    scenario_rows: list[ScenarioResult] = []
    for name, observations in sorted(by_scenario.items()):
        statuses = sorted({str(item["status"]) for item in observations})
        status = "passed" if statuses == ["passed"] else "failed"
        if len(statuses) > 1:
            status = "warning"
            findings.append(
                Finding(
                    rule_id="flaky_scenario",
                    severity="warning",
                    scenario=name,
                    message=f"{name} changed status across runs: {', '.join(statuses)}.",
                )
            )
            flake_groups.append({"scenario": name, "statuses": statuses, "observations": observations})
        scenario_rows.append(
            ScenarioResult(
                name=name,
                status=status,
                duration_ms=sum(float(item["duration_ms"]) for item in observations),
                assertions=[],
                artifacts=[],
            )
        )
    report = _report("flake_compare", scenario_rows, findings)
    report["runs"] = runs
    report["flake_groups"] = flake_groups
    report["retry_groups"] = retry_groups
    report["summary"]["flaky"] = len(flake_groups)
    report["summary"]["retried"] = len(retry_groups)
    return report


def _unique_in_order(values: Iterable[str]) -> list[str]:
    unique: list[str] = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return unique


def bundle(
    results_path: Path,
    manifest_path: Path | None = None,
    telemetry_path: Path | None = None,
    visual_path: Path | None = None,
    evidence_links: list[tuple[str, Path]] | None = None,
) -> dict[str, Any]:
    results, findings = load_results(results_path)
    base_dir = results_path if results_path.is_dir() else results_path.parent
    scenario_rows: list[dict[str, Any]] = []
    for result in results:
        artifacts: list[dict[str, Any]] = []
        for artifact in result.artifacts:
            artifact_path = base_dir / artifact
            exists = artifact_path.exists()
            artifacts.append({"path": artifact, "exists": exists})
            if not exists:
                findings.append(
                    Finding(
                        rule_id="bundle_missing_artifact",
                        severity="warning",
                        scenario=result.name,
                        source=result.source,
                        message=f"{result.name} lists missing bundle artifact {artifact!r}.",
                    )
                )
        scenario_rows.append({**result.to_dict(), "bundle_artifacts": artifacts})

    links = {
        "manifest": _bundle_link(manifest_path, base_dir, findings, "manifest"),
        "telemetry": _bundle_link(telemetry_path, base_dir, findings, "telemetry"),
        "visual": _bundle_link(visual_path, base_dir, findings, "visual"),
    }
    telemetry_summary = _telemetry_summary(telemetry_path, base_dir, findings)
    visual_summary = _visual_summary(visual_path, base_dir, findings)
    custom_evidence = [
        _bundle_link(path, base_dir, findings, kind)
        for kind, path in evidence_links or []
    ]
    report = _report("scenario_bundle", results, findings)
    report["results"] = str(results_path)
    report["bundle"] = {
        "base_dir": str(base_dir),
        "scenarios": scenario_rows,
        "links": {key: value for key, value in links.items() if value is not None},
        "evidence_links": custom_evidence,
    }
    if telemetry_summary is not None:
        report["bundle"]["telemetry_summary"] = telemetry_summary
    if visual_summary is not None:
        report["bundle"]["visual_summary"] = visual_summary
    if manifest_path is not None:
        manifest_report = manifest_check(manifest_path, results_path)
        report["coverage"] = manifest_report.get("coverage")
        report["manifest_findings"] = manifest_report.get("findings", [])
    report["summary"]["artifacts"] = sum(len(row["bundle_artifacts"]) for row in scenario_rows)
    report["summary"]["linked_evidence"] = sum(1 for value in links.values() if value is not None) + len(
        custom_evidence
    )
    if telemetry_summary is not None:
        report["summary"]["telemetry_samples"] = telemetry_summary.get("samples", 0)
        report["summary"]["telemetry_spikes"] = telemetry_summary.get("spikes", 0)
        report["summary"]["telemetry_warnings"] = telemetry_summary.get("warnings", 0)
        report["summary"]["telemetry_errors"] = telemetry_summary.get("errors", 0)
    if visual_summary is not None:
        report["summary"]["visual_captures"] = visual_summary.get("captures", 0)
        report["summary"]["visual_comparisons"] = visual_summary.get("comparisons", 0)
        report["summary"]["visual_changed"] = visual_summary.get("changed", 0)
        report["summary"]["visual_warnings"] = visual_summary.get("warnings", 0)
        report["summary"]["visual_errors"] = visual_summary.get("errors", 0)
    return report


def _bundle_link(
    path: Path | None,
    base_dir: Path,
    findings: list[Finding],
    kind: str,
) -> dict[str, Any] | None:
    if path is None:
        return None
    exists = path.exists()
    if not exists:
        findings.append(
            Finding(
                rule_id="bundle_link_missing",
                severity="warning",
                source=str(path),
                message=f"Linked {kind} evidence path {str(path)!r} does not exist.",
            )
        )
    link: dict[str, Any] = {
        "kind": kind,
        "path": str(path),
        "relative_path": _relative_path(path, base_dir),
        "exists": exists,
    }
    if exists:
        link["is_dir"] = path.is_dir()
        if path.is_file():
            link["size_bytes"] = path.stat().st_size
    return link


def _relative_path(path: Path, base_dir: Path) -> str:
    try:
        return path.resolve().relative_to(base_dir.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _telemetry_summary(
    path: Path | None,
    base_dir: Path,
    findings: list[Finding],
) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    source = _telemetry_source(path)
    if source is None:
        return None
    if source.suffix.lower() in {".md", ".markdown"}:
        try:
            summary = _compact_telemetry_markdown(source.read_text(encoding="utf-8"))
        except OSError as exc:
            findings.append(
                Finding(
                    rule_id="bundle_telemetry_unreadable",
                    severity="warning",
                    source=str(source),
                    message=f"Linked telemetry Markdown could not be summarized: {exc}",
                )
            )
            return None
        if summary is None:
            return None
        return {
            "path": str(source),
            "relative_path": _relative_path(source, base_dir),
            **summary,
        }
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(
            Finding(
                rule_id="bundle_telemetry_unreadable",
                severity="warning",
                source=str(source),
                message=f"Linked telemetry JSON could not be summarized: {exc}",
            )
        )
        return None
    summary = _compact_telemetry_summary(data)
    if summary is None:
        return None
    return {
        "path": str(source),
        "relative_path": _relative_path(source, base_dir),
        **summary,
    }


def _telemetry_source(path: Path) -> Path | None:
    supported = {".json", ".md", ".markdown"}
    if path.is_file():
        return path if path.suffix.lower() in supported else None
    for candidate in sorted(path.glob("*.json")):
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and str(data.get("kind", "")).startswith("runtime_telemetry_"):
            return candidate
    markdown_candidates = sorted(path.glob("*.md")) + sorted(path.glob("*.markdown"))
    for candidate in markdown_candidates:
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        if "Runtime Telemetry" in text or "Frame p95" in text:
            return candidate
    return None


def _visual_summary(
    path: Path | None,
    base_dir: Path,
    findings: list[Finding],
) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    source = _visual_source(path)
    if source is None:
        return None
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(
            Finding(
                rule_id="bundle_visual_unreadable",
                severity="warning",
                source=str(source),
                message=f"Linked visual evidence JSON could not be summarized: {exc}",
            )
        )
        return None
    summary = _compact_visual_summary(data)
    if summary is None:
        return None
    return {
        "path": str(source),
        "relative_path": _relative_path(source, base_dir),
        **summary,
    }


def _visual_source(path: Path) -> Path | None:
    if path.is_file():
        return path if path.suffix.lower() == ".json" else None
    for candidate in sorted(path.glob("*.json")):
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if _compact_visual_summary(data) is not None:
            return candidate
    return None


def _compact_visual_summary(data: object) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    finding_rows = [item for item in data.get("findings", []) if isinstance(item, dict)]
    screenshots = data.get("screenshots")
    captures = data.get("captures")
    comparisons = data.get("comparisons")
    capture_count = _int_value(summary.get("captures") or summary.get("screenshots"))
    if capture_count == 0:
        capture_count = _list_count(screenshots) or _list_count(captures)
    comparison_count = _int_value(summary.get("comparisons"))
    if comparison_count == 0:
        comparison_count = _list_count(comparisons)
    changed = _int_value(summary.get("changed") or summary.get("changed_comparisons") or summary.get("diffs"))
    warnings = _int_value(summary.get("warnings")) or sum(
        1 for finding in finding_rows if finding.get("severity") == "warning"
    )
    errors = _int_value(summary.get("errors")) or sum(
        1 for finding in finding_rows if finding.get("severity") == "error"
    )
    if capture_count == 0 and comparison_count == 0 and changed == 0 and warnings == 0 and errors == 0:
        return None
    return {
        "kind": str(data.get("kind") or data.get("tool") or "visual_smoke_report"),
        "captures": capture_count,
        "comparisons": comparison_count,
        "changed": changed,
        "warnings": warnings,
        "errors": errors,
    }


def _compact_telemetry_summary(data: object) -> dict[str, Any] | None:
    if isinstance(data, list):
        return _compact_raw_samples(data)
    if not isinstance(data, dict):
        return None
    kind = str(data.get("kind") or "runtime_telemetry_samples")
    if kind == "runtime_telemetry_compare":
        metric_source = data.get("current") if isinstance(data.get("current"), dict) else {}
        count_source = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    elif isinstance(data.get("summary"), dict):
        metric_source = data["summary"]
        count_source = data["summary"]
    elif isinstance(data.get("samples"), list):
        return _compact_raw_samples(data["samples"], kind=kind)
    else:
        return None
    findings = data.get("findings", [])
    finding_rows = [item for item in findings if isinstance(item, dict)]
    return {
        "kind": kind,
        "samples": _int_value(count_source.get("samples")),
        "scenarios": _string_list(metric_source.get("scenarios")),
        "frame_p95_ms": _metric_value(metric_source, "frame_ms", "p95"),
        "frame_max_ms": _metric_value(metric_source, "frame_ms", "max"),
        "memory_max_mb": _metric_value(metric_source, "memory_mb", "max"),
        "spikes": _int_value(count_source.get("spikes")),
        "warnings": _int_value(count_source.get("warnings"))
        or sum(1 for finding in finding_rows if finding.get("severity") == "warning"),
        "errors": _int_value(count_source.get("errors"))
        or sum(1 for finding in finding_rows if finding.get("severity") == "error"),
    }


def _compact_raw_samples(samples: object, kind: str = "runtime_telemetry_samples") -> dict[str, Any] | None:
    if not isinstance(samples, list):
        return None
    rows = [item for item in samples if isinstance(item, dict)]
    frame_values = sorted(_number(item.get("frame_ms")) for item in rows if _number(item.get("frame_ms")) is not None)
    memory_values = sorted(_number(item.get("memory_mb")) for item in rows if _number(item.get("memory_mb")) is not None)
    return {
        "kind": kind,
        "samples": len(rows),
        "scenarios": sorted({str(item.get("scenario") or "default") for item in rows}),
        "frame_p95_ms": _percentile(frame_values, 0.95),
        "frame_max_ms": frame_values[-1] if frame_values else 0.0,
        "memory_max_mb": memory_values[-1] if memory_values else 0.0,
        "spikes": 0,
        "warnings": 0,
        "errors": 0,
    }


def _compact_telemetry_markdown(text: str) -> dict[str, Any] | None:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        values[cells[0].lower()] = cells[1]
    if not values:
        return None
    samples = _int_value(values.get("samples"))
    frame_p95 = _number(values.get("frame p95 ms")) or 0.0
    frame_max = _number(values.get("frame max ms")) or 0.0
    memory_max = _number(values.get("memory max mb")) or 0.0
    spikes = _int_value(values.get("spikes"))
    warnings = _int_value(values.get("warnings"))
    if samples == 0 and frame_p95 == 0 and frame_max == 0 and spikes == 0:
        return None
    return {
        "kind": "runtime_telemetry_markdown",
        "samples": samples,
        "scenarios": [],
        "frame_p95_ms": frame_p95,
        "frame_max_ms": frame_max,
        "memory_max_mb": memory_max,
        "spikes": spikes,
        "warnings": warnings,
        "errors": _int_value(values.get("errors")),
    }


def _metric_value(summary: dict[str, Any], metric: str, field: str) -> float:
    value = summary.get(metric)
    if not isinstance(value, dict):
        return 0.0
    return _number(value.get(field)) or 0.0


def _number(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_value(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return sorted(str(item) for item in value if str(item).strip())
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _list_count(value: object) -> int:
    return len(value) if isinstance(value, list) else 0


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    index = round((len(values) - 1) * fraction)
    return values[index]


def _load_manifest(path: Path) -> tuple[dict[str, Any], list[Finding]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [
            Finding(
                rule_id="manifest_invalid_json",
                severity="error",
                source=str(path),
                message=f"Could not read scenario manifest JSON: {exc}",
            )
        ]
    if not isinstance(raw, dict):
        return {}, [
            Finding(
                rule_id="manifest_invalid_json",
                severity="error",
                source=str(path),
                message="Scenario manifest must be a JSON object.",
            )
        ]
    return raw, []


def _entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = manifest.get("scenarios", [])
    if not isinstance(scenarios, list):
        return []
    return [item for item in scenarios if isinstance(item, dict)]


def _manifest_findings(entries: list[dict[str, Any]], source: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not entries:
        findings.append(
            Finding(
                rule_id="manifest_missing_scenarios",
                severity="error",
                source=str(source),
                message="Scenario manifest does not contain any scenario entries.",
            )
        )
        return findings
    seen: set[str] = set()
    for entry in entries:
        scenario_id = _scenario_id(entry)
        if not scenario_id:
            findings.append(
                Finding(
                    rule_id="missing_scenario_name",
                    severity="error",
                    source=str(source),
                    message="Scenario manifest entry is missing an id, scenario, or name field.",
                )
            )
            continue
        if scenario_id in seen:
            findings.append(
                Finding(
                    rule_id="manifest_duplicate_id",
                    severity="error",
                    scenario=scenario_id,
                    source=str(source),
                    message=f"Scenario id {scenario_id!r} appears more than once in the manifest.",
                )
            )
        seen.add(scenario_id)
        if not str(entry.get("owner") or entry.get("area") or "").strip():
            findings.append(
                Finding(
                    rule_id="manifest_missing_owner",
                    severity="warning",
                    scenario=scenario_id,
                    source=str(source),
                    message=f"{scenario_id} has no owner or area field.",
                )
            )
        if not _list(entry.get("tags")):
            findings.append(
                Finding(
                    rule_id="manifest_missing_tags",
                    severity="warning",
                    scenario=scenario_id,
                    source=str(source),
                    message=f"{scenario_id} has no tags.",
                )
            )
    return findings


def _coverage_findings(coverage_summary: dict[str, Any], source: Path) -> list[Finding]:
    findings: list[Finding] = []
    for tag in coverage_summary["missing_required_tags"]:
        findings.append(
            Finding(
                rule_id="coverage_required_tag_missing",
                severity="warning",
                source=str(source),
                message=f"Required tag {tag!r} has no listed scenario.",
            )
        )
    for flow in coverage_summary["missing_required_critical_flows"]:
        findings.append(
            Finding(
                rule_id="coverage_required_flow_missing",
                severity="warning",
                source=str(source),
                message=f"Required critical flow {flow!r} has no listed scenario.",
            )
        )
    for platform in coverage_summary["missing_required_platforms"]:
        findings.append(
            Finding(
                rule_id="coverage_required_platform_missing",
                severity="warning",
                source=str(source),
                message=f"Required platform {platform!r} has no listed scenario.",
            )
        )
    return findings


def _result_alignment_findings(
    entries: list[dict[str, Any]], results: list[ScenarioResult], source: Path
) -> list[Finding]:
    findings: list[Finding] = []
    expected = {_scenario_id(entry) for entry in entries}
    actual = {result.name for result in results}
    for scenario_id in sorted(expected - actual):
        findings.append(
            Finding(
                rule_id="manifest_result_missing",
                severity="error",
                scenario=scenario_id,
                source=str(source),
                message=f"{scenario_id} is listed in the manifest but has no result.",
            )
        )
    for scenario_id in sorted(actual - expected):
        findings.append(
            Finding(
                rule_id="manifest_unlisted_result",
                severity="warning",
                scenario=scenario_id,
                source=str(source),
                message=f"{scenario_id} has a result but is not listed in the manifest.",
            )
        )
    return findings


def _expected_artifact_findings(entries: list[dict[str, Any]], results_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    base_dir = results_path if results_path.is_dir() else results_path.parent
    for entry in entries:
        scenario_id = _scenario_id(entry)
        for artifact in _list(entry.get("expected_artifacts") or entry.get("artifacts")):
            if not (base_dir / artifact).exists():
                findings.append(
                    Finding(
                        rule_id="manifest_expected_artifact_missing",
                        severity="warning",
                        scenario=scenario_id,
                        source=str(results_path),
                        message=f"{scenario_id} expects missing artifact {artifact!r}.",
                    )
                )
    return findings


def _coverage_summary(entries: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    tags = sorted({tag for entry in entries for tag in _list(entry.get("tags"))})
    flows = sorted({flow for entry in entries for flow in _list(entry.get("critical_flows") or entry.get("flows"))})
    platforms = sorted({platform for entry in entries for platform in _list(entry.get("platforms"))})
    policy = manifest.get("coverage", {})
    missing_tags = sorted(set(_list(policy.get("required_tags") if isinstance(policy, dict) else [])) - set(tags))
    missing_flows = sorted(
        set(_list(policy.get("required_critical_flows") if isinstance(policy, dict) else [])) - set(flows)
    )
    missing_platforms = sorted(
        set(_list(policy.get("required_platforms") if isinstance(policy, dict) else [])) - set(platforms)
    )
    return {
        "tags": tags,
        "critical_flows": flows,
        "platforms": platforms,
        "missing_required_tags": missing_tags,
        "missing_required_critical_flows": missing_flows,
        "missing_required_platforms": missing_platforms,
    }


def _entry_as_result(entry: dict[str, Any], source: Path) -> ScenarioResult:
    return ScenarioResult(
        name=_scenario_id(entry),
        status="passed",
        duration_ms=0,
        source=str(source),
        assertions=[],
        artifacts=_list(entry.get("expected_artifacts") or entry.get("artifacts")),
    )


def _scenario_id(entry: dict[str, Any]) -> str:
    return str(entry.get("id") or entry.get("scenario") or entry.get("name") or "").strip()


def _list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []
