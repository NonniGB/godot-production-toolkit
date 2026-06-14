from __future__ import annotations

from typing import Any


RULE_HELP: dict[str, dict[str, str]] = {
    "unowned_script": {
        "title": "Script is outside every module",
        "explanation": "A GDScript file was not matched by any configured module path.",
        "suggestion": "Add the folder to an existing module or create a new module entry.",
    },
    "unresolved_resource": {
        "title": "Loaded resource does not exist",
        "explanation": "A preload or load path points at a resource that was not found in the project.",
        "suggestion": "Fix the res:// path or remove the stale dependency.",
    },
    "module_boundary_violation": {
        "title": "Module dependency is not allowed",
        "explanation": "A script loaded another module that is not listed in its allowed dependencies.",
        "suggestion": "Move shared code to an allowed module or update the policy if the dependency is intentional.",
    },
    "autoload_access_violation": {
        "title": "Autoload access is not allowed",
        "explanation": "A module referenced an autoload that is not listed in its allowed autoloads.",
        "suggestion": "Pass data through an allowed boundary or add the autoload to the module policy.",
    },
}


def enrich_finding(finding: dict[str, Any]) -> dict[str, Any]:
    rule = RULE_HELP.get(str(finding.get("rule_id", "")))
    if not rule:
        return finding
    return {**finding, **rule}
