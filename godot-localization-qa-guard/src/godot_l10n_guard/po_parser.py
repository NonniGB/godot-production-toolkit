from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

from .models import PoCatalog, TranslationEntry


def parse_po_file(path: Path) -> PoCatalog:
    language = path.stem
    entries: list[TranslationEntry] = []
    flags: set[str] = set()
    msgid: str | None = None
    msgstr: str | None = None
    msgid_line = 0
    state: str | None = None

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if line.startswith("#,"):
            flags.update(part.strip() for part in line[2:].split(","))
            continue
        if line.startswith("msgid "):
            if msgid is not None:
                _append_entry(entries, language, path, msgid, msgstr or "", flags, msgid_line)
            msgid = _po_string(line[6:])
            msgstr = ""
            msgid_line = line_number
            state = "msgid"
            continue
        if line.startswith("msgstr "):
            msgstr = _po_string(line[7:])
            state = "msgstr"
            continue
        if line.startswith('"') and state == "msgid" and msgid is not None:
            msgid += _po_string(line)
            continue
        if line.startswith('"') and state == "msgstr" and msgstr is not None:
            msgstr += _po_string(line)
            continue
        if not line and msgid is not None:
            _append_entry(entries, language, path, msgid, msgstr or "", flags, msgid_line)
            msgid = None
            msgstr = None
            flags = set()
            state = None

    if msgid is not None:
        _append_entry(entries, language, path, msgid, msgstr or "", flags, msgid_line)

    keys = [entry.key for entry in entries]
    duplicate_keys = {key for key, count in Counter(keys).items() if count > 1}
    return PoCatalog(path=str(path), language=language, entries=entries, duplicate_keys=duplicate_keys)


def _append_entry(
    entries: list[TranslationEntry],
    language: str,
    path: Path,
    msgid: str,
    msgstr: str,
    flags: set[str],
    line: int,
) -> None:
    if not msgid:
        return
    entries.append(
        TranslationEntry(
            key=msgid,
            source=msgid,
            translations={language: msgstr},
            path=str(path),
            line=line,
            fuzzy="fuzzy" in flags,
        )
    )


def _po_string(raw: str) -> str:
    try:
        return ast.literal_eval(raw)
    except (SyntaxError, ValueError):
        return raw.strip().strip('"')
