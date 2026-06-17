from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: to_current.py <input.json> <output.json>", file=sys.stderr)
        return 2
    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    save = json.loads(source.read_text(encoding="utf-8"))
    save["version"] = 3
    save["credits"] = 125
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(save, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
