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
    "manifest_invalid_json": {
        "title": "Unreadable manifest JSON",
        "help": "Check that the scenario manifest is valid UTF-8 JSON before publishing it as run evidence.",
    },
    "manifest_missing_scenarios": {
        "title": "No manifest scenarios",
        "help": "Add a scenarios list so scenario coverage can be checked before a release.",
    },
    "manifest_duplicate_id": {
        "title": "Duplicate scenario id",
        "help": "Use stable unique scenario ids so results, coverage, and history can be matched reliably.",
    },
    "manifest_missing_owner": {
        "title": "Missing scenario owner",
        "help": "Add an owner or area field so failures can be routed to the right maintainer or team.",
    },
    "manifest_missing_tags": {
        "title": "Missing scenario tags",
        "help": "Tag scenarios by workflow, platform, mechanic, or risk area so coverage reports stay useful.",
    },
    "manifest_result_missing": {
        "title": "Listed scenario has no result",
        "help": "Run the scenario or remove it from the release manifest if it is no longer part of the suite.",
    },
    "manifest_unlisted_result": {
        "title": "Result is not listed in manifest",
        "help": "Add the scenario to the manifest if it is part of the supported release suite.",
    },
    "manifest_expected_artifact_missing": {
        "title": "Expected artifact missing",
        "help": "Check the runner output path or update the manifest if the artifact name changed.",
    },
    "coverage_required_tag_missing": {
        "title": "Required tag has no scenario",
        "help": "Add at least one scenario for the required tag or remove the tag from the manifest coverage policy.",
    },
    "coverage_required_flow_missing": {
        "title": "Required flow has no scenario",
        "help": "Add a scenario for this user journey or update the manifest coverage policy.",
    },
    "coverage_required_platform_missing": {
        "title": "Required platform has no scenario",
        "help": "Add platform-specific coverage or adjust the policy for this release.",
    },
    "flaky_scenario": {
        "title": "Scenario changed status across runs",
        "help": "Inspect logs and artifacts from both passing and failing runs before treating this scenario as stable.",
    },
    "bundle_missing_artifact": {
        "title": "Bundle artifact missing",
        "help": "Check that scenario artifact paths are relative to the result folder before publishing the bundle.",
    },
    "bundle_link_missing": {
        "title": "Bundle linked evidence missing",
        "help": "Check the telemetry or visual evidence path before attaching the bundle to a release review.",
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
