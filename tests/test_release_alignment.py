from pathlib import Path
import tempfile
import unittest

from verify_release_alignment import check_release_alignment


ROOT = Path(__file__).resolve().parents[1]


class ReleaseAlignmentTests(unittest.TestCase):
    def test_release_facing_versions_are_aligned(self) -> None:
        self.assertEqual([], check_release_alignment(ROOT))

    def test_package_versions_can_move_independently_from_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            _copy_required_files(ROOT, tmp_root)

            package_root = tmp_root / "godot-asset-pipeline-doctor"
            (package_root / "pyproject.toml").write_text(
                (package_root / "pyproject.toml").read_text(encoding="utf-8").replace(
                    'version = "0.1.2"',
                    'version = "0.1.3"',
                ),
                encoding="utf-8",
            )
            (package_root / "CHANGELOG.md").write_text(
                (package_root / "CHANGELOG.md").read_text(encoding="utf-8").replace(
                    "# Changelog\n\n",
                    "# Changelog\n\n## 0.1.3 - 2026-06-09\n\n- Test package-only release.\n\n",
                ),
                encoding="utf-8",
            )
            init_path = package_root / "src" / "godot_asset_doctor" / "__init__.py"
            init_path.write_text(
                init_path.read_text(encoding="utf-8").replace('__version__ = "0.1.2"', '__version__ = "0.1.3"'),
                encoding="utf-8",
            )
            cli_path = package_root / "src" / "godot_asset_doctor" / "cli.py"
            cli_path.write_text(
                cli_path.read_text(encoding="utf-8").replace("godot-asset-doctor 0.1.2", "godot-asset-doctor 0.1.3"),
                encoding="utf-8",
            )

            self.assertEqual([], check_release_alignment(tmp_root))


def _copy_required_files(source: Path, target: Path) -> None:
    for rel_path in (
        "pyproject.toml",
        "CHANGELOG.md",
        "README.md",
        "docs/RELEASE_CHECKLIST.md",
        "docs/PUBLICATION_GUIDE.md",
        "godot-ci-doctor-action/README.md",
        "godot-ci-doctor-action/tool-manifest.json",
    ):
        source_path = source / rel_path
        target_path = target / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")

    for package, paths in {
        "godot-asset-pipeline-doctor": (
            "pyproject.toml",
            "CHANGELOG.md",
            "src/godot_asset_doctor/__init__.py",
            "src/godot_asset_doctor/cli.py",
        ),
        "godot-export-preset-doctor": (
            "pyproject.toml",
            "CHANGELOG.md",
            "src/godot_export_doctor/__init__.py",
            "src/godot_export_doctor/cli.py",
        ),
        "godot-input-map-auditor": (
            "pyproject.toml",
            "CHANGELOG.md",
            "src/godot_input_auditor/__init__.py",
            "src/godot_input_auditor/cli.py",
        ),
        "godot-localization-qa-guard": (
            "pyproject.toml",
            "CHANGELOG.md",
            "src/godot_l10n_guard/__init__.py",
            "src/godot_l10n_guard/cli.py",
        ),
        "godot-mobile-perf-doctor": (
            "pyproject.toml",
            "CHANGELOG.md",
            "src/godot_mobile_perf_doctor/__init__.py",
            "src/godot_mobile_perf_doctor/cli.py",
        ),
        "godot-save-schema-guard": (
            "pyproject.toml",
            "CHANGELOG.md",
            "src/godot_save_guard/__init__.py",
            "src/godot_save_guard/cli.py",
        ),
    }.items():
        for rel_path in paths:
            source_path = source / package / rel_path
            target_path = target / package / rel_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
