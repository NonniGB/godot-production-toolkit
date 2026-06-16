import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {".git", ".pytest_cache", "__pycache__", "build", "dist", ".venv", "venv"}
TEXT_SUFFIXES = {".cfg", ".gd", ".html", ".json", ".md", ".py", ".toml", ".txt", ".yml", ".yaml"}
DENIED_PHRASES = (
    ("AI", "reviewer"),
    ("AI", "review"),
    ("OSS", "application"),
    ("OSS", "scheme"),
    ("quali" + "fication", "pro" + "gramme"),
    ("sub" + "scription", "plan"),
    ("ChatGPT", "Pro"),
    ("Codex", "Pro"),
    ("application", "strategy"),
)
DENIED_PATTERNS = (
    *(re.compile(r"\s+".join(parts), re.IGNORECASE) for parts in DENIED_PHRASES),
    re.compile(r"trusted\s+by\s+\d+", re.IGNORECASE),
    re.compile(r"used\s+by\s+\d+", re.IGNORECASE),
)


class PublicWordingTests(unittest.TestCase):
    def test_public_text_avoids_application_and_fake_adoption_language(self) -> None:
        matches: list[str] = []

        for path in ROOT.rglob("*"):
            if any(part in IGNORED_DIRS for part in path.parts):
                continue
            if path.name == "test_public_wording.py":
                continue
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in DENIED_PATTERNS:
                if pattern.search(text):
                    matches.append(f"{path.relative_to(ROOT)}: {pattern.pattern}")

        self.assertEqual([], matches)


if __name__ == "__main__":
    unittest.main()
