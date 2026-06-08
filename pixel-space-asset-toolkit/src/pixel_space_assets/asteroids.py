from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

PALETTES = {
    "ferric": [(63, 43, 47, 255), (126, 72, 57, 255), (214, 117, 77, 255), (255, 188, 112, 255)],
    "ice": [(37, 58, 82, 255), (72, 118, 145, 255), (145, 214, 226, 255), (232, 255, 255, 255)],
    "carbon": [(20, 24, 32, 255), (48, 55, 69, 255), (92, 102, 118, 255), (170, 186, 202, 255)],
}


def generate_asteroid_tiles(
    output: Path,
    *,
    material: str,
    count: int,
    size: int,
    seed: int,
) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    palette = PALETTES.get(material, PALETTES["carbon"])
    tiles = []
    for index in range(count):
        tile_seed = seed + index
        image = _generate_tile(size=size, palette=palette, seed=tile_seed)
        filename = f"{material}_{index:03d}.png"
        image.save(output / filename)
        tiles.append({"file": filename, "seed": tile_seed})
    manifest = {"type": "asteroid-hex", "material": material, "count": count, "size": size, "seed": seed, "tiles": tiles}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def _generate_tile(*, size: int, palette: list[tuple[int, int, int, int]], seed: int) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    center = (size / 2, size / 2)
    radius = size * rng.uniform(0.34, 0.44)
    points = []
    for side in range(6):
        angle = math.radians(60 * side - 30)
        jitter = rng.uniform(0.82, 1.12)
        points.append((center[0] + math.cos(angle) * radius * jitter, center[1] + math.sin(angle) * radius * jitter))
    draw.polygon(points, fill=palette[1], outline=palette[3])
    for _ in range(max(3, size // 8)):
        x = rng.randrange(size)
        y = rng.randrange(size)
        if image.getpixel((x, y))[3] == 0:
            continue
        color = rng.choice(palette)
        draw.rectangle((x, y, min(size - 1, x + rng.randrange(1, 4)), min(size - 1, y + rng.randrange(1, 4))), fill=color)
    return image
