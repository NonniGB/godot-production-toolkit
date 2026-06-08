from __future__ import annotations

import csv
from collections import Counter
from io import StringIO
from pathlib import Path

from .models import CsvTable, TranslationEntry


def parse_csv_file(path: Path) -> CsvTable:
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    rows = list(csv.reader(StringIO(text)))
    if not rows:
        return CsvTable(str(path), [], [], had_bom=had_bom, has_keys_header=False)

    header = [cell.strip() for cell in rows[0]]
    has_keys_header = bool(header) and header[0] == "keys"
    languages = header[1:] if has_keys_header else []
    entries: list[TranslationEntry] = []
    keys: list[str] = []

    if has_keys_header:
        for line_number, row in enumerate(rows[1:], start=2):
            if not row:
                continue
            key = row[0].strip()
            if not key:
                continue
            values = list(row[1:])
            while len(values) < len(languages):
                values.append("")
            translations = {
                language: values[index].strip() for index, language in enumerate(languages)
            }
            source = translations.get("en") or next(iter(translations.values()), "")
            entries.append(
                TranslationEntry(
                    key=key,
                    source=source,
                    translations=translations,
                    path=str(path),
                    line=line_number,
                )
            )
            keys.append(key)

    duplicate_keys = {key for key, count in Counter(keys).items() if count > 1}
    return CsvTable(
        path=str(path),
        languages=languages,
        entries=entries,
        duplicate_keys=duplicate_keys,
        had_bom=had_bom,
        has_keys_header=has_keys_header,
    )
