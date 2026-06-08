from __future__ import annotations

from collections import defaultdict

from .models import Finding, InputAction


def evaluate_actions(actions: list[InputAction], required_devices: set[str]) -> list[Finding]:
    findings: list[Finding] = []
    if not actions:
        return [
            Finding(
                rule_id="input_map_empty",
                severity="warning",
                action=None,
                message="No input actions were found in the [input] section.",
            )
        ]

    for action in actions:
        if not action.events:
            findings.append(
                Finding(
                    rule_id="action_has_no_events",
                    severity="warning",
                    action=action.name,
                    message=f"Input action '{action.name}' has no bound events.",
                )
            )
        missing = sorted(required_devices - action.devices)
        if missing:
            findings.append(
                Finding(
                    rule_id="missing_required_device",
                    severity="error",
                    action=action.name,
                    message=f"Input action '{action.name}' is missing required device(s): {', '.join(missing)}.",
                )
            )

    findings.extend(_duplicate_binding_findings(actions))
    return findings


def _duplicate_binding_findings(actions: list[InputAction]) -> list[Finding]:
    by_signature: dict[str, list[str]] = defaultdict(list)
    for action in actions:
        for event in action.events:
            if event.signature:
                by_signature[event.signature].append(action.name)

    findings: list[Finding] = []
    for signature, action_names in sorted(by_signature.items()):
        unique_names = sorted(set(action_names))
        if len(unique_names) > 1:
            findings.append(
                Finding(
                    rule_id="duplicate_binding",
                    severity="warning",
                    action=None,
                    message=(
                        f"Binding '{signature}' is used by multiple actions: "
                        f"{', '.join(unique_names)}."
                    ),
                )
            )
    return findings
