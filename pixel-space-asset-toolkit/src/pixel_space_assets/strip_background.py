from __future__ import annotations

from PIL import Image


def strip_background(image: Image.Image, *, tolerance: int = 0) -> Image.Image:
    source = image.convert("RGBA")
    background = source.getpixel((0, 0))
    output = Image.new("RGBA", source.size, (0, 0, 0, 0))
    for y in range(source.height):
        for x in range(source.width):
            pixel = source.getpixel((x, y))
            if _within_tolerance(pixel, background, tolerance):
                output.putpixel((x, y), (pixel[0], pixel[1], pixel[2], 0))
            else:
                output.putpixel((x, y), pixel)
    return output


def _within_tolerance(pixel: tuple[int, int, int, int], background: tuple[int, int, int, int], tolerance: int) -> bool:
    return max(abs(pixel[index] - background[index]) for index in range(3)) <= tolerance
