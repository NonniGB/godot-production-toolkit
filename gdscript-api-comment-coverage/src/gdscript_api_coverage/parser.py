from __future__ import annotations

import re
from pathlib import Path

from .models import ApiItem

CLASS_RE = re.compile(r"^\s*class_name\s+([A-Za-z_]\w*)")
SIGNAL_RE = re.compile(r"^\s*signal\s+([A-Za-z_]\w*)")
FUNC_RE = re.compile(r"^\s*(?:static\s+)?func\s+([A-Za-z_]\w*)\s*\(")
VAR_RE = re.compile(r"^\s*(?:@export(?:\([^)]*\))?\s*)?var\s+([A-Za-z_]\w*)")
CONST_RE = re.compile(r"^\s*const\s+([A-Za-z_]\w*)")


def parse_gdscript(path: Path, content: str) -> list[ApiItem]:
    items: list[ApiItem] = []
    pending_comment = False
    pending_export = False

    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        stripped = raw_line.strip()

        if not stripped:
            pending_comment = False
            pending_export = False
            continue

        if stripped.startswith("##") or stripped.startswith("#"):
            pending_comment = True
            continue

        if stripped.startswith("@export") and " var " not in f" {stripped} ":
            pending_export = True
            continue

        item = _parse_api_line(path, line_number, stripped, pending_comment, pending_export)
        if item:
            items.append(item)
            pending_comment = False
            pending_export = False
            continue

        pending_comment = False
        if not stripped.startswith("@"):
            pending_export = False

    return items


def _parse_api_line(
    path: Path,
    line_number: int,
    stripped: str,
    pending_comment: bool,
    pending_export: bool,
) -> ApiItem | None:
    class_match = CLASS_RE.match(stripped)
    if class_match:
        return _item(path, line_number, "class", class_match.group(1), pending_comment, stripped)

    signal_match = SIGNAL_RE.match(stripped)
    if signal_match:
        return _item(path, line_number, "signal", signal_match.group(1), pending_comment, stripped)

    var_match = VAR_RE.match(stripped)
    if var_match and (pending_export or stripped.startswith("@export")):
        return _item(
            path,
            line_number,
            "exported_property",
            var_match.group(1),
            pending_comment,
            stripped,
        )

    func_match = FUNC_RE.match(stripped)
    if func_match:
        name = func_match.group(1)
        if not name.startswith("_"):
            return _item(path, line_number, "public_func", name, pending_comment, stripped)

    const_match = CONST_RE.match(stripped)
    if const_match:
        name = const_match.group(1)
        if not name.startswith("_"):
            return _item(path, line_number, "constant", name, pending_comment, stripped)

    return None


def _item(
    path: Path,
    line_number: int,
    kind: str,
    name: str,
    documented: bool,
    signature: str,
) -> ApiItem:
    return ApiItem(
        path=path.as_posix(),
        line=line_number,
        kind=kind,
        name=name,
        documented=documented,
        signature=signature,
    )
