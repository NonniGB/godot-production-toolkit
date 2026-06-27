from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DEMO_ROOT = ROOT / "examples" / "demo-paths"
GALLERY = ROOT / "docs" / "assets" / "sample-reports" / "README.md"


class DemoPathTests(unittest.TestCase):
    def test_demo_paths_exist_with_commands_and_report_snapshots(self) -> None:
        for name in ("tiny-mobile-release", "tiny-content-game", "tiny-runtime-regression"):
            readme = DEMO_ROOT / name / "README.md"
            self.assertTrue(readme.exists(), f"{name} README missing")
            text = readme.read_text(encoding="utf-8")
            self.assertIn("## Source Inputs", text)
            self.assertIn("## Commands", text)
            self.assertIn("## Report Snapshots", text)
            self.assertIn("```powershell", text)
            self.assertGreaterEqual(text.count("godot-"), 3)

    def test_demo_path_links_point_to_existing_files(self) -> None:
        markdown_files = [DEMO_ROOT / "README.md", GALLERY]
        markdown_files.extend((DEMO_ROOT / name / "README.md") for name in (
            "tiny-mobile-release",
            "tiny-content-game",
            "tiny-runtime-regression",
        ))

        missing: list[str] = []
        for markdown_file in markdown_files:
            text = markdown_file.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if target.startswith(("http://", "https://", "#")):
                    continue
                path = (markdown_file.parent / target).resolve()
                if not path.exists():
                    missing.append(f"{markdown_file.relative_to(ROOT)} -> {target}")

        self.assertEqual([], missing)

    def test_gallery_surfaces_all_three_demo_paths(self) -> None:
        text = GALLERY.read_text(encoding="utf-8")

        for heading in ("Tiny Mobile Release", "Tiny Content Game", "Tiny Runtime Regression"):
            self.assertIn(f"## {heading}", text)

        for report in (
            "release-readiness-summary.md",
            "project-doctor-terminal.png",
            "content-graph-summary.md",
            "content-graph-terminal.svg",
            "scenario-compare.md",
            "runtime-telemetry-timeline.html",
            "runtime-telemetry-timeline.png",
        ):
            self.assertIn(report, text)


if __name__ == "__main__":
    unittest.main()
