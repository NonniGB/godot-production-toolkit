from __future__ import annotations

import re
from pathlib import Path

from .models import ConnectCall, ParsedScript

SIGNAL_RE = re.compile(r"^\s*signal\s+([A-Za-z_]\w*)")
FUNC_RE = re.compile(r"^\s*(?:static\s+)?func\s+([A-Za-z_]\w*)\s*\(")
EXPORT_INLINE_RE = re.compile(r"^\s*@export(?:_[A-Za-z_]\w*)?(?:\([^)]*\))?\s+(?:var\s+)?([A-Za-z_]\w*)")
VAR_RE = re.compile(r"^\s*var\s+([A-Za-z_]\w*)")
AUTOLOAD_CONNECT_RE = re.compile(r"\b([A-Za-z_]\w*)\.([A-Za-z_]\w*)\.connect\(")
STRING_CONNECT_RE = re.compile(r'\.connect\(\s*"([^"]+)"')
NON_PROPERTY_EXPORT_PREFIXES = ("@export_category", "@export_group", "@export_subgroup")


def parse_gdscript_signals(path: Path, content: str, *, autoloads: set[str] | None = None) -> ParsedScript:
    autoloads = autoloads or set()
    signals: set[str] = set()
    methods: set[str] = set()
    exported_properties: set[str] = set()
    connect_calls: list[ConnectCall] = []
    pending_export = False

    for line_number, line in enumerate(content.splitlines(), start=1):
        signal_match = SIGNAL_RE.match(line)
        if signal_match:
            signals.add(signal_match.group(1))

        func_match = FUNC_RE.match(line)
        if func_match:
            methods.add(func_match.group(1))

        stripped = line.strip()
        if _is_property_export_annotation(stripped):
            inline_match = EXPORT_INLINE_RE.match(line)
            if inline_match:
                exported_properties.add(inline_match.group(1))
                pending_export = False
            else:
                pending_export = True
            continue

        if pending_export:
            var_match = VAR_RE.match(line)
            if var_match:
                exported_properties.add(var_match.group(1))
            pending_export = False

        for match in AUTOLOAD_CONNECT_RE.finditer(line):
            owner, signal = match.groups()
            if owner in autoloads:
                connect_calls.append(ConnectCall(path=path, line=line_number, signal=signal, autoload=owner))

        string_match = STRING_CONNECT_RE.search(line)
        if string_match:
            connect_calls.append(ConnectCall(path=path, line=line_number, signal=string_match.group(1)))

    return ParsedScript(
        path=path,
        signals=signals,
        methods=methods,
        connect_calls=connect_calls,
        exported_properties=exported_properties,
    )


def _is_property_export_annotation(stripped_line: str) -> bool:
    return stripped_line.startswith("@export") and not stripped_line.startswith(NON_PROPERTY_EXPORT_PREFIXES)
