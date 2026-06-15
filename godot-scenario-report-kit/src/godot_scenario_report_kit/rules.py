from __future__ import annotations

from typing import Any


RULES: dict[str, dict[str, str]] = {
    "invalid_json": {
        "title": "Unreadable result JSON",
        "help": "Check that the result file is valid UTF-8 JSON before publishing it as run evidence.",
    },
    "missing_scenario_name": {
        "title": "Missing scenario name",
        "help": "Add a scenario or name field so regressions can be matched across runs.",
    },
    "invalid_status": {
        "title": "Unsupported scenario status",
        "help": "Use one of passed, failed, skipped, or warning for each scenario result.",
    },
    "scenario_failed": {
        "title": "Scenario failed",
        "help": "Open the scenario source and attached artifacts first; this is the top-level run failure.",
    },
    "assertion_failed": {
        "title": "Assertion failed",
        "help": "Inspect the named assertion and its message before rerunning the whole scenario suite.",
    },
    "missing_artifact": {
        "title": "Missing artifact",
        "help": "Confirm the artifact path is relative to the result directory or remove stale artifact references.",
    },
    "new_scenario_failure": {
        "title": "New failure against baseline",
        "help": "Compare the current run with the baseline run to find what changed in this scenario.",
    },
    "duration_regression": {
        "title": "Duration regression",
        "help": "Check recent runtime, scene loading, fixture, or wait-condition changes before raising the threshold.",
    },
}


def enrich_finding(finding: dict[str, Any]) -> dict[str, Any]:
    """Add stable rule metadata while preserving the original finding fields."""
    rule = RULES.get(str(finding.get("rule_id", "")))
    if not rule:
        return finding
    return {
        **finding,
        "rule_title": rule["title"],
        "rule_help": rule["help"],
    }


def rule_catalog() -> dict[str, dict[str, str]]:
    """Return the public rule catalog in a JSON-friendly shape."""
    return {rule_id: dict(rule) for rule_id, rule in sorted(RULES.items())}
