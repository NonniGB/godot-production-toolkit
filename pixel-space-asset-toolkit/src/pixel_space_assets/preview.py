from __future__ import annotations

import math
from pathlib import Path

from PIL import Image


def build_contact_sheet(paths: list[Path], *, columns: int, cell_size: int) -> Image.Image:
    if not paths:
        return Image.new("RGBA", (cell_size, cell_size), (0, 0, 0, 0))
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGBA", (columns * cell_size, rows * cell_size), (8, 10, 18, 255))
    for index, path in enumerate(paths):
        with Image.open(path) as image:
            tile = image.convert("RGBA")
            tile.thumbnail((cell_size, cell_size), Image.Resampling.NEAREST)
            x = (index % columns) * cell_size + (cell_size - tile.width) // 2
            y = (index // columns) * cell_size + (cell_size - tile.height) // 2
            sheet.alpha_composite(tile, (x, y))
    return sheet
