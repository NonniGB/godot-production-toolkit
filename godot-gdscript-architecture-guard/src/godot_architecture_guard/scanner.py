from __future__ import annotations

import fnmatch
from pathlib import Path
import re
from typing import Any

from . import __version__
from .models import Finding, ModulePolicy
from .rule_help import RULE_HELP, enrich_finding

RESOURCE_RE = re.compile(r"""(?:preload|load)\(\s*["'](res://[^"']+)["']\s*\)""")
RESOURCE_PATH_RE = re.compile(r"""["']\*?(res://[^"']+\.gd)["']""")
ANY_RESOURCE_PATH_RE = re.compile(r"""["']\*?(res://[^"']+)["']""")
CLASS_NAME_RE = re.compile(r"^\s*class_name\s+\w+", re.MULTILINE)
TEXT_REFERENCE_SUFFIXES = {".gd", ".tscn", ".tres", ".cfg", ".godot"}
RESOURCE_CANDIDATE_SUFFIXES = {
    ".atlas",
    ".csv",
    ".fnt",
    ".gdshader",
    ".jpeg",
    ".jpg",
    ".json",
    ".material",
    ".mp3",
    ".ogg",
    ".otf",
    ".png",
    ".res",
    ".scn",
    ".shader",
    ".svg",
    ".theme",
    ".tres",
    ".tscn",
    ".ttf",
    ".wav",
    ".webp",
}
HOTSPOT_LIMIT = 10


def audit_project(
    project: Path,
    modules: tuple[ModulePolicy, ...],
    autoloads: tuple[str, ...],
    policy_path: Path | None = None,
) -> dict[str, Any]:
    root = project.resolve()
    policy_report_path = _display_path(root, policy_path) if policy_path else "architecture-guard.toml"
    files = sorted(path for path in root.rglob("*.gd") if ".godot" not in path.parts)
    module_by_file = {path: _module_for_path(root, path, modules) for path in files}
    references_by_file: dict[Path, set[Path]] = {path: set() for path in files}
    autoload_references_by_file: dict[Path, int] = {path: 0 for path in files}
    class_name_files: set[Path] = set()
    findings: list[Finding] = []
    edges: set[tuple[str, str]] = set()
    _check_module_path_coverage(root, files, modules, findings, policy_report_path)

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
        if CLASS_NAME_RE.search(text):
            class_name_files.add(path)
        references_by_file[path].update(_existing_script_targets(root, text))
        autoload_references_by_file[path] = _count_autoload_references(text, autoloads)
        _check_resource_dependencies(root, rel, text, module, modules, findings, edges)
        _check_autoload_access(rel, text, module, autoloads, findings)

    project_references = _project_script_references(root)
    resource_files = _resource_files(root)
    project_resource_references = _project_resource_references(root)
    hotspots = _build_hotspots(root, files, module_by_file, references_by_file, autoload_references_by_file)
    possible_unused_scripts = _build_possible_unused_scripts(
        root,
        files,
        module_by_file,
        references_by_file,
        project_references,
        class_name_files,
    )
    possible_unused_resources = _build_possible_unused_resources(
        root,
        resource_files,
        modules,
        project_resource_references,
    )
    owner_summaries = _build_owner_summaries(
        root,
        files,
        modules,
        module_by_file,
        references_by_file,
        autoload_references_by_file,
        findings,
        hotspots,
        possible_unused_scripts,
    )

    return {
        "tool": "godot-gdscript-architecture-guard",
        "version": __version__,
        "metadata": {
            "schema_version": "1.1",
            "rule_count": len(RULE_HELP),
            "report_kind": "gdscript_architecture_guard",
        },
        "summary": {
            "scripts": len(files),
            "modules": len(modules),
            "dependencies": len(edges),
            "hotspots": len(hotspots),
            "possible_unused_scripts": len(possible_unused_scripts),
            "possible_unused_resources": len(possible_unused_resources),
            "owner_summaries": len(owner_summaries),
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
        "owner_summaries": owner_summaries,
        "hotspots": hotspots,
        "possible_unused_scripts": possible_unused_scripts,
        "possible_unused_resources": possible_unused_resources,
        "findings": [enrich_finding(finding.to_dict()) for finding in findings],
    }


def render_mermaid(report: dict[str, Any]) -> str:
    lines = ["flowchart LR"]
    for name in report["modules"]:
        lines.append(f"  {name}[{name}]")
    for edge in report["dependencies"]:
        lines.append(f"  {edge['source']} --> {edge['target']}")
    return "\n".join(lines)


def _check_module_path_coverage(
    root: Path,
    files: list[Path],
    modules: tuple[ModulePolicy, ...],
    findings: list[Finding],
    policy_report_path: str,
) -> None:
    rel_files = [path.relative_to(root).as_posix() for path in files]
    for module in modules:
        for pattern in module.paths:
            if any(fnmatch.fnmatch(rel, pattern) for rel in rel_files):
                continue
            findings.append(
                Finding(
                    rule_id="module_path_without_scripts",
                    severity="warning",
                    path=policy_report_path,
                    module=module.name,
                    target=pattern,
                    message=f"Module {module.name} path pattern {pattern} did not match any GDScript files.",
                )
            )


def _display_path(root: Path, path: Path | None) -> str:
    if path is None:
        return "architecture-guard.toml"
    resolved = path.resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _check_resource_dependencies(
    root: Path,
    rel: str,
    text: str,
    module: ModulePolicy | None,
    modules: tuple[ModulePolicy, ...],
    findings: list[Finding],
    edges: set[tuple[str, str]],
) -> None:
    for target_res in _load_targets(text):
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


def _load_targets(text: str) -> list[str]:
    return [match.group(1) for match in RESOURCE_RE.finditer(text)]


def _existing_script_targets(root: Path, text: str) -> set[Path]:
    targets: set[Path] = set()
    for match in RESOURCE_PATH_RE.finditer(text):
        target = root / match.group(1).removeprefix("res://")
        if target.exists() and target.suffix == ".gd":
            targets.add(target.resolve())
    return targets


def _count_autoload_references(text: str, autoloads: tuple[str, ...]) -> int:
    return sum(len(re.findall(rf"\b{re.escape(name)}\b", text)) for name in autoloads)


def _project_script_references(root: Path) -> set[Path]:
    references: set[Path] = set()
    for path in root.rglob("*"):
        if not path.is_file() or ".godot" in path.parts:
            continue
        if path.suffix not in TEXT_REFERENCE_SUFFIXES and path.name != "project.godot":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        references.update(_existing_script_targets(root, text))
    return references


def _resource_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or ".godot" in path.parts:
            continue
        if path.suffix.lower() in RESOURCE_CANDIDATE_SUFFIXES:
            files.append(path.resolve())
    return sorted(files)


def _project_resource_references(root: Path) -> set[Path]:
    references: set[Path] = set()
    for path in root.rglob("*"):
        if not path.is_file() or ".godot" in path.parts:
            continue
        if path.suffix not in TEXT_REFERENCE_SUFFIXES and path.name != "project.godot":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        references.update(_existing_resource_targets(root, text))
    return references


def _existing_resource_targets(root: Path, text: str) -> set[Path]:
    targets: set[Path] = set()
    for match in ANY_RESOURCE_PATH_RE.finditer(text):
        target = root / match.group(1).removeprefix("res://")
        if target.exists() and target.suffix.lower() in RESOURCE_CANDIDATE_SUFFIXES:
            targets.add(target.resolve())
    return targets


def _build_hotspots(
    root: Path,
    files: list[Path],
    module_by_file: dict[Path, ModulePolicy | None],
    references_by_file: dict[Path, set[Path]],
    autoload_references_by_file: dict[Path, int],
) -> list[dict[str, object]]:
    incoming_counts = {path: 0 for path in files}
    for source, targets in references_by_file.items():
        for target in targets:
            if target != source and target in incoming_counts:
                incoming_counts[target] += 1

    rows: list[dict[str, object]] = []
    for path in files:
        outgoing = len({target for target in references_by_file[path] if target != path})
        incoming = incoming_counts[path]
        autoload_refs = autoload_references_by_file[path]
        score = incoming * 2 + outgoing + autoload_refs
        if score <= 0:
            continue
        module = module_by_file[path]
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "module": module.name if module else None,
                "incoming": incoming,
                "outgoing": outgoing,
                "autoload_references": autoload_refs,
                "score": score,
            }
        )
    rows.sort(key=lambda item: (-int(item["score"]), str(item["path"])))
    return rows[:HOTSPOT_LIMIT]


def _build_possible_unused_scripts(
    root: Path,
    files: list[Path],
    module_by_file: dict[Path, ModulePolicy | None],
    references_by_file: dict[Path, set[Path]],
    project_references: set[Path],
    class_name_files: set[Path],
) -> list[dict[str, object]]:
    referenced = set(project_references)
    for targets in references_by_file.values():
        referenced.update(targets)

    rows: list[dict[str, object]] = []
    for path in files:
        if path in referenced or path in class_name_files:
            continue
        module = module_by_file[path]
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "module": module.name if module else None,
                "reason": "No res:// reference or class_name declaration was found.",
            }
        )
    return rows


def _build_possible_unused_resources(
    root: Path,
    resource_files: list[Path],
    modules: tuple[ModulePolicy, ...],
    project_resource_references: set[Path],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in resource_files:
        if path in project_resource_references:
            continue
        module = _module_for_path(root, path, modules)
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "module": module.name if module else None,
                "reason": "No visible res:// reference was found in scripts, scenes, resources, or project settings.",
            }
        )
    return rows


def _build_owner_summaries(
    root: Path,
    files: list[Path],
    modules: tuple[ModulePolicy, ...],
    module_by_file: dict[Path, ModulePolicy | None],
    references_by_file: dict[Path, set[Path]],
    autoload_references_by_file: dict[Path, int],
    findings: list[Finding],
    hotspots: list[dict[str, object]],
    possible_unused_scripts: list[dict[str, object]],
) -> list[dict[str, object]]:
    module_names = [module.name for module in modules]
    if any(module_by_file[path] is None for path in files):
        module_names.append("<unowned>")

    rows: dict[str, dict[str, object]] = {
        name: {
            "module": name,
            "configured_paths": 0,
            "matched_scripts": 0,
            "incoming_dependencies": 0,
            "outgoing_dependencies": 0,
            "autoload_references": 0,
            "boundary_violations": 0,
            "autoload_violations": 0,
            "unmatched_path_patterns": 0,
            "hotspots": 0,
            "possible_unused_scripts": 0,
        }
        for name in module_names
    }
    for module in modules:
        rows[module.name]["configured_paths"] = len(module.paths)

    incoming_sources: dict[str, set[str]] = {name: set() for name in module_names}
    outgoing_targets: dict[str, set[str]] = {name: set() for name in module_names}
    for source, targets in references_by_file.items():
        source_module = _module_name(module_by_file.get(source))
        rows[source_module]["matched_scripts"] = int(rows[source_module]["matched_scripts"]) + 1
        rows[source_module]["autoload_references"] = (
            int(rows[source_module]["autoload_references"])
            + autoload_references_by_file.get(source, 0)
        )
        source_rel = source.relative_to(root).as_posix()
        for target in targets:
            target_module = _module_name(module_by_file.get(target))
            if target_module == source_module:
                continue
            outgoing_targets[source_module].add(target_module)
            incoming_sources[target_module].add(source_rel)

    for finding in findings:
        module = finding.module or "<unowned>"
        if module not in rows:
            continue
        if finding.rule_id == "module_boundary_violation":
            rows[module]["boundary_violations"] = int(rows[module]["boundary_violations"]) + 1
        elif finding.rule_id == "autoload_access_violation":
            rows[module]["autoload_violations"] = int(rows[module]["autoload_violations"]) + 1
        elif finding.rule_id == "module_path_without_scripts":
            rows[module]["unmatched_path_patterns"] = int(rows[module]["unmatched_path_patterns"]) + 1

    for row in hotspots:
        module = str(row.get("module") or "<unowned>")
        if module in rows:
            rows[module]["hotspots"] = int(rows[module]["hotspots"]) + 1
    for row in possible_unused_scripts:
        module = str(row.get("module") or "<unowned>")
        if module in rows:
            rows[module]["possible_unused_scripts"] = int(rows[module]["possible_unused_scripts"]) + 1

    for module in module_names:
        rows[module]["incoming_dependencies"] = len(incoming_sources[module])
        rows[module]["outgoing_dependencies"] = len(outgoing_targets[module])
    return [rows[name] for name in module_names]


def _module_name(module: ModulePolicy | None) -> str:
    return module.name if module else "<unowned>"


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
