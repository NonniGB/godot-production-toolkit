from pathlib import Path
import unittest

from project_health_snapshot import build_snapshot


ROOT = Path(__file__).resolve().parents[1]


class ProjectHealthSnapshotTests(unittest.TestCase):
    def test_snapshot_reports_current_local_health(self) -> None:
        snapshot = build_snapshot(ROOT)

        self.assertTrue(snapshot["ok"], snapshot["errors"])
        self.assertEqual("godot-production-toolkit", snapshot["project"])
        self.assertEqual("0.1.2", snapshot["version"])
        self.assertEqual(12, snapshot["tool_count"])
        self.assertEqual("ok", snapshot["release_alignment"])
        self.assertEqual(
            {
                "godot-asset-pipeline-doctor": "0.1.2",
                "godot-export-preset-doctor": "0.1.2",
                "godot-mobile-perf-doctor": "0.1.2",
            },
            snapshot["published_packages"],
        )


if __name__ == "__main__":
    unittest.main()
