from __future__ import annotations

import json
from pathlib import Path

TOOLS = [
    "godot-asset-pipeline-doctor",
    "godot-export-preset-doctor",
    "gdscript-api-comment-coverage",
    "godot-input-map-auditor",
    "godot-localization-qa-guard",
    "godot-save-schema-guard",
    "godot-scene-signal-auditor",
    "godot-visual-smoke-test-kit",
    "godot-mobile-perf-doctor",
    "pixel-space-asset-toolkit",
    "godot-project-doctor",
    "godot-ci-doctor-action",
]

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "name",
    "entrypoint",
    "module",
    "interfaces",
    "agent_contract",
    "recommended_commands",
}
REQUIRED_INTERFACES = {"cli", "machine_output", "human_output"}
REQUIRED_CONTRACT = {"noninteractive", "safe_on_private_projects", "network_required", "exit_codes"}


def main() -> int:
    root = Path(__file__).resolve().parent
    errors: list[str] = []
    for tool in TOOLS:
        manifest_path = root / tool / "agent-tool.json"
        if not manifest_path.exists():
            errors.append(f"{tool}: missing agent-tool.json")
            continue
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        missing = REQUIRED_TOP_LEVEL - set(data)
        if missing:
            errors.append(f"{tool}: missing top-level keys {sorted(missing)}")
        interface_missing = REQUIRED_INTERFACES - set(data.get("interfaces", {}))
        if interface_missing:
            errors.append(f"{tool}: missing interface keys {sorted(interface_missing)}")
        contract_missing = REQUIRED_CONTRACT - set(data.get("agent_contract", {}))
        if contract_missing:
            errors.append(f"{tool}: missing contract keys {sorted(contract_missing)}")
        if not data.get("recommended_commands"):
            errors.append(f"{tool}: recommended_commands is empty")

    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"Validated {len(TOOLS)} agent tool manifests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
