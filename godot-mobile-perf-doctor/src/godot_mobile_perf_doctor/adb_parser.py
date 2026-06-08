from __future__ import annotations

import re

from .models import AdbSummary


def parse_adb_summary(text: str) -> AdbSummary:
    return AdbSummary(
        device=_match(text, r"Device:\s*(.+)"),
        android=_match(text, r"Android:\s*(.+)"),
        total_frames=int(_match(text, r"Total frames rendered:\s*(\d+)") or 0),
        janky_frames=int(_match(text, r"Janky frames:\s*(\d+)") or 0),
    )


def _match(text: str, pattern: str) -> str:
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""
