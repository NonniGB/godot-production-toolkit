from __future__ import annotations

from collections import defaultdict

from .models import ApiItem, ThresholdFinding


def build_summary(items: list[ApiItem]) -> dict[str, dict[str, float | int]]:
    kinds = sorted({item.kind for item in items})
    summary: dict[str, dict[str, float | int]] = {"all": _summary_row(items)}
    grouped: dict[str, list[ApiItem]] = defaultdict(list)
    for item in items:
        grouped[item.kind].append(item)
    for kind in kinds:
        summary[kind] = _summary_row(grouped[kind])
    return summary


def evaluate_thresholds(
    items: list[ApiItem],
    thresholds: dict[str, float],
) -> list[ThresholdFinding]:
    summary = build_summary(items)
    findings: list[ThresholdFinding] = []
    for kind, expected in thresholds.items():
        if expected <= 0:
            continue
        row = summary.get(kind, {"total": 0, "coverage": 100.0})
        if row["total"] == 0:
            continue
        actual = float(row["coverage"])
        if actual < expected:
            findings.append(
                ThresholdFinding(
                    kind=kind,
                    severity="error",
                    actual=actual,
                    expected=float(expected),
                    message=f"{kind} comment coverage is {actual:.2f}% but {expected:.2f}% is required.",
                )
            )
    return findings


def _summary_row(items: list[ApiItem]) -> dict[str, float | int]:
    total = len(items)
    documented = sum(1 for item in items if item.documented)
    coverage = 100.0 if total == 0 else round((documented / total) * 100, 2)
    return {"total": total, "documented": documented, "coverage": coverage}
