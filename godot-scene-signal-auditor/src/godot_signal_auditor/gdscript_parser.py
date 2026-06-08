from __future__ import annotations

import re
from pathlib import Path

from .models import ConnectCall, ParsedScript

SIGNAL_RE = re.compile(r"^\s*signal\s+([A-Za-z_]\w*)")
FUNC_RE = re.compile(r"^\s*(?:static\s+)?func\s+([A-Za-z_]\w*)\s*\(")
AUTOLOAD_CONNECT_RE = re.compile(r"\b([A-Za-z_]\w*)\.([A-Za-z_]\w*)\.connect\(")
STRING_CONNECT_RE = re.compile(r'\.connect\(\s*"([^"]+)"')


def parse_gdscript_signals(path: Path, content: str, *, autoloads: set[str] | None = None) -> ParsedScript:
    autoloads = autoloads or set()
    signals: set[str] = set()
    methods: set[str] = set()
    connect_calls: list[ConnectCall] = []

    for line_number, line in enumerate(content.splitlines(), start=1):
        signal_match = SIGNAL_RE.match(line)
        if signal_match:
            signals.add(signal_match.group(1))

        func_match = FUNC_RE.match(line)
        if func_match:
            methods.add(func_match.group(1))

        for match in AUTOLOAD_CONNECT_RE.finditer(line):
            owner, signal = match.groups()
            if owner in autoloads:
                connect_calls.append(ConnectCall(path=path, line=line_number, signal=signal, autoload=owner))

        string_match = STRING_CONNECT_RE.search(line)
        if string_match:
            connect_calls.append(ConnectCall(path=path, line=line_number, signal=string_match.group(1)))

    return ParsedScript(path=path, signals=signals, methods=methods, connect_calls=connect_calls)
