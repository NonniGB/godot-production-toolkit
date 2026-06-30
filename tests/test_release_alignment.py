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
                    'version = "0.1.10"',
                    'version = "0.1.11"',
                ),
                encoding="utf-8",
            )
            (package_root / "CHANGELOG.md").write_text(
                (package_root / "CHANGELOG.md").read_text(encoding="utf-8").replace(
                    "# Changelog\n\n",
                    "# Changelog\n\n## 0.1.11 - 2026-06-30\n\n- Test package-only release.\n\n",
                ),
                encoding="utf-8",
            )
            init_path = package_root / "src" / "godot_asset_doctor" / "__init__.py"
            init_path.write_text(
                init_path.read_text(encoding="utf-8").replace('__version__ = "0.1.10"', '__version__ = "0.1.11"'),
                encoding="utf-8",
            )
            cli_path = package_root / "src" / "godot_asset_doctor" / "cli.py"
            cli_path.write_text(
                cli_path.read_text(encoding="utf-8").replace("godot-asset-doctor 0.1.10", "godot-asset-doctor 0.1.11"),
                encoding="utf-8",
            )
            readme_path = tmp_root / "README.md"
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    "| [`godot-asset-pipeline-doctor`](https://pypi.org/project/godot-asset-pipeline-doctor/) | `0.1.10` |",
                    "| [`godot-asset-pipeline-doctor`](https://pypi.org/project/godot-asset-pipeline-doctor/) | `0.1.11` |",
                ),
                encoding="utf-8",
            )

            self.assertEqual([], check_release_alignment(tmp_root))

    def test_package_finder_install_drift_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            _copy_required_files(ROOT, tmp_root)

            package_finder_path = tmp_root / "docs" / "PACKAGE_FINDER.md"
            package_finder_path.write_text(
                package_finder_path.read_text(encoding="utf-8").replace(
                    "python -m pip install godot-asset-pipeline-doctor",
                    "python -m pip install godot-asset-pipeline-checker",
                ),
                encoding="utf-8",
            )

            errors = check_release_alignment(tmp_root)

            self.assertTrue(
                any(
                    error.endswith(
                        "docs/PACKAGE_FINDER.md does not contain 'python -m pip install godot-asset-pipeline-doctor'"
                    )
                    for error in errors
                ),
                errors,
            )
            self.assertIn(
                "docs/PACKAGE_FINDER.md references unknown install package 'godot-asset-pipeline-checker'",
                errors,
            )


def _copy_required_files(source: Path, target: Path) -> None:
    for rel_path in (
        "pyproject.toml",
        "CHANGELOG.md",
        "README.md",
        "docs/PACKAGE_FINDER.md",
        "project-metadata.json",
        "godot-ci-doctor-action/README.md",
        "godot-ci-doctor-action/tool-manifest.json",
    ):
        source_path = source / rel_path
        target_path = target / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")

    for package, paths in {
        "gdscript-api-comment-coverage": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/gdscript_api_coverage/__init__.py",
            "src/gdscript_api_coverage/cli.py",
        ),
        "godot-asset-pipeline-doctor": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_asset_doctor/__init__.py",
            "src/godot_asset_doctor/cli.py",
        ),
        "godot-content-graph-doctor": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_content_graph_doctor/__init__.py",
            "src/godot_content_graph_doctor/cli.py",
        ),
        "godot-export-preset-doctor": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_export_doctor/__init__.py",
            "src/godot_export_doctor/cli.py",
        ),
        "godot-gdscript-architecture-guard": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_architecture_guard/__init__.py",
            "src/godot_architecture_guard/cli.py",
        ),
        "godot-input-map-auditor": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_input_auditor/__init__.py",
            "src/godot_input_auditor/cli.py",
        ),
        "godot-localization-qa-guard": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_l10n_guard/__init__.py",
            "src/godot_l10n_guard/cli.py",
        ),
        "godot-mobile-perf-doctor": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_mobile_perf_doctor/__init__.py",
            "src/godot_mobile_perf_doctor/cli.py",
        ),
        "godot-mobile-ui-doctor": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_mobile_ui_doctor/__init__.py",
            "src/godot_mobile_ui_doctor/cli.py",
        ),
        "godot-pack-mod-doctor": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_pack_mod_doctor/__init__.py",
            "src/godot_pack_mod_doctor/cli.py",
        ),
        "godot-production-doctor": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_project_doctor/__init__.py",
            "src/godot_project_doctor/cli.py",
        ),
        "godot-release-dashboard-kit": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_release_dashboard_kit/__init__.py",
            "src/godot_release_dashboard_kit/cli.py",
        ),
        "godot-runtime-telemetry-lab": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_runtime_telemetry_lab/__init__.py",
            "src/godot_runtime_telemetry_lab/cli.py",
        ),
        "godot-save-schema-guard": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_save_guard/__init__.py",
            "src/godot_save_guard/cli.py",
        ),
        "godot-scenario-report-kit": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_scenario_report_kit/__init__.py",
            "src/godot_scenario_report_kit/cli.py",
        ),
        "godot-scene-signal-auditor": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_signal_auditor/__init__.py",
            "src/godot_signal_auditor/cli.py",
        ),
        "godot-visual-smoke-test-kit": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/godot_visual_smoke/__init__.py",
            "src/godot_visual_smoke/cli.py",
        ),
        "pixel-space-asset-toolkit": (
            "pyproject.toml",
            "tool-manifest.json",
            "CHANGELOG.md",
            "src/pixel_space_assets/__init__.py",
            "src/pixel_space_assets/cli.py",
        ),
    }.items():
        for rel_path in paths:
            source_path = source / package / rel_path
            target_path = target / package / rel_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
