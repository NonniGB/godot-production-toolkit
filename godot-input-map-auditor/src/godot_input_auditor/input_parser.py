from __future__ import annotations

import re

from .models import InputAction, InputEvent

SECTION_RE = re.compile(r"^\[([^\]]+)\]$")
EVENT_RE = re.compile(r"Object\((InputEvent[A-Za-z0-9_]+)(.*?)\)", re.DOTALL)


def parse_input_map(project_godot_content: str) -> list[InputAction]:
    actions: list[InputAction] = []
    in_input_section = False
    current_name: str | None = None
    current_lines: list[str] = []
    brace_depth = 0

    for raw_line in project_godot_content.splitlines():
        line = raw_line.strip()
        section = SECTION_RE.match(line)
        if section:
            if current_name is not None:
                actions.append(_parse_action(current_name, "\n".join(current_lines)))
                current_name = None
                current_lines = []
                brace_depth = 0
            in_input_section = section.group(1) == "input"
            continue

        if not in_input_section or not line or line.startswith(";") or line.startswith("#"):
            continue

        if current_name is None:
            if "=" not in line:
                continue
            name, rest = line.split("=", 1)
            current_name = name.strip().strip('"')
            current_lines = [rest]
            brace_depth = rest.count("{") - rest.count("}")
            if brace_depth <= 0:
                actions.append(_parse_action(current_name, "\n".join(current_lines)))
                current_name = None
                current_lines = []
            continue

        current_lines.append(line)
        brace_depth += line.count("{") - line.count("}")
        if brace_depth <= 0:
            actions.append(_parse_action(current_name, "\n".join(current_lines)))
            current_name = None
            current_lines = []
            brace_depth = 0

    if current_name is not None:
        actions.append(_parse_action(current_name, "\n".join(current_lines)))

    return actions


def _parse_action(name: str, body: str) -> InputAction:
    events = []
    for match in EVENT_RE.finditer(body):
        event_type = match.group(1)
        event_body = match.group(2)
        device = _classify_event(event_type)
        events.append(InputEvent(event_type=event_type, device=device, signature=_signature(event_type, event_body)))
    return InputAction(name=name, events=events)


def _classify_event(event_type: str) -> str:
    if event_type == "InputEventKey":
        return "keyboard"
    if event_type in {"InputEventMouseButton", "InputEventMouseMotion"}:
        return "mouse"
    if event_type in {"InputEventJoypadButton", "InputEventJoypadMotion"}:
        return "gamepad"
    if event_type in {"InputEventScreenTouch", "InputEventScreenDrag", "InputEventGesture"}:
        return "touch"
    return "unknown"


def _signature(event_type: str, event_body: str) -> str:
    if event_type == "InputEventKey":
        return f"keyboard:key:{_field(event_body, 'physical_keycode') or _field(event_body, 'keycode')}"
    if event_type == "InputEventMouseButton":
        return f"mouse:button:{_field(event_body, 'button_index')}"
    if event_type == "InputEventJoypadButton":
        return f"gamepad:button:{_field(event_body, 'button_index')}"
    if event_type == "InputEventJoypadMotion":
        return f"gamepad:axis:{_field(event_body, 'axis')}"
    if event_type in {"InputEventScreenTouch", "InputEventScreenDrag", "InputEventGesture"}:
        return f"touch:index:{_field(event_body, 'index') or 'any'}"
    return f"{event_type}:{' '.join(event_body.split())}"


def _field(event_body: str, name: str) -> str:
    match = re.search(rf'"{re.escape(name)}"\s*:\s*([^,\)]+)', event_body)
    if not match:
        return ""
    return match.group(1).strip().strip('"')
