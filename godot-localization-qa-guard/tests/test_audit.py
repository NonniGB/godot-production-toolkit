import unittest

from godot_l10n_guard.audit import audit_catalogs
from godot_l10n_guard.models import CsvTable, TranslationEntry


class AuditTests(unittest.TestCase):
    def test_empty_unchanged_and_placeholder_mismatch_findings(self) -> None:
        table = CsvTable(
            path="strings.csv",
            languages=["en", "fr"],
            entries=[
                TranslationEntry(
                    key="HELLO",
                    source="Hello {name}",
                    translations={"en": "Hello {name}", "fr": "Bonjour {nom}"},
                    path="strings.csv",
                    line=2,
                ),
                TranslationEntry(
                    key="EXIT",
                    source="Exit",
                    translations={"en": "Exit", "fr": ""},
                    path="strings.csv",
                    line=3,
                ),
                TranslationEntry(
                    key="COPY",
                    source="Copy",
                    translations={"en": "Copy", "fr": "Copy"},
                    path="strings.csv",
                    line=4,
                ),
            ],
        )

        findings = audit_catalogs([table], required_languages={"fr"}, source_language="en")
        rule_ids = {finding.rule_id for finding in findings}

        self.assertIn("placeholder_mismatch", rule_ids)
        self.assertIn("empty_translation", rule_ids)
        self.assertIn("unchanged_translation", rule_ids)

    def test_missing_and_unused_keys_from_usage_scan(self) -> None:
        table = CsvTable(
            path="strings.csv",
            languages=["en"],
            entries=[
                TranslationEntry("MENU_START", "Start", {"en": "Start"}, "strings.csv", 2),
                TranslationEntry("MENU_UNUSED", "Unused", {"en": "Unused"}, "strings.csv", 3),
            ],
        )

        findings = audit_catalogs(
            [table],
            required_languages=set(),
            source_language="en",
            used_keys={"MENU_START", "MENU_EXIT"},
        )
        rule_ids = {finding.rule_id for finding in findings}

        self.assertIn("missing_key", rule_ids)
        self.assertIn("unused_key", rule_ids)

    def test_optional_expansion_and_glyph_checks(self) -> None:
        table = CsvTable(
            path="strings.csv",
            languages=["en", "fr"],
            entries=[
                TranslationEntry("MENU_GO", "Go", {"en": "Go", "fr": "Aller tres loin!"}, "strings.csv", 2),
            ],
        )

        findings = audit_catalogs(
            [table],
            required_languages={"fr"},
            source_language="en",
            max_expansion=2.0,
            allowed_glyphs=set("Aler tsion"),
        )
        rule_ids = {finding.rule_id for finding in findings}

        self.assertIn("string_expansion", rule_ids)
        self.assertIn("glyph_not_allowed", rule_ids)


if __name__ == "__main__":
    unittest.main()
