from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from godot_release_dashboard_kit.cli import main


class ReleaseDashboardTests(unittest.TestCase):
    def test_builds_html_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "export.json").write_text(
                json.dumps({"tool": "godot-export-doctor", "summary": {"errors": 1, "warnings": 2}}),
                encoding="utf-8",
            )
            output = root / "dashboard.html"

            exit_code = main(["build", str(reports), "--output", str(output)])

            html = output.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn("Godot Release Dashboard", html)
            self.assertIn("godot-export-doctor", html)
            self.assertIn("Errors: 1", html)
            self.assertIn("Visual Artifacts", html)

    def test_builds_json_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "notes.md").write_text("# Notes\n\nwarning: check this", encoding="utf-8")
            (reports / "overlay.svg").write_text(
                "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"120\" height=\"80\"><rect width=\"120\" height=\"80\" fill=\"#111827\"/></svg>",
                encoding="utf-8",
            )
            output = root / "dashboard.json"

            exit_code = main(["build", str(reports), "--format", "json", "--output", str(output)])

            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 0)
            self.assertEqual(data["tool_version"], "0.1.1")
            self.assertEqual(data["summary"]["reports"], 1)
            self.assertEqual(data["summary"]["images"], 1)
            self.assertEqual(data["images"][0]["mime"], "image/svg+xml")
            self.assertTrue(data["images"][0]["data_uri"].startswith("data:image/svg+xml;base64,"))


if __name__ == "__main__":
    unittest.main()
