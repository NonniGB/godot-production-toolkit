from __future__ import annotations

import shutil
from pathlib import Path


def approve_baseline(current: Path, baseline: Path) -> None:
    baseline.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(current, baseline)
