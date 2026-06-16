import json
import tempfile
import unittest
from pathlib import Path

from godot_save_guard.redaction import RedactionOptions, redact_fixtures


class RedactionTests(unittest.TestCase):
    def test_redacts_dotted_paths_and_wildcards_without_changing_original(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures = root / "fixtures"
            output_dir = root / "sanitized"
            fixtures.mkdir()
            fixture = fixtures / "save.json"
            fixture.write_text(
                json.dumps(
                    {
                        "version": 2,
                        "player_name": "Ada",
                        "credits": 42,
                        "founder": True,
                        "profile": {"email": "ada@example.invalid"},
                        "party": [{"player_name": "Ben"}],
                    }
                ),
                encoding="utf-8",
            )

            results = redact_fixtures(
                fixtures,
                RedactionOptions(
                    paths=["player_name", "profile.email", "party.*.player_name", "credits", "founder"],
                    output_dir=output_dir,
                ),
            )

            sanitized = json.loads((output_dir / "save.json").read_text(encoding="utf-8"))
            original = json.loads(fixture.read_text(encoding="utf-8"))
            self.assertEqual(sanitized["player_name"], "<redacted>")
            self.assertEqual(sanitized["profile"]["email"], "<redacted>")
            self.assertEqual(sanitized["party"][0]["player_name"], "<redacted>")
            self.assertEqual(sanitized["credits"], 0)
            self.assertFalse(sanitized["founder"])
            self.assertEqual(original["player_name"], "Ada")
            self.assertEqual([finding.rule_id for finding in results[0].findings], ["redaction_applied"])

    def test_reports_missing_redaction_field_as_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / "save.json"
            fixture.write_text(json.dumps({"version": 1}), encoding="utf-8")

            results = redact_fixtures(
                fixture,
                RedactionOptions(paths=["player_id"], output_dir=root / "out", replacement="<private>"),
            )

            rule_ids = [finding.rule_id for finding in results[0].findings]
            self.assertIn("redaction_path_missing", rule_ids)
            self.assertIn("redaction_applied", rule_ids)

    def test_dry_run_does_not_create_output_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / "save.json"
            output_dir = root / "out"
            fixture.write_text(json.dumps({"version": 1, "player": {"name": "Ada"}}), encoding="utf-8")

            results = redact_fixtures(
                fixture,
                RedactionOptions(paths=["player.name"], output_dir=output_dir, dry_run=True),
            )

            self.assertFalse(output_dir.exists())
            self.assertEqual([finding.rule_id for finding in results[0].findings], ["redaction_planned"])

    def test_output_collision_fails_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / "save.json"
            output_dir = root / "out"
            output_dir.mkdir()
            fixture.write_text(json.dumps({"version": 1, "player_name": "Ada"}), encoding="utf-8")
            (output_dir / "save.json").write_text("{}", encoding="utf-8")

            results = redact_fixtures(
                fixture,
                RedactionOptions(paths=["player_name"], output_dir=output_dir),
            )

            self.assertEqual(results[0].findings[-1].rule_id, "redaction_output_exists")

    def test_preserves_directory_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures = root / "fixtures"
            (fixtures / "v1").mkdir(parents=True)
            (fixtures / "v2").mkdir(parents=True)
            (fixtures / "v1" / "save.json").write_text(json.dumps({"player_name": "Ada"}), encoding="utf-8")
            (fixtures / "v2" / "save.json").write_text(json.dumps({"player_name": "Ben"}), encoding="utf-8")

            redact_fixtures(
                fixtures,
                RedactionOptions(paths=["player_name"], output_dir=root / "out"),
            )

            self.assertTrue((root / "out" / "v1" / "save.json").exists())
            self.assertTrue((root / "out" / "v2" / "save.json").exists())


if __name__ == "__main__":
    unittest.main()
