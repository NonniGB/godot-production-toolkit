from pathlib import Path
import tomllib
import unittest

from project_health_snapshot import build_snapshot
from verify_tool_manifests import TOOLS
from verify_release_alignment import PUBLISHED_PACKAGES


ROOT = Path(__file__).resolve().parents[1]


class ProjectHealthSnapshotTests(unittest.TestCase):
    def test_snapshot_reports_current_local_health(self) -> None:
        snapshot = build_snapshot(ROOT)

        self.assertTrue(snapshot["ok"], snapshot["errors"])
        self.assertEqual("godot-production-toolkit", snapshot["project"])
        self.assertEqual("0.1.2", snapshot["version"])
        self.assertEqual(len(TOOLS), snapshot["tool_count"])
        self.assertEqual("ok", snapshot["release_alignment"])
        expected = {
            package: tomllib.loads((ROOT / package / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
            for package in PUBLISHED_PACKAGES
        }
        self.assertEqual(expected, snapshot["published_packages"])


if __name__ == "__main__":
    unittest.main()
