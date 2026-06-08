from __future__ import annotations

import random

from PIL import Image, ImageDraw

STAR_COLORS = [
    (124, 247, 255, 255),
    (255, 255, 255, 255),
    (255, 218, 121, 255),
    (198, 176, 255, 255),
]


def generate_starfield(*, width: int, height: int, seed: int, stars: int) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGBA", (width, height), (5, 7, 18, 255))
    draw = ImageDraw.Draw(image)
    for _ in range(stars):
        x = rng.randrange(width)
        y = rng.randrange(height)
        color = rng.choice(STAR_COLORS)
        size = 1 if rng.random() < 0.86 else 2
        draw.rectangle((x, y, min(width - 1, x + size - 1), min(height - 1, y + size - 1)), fill=color)
        if rng.random() < 0.12:
            glow = (color[0], color[1], color[2], 90)
            if x > 0:
                image.putpixel((x - 1, y), glow)
            if x + 1 < width:
                image.putpixel((x + 1, y), glow)
    return image
