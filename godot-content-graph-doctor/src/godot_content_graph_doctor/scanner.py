from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import median
import tomllib
from typing import Any

from . import __version__
from .models import CollectionData, CollectionSpec, Finding
from .rules import catalog_for, explain_rule


def validate_content_graph(project: Path, specs: tuple[CollectionSpec, ...]) -> dict[str, Any]:
    root = project.resolve()
    collections: dict[str, CollectionData] = {}
    findings: list[Finding] = []
    unavailable: set[str] = set()

    for spec in specs:
        data, load_findings = _load_collection(root, spec)
        collections[spec.name] = data
        findings.extend(load_findings)
        if load_findings:
            unavailable.add(spec.name)
        _index_ids(data, findings)

    referenced: dict[str, set[str]] = {name: set() for name in collections}
    for source_name, data in collections.items():
        for ref_spec in data.spec.references:
            target = collections.get(ref_spec.collection)
            if target is None:
                findings.append(
                    Finding(
                        rule_id="unknown_target_collection",
                        severity="error",
                        collection=source_name,
                        field=ref_spec.field,
                        target_collection=ref_spec.collection,
                        message=f"Reference field {ref_spec.field!r} targets unknown collection {ref_spec.collection!r}.",
                    )
                )
                continue
            if target.spec.name in unavailable:
                continue
            for record in data.records:
                source_id = str(record.get(data.spec.id_field, "<missing id>"))
                values = _extract_values(record, ref_spec.field)
                if not values and ref_spec.required:
                    findings.append(
                        Finding(
                            rule_id="missing_reference_field",
                            severity="warning",
                            collection=source_name,
                            item_id=source_id,
                            field=ref_spec.field,
                            target_collection=target.spec.name,
                            message=f"{source_name}.{source_id} does not provide reference field {ref_spec.field!r}.",
                        )
                    )
                for value in values:
                    if value in (None, ""):
                        continue
                    text = str(value)
                    referenced[target.spec.name].add(text)
                    if text not in target.ids:
                        findings.append(
                            Finding(
                                rule_id="missing_reference",
                                severity="error",
                                collection=source_name,
                                item_id=source_id,
                                field=ref_spec.field,
                                target_collection=target.spec.name,
                                message=(
                                    f"{source_name}.{source_id} references {target.spec.name}.{text}, "
                                    "but that id does not exist."
                                ),
                            )
                        )

    for name, data in collections.items():
        if data.spec.warn_unused:
            allowed = set(data.spec.roots)
            for item_id in sorted(data.ids):
                if item_id not in referenced[name] and item_id not in allowed:
                    findings.append(
                        Finding(
                            rule_id="unused_content",
                            severity="warning",
                            collection=name,
                            item_id=item_id,
                            message=f"{name}.{item_id} is not referenced by configured content.",
                        )
                    )

    numeric_summary = _numeric_summary(collections, findings)
    finding_dicts = [_finding_dict(finding) for finding in findings]
    return {
        "tool": "godot-content-graph-doctor",
        "metadata": {
            "schema_version": "1.1",
            "tool_version": __version__,
            "report_kind": "content_graph_validation",
            "project": str(root),
            "formats": ["text", "json", "markdown", "mermaid"],
        },
        "summary": {
            "collections": len(collections),
            "records": sum(len(data.records) for data in collections.values()),
            "findings": len(findings),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
        },
        "collections": {
            name: {
                "path": data.source_path,
                "records": len(data.records),
                "unique_ids": len(data.ids),
                "references": [
                    {"field": ref.field, "collection": ref.collection, "required": ref.required}
                    for ref in data.spec.references
                ],
            }
            for name, data in collections.items()
        },
        "numeric_summary": numeric_summary,
        "rules": catalog_for({finding.rule_id for finding in findings}),
        "findings": finding_dicts,
    }


def render_mermaid(specs: tuple[CollectionSpec, ...]) -> str:
    lines = ["flowchart LR"]
    for spec in specs:
        lines.append(f"  {spec.name}[{spec.name}]")
    for spec in specs:
        for ref in spec.references:
            label = ref.field.replace('"', "'")
            lines.append(f"  {spec.name} -->|{label}| {ref.collection}")
    return "\n".join(lines)


def changed_file_impact(project: Path, specs: tuple[CollectionSpec, ...], changed_files: list[str]) -> dict[str, Any]:
    root = project.resolve()
    collection_paths = {_resolve_changed_path(root, spec.path): spec.name for spec in specs}
    downstream: dict[str, set[str]] = {spec.name: set() for spec in specs}
    for spec in specs:
        for ref in spec.references:
            downstream.setdefault(ref.collection, set()).add(spec.name)

    changed: list[dict[str, str]] = []
    direct: set[str] = set()
    unknown: list[str] = []
    for raw_path in changed_files:
        resolved = _resolve_changed_path(root, raw_path)
        collection = collection_paths.get(resolved)
        item = {"path": raw_path}
        if collection:
            item["collection"] = collection
            direct.add(collection)
        else:
            item["collection"] = ""
            unknown.append(raw_path)
        changed.append(item)

    affected = set(direct)
    pending = list(direct)
    while pending:
        current = pending.pop()
        for dependent in downstream.get(current, set()):
            if dependent not in affected:
                affected.add(dependent)
                pending.append(dependent)

    return {
        "changed_files": changed,
        "direct_collections": sorted(direct),
        "affected_collections": sorted(affected),
        "downstream_collections": sorted(affected - direct),
        "unmatched_files": sorted(unknown),
    }


def _load_collection(root: Path, spec: CollectionSpec) -> tuple[CollectionData, list[Finding]]:
    path = (root / spec.path).resolve()
    empty = CollectionData(spec=spec, records=[], source_path=str(path), ids={})
    if not path.exists():
        return empty, [_collection_input_finding(spec, "collection_input_missing", f"Collection file does not exist: {path}.")]
    if not path.is_file():
        return empty, [_collection_input_finding(spec, "collection_input_unsupported", f"Collection path is not a file: {path}.")]
    suffix = path.suffix.lower()
    if suffix not in {".json", ".csv", ".toml"}:
        return empty, [_collection_input_finding(spec, "collection_input_unsupported", f"Unsupported collection format {suffix or '<none>'}: {path}.")]
    try:
        if suffix == ".json":
            raw = json.loads(path.read_text(encoding="utf-8"))
        elif suffix == ".csv":
            with path.open(newline="", encoding="utf-8") as handle:
                raw = list(csv.DictReader(handle))
        else:
            raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, tomllib.TOMLDecodeError, csv.Error) as exc:
        return empty, [_collection_input_finding(spec, "collection_input_unreadable", f"Could not read collection {path}: {exc}.")]
    records = _records_from_raw(raw, spec.name)
    if not _supported_collection_shape(raw, spec.name):
        return empty, [_collection_input_finding(spec, "collection_input_unsupported", f"Collection {path} has an unsupported top-level shape.")]
    return CollectionData(spec=spec, records=records, source_path=str(path), ids={}), []


def _collection_input_finding(spec: CollectionSpec, rule_id: str, message: str) -> Finding:
    return Finding(rule_id=rule_id, severity="error", collection=spec.name, message=message)


def _supported_collection_shape(raw: Any, collection_name: str) -> bool:
    if isinstance(raw, list):
        return all(isinstance(item, dict) for item in raw)
    if not isinstance(raw, dict):
        return False
    if not raw:
        return True
    for key in ("items", "data", "rows", collection_name):
        value = raw.get(key)
        if isinstance(value, list):
            return all(isinstance(item, dict) for item in value)
    return all(isinstance(value, dict) for value in raw.values())


def _finding_dict(finding: Finding) -> dict[str, Any]:
    item = finding.to_dict()
    item.update(explain_rule(finding.rule_id))
    return item


def _resolve_changed_path(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    return (root / path).resolve()


def _records_from_raw(raw: Any, collection_name: str) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict):
        for key in ("items", "data", "rows", collection_name):
            value = raw.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        if raw and all(isinstance(value, dict) for value in raw.values()):
            return [dict({"id": key}, **value) for key, value in raw.items()]
    return []


def _index_ids(data: CollectionData, findings: list[Finding]) -> None:
    ids: dict[str, list[dict[str, Any]]] = {}
    for index, record in enumerate(data.records):
        value = record.get(data.spec.id_field)
        if value in (None, ""):
            findings.append(
                Finding(
                    rule_id="missing_id",
                    severity="error",
                    collection=data.spec.name,
                    message=f"{data.spec.name} record {index} is missing id field {data.spec.id_field!r}.",
                )
            )
            continue
        ids.setdefault(str(value), []).append(record)
    data.ids = ids
    for item_id, records in ids.items():
        if len(records) > 1:
            findings.append(
                Finding(
                    rule_id="duplicate_id",
                    severity="error",
                    collection=data.spec.name,
                    item_id=item_id,
                    message=f"{data.spec.name}.{item_id} appears {len(records)} times.",
                )
            )


def _extract_values(record: dict[str, Any], field_path: str) -> list[Any]:
    values: list[Any] = [record]
    for part in field_path.split("."):
        list_mode = part.endswith("[]")
        key = part[:-2] if list_mode else part
        next_values: list[Any] = []
        for value in values:
            if not isinstance(value, dict) or key not in value:
                continue
            child = value[key]
            if list_mode:
                if isinstance(child, list):
                    next_values.extend(child)
            else:
                next_values.append(child)
        values = next_values
    return values


def _numeric_summary(collections: dict[str, CollectionData], findings: list[Finding]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for name, data in collections.items():
        collection_summary: dict[str, Any] = {}
        for field in data.spec.numeric_fields:
            values: list[tuple[str, float]] = []
            for record in data.records:
                raw = record.get(field)
                if isinstance(raw, int | float):
                    values.append((str(record.get(data.spec.id_field, "<missing id>")), float(raw)))
                elif isinstance(raw, str):
                    try:
                        values.append((str(record.get(data.spec.id_field, "<missing id>")), float(raw)))
                    except ValueError:
                        continue
            if not values:
                continue
            numeric_values = [value for _, value in values]
            med = median(numeric_values)
            collection_summary[field] = {
                "count": len(values),
                "min": min(numeric_values),
                "max": max(numeric_values),
                "median": med,
            }
            if med > 0:
                for item_id, value in values:
                    if value >= med * 8:
                        findings.append(
                            Finding(
                                rule_id="numeric_outlier",
                                severity="warning",
                                collection=name,
                                item_id=item_id,
                                field=field,
                                message=(
                                    f"{name}.{item_id} has {field}={value:g}, "
                                    f"which is at least 8x the median {med:g}."
                                ),
                            )
                        )
        if collection_summary:
            summary[name] = collection_summary
    return summary
