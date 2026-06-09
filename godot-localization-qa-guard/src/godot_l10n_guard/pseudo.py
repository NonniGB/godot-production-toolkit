from __future__ import annotations

import csv
import re
from pathlib import Path

from .audit import BRACE_PLACEHOLDER_RE, PERCENT_PLACEHOLDER_RE
from .models import CsvTable, PoCatalog, TranslationEntry

Catalog = CsvTable | PoCatalog

ACCENT_MAP = str.maketrans(
    {
        "a": "à",
        "b": "ƀ",
        "c": "ç",
        "d": "ď",
        "e": "é",
        "f": "ƒ",
        "g": "ĝ",
        "h": "ĥ",
        "i": "í",
        "j": "ĵ",
        "k": "ķ",
        "l": "ļ",
        "m": "ɱ",
        "n": "ñ",
        "o": "ô",
        "p": "ƥ",
        "q": "ɋ",
        "r": "ř",
        "s": "š",
        "t": "ŧ",
        "u": "ú",
        "v": "ṽ",
        "w": "ŵ",
        "x": "ẋ",
        "y": "ý",
        "z": "ž",
        "A": "À",
        "B": "Ɓ",
        "C": "Ç",
        "D": "Ď",
        "E": "É",
        "F": "Ƒ",
        "G": "Ĝ",
        "H": "Ĥ",
        "I": "Í",
        "J": "Ĵ",
        "K": "Ķ",
        "L": "Ļ",
        "M": "Ṁ",
        "N": "Ñ",
        "O": "Ô",
        "P": "Ƥ",
        "Q": "Ɋ",
        "R": "Ř",
        "S": "Š",
        "T": "Ŧ",
        "U": "Ú",
        "V": "Ṽ",
        "W": "Ŵ",
        "X": "Ẋ",
        "Y": "Ý",
        "Z": "Ž",
    }
)

PLACEHOLDER_RE = re.compile(f"({BRACE_PLACEHOLDER_RE.pattern}|{PERCENT_PLACEHOLDER_RE.pattern})")


def pseudo_localize(text: str, expansion: float = 0.3) -> str:
    pieces: list[str] = []
    for part in PLACEHOLDER_RE.split(text):
        if not part:
            continue
        if PLACEHOLDER_RE.fullmatch(part):
            pieces.append(part)
        else:
            pieces.append(part.translate(ACCENT_MAP))
    expanded = "".join(pieces)
    padding = "~" * max(1, int(len(text) * expansion)) if text else ""
    return f"[!! {expanded} {padding} !!]"


def write_pseudo_csv(
    catalogs: list[Catalog],
    output: Path,
    *,
    source_language: str,
    pseudo_language: str,
    expansion: float = 0.3,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    entries = _unique_entries(catalogs)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["keys", source_language, pseudo_language])
        for entry in entries:
            writer.writerow([entry.key, entry.source, pseudo_localize(entry.source, expansion=expansion)])


def _unique_entries(catalogs: list[Catalog]) -> list[TranslationEntry]:
    entries: list[TranslationEntry] = []
    seen: set[str] = set()
    for catalog in catalogs:
        for entry in catalog.entries:
            if entry.key in seen:
                continue
            seen.add(entry.key)
            entries.append(entry)
    return entries
