from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tomllib
from typing import Any


@dataclass(frozen=True)
class ToolSpec:
    id: str
    title: str
    command: str
    output_name: str
    default_enabled: bool
    package: str
    project_arg: bool = True
    required_config: tuple[str, ...] = ()
    base_args: tuple[str, ...] = ()


TOOL_REGISTRY: tuple[ToolSpec, ...] = (
    ToolSpec("assets", "Asset Pipeline Doctor", "godot-asset-doctor", "assets.json", True, "godot-asset-pipeline-doctor"),
    ToolSpec("export", "Export Preset Doctor", "godot-export-doctor", "export.json", True, "godot-export-preset-doctor"),
    ToolSpec(
        "api_comments",
        "GDScript API Comment Coverage",
        "gdscript-api-coverage",
        "api-comments.json",
        True,
        "gdscript-api-comment-coverage",
    ),
    ToolSpec("input", "Input Map Auditor", "godot-input-audit", "input-map.json", True, "godot-input-map-auditor"),
    ToolSpec(
        "localization",
        "Localization QA Guard",
        "godot-l10n-guard",
        "localization.json",
        True,
        "godot-localization-qa-guard",
    ),
    ToolSpec(
        "save_schema",
        "Save Schema Guard",
        "godot-save-guard",
        "save-schema.json",
        False,
        "godot-save-schema-guard",
        required_config=("fixtures", "schema"),
    ),
    ToolSpec("signals", "Scene Signal Auditor", "godot-signal-audit", "signals.json", True, "godot-scene-signal-auditor"),
    ToolSpec(
        "visual_smoke",
        "Visual Smoke Test Kit",
        "godot-visual-smoke",
        "visual-smoke-plan.json",
        False,
        "godot-visual-smoke-test-kit",
        required_config=("config",),
    ),
    ToolSpec(
        "mobile_perf",
        "Mobile Perf Doctor",
        "godot-mobile-perf-doctor",
        "mobile-perf.json",
        True,
        "godot-mobile-perf-doctor",
        base_args=("--static",),
    ),
    ToolSpec(
        "mobile_ui",
        "Mobile UI Doctor",
        "godot-mobile-ui-doctor",
        "mobile-ui.json",
        False,
        "godot-mobile-ui-doctor",
        required_config=("metadata",),
        project_arg=False,
    ),
    ToolSpec(
        "pixel_assets",
        "Pixel Space Asset Toolkit",
        "pixel-space-assets",
        "pixel-assets.json",
        False,
        "pixel-space-asset-toolkit",
        required_config=("command",),
    ),
    ToolSpec(
        "content_graph",
        "Content Graph Doctor",
        "godot-content-graph",
        "content-graph.json",
        False,
        "godot-content-graph-doctor",
        required_config=("config",),
    ),
    ToolSpec(
        "pack_mod",
        "Pack/Mod Doctor",
        "godot-pack-mod-doctor",
        "pack-mod.json",
        False,
        "godot-pack-mod-doctor",
        required_config=("manifest",),
        project_arg=False,
    ),
    ToolSpec(
        "scenario_report",
        "Scenario Report Kit",
        "godot-scenario-report",
        "scenario-report.json",
        False,
        "godot-scenario-report-kit",
        required_config=("path",),
        project_arg=False,
    ),
    ToolSpec(
        "runtime_telemetry",
        "Runtime Telemetry Lab",
        "godot-telemetry-lab",
        "runtime-telemetry.json",
        False,
        "godot-runtime-telemetry-lab",
        required_config=("path",),
        project_arg=False,
    ),
    ToolSpec(
        "architecture",
        "GDScript Architecture Guard",
        "godot-architecture-guard",
        "architecture.json",
        False,
        "godot-gdscript-architecture-guard",
        required_config=("config",),
    ),
)

CHECK_GUIDANCE: dict[str, dict[str, str]] = {
    "assets": {
        "why": "Catches texture/import settings that often break pixel art, memory budgets, and mobile exports.",
        "when": "Run before merging new sprites, icons, UI art, or imported textures.",
    },
    "export": {
        "why": "Finds incomplete export preset settings before a release job fails or ships a debug build.",
        "when": "Run before any desktop, web, or Android export.",
    },
    "api_comments": {
        "why": "Keeps public GDScript APIs understandable when generated docs or code review depend on comments.",
        "when": "Run before treating scripts as stable integration points.",
    },
    "input": {
        "why": "Checks input actions for duplicate bindings and missing keyboard, gamepad, mouse, or touch coverage.",
        "when": "Run before merging control, UI, or mobile-touch changes.",
    },
    "localization": {
        "why": "Catches missing translations, placeholder mismatches, stale keys, and unused localization entries.",
        "when": "Run before importing translations or shipping localized builds.",
    },
    "save_schema": {
        "why": "Validates save fixtures and migration commands against the schema a project promises to support.",
        "when": "Run before changing save formats or migration code.",
    },
    "signals": {
        "why": "Highlights scene signal wiring and autoload coupling that can drift during refactors.",
        "when": "Run before refactoring scenes, singletons, or event wiring.",
    },
    "visual_smoke": {
        "why": "Turns screenshot capture and comparison into repeatable review evidence.",
        "when": "Run before approving UI, scene, or rendering changes.",
    },
    "mobile_perf": {
        "why": "Flags static Godot settings that create avoidable Android performance and battery risk.",
        "when": "Run before testing on Android hardware or preparing a mobile build.",
    },
    "mobile_ui": {
        "why": "Checks exported UI rectangles for safe-area overlap, touch target size, spacing, and text overflow risk.",
        "when": "Run after a UI smoke test, debug exporter, or editor script writes mobile UI metadata.",
    },
    "pixel_assets": {
        "why": "Generates and checks deterministic pixel asset previews for repeatable asset review.",
        "when": "Run when preparing sprite sheets, preview sheets, or generated pixel assets.",
    },
    "content_graph": {
        "why": "Validates ids, references, and numeric outliers across data-driven content files.",
        "when": "Run before merging item, recipe, quest, level, dialogue, or content-pack data.",
    },
    "pack_mod": {
        "why": "Checks pack, DLC, patch, or mod manifests for identity, dependency, path, and shipped-file risks.",
        "when": "Run before sharing optional content packs or comparing a pack update against a baseline.",
    },
    "scenario_report": {
        "why": "Summarizes and compares runtime scenario evidence from a project's own runner.",
        "when": "Run after scenario, smoke, or regression runs have produced JSON evidence.",
    },
    "runtime_telemetry": {
        "why": "Summarizes frame, memory, node, and draw-call samples from project-owned runtime logs.",
        "when": "Run after smoke, soak, or scenario runs produce telemetry JSON or CSV files.",
    },
    "architecture": {
        "why": "Checks module dependency direction, autoload access, and unresolved GDScript resource links.",
        "when": "Run before refactors or when a codebase starts accumulating cross-module coupling.",
    },
}

PROFILE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "release": {
        "title": "Release readiness",
        "description": "Export presets, assets, input coverage, localization, mobile performance, and report collection.",
        "checks": ["export", "assets", "input", "localization", "mobile_perf"],
    },
    "android": {
        "title": "Android release review",
        "description": "Android export settings, static mobile performance, input coverage, asset imports, and localization basics.",
        "checks": ["export", "mobile_perf", "input", "assets", "localization"],
    },
    "html5": {
        "title": "Web export review",
        "description": "Web export settings, asset imports, input coverage, localization, and visual smoke planning.",
        "checks": ["export", "assets", "input", "localization", "visual_smoke"],
    },
    "mobile": {
        "title": "Mobile review",
        "description": "Android/export readiness, static mobile performance, touch input, mobile UI metadata, and visual smoke planning.",
        "checks": ["export", "mobile_perf", "input", "mobile_ui", "visual_smoke"],
    },
    "mobile-ui": {
        "title": "Mobile UI review",
        "description": "Touch input, safe-area metadata, localization stress inputs, visual smoke planning, and static mobile settings.",
        "checks": ["input", "mobile_ui", "localization", "visual_smoke", "mobile_perf"],
    },
    "localization": {
        "title": "Localization review",
        "description": "Translation files, script key usage, mobile layout risk inputs, visual smoke planning, and input text flows.",
        "checks": ["localization", "mobile_ui", "visual_smoke", "input"],
    },
    "runtime": {
        "title": "Runtime evidence",
        "description": "Scenario reports, runtime telemetry, static performance checks, visual smoke planning, and signal evidence.",
        "checks": ["scenario_report", "runtime_telemetry", "mobile_perf", "visual_smoke", "signals"],
    },
    "content": {
        "title": "Content safety",
        "description": "Data graph integrity, save fixtures, scenario evidence, pack/content checks, and release dashboard inputs.",
        "checks": ["content_graph", "save_schema", "scenario_report", "pack_mod", "assets"],
    },
    "save-migration": {
        "title": "Save migration review",
        "description": "Save fixtures, schema validation, migration evidence, scenario reports, and content reference checks.",
        "checks": ["save_schema", "scenario_report", "content_graph", "runtime_telemetry"],
    },
    "mods": {
        "title": "Mod and pack review",
        "description": "Pack manifests, content graph checks, scenario evidence, asset imports, and save compatibility inputs.",
        "checks": ["pack_mod", "content_graph", "scenario_report", "assets", "save_schema"],
    },
    "architecture": {
        "title": "Architecture review",
        "description": "GDScript module boundaries, scene signal wiring, public API comments, and scenario evidence.",
        "checks": ["architecture", "signals", "api_comments", "scenario_report"],
    },
    "visual": {
        "title": "Visual review",
        "description": "Screenshot plans, UI metadata, asset imports, localization stress inputs, and input coverage.",
        "checks": ["visual_smoke", "mobile_ui", "assets", "localization", "input"],
    },
    "qa": {
        "title": "QA evidence",
        "description": "Scenario reports, visual smoke plans, mobile UI readiness, architecture checks, and combined evidence folders.",
        "checks": ["scenario_report", "visual_smoke", "mobile_ui", "architecture", "signals"],
    },
}


class ConfigError(ValueError):
    """Raised when the doctor config cannot be loaded."""


def load_config(config_path: Path | None) -> tuple[dict[str, Any], Path]:
    if not config_path:
        return {}, Path.cwd()
    resolved = config_path.resolve()
    if not resolved.exists():
        raise ConfigError(
            f"Config file not found: {resolved}. Run `godot-project-doctor init --dry-run` "
            "to preview a starter config, or pass --project and --checks to run without a config file."
        )
    return tomllib.loads(resolved.read_text(encoding="utf-8")), resolved.parent


def build_plan(
    config_path: Path | None = None,
    project: Path | None = None,
    checks: list[str] | None = None,
    reports_dir: Path | None = None,
    fail_on: str | None = None,
) -> dict[str, Any]:
    config, base_dir = load_config(config_path)
    project_config = config.get("project", {})
    tool_config = config.get("tools", {})

    project_root = _resolve_path(base_dir, str(project or project_config.get("path", ".")))
    report_root = _resolve_path(base_dir, str(reports_dir or project_config.get("reports_dir", "reports/godot-project-doctor")))
    selected = _selected_checks(project_config, checks)
    fail_threshold = fail_on or str(project_config.get("fail_on", "error"))

    check_plans: list[dict[str, Any]] = []
    for spec in TOOL_REGISTRY:
        specific_config = tool_config.get(spec.id, {})
        enabled = _is_enabled(spec, selected, specific_config)
        reason = "" if enabled else _disabled_reason(spec, selected, specific_config)
        missing_config = [key for key in spec.required_config if not specific_config.get(key)]
        if enabled and missing_config:
            enabled = False
            reason = f"missing required config: {', '.join(missing_config)}"
        report_path = report_root / spec.output_name
        argv = _build_tool_argv(spec, project_root, report_path, specific_config)
        check_plans.append(
            {
                "id": spec.id,
                "title": spec.title,
                "enabled": enabled,
                "reason": reason,
                "report": str(report_path),
                "argv": argv,
            }
        )

    return {
        "tool": "godot-project-doctor",
        "project": str(project_root),
        "reports_dir": str(report_root),
        "fail_on": fail_threshold,
        "checks": check_plans,
        "commands": [
            {"id": item["id"], "argv": item["argv"], "report": item["report"]}
            for item in check_plans
            if item["enabled"]
        ],
    }


def inspect_project(project: Path) -> dict[str, Any]:
    root = project.resolve()
    files = _project_files(root)
    suffixes = {path.suffix.lower() for path in files}
    names = {path.name.lower() for path in files}
    rel_paths = sorted(path.relative_to(root).as_posix() for path in files if path.is_relative_to(root))
    test_frameworks = _detect_test_frameworks(rel_paths, names)
    features = {
        "project_file": (root / "project.godot").exists(),
        "export_presets": (root / "export_presets.cfg").exists(),
        "gdscript_files": any(path.suffix.lower() == ".gd" for path in files),
        "png_assets": ".png" in suffixes,
        "import_files": ".import" in suffixes,
        "localization_files": bool({".csv", ".po", ".pot", ".mo"} & suffixes),
        "input_map_likely": _file_contains(root / "project.godot", "[input]"),
        "mobile_settings_likely": _file_contains(root / "project.godot", "handheld/orientation")
        or _file_contains(root / "project.godot", "display/window"),
        "mobile_ui_metadata_likely": any(
            path.lower().endswith((".json", ".toml"))
            and ("mobile-ui" in path.lower() or "mobile_ui" in path.lower() or "ui-metadata" in path.lower())
            for path in rel_paths
        ),
        "save_fixtures_likely": any("save" in path.lower() and path.endswith((".json", ".toml")) for path in rel_paths),
        "visual_smoke_likely": any("screenshot" in path.lower() or "visual" in path.lower() for path in rel_paths),
        "scenario_results_likely": any(
            ("scenario" in path.lower() or "smoke" in path.lower()) and path.endswith(".json")
            for path in rel_paths
        ),
        "runtime_telemetry_likely": any(
            ("telemetry" in path.lower() or "runtime" in path.lower() or "perf" in path.lower())
            and path.endswith((".json", ".csv"))
            for path in rel_paths
        ),
        "content_data_likely": any(
            path.startswith(("data/", "content/", "resources/")) and path.endswith((".json", ".csv", ".toml"))
            for path in rel_paths
        ),
        "test_framework_likely": bool(test_frameworks),
    }
    details = {
        "project_name": _project_name(root / "project.godot"),
        "file_count": len(files),
        "gdscript_count": sum(1 for path in files if path.suffix.lower() == ".gd"),
        "png_count": sum(1 for path in files if path.suffix.lower() == ".png"),
        "import_count": sum(1 for path in files if path.suffix.lower() == ".import"),
        "localization_count": sum(1 for path in files if path.suffix.lower() in {".csv", ".po", ".pot", ".mo"}),
        "content_file_count": sum(
            1
            for path in rel_paths
            if path.startswith(("data/", "content/", "resources/")) and path.endswith((".json", ".csv", ".toml"))
        ),
        "scenario_result_count": sum(
            1
            for path in rel_paths
            if ("scenario" in path.lower() or "smoke" in path.lower()) and path.endswith(".json")
        ),
        "runtime_telemetry_count": sum(
            1
            for path in rel_paths
            if ("telemetry" in path.lower() or "runtime" in path.lower() or "perf" in path.lower())
            and path.endswith((".json", ".csv"))
        ),
        "test_frameworks": test_frameworks,
        "sample_paths": {
            "scripts": _sample_paths(rel_paths, lambda path: path.endswith(".gd")),
            "assets": _sample_paths(rel_paths, lambda path: path.endswith((".png", ".import"))),
            "content": _sample_paths(
                rel_paths,
                lambda path: path.startswith(("data/", "content/", "resources/"))
                and path.endswith((".json", ".csv", ".toml")),
            ),
            "localization": _sample_paths(rel_paths, lambda path: path.endswith((".csv", ".po", ".pot", ".mo"))),
            "scenario_results": _sample_paths(
                rel_paths,
                lambda path: ("scenario" in path.lower() or "smoke" in path.lower()) and path.endswith(".json"),
            ),
            "runtime_telemetry": _sample_paths(
                rel_paths,
                lambda path: ("telemetry" in path.lower() or "runtime" in path.lower() or "perf" in path.lower())
                and path.endswith((".json", ".csv")),
            ),
        },
    }
    recommendations = recommend_checks_from_features(features, str(root))
    return {
        "tool": "godot-project-doctor",
        "project": str(root),
        "features": features,
        "details": details,
        "recommendations": recommendations,
        "suggested_checks": [item["id"] for item in recommendations[:6]],
    }


def build_doctor_profile(
    project: Path,
    profile: str,
    reports_dir: Path | None = None,
) -> dict[str, Any]:
    if profile not in PROFILE_DEFINITIONS:
        known = ", ".join(sorted(PROFILE_DEFINITIONS))
        raise KeyError(f"unknown profile {profile!r}; known profiles: {known}")
    definition = PROFILE_DEFINITIONS[profile]
    checks = [str(check_id) for check_id in definition["checks"]]
    profile_reports_dir = _profile_reports_dir(project, profile, reports_dir)
    plan = build_plan(
        project=project,
        checks=checks,
        reports_dir=profile_reports_dir,
        fail_on="error",
    )
    inspected = inspect_project(project)
    plan_by_id = {str(item["id"]): item for item in plan["checks"]}
    project_root = Path(str(plan["project"]))
    tasks = [_doctor_task(plan_by_id[check_id], project_root) for check_id in checks if check_id in plan_by_id]
    payload = {
        "tool": "godot-project-doctor",
        "kind": "doctor_profile",
        "profile": profile,
        "title": definition["title"],
        "description": definition["description"],
        "project": plan["project"],
        "reports_dir": plan["reports_dir"],
        "summary": {
            "tasks": len(tasks),
            "ready": sum(1 for task in tasks if task["ready"]),
            "needs_setup": sum(1 for task in tasks if not task["ready"]),
        },
        "detected": inspected["features"],
        "tasks": tasks,
        "next_steps": [
            "Review setup notes for tasks marked needs_setup.",
            "Run the listed commands locally first, then put them in CI.",
            "Use collect or godot-release-dashboard to bundle the resulting reports.",
        ],
        "workflow": render_github_action_example(checks),
    }
    payload["guided_plan"] = build_guided_plan(payload)
    payload["review_handoff"] = build_review_handoff(payload)
    return payload


def build_guided_plan(profile: dict[str, Any]) -> dict[str, Any]:
    project = Path(str(profile["project"]))
    reports_dir = _display_path(Path(str(profile["reports_dir"])), project)
    checks = [str(task["id"]) for task in profile["tasks"]]
    ready_tasks = [task for task in profile["tasks"] if task["ready"]]
    missing_tasks = [task for task in profile["tasks"] if not task["ready"]]
    packages = _packages_for_checks(checks)
    config_preview = render_starter_config(project, reports_dir)
    check_list = ",".join(checks)
    return {
        "format": "markdown",
        "path_hint": f"reports/godot-project-doctor/{profile['profile']}-plan.md",
        "ready_checks": [str(task["id"]) for task in ready_tasks],
        "packages": packages,
        "install_commands": _install_commands(packages),
        "needs_setup": [
            {
                "id": str(task["id"]),
                "package": str(task.get("package", "")),
                "expected_inputs": list(task["expected_inputs"]),
                "setup": str(task["setup"]),
            }
            for task in missing_tasks
        ],
        "commands": [
            _shell_join(
                [
                    "godot-project-doctor",
                    "run",
                    "--project",
                    ".",
                    "--checks",
                    check_list,
                    "--reports-dir",
                    reports_dir,
                    "--dry-run",
                    "--format",
                    "json",
                ]
            ),
            _shell_join(
                [
                    "godot-project-doctor",
                    "run",
                    "--project",
                    ".",
                    "--checks",
                    check_list,
                    "--reports-dir",
                    reports_dir,
                    "--format",
                    "markdown",
                    "--output",
                    f"{reports_dir}/summary.md",
                ]
            ),
            _shell_join(
                [
                    "godot-project-doctor",
                    "collect",
                    "--project",
                    ".",
                    "--checks",
                    check_list,
                    "--reports-dir",
                    reports_dir,
                    "--evidence-dir",
                    f"{reports_dir}/evidence",
                    "--skip-run",
                ]
            ),
            _shell_join(
                [
                    "godot-release-dashboard",
                    "build",
                    reports_dir,
                    "--output",
                    f"{reports_dir}/dashboard.html",
                ]
            ),
        ],
        "config_preview": config_preview,
        "workflow_preview": str(profile["workflow"]),
    }


def build_review_handoff(profile: dict[str, Any]) -> dict[str, Any]:
    project = Path(str(profile["project"]))
    reports_dir = _display_path(Path(str(profile["reports_dir"])), project)
    guided = profile.get("guided_plan", {})
    commands = list(guided.get("commands", [])) if isinstance(guided, dict) else []
    first_run = next((command for command in commands if "--dry-run" in command), "")
    report_run = next((command for command in commands if "--format markdown" in command), "")
    dashboard = next((command for command in commands if command.startswith("godot-release-dashboard build")), "")
    setup_blockers = [
        {
            "id": str(task["id"]),
            "title": str(task["title"]),
            "package": str(task.get("package", "")),
            "expected_inputs": list(task.get("expected_inputs", [])),
            "setup": str(task.get("setup", "")),
        }
        for task in profile["tasks"]
        if not task["ready"]
    ]
    return {
        "reports_dir": reports_dir,
        "first_run_command": first_run,
        "report_command": report_run,
        "dashboard_command": dashboard,
        "artifact_paths": [
            f"{reports_dir}/summary.md",
            f"{reports_dir}/evidence/manifest.json",
            f"{reports_dir}/evidence/summary.json",
            f"{reports_dir}/evidence/summary.html",
            f"{reports_dir}/dashboard.html",
        ],
        "setup_blockers": setup_blockers,
    }


def render_guided_plan_markdown(profile: dict[str, Any]) -> str:
    guided = profile["guided_plan"]
    handoff = profile.get("review_handoff", {})
    project = Path(str(profile["project"]))
    reports_dir = _display_path(Path(str(profile["reports_dir"])), project)
    lines = [
        f"# {profile['title']} First-Run Plan",
        "",
        "- Project: `.` (run commands from the project root)",
        f"- Profile: `{profile['profile']}`",
        f"- Reports: `{reports_dir}`",
        f"- Ready checks: {len(guided['ready_checks'])}",
        f"- Needs setup: {len(guided['needs_setup'])}",
        "",
        str(profile["description"]),
        "",
        "## Install",
        "",
        "Install the package set for this profile in the Python environment that will run the checks:",
        "",
    ]
    if guided["install_commands"]:
        lines.extend(f"```powershell\n{command}\n```" for command in guided["install_commands"])
    else:
        lines.append("No standalone package installs are required for this profile.")
    lines.extend(
        [
            "",
            "| Check | Package | Command |",
            "|---|---|---|",
        ]
    )
    for package in guided["packages"]:
        lines.append(f"| `{package['check']}` | `{package['package']}` | `{package['command']}` |")
    lines.extend(
        [
            "",
            "## Checks",
            "",
        ]
    )
    for task in profile["tasks"]:
        lines.extend(
            [
                f"### {task['title']}",
                "",
                f"- Check id: `{task['id']}`",
                f"- Package: `{task['package']}`",
                f"- Status: `{task['status']}`",
                f"- Why: {task['why']}",
                f"- Output: `{_display_path(Path(str(task['output'])), project)}`",
                f"- Command: `{task['command']}`",
            ]
        )
        if task["expected_inputs"]:
            lines.append(f"- Expected input: {', '.join(_display_input(item, project) for item in task['expected_inputs'])}")
        if not task["ready"]:
            lines.append(f"- Setup: {task['setup']}")
        lines.append("")
    lines.extend(["## Suggested Commands", ""])
    lines.extend(f"```powershell\n{command}\n```" for command in guided["commands"])
    if isinstance(handoff, dict):
        lines.extend(
            [
                "",
                "## Review Handoff",
                "",
                f"- Reports folder: `{handoff.get('reports_dir', reports_dir)}`",
            ]
        )
        first_run = str(handoff.get("first_run_command", ""))
        report_command = str(handoff.get("report_command", ""))
        dashboard_command = str(handoff.get("dashboard_command", ""))
        if first_run:
            lines.append(f"- First local check: `{first_run}`")
        if report_command:
            lines.append(f"- PR or release summary: `{report_command}`")
        if dashboard_command:
            lines.append(f"- Dashboard handoff: `{dashboard_command}`")
        artifacts = [str(item) for item in handoff.get("artifact_paths", [])]
        if artifacts:
            lines.extend(["", "Expected report artifacts:"])
            lines.extend(f"- `{artifact}`" for artifact in artifacts)
        blockers = list(handoff.get("setup_blockers", []))
        lines.extend(["", "Setup blockers:"])
        if blockers:
            for blocker in blockers:
                expected_inputs = ", ".join(_display_input(item, project) for item in blocker.get("expected_inputs", []))
                lines.append(
                    f"- `{blocker['id']}`: {blocker['setup']}"
                    + (f" Expected input: {expected_inputs}." if expected_inputs else "")
                )
        else:
            lines.append("- None detected for this profile.")
    lines.extend(
        [
            "",
            "## Starter Config Preview",
            "",
            "```toml",
            str(guided["config_preview"]),
            "```",
            "",
            "## GitHub Actions Preview",
            "",
            "```yaml",
            str(guided["workflow_preview"]),
            "```",
            "",
            "Review paths and package installation before using the previews in CI.",
        ]
    )
    return "\n".join(lines)


def recommend_checks_from_features(features: dict[str, Any], project: str | None = None) -> list[dict[str, str]]:
    recommended: list[dict[str, str]] = []
    rules = [
        ("export", bool(features.get("export_presets")), "export_presets.cfg is present."),
        ("assets", bool(features.get("png_assets") or features.get("import_files")), "PNG or .import files were found."),
        ("input", bool(features.get("input_map_likely")), "project.godot appears to define input actions."),
        ("localization", bool(features.get("localization_files")), "CSV/gettext localization files were found."),
        ("signals", bool(features.get("gdscript_files")), "GDScript files were found."),
        ("api_comments", bool(features.get("gdscript_files")), "GDScript files were found."),
        ("mobile_perf", bool(features.get("mobile_settings_likely")), "Mobile/display settings were found in project.godot."),
        ("save_schema", bool(features.get("save_fixtures_likely")), "Save-like JSON/TOML fixtures were found."),
        ("visual_smoke", bool(features.get("visual_smoke_likely")), "Visual/screenshot files or folders were found."),
        ("content_graph", bool(features.get("content_data_likely")), "Data/content JSON, CSV, or TOML files were found."),
        (
            "scenario_report",
            bool(features.get("scenario_results_likely") or features.get("test_framework_likely")),
            "Scenario results or a Godot test framework were found.",
        ),
        (
            "runtime_telemetry",
            bool(features.get("runtime_telemetry_likely")),
            "Runtime, telemetry, or performance JSON/CSV files were found.",
        ),
        ("mobile_ui", bool(features.get("mobile_ui_metadata_likely")), "Mobile UI metadata files were found."),
        ("architecture", bool(features.get("gdscript_files")), "GDScript files were found."),
    ]
    for check_id, enabled, reason in rules:
        if enabled:
            recommended.append(_recommendation(check_id, reason, project))
    if not recommended:
        for check_id in ("export", "assets", "input", "mobile_perf"):
            recommended.append(_recommendation(check_id, "Good first check for a Godot project.", project))
    return recommended


def _doctor_task(plan_item: dict[str, Any], project: Path) -> dict[str, Any]:
    check_id = str(plan_item["id"])
    guidance = CHECK_GUIDANCE.get(check_id, {"why": "", "when": ""})
    expected_inputs = _expected_inputs(check_id, project)
    return {
        "id": check_id,
        "title": str(plan_item["title"]),
        "ready": bool(plan_item["enabled"]),
        "status": "ready" if plan_item["enabled"] else "needs_setup",
        "reason": str(plan_item.get("reason", "")),
        "why": guidance["why"],
        "when": guidance["when"],
        "expected_inputs": expected_inputs,
        "package": _package_for_check(check_id),
        "install": _install_command(_package_for_check(check_id)),
        "output": str(plan_item["report"]),
        "command": _shell_join([_display_input(part, project) for part in plan_item["argv"]]),
        "setup": _profile_setup_note(check_id, expected_inputs),
    }


def _profile_reports_dir(project: Path, profile: str, reports_dir: Path | None) -> Path:
    if reports_dir is None:
        return project / f"reports/godot-project-doctor/{profile}"
    if reports_dir.is_absolute():
        return reports_dir
    return project / reports_dir


def _expected_inputs(check_id: str, project: Path) -> list[str]:
    hints = {
        "export": ["export_presets.cfg"],
        "assets": ["PNG assets and .import files"],
        "input": ["project.godot [input] actions"],
        "localization": ["CSV, PO, POT, or MO localization files"],
        "mobile_perf": ["project.godot display/rendering settings"],
        "mobile_ui": ["mobile UI metadata JSON"],
        "visual_smoke": ["visual-smoke.toml capture plan"],
        "content_graph": ["content-graph.toml and JSON/CSV/TOML content files"],
        "pack_mod": ["pack manifest JSON"],
        "save_schema": ["save fixtures directory and JSON schema"],
        "scenario_report": ["scenario result JSON file or folder"],
        "runtime_telemetry": ["runtime telemetry JSON/CSV file or folder"],
        "architecture": ["architecture-guard.toml and GDScript files"],
        "signals": ["Godot scenes and GDScript files"],
        "api_comments": ["GDScript files"],
    }
    return [str(project / hint) if hint.endswith((".cfg", ".toml")) else hint for hint in hints.get(check_id, [])]


def _profile_setup_note(check_id: str, expected_inputs: list[str]) -> str:
    config_hint = _config_hint(check_id)
    if config_hint == "ready from project path":
        return "No extra config is usually needed; run the command and review the report."
    return f"Provide {', '.join(expected_inputs) if expected_inputs else config_hint}."


def _package_for_check(check_id: str) -> str:
    for spec in TOOL_REGISTRY:
        if spec.id == check_id:
            return spec.package
    return ""


def _packages_for_checks(checks: list[str]) -> list[dict[str, str]]:
    packages: list[dict[str, str]] = []
    seen: set[str] = set()
    for check_id in checks:
        package = _package_for_check(check_id)
        if not package or package in seen:
            continue
        seen.add(package)
        packages.append(
            {
                "check": check_id,
                "package": package,
                "command": _command_for_check(check_id),
                "install": _install_command(package),
            }
        )
    return packages


def _install_commands(packages: list[dict[str, str]]) -> list[str]:
    if not packages:
        return []
    package_names = [str(item["package"]) for item in packages]
    return [_shell_join(["python", "-m", "pip", "install", *package_names])]


def _install_command(package: str) -> str:
    return _shell_join(["python", "-m", "pip", "install", package]) if package else ""


def _command_for_check(check_id: str) -> str:
    for spec in TOOL_REGISTRY:
        if spec.id == check_id:
            return spec.command
    return ""


def _display_path(path: Path, project: Path) -> str:
    try:
        return path.resolve().relative_to(project.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _display_input(value: object, project: Path) -> str:
    text = str(value)
    path = Path(text)
    if path.is_absolute():
        return _display_path(path, project)
    return text


def _shell_join(parts: list[str]) -> str:
    return " ".join(_quote_shell_part(part) for part in parts)


def _quote_shell_part(value: str) -> str:
    if not value:
        return '""'
    if any(char.isspace() for char in value):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def render_starter_config(project: Path, reports_dir: str = "reports/godot-project-doctor") -> str:
    inspected = inspect_project(project)
    checks = [item["id"] for item in inspected["recommendations"][:6]]
    quoted_checks = ", ".join(f'"{check}"' for check in checks)
    lines = [
        "[project]",
        'path = "."',
        f'reports_dir = "{reports_dir}"',
        'fail_on = "error"',
        f"checks = [{quoted_checks}]",
        "",
        "# Enable specialized checks when their config files exist.",
        "# [tools.visual_smoke]",
        '# config = "visual-smoke.toml"',
        "",
        "# [tools.save_schema]",
        '# fixtures = "tests/fixtures/saves"',
        '# schema = "schemas/save.schema.json"',
        "",
        "# [tools.content_graph]",
        '# config = "content-graph.toml"',
        "",
        "# [tools.pack_mod]",
        '# manifest = "pack-manifest.json"',
        "",
        "# [tools.scenario_report]",
        '# path = "reports/scenarios"',
        "",
        "# [tools.runtime_telemetry]",
        '# path = "reports/runtime"',
        "",
        "# [tools.architecture]",
        '# config = "architecture-guard.toml"',
        "",
        "# [tools.mobile_ui]",
        '# metadata = "reports/mobile-ui.json"',
    ]
    return "\n".join(lines)


def render_github_action_example(checks: list[str] | None = None) -> str:
    check_text = ",".join(checks or ["assets", "export", "input", "localization", "signals", "mobile_perf"])
    return "\n".join(
        [
            "name: Godot release evidence",
            "",
            "on:",
            "  pull_request:",
            "  workflow_dispatch:",
            "",
            "jobs:",
            "  godot-release-evidence:",
            "    runs-on: ubuntu-latest",
            "    steps:",
            "      - uses: actions/checkout@v4",
            "      - uses: NonniGB/godot-production-toolkit/godot-ci-doctor-action@v0.1.2",
            "        with:",
            "          project: .",
            f"          checks: {check_text}",
            "          fail-on: error",
            "          reports-dir: reports/godot-project-doctor",
        ]
    )


def explain_check(check_id: str) -> dict[str, str]:
    if check_id not in CHECK_GUIDANCE:
        known = ", ".join(sorted(CHECK_GUIDANCE))
        raise KeyError(f"unknown check id {check_id!r}; known ids: {known}")
    guidance = CHECK_GUIDANCE[check_id]
    return {
        "id": check_id,
        "title": _title_for_check(check_id),
        "why": guidance["why"],
        "when": guidance["when"],
    }


def run_plan(plan: dict[str, Any], dry_run: bool = False, timeout: int = 120) -> dict[str, Any]:
    if dry_run:
        return {"status": "planned", **plan}

    reports_dir = Path(str(plan["reports_dir"]))
    reports_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for command in plan["commands"]:
        completed = subprocess.run(command["argv"], capture_output=True, text=True, timeout=timeout, check=False)
        results.append(
            {
                "id": command["id"],
                "returncode": completed.returncode,
                "stdout": completed.stdout[-4000:],
                "stderr": completed.stderr[-4000:],
                "report": command["report"],
            }
        )
    summary = summarize_reports(reports_dir)
    return {"status": "completed", "plan": plan, "results": results, "summary": summary["summary"], "reports": summary["reports"]}


def collect_evidence(
    plan: dict[str, Any],
    evidence_dir: Path,
    skip_run: bool = False,
    timeout: int = 120,
) -> dict[str, Any]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    run_result: dict[str, Any] | None = None
    if not skip_run:
        run_result = run_plan(plan, timeout=timeout)

    summary = summarize_reports(Path(str(plan["reports_dir"])), commands=plan["commands"])
    manifest = {
        "tool": "godot-project-doctor",
        "schema_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project": plan["project"],
        "reports_dir": plan["reports_dir"],
        "evidence_dir": str(evidence_dir),
        "fail_on": plan["fail_on"],
        "commands": plan["commands"],
        "tool_versions": _tool_versions(plan),
        "run_results": run_result["results"] if run_result else [],
        "summary": summary["summary"],
        "reports": summary["reports"],
        "artifacts": _all_artifacts(summary["reports"]),
    }
    (evidence_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    from .reports import render_summary

    (evidence_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (evidence_dir / "summary.md").write_text(render_summary(summary, "markdown") + "\n", encoding="utf-8")
    (evidence_dir / "summary.html").write_text(render_summary(summary, "html") + "\n", encoding="utf-8")
    (evidence_dir / "artifacts.json").write_text(
        json.dumps(manifest["artifacts"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def summarize_reports(reports_dir: Path, commands: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    command_by_report = _commands_by_report_path(commands or [])
    reports: list[dict[str, Any]] = []
    for path in sorted(reports_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        errors, warnings = _severity_counts(data)
        report = {
            "tool": _tool_name(data, path),
            "path": str(path),
            "source_report_path": str(path),
            "summary": {"errors": errors, "warnings": warnings},
            "finding_count": _finding_count(data),
            "findings": _findings(data),
            "artifacts": _artifact_paths(data),
        }
        command = command_by_report.get(str(path.resolve()))
        if command:
            report["reproduction"] = {
                "check_id": str(command["id"]),
                "command": _shell_join([str(part) for part in command["argv"]]),
                "source_report_path": str(path),
            }
        reports.append(report)
    return {
        "tool": "godot-project-doctor",
        "reports_dir": str(reports_dir),
        "summary": {
            "tools": len(reports),
            "errors": sum(int(report["summary"]["errors"]) for report in reports),
            "warnings": sum(int(report["summary"]["warnings"]) for report in reports),
        },
        "reports": reports,
    }


def _commands_by_report_path(commands: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for command in commands:
        report_path = command.get("report")
        if report_path:
            indexed[str(Path(str(report_path)).resolve())] = command
    return indexed


def compare_report_dirs(baseline_dir: Path, current_dir: Path) -> dict[str, Any]:
    baseline = summarize_reports(baseline_dir)
    current = summarize_reports(current_dir)
    baseline_by_tool = {str(report["tool"]): report for report in baseline["reports"]}
    current_by_tool = {str(report["tool"]): report for report in current["reports"]}
    tool_names = sorted(set(baseline_by_tool) | set(current_by_tool))

    comparisons: list[dict[str, Any]] = []
    for tool_name in tool_names:
        baseline_report = baseline_by_tool.get(tool_name)
        current_report = current_by_tool.get(tool_name)
        before = _comparison_counts(baseline_report)
        after = _comparison_counts(current_report)
        delta = {
            "errors": after["errors"] - before["errors"],
            "warnings": after["warnings"] - before["warnings"],
            "findings": after["findings"] - before["findings"],
        }
        comparisons.append(
            {
                "tool": tool_name,
                "status": _comparison_status(baseline_report, current_report, delta),
                "baseline": before,
                "current": after,
                "delta": delta,
                "baseline_path": baseline_report["path"] if baseline_report else None,
                "current_path": current_report["path"] if current_report else None,
            }
        )

    return {
        "tool": "godot-project-doctor",
        "baseline_reports_dir": str(baseline_dir),
        "current_reports_dir": str(current_dir),
        "summary": {
            "tools": len(comparisons),
            "regressions": sum(1 for item in comparisons if item["status"] == "regressed"),
            "improvements": sum(1 for item in comparisons if item["status"] == "improved"),
            "new_tools": sum(1 for item in comparisons if item["status"] == "new"),
            "removed_tools": sum(1 for item in comparisons if item["status"] == "removed"),
            "error_delta": sum(int(item["delta"]["errors"]) for item in comparisons),
            "warning_delta": sum(int(item["delta"]["warnings"]) for item in comparisons),
            "finding_delta": sum(int(item["delta"]["findings"]) for item in comparisons),
        },
        "comparisons": comparisons,
    }


def exit_code_for_compare(comparison: dict[str, Any], fail_on: str) -> int:
    if fail_on == "none":
        return 0
    for item in comparison["comparisons"]:
        delta = item["delta"]
        if fail_on == "error" and int(delta["errors"]) > 0:
            return 1
        if fail_on == "warning" and (int(delta["errors"]) > 0 or int(delta["warnings"]) > 0):
            return 1
    return 0


def exit_code_for_summary(summary: dict[str, Any], fail_on: str) -> int:
    totals = summary["summary"] if "summary" in summary else summary
    if fail_on == "none":
        return 0
    if fail_on == "warning" and int(totals["errors"]) + int(totals["warnings"]) > 0:
        return 1
    if fail_on == "error" and int(totals["errors"]) > 0:
        return 1
    return 0


def _comparison_counts(report: dict[str, Any] | None) -> dict[str, int]:
    if not report:
        return {"errors": 0, "warnings": 0, "findings": 0}
    summary = report["summary"]
    return {
        "errors": int(summary["errors"]),
        "warnings": int(summary["warnings"]),
        "findings": int(report.get("finding_count", 0)),
    }


def _comparison_status(
    baseline_report: dict[str, Any] | None,
    current_report: dict[str, Any] | None,
    delta: dict[str, int],
) -> str:
    if baseline_report is None:
        return "new"
    if current_report is None:
        return "removed"
    if delta["errors"] > 0 or delta["warnings"] > 0:
        return "regressed"
    if delta["errors"] < 0 or delta["warnings"] < 0 or delta["findings"] < 0:
        return "improved"
    if delta["findings"] > 0:
        return "changed"
    return "unchanged"


def _selected_checks(project_config: dict[str, Any], cli_checks: list[str] | None) -> set[str] | None:
    raw_checks = cli_checks if cli_checks is not None else project_config.get("checks")
    if not raw_checks:
        return None
    if isinstance(raw_checks, str):
        raw_checks = [item.strip() for item in raw_checks.split(",")]
    return {str(item).strip() for item in raw_checks if str(item).strip()}


def _is_enabled(spec: ToolSpec, selected: set[str] | None, config: dict[str, Any]) -> bool:
    if "enabled" in config:
        return bool(config["enabled"])
    if selected is not None:
        return spec.id in selected
    return spec.default_enabled


def _disabled_reason(spec: ToolSpec, selected: set[str] | None, config: dict[str, Any]) -> str:
    if config.get("enabled") is False:
        return "disabled by config"
    if selected is not None and spec.id not in selected:
        return "not selected"
    if not spec.default_enabled:
        return "specialized tool; enable with required config"
    return ""


def _build_tool_argv(spec: ToolSpec, project: Path, report_path: Path, config: dict[str, Any]) -> list[str]:
    args = [str(item) for item in config.get("args", [])]
    if spec.id == "save_schema":
        return [
            spec.command,
            "validate",
            str(_resolve_path(project, str(config.get("fixtures", ".")))),
            "--schema",
            str(_resolve_path(project, str(config.get("schema", "schema.json")))),
            "--format",
            "json",
            "--output",
            str(report_path),
            *args,
        ]
    if spec.id == "visual_smoke":
        return [
            spec.command,
            "plan",
            str(_resolve_path(project, str(config.get("config", "visual-smoke.toml")))),
            "--project",
            str(project),
            "--format",
            "json",
            *args,
        ]
    if spec.id == "pixel_assets":
        command = str(config.get("command", "preview"))
        return [spec.command, command, *args, "--format", "json"]
    if spec.id == "content_graph":
        return [
            spec.command,
            str(project),
            "--config",
            str(_resolve_path(project, str(config.get("config", "content-graph.toml")))),
            "--format",
            "json",
            "--output",
            str(report_path),
            *args,
        ]
    if spec.id == "pack_mod":
        argv = [
            spec.command,
            "check",
            str(_resolve_path(project, str(config.get("manifest", "pack-manifest.json")))),
        ]
        if config.get("base"):
            argv.extend(["--base", str(_resolve_path(project, str(config.get("base"))))])
        if config.get("allow_overrides"):
            argv.append("--allow-overrides")
        argv.extend(["--format", "json", "--output", str(report_path), *args])
        return argv
    if spec.id == "scenario_report":
        return [
            spec.command,
            "summarize",
            str(_resolve_path(project, str(config.get("path", "reports/scenarios")))),
            "--format",
            "json",
            "--output",
            str(report_path),
            *args,
        ]
    if spec.id == "runtime_telemetry":
        return [
            spec.command,
            "summarize",
            str(_resolve_path(project, str(config.get("path", "reports/runtime")))),
            "--format",
            "json",
            "--output",
            str(report_path),
            *args,
        ]
    if spec.id == "mobile_ui":
        return [
            spec.command,
            str(_resolve_path(project, str(config.get("metadata", "mobile-ui.json")))),
            "--format",
            "json",
            "--output",
            str(report_path),
            *args,
        ]
    if spec.id == "architecture":
        return [
            spec.command,
            str(project),
            "--config",
            str(_resolve_path(project, str(config.get("config", "architecture-guard.toml")))),
            "--format",
            "json",
            "--output",
            str(report_path),
            *args,
        ]

    return [
        spec.command,
        str(project),
        *spec.base_args,
        "--format",
        "json",
        "--output",
        str(report_path),
        *args,
    ]


def _resolve_path(base: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    return (base / path).resolve()


def _project_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    if not root.exists():
        return []
    ignored = {".git", ".godot", ".import", "__pycache__", "dist", "build"}
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in ignored for part in path.parts):
            continue
        if path.is_file():
            files.append(path)
    return files


def _file_contains(path: Path, needle: str) -> bool:
    if not path.exists():
        return False
    try:
        return needle in path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False


def _project_name(project_file: Path) -> str | None:
    if not project_file.exists():
        return None
    try:
        for line in project_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if stripped.startswith("config/name="):
                return stripped.split("=", 1)[1].strip().strip('"')
    except OSError:
        return None
    return None


def _sample_paths(paths: list[str], predicate: Any, limit: int = 5) -> list[str]:
    return [path for path in paths if predicate(path)][:limit]


def _detect_test_frameworks(paths: list[str], names: set[str]) -> list[str]:
    frameworks: list[str] = []
    if "gut" in names or any("addons/gut" in path.lower() for path in paths):
        frameworks.append("GUT")
    if "gdunit4" in names or any("addons/gdunit4" in path.lower() for path in paths):
        frameworks.append("GdUnit4")
    return frameworks


def _recommendation(check_id: str, reason: str, project: str | None) -> dict[str, str]:
    guidance = CHECK_GUIDANCE[check_id]
    config_hint = _config_hint(check_id)
    command_project = project or "<project>"
    return {
        "id": check_id,
        "title": _title_for_check(check_id),
        "priority": _priority_for_check(check_id),
        "reason": reason,
        "why": guidance["why"],
        "when": guidance["when"],
        "config": config_hint,
        "package": _package_for_check(check_id),
        "install": _install_command(_package_for_check(check_id)),
        "command": f"godot-project-doctor run --project {command_project} --checks {check_id} --dry-run",
    }


def _priority_for_check(check_id: str) -> str:
    if check_id in {"export", "assets", "input", "localization", "mobile_perf", "content_graph", "pack_mod"}:
        return "high"
    if check_id in {"api_comments", "signals", "architecture", "scenario_report", "runtime_telemetry"}:
        return "medium"
    return "specialized"


def _config_hint(check_id: str) -> str:
    for spec in TOOL_REGISTRY:
        if spec.id == check_id:
            if spec.required_config:
                return f"needs config: {', '.join(spec.required_config)}"
            return "ready from project path"
    return "ready from project path"


def _title_for_check(check_id: str) -> str:
    for spec in TOOL_REGISTRY:
        if spec.id == check_id:
            return spec.title
    return check_id.replace("_", " ").title()


def _tool_name(data: dict[str, Any], path: Path) -> str:
    return str(data.get("tool") or data.get("name") or path.stem)


def _severity_counts(data: dict[str, Any]) -> tuple[int, int]:
    summary = data.get("summary", {})
    errors = int(summary.get("errors", summary.get("error_count", 0)))
    warnings = int(summary.get("warnings", summary.get("warning_count", 0)))
    if errors or warnings:
        return errors, warnings

    errors = 0
    warnings = 0
    for finding in _findings(data):
        severity = str(finding.get("severity", "")).lower()
        if severity == "error":
            errors += 1
        elif severity == "warning":
            warnings += 1
    return errors, warnings


def _finding_count(data: dict[str, Any]) -> int:
    return len(_findings(data))


def _findings(data: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("findings", "issues"):
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _artifact_paths(data: Any) -> list[str]:
    values: list[str] = []

    def walk(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                walk(child_value, str(child_key))
            return
        if isinstance(value, list):
            for item in value:
                walk(item, key)
            return
        if isinstance(value, str) and key in {"artifact", "artifacts", "screenshot", "screenshots", "diff"}:
            values.append(value)

    walk(data)
    return sorted(set(values))


def _all_artifacts(reports: list[dict[str, Any]]) -> list[dict[str, str]]:
    indexed: list[dict[str, str]] = []
    for report in reports:
        for artifact in report.get("artifacts", []):
            indexed.append({"tool": str(report["tool"]), "path": str(artifact)})
    return indexed


def _tool_versions(plan: dict[str, Any]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for command in plan["commands"]:
        argv = command.get("argv", [])
        if not argv:
            continue
        executable = str(argv[0])
        try:
            completed = subprocess.run(
                [executable, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            versions[str(command["id"])] = "unavailable"
            continue
        version_text = (completed.stdout or completed.stderr).strip()
        versions[str(command["id"])] = version_text or f"{executable} exited {completed.returncode}"
    return versions
