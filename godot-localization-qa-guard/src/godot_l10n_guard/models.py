from __future__ import annotations

from dataclasses import dataclass, field

from .rule_help import explain_rule


@dataclass(frozen=True)
class TranslationEntry:
    key: str
    source: str
    translations: dict[str, str]
    path: str
    line: int
    fuzzy: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "source": self.source,
            "translations": self.translations,
            "path": self.path,
            "line": self.line,
            "fuzzy": self.fuzzy,
        }


@dataclass(frozen=True)
class CsvTable:
    path: str
    languages: list[str]
    entries: list[TranslationEntry]
    duplicate_keys: set[str] = field(default_factory=set)
    had_bom: bool = False
    has_keys_header: bool = True

    def keys(self) -> set[str]:
        return {entry.key for entry in self.entries}

    def to_dict(self) -> dict[str, object]:
        return {
            "type": "csv",
            "path": self.path,
            "languages": self.languages,
            "duplicate_keys": sorted(self.duplicate_keys),
            "had_bom": self.had_bom,
            "has_keys_header": self.has_keys_header,
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass(frozen=True)
class PoCatalog:
    path: str
    language: str
    entries: list[TranslationEntry]
    duplicate_keys: set[str] = field(default_factory=set)

    def keys(self) -> set[str]:
        return {entry.key for entry in self.entries}

    def to_dict(self) -> dict[str, object]:
        return {
            "type": "po",
            "path": self.path,
            "language": self.language,
            "duplicate_keys": sorted(self.duplicate_keys),
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    key: str | None
    message: str
    path: str | None = None
    line: int | None = None

    def to_dict(self) -> dict[str, object]:
        help_text = explain_rule(self.rule_id)
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "key": self.key,
            "title": help_text["title"],
            "explanation": help_text["explanation"],
            "message": self.message,
            "path": self.path,
            "line": self.line,
        }
