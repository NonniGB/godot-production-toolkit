from __future__ import annotations

import os
import re
from pathlib import Path

TR_RE = re.compile(r"\btr\(\s*[\"']([^\"']+)[\"']\s*\)")
TRANSLATION_SERVER_RE = re.compile(r"TranslationServer\.translate\(\s*[\"']([^\"']+)[\"']\s*\)")
SCENE_TEXT_RE = re.compile(r"\btext\s*=\s*\"([A-Z][A-Z0-9_.-]{2,})\"")
EXCLUDED_DIRS = {".git", ".godot", ".venv", "__pycache__", "build", "dist", "logs"}


def scan_project_keys(root: Path, *, scan_scripts: bool, scan_scenes: bool) -> set[str]:
    keys: set[str] = set()
    for current, dirs, files in os.walk(root):
        dirs[:] = [directory for directory in dirs if directory not in EXCLUDED_DIRS]
        current_path = Path(current)
        for filename in files:
            path = current_path / filename
            if scan_scripts and filename.endswith(".gd"):
                keys.update(_scan_text(path.read_text(encoding="utf-8"), scripts=True, scenes=False))
            elif scan_scenes and filename.endswith((".tscn", ".scn")):
                keys.update(_scan_text(path.read_text(encoding="utf-8"), scripts=False, scenes=True))
    return keys


def _scan_text(text: str, *, scripts: bool, scenes: bool) -> set[str]:
    keys: set[str] = set()
    if scripts:
        keys.update(TR_RE.findall(text))
        keys.update(TRANSLATION_SERVER_RE.findall(text))
    if scenes:
        keys.update(SCENE_TEXT_RE.findall(text))
    return keys
