from __future__ import annotations

import fnmatch
from pathlib import Path
import re
from typing import Any

from .models import Finding, ModulePolicy
from .rule_help import RULE_HELP, enrich_finding

RESOURCE_RE = re.compile(r"""(?:preload|load)\(\s*["'](res://[^"']+)["']\s*\)""")


def audit_project(project: Path, modules: tuple[ModulePolicy, ...], autoloads: tuple[str, ...]) -> dict[str, Any]:
    root = project.resolve()
    files = sorted(path for path in root.rglob("*.gd") if ".godot" not in path.parts)
    module_by_file = {path: _module_for_path(root, path, modules) for path in files}
    findings: list[Finding] = []
    edges: set[tuple[str, str]] = set()

    for path in files:
        rel = path.relative_to(root).as_posix()
        module = module_by_file[path]
        if module is None:
            findings.append(
                Finding(
                    rule_id="unowned_script",
                    severity="warning",
                    path=rel,
                    message=f"{rel} is not covered by any module path policy.",
                )
            )
        text = path.read_text(encoding="utf-8", errors="ignore")
        _check_resource_dependencies(root, rel, text, module, modules, findings, edges)
        _check_autoload_access(rel, text, module, autoloads, findings)

    return {
        "tool": "godot-gdscript-architecture-guard",
        "version": "0.1.1",
        "metadata": {
            "schema_version": "1.1",
            "rule_count": len(RULE_HELP),
            "report_kind": "gdscript_architecture_guard",
        },
        "summary": {
            "scripts": len(files),
            "modules": len(modules),
            "dependencies": len(edges),
            "findings": len(findings),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
        },
        "rule_help": RULE_HELP,
        "modules": {
            module.name: {
                "paths": list(module.paths),
                "may_depend_on": list(module.may_depend_on),
                "allowed_autoloads": list(module.allowed_autoloads),
            }
            for module in modules
        },
        "dependencies": [{"source": source, "target": target} for source, target in sorted(edges)],
        "findings": [enrich_finding(finding.to_dict()) for finding in findings],
    }


def render_mermaid(report: dict[str, Any]) -> str:
    lines = ["flowchart LR"]
    for name in report["modules"]:
        lines.append(f"  {name}[{name}]")
    for edge in report["dependencies"]:
        lines.append(f"  {edge['source']} --> {edge['target']}")
    return "\n".join(lines)


def _check_resource_dependencies(
    root: Path,
    rel: str,
    text: str,
    module: ModulePolicy | None,
    modules: tuple[ModulePolicy, ...],
    findings: list[Finding],
    edges: set[tuple[str, str]],
) -> None:
    for match in RESOURCE_RE.finditer(text):
        target_res = match.group(1)
        target_path = root / target_res.removeprefix("res://")
        target_module = _module_for_res_path(target_res, modules)
        if not target_path.exists():
            findings.append(
                Finding(
                    rule_id="unresolved_resource",
                    severity="error",
                    path=rel,
                    module=module.name if module else None,
                    target=target_res,
                    message=f"{rel} loads {target_res}, but the file does not exist.",
                )
            )
            continue
        if module and target_module:
            edges.add((module.name, target_module.name))
            if target_module.name != module.name and target_module.name not in module.may_depend_on:
                findings.append(
                    Finding(
                        rule_id="module_boundary_violation",
                        severity="error",
                        path=rel,
                        module=module.name,
                        target=target_module.name,
                        message=f"{module.name} depends on {target_module.name}, which is not allowed by policy.",
                    )
                )


def _check_autoload_access(
    rel: str,
    text: str,
    module: ModulePolicy | None,
    autoloads: tuple[str, ...],
    findings: list[Finding],
) -> None:
    if not module:
        return
    allowed = set(module.allowed_autoloads)
    for name in autoloads:
        if name in allowed:
            continue
        if re.search(rf"\b{re.escape(name)}\b", text):
            findings.append(
                Finding(
                    rule_id="autoload_access_violation",
                    severity="warning",
                    path=rel,
                    module=module.name,
                    target=name,
                    message=f"{module.name} accesses autoload {name}, which is not allowed by policy.",
                )
            )


def _module_for_path(root: Path, path: Path, modules: tuple[ModulePolicy, ...]) -> ModulePolicy | None:
    rel = path.relative_to(root).as_posix()
    for module in modules:
        if any(fnmatch.fnmatch(rel, pattern) for pattern in module.paths):
            return module
    return None


def _module_for_res_path(res_path: str, modules: tuple[ModulePolicy, ...]) -> ModulePolicy | None:
    rel = res_path.removeprefix("res://")
    for module in modules:
        if any(fnmatch.fnmatch(rel, pattern) for pattern in module.paths):
            return module
    return None
