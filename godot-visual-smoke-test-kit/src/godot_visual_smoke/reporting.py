from __future__ import annotations

import json

from .models import DiffResult


def render_text_result(result: DiffResult) -> str:
    status = "PASS" if result.passed else "FAIL"
    lines = [
        f"Visual smoke diff: {status}",
        f"Changed pixels: {result.changed_pixels}/{result.total_pixels} ({result.changed_percent:.4f}%).",
        f"Max delta: {result.max_delta}.",
    ]
    if result.reason:
        lines.append(result.reason)
    return "\n".join(lines)


def render_json_result(result: DiffResult) -> str:
    return json.dumps(result.to_dict(), indent=2, sort_keys=True)
