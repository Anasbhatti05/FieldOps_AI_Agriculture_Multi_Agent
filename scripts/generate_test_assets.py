import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

from tools.spreadsheet import create_test_workbook


ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "data" / "sample_images"


def _background(seed: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    random.seed(seed)
    width, height = 960, 640
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y in range(height):
        if y < 250:
            amount = y / 250
            start, end = (185, 207, 195), (216, 221, 172)
        else:
            amount = (y - 250) / (height - 250)
            start, end = (117, 132, 68), (92, 86, 48)
        color = tuple(round(a + (b - a) * amount) for a, b in zip(start, end))
        for x in range(width):
            noise = random.randint(-5, 5)
            pixels[x, y] = tuple(max(0, min(255, channel + noise)) for channel in color)
    draw = ImageDraw.Draw(image, "RGB")
    for _ in range(900):
        x, y = random.randrange(width), random.randrange(270, height)
        color = random.choice([(112, 126, 61), (138, 143, 70), (77, 106, 58), (162, 151, 81)])
        draw.ellipse((x, y, x + 2, y + 2), fill=color)
    return image, draw


def _leaf(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float], color: tuple[int, int, int], width: int) -> None:
    sx, sy = start
    ex, ey = end
    dx, dy = ex - sx, ey - sy
    length = math.hypot(dx, dy) or 1
    px, py = -dy / length, dx / length
    shape = [
        (sx, sy),
        (sx + dx * .28 + px * width, sy + dy * .28 + py * width),
        (sx + dx * .68 + px * width * .58, sy + dy * .68 + py * width * .58),
        (ex, ey),
        (sx + dx * .68 - px * width * .58, sy + dy * .68 - py * width * .58),
        (sx + dx * .28 - px * width, sy + dy * .28 - py * width),
    ]
    draw.polygon(shape, fill=color)
    draw.line([start, end], fill=(171, 184, 106), width=2)


def create_wheat() -> Image.Image:
    image, draw = _background(42)
    random.seed(42)
    for index in range(24):
        base_x = random.randint(70, 920)
        base_y = random.randint(500, 635)
        top_x = base_x + random.randint(-110, 110)
        top_y = random.randint(95, 310)
        draw.line((base_x, base_y, top_x, top_y), fill=(113, 133, 63), width=4)
        for leaf_index in range(3):
            point_y = base_y - random.randint(60, 270)
            point_x = base_x + (top_x - base_x) * (base_y - point_y) / max(1, base_y - top_y)
            side = -1 if (index + leaf_index) % 2 else 1
            length = random.randint(60, 150)
            _leaf(draw, (point_x, point_y), (point_x + side * length, point_y - random.randint(25, 75)), random.choice([(91, 119, 52), (131, 145, 65), (164, 159, 76)]), random.randint(9, 16))
        for grain in range(8):
            gx = top_x + (grain % 2) * 11 - 5
            gy = top_y + grain * 9
            draw.ellipse((gx - 5, gy - 9, gx + 5, gy + 2), fill=(198, 177, 93))
    return image


def create_cotton() -> Image.Image:
    image, draw = _background(84)
    random.seed(84)
    for index in range(14):
        base_x = random.randint(40, 900)
        base_y = random.randint(455, 640)
        top_x = base_x + random.randint(-75, 75)
        top_y = random.randint(140, 360)
        draw.line((base_x, base_y, top_x, top_y), fill=(88, 107, 52), width=7)
        for leaf_index in range(4):
            fraction = (leaf_index + 1) / 5
            anchor = (base_x + (top_x - base_x) * fraction, base_y + (top_y - base_y) * fraction)
            side = -1 if (index + leaf_index) % 2 else 1
            tip = (anchor[0] + side * random.randint(75, 145), anchor[1] - random.randint(10, 80))
            _leaf(draw, anchor, tip, random.choice([(42, 99, 54), (57, 120, 61), (77, 137, 66)]), random.randint(20, 34))
            for _ in range(5):
                spot_x = random.uniform(min(anchor[0], tip[0]), max(anchor[0], tip[0]))
                spot_y = random.uniform(min(anchor[1], tip[1]) - 12, max(anchor[1], tip[1]) + 12)
                radius = random.randint(2, 5)
                draw.ellipse((spot_x - radius, spot_y - radius, spot_x + radius, spot_y + radius), fill=(166, 126, 59))
        draw.ellipse((top_x - 18, top_y - 18, top_x + 18, top_y + 18), fill=(220, 217, 186))
    return image


def create_rice() -> Image.Image:
    image, draw = _background(126)
    random.seed(126)
    for index in range(35):
        base_x = random.randint(0, 960)
        base_y = random.randint(465, 640)
        top_x = base_x + random.randint(-90, 90)
        top_y = random.randint(90, 320)
        draw.line((base_x, base_y, top_x, top_y), fill=(78, 116, 54), width=3)
        for leaf_index in range(4):
            fraction = (leaf_index + 1) / 6
            anchor = (base_x + (top_x - base_x) * fraction, base_y + (top_y - base_y) * fraction)
            side = -1 if (index + leaf_index) % 2 else 1
            tip = (anchor[0] + side * random.randint(55, 120), anchor[1] - random.randint(35, 105))
            _leaf(draw, anchor, tip, random.choice([(46, 107, 58), (68, 126, 63), (110, 142, 67)]), random.randint(7, 13))
    return image


def save_sample(name: str, image: Image.Image) -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    image.save(IMAGE_DIR / name, format="JPEG", quality=88, optimize=True)


def main() -> None:
    workbook_path = ROOT / "data" / "fieldops_test_workbook.xlsx"
    workbook_path.parent.mkdir(parents=True, exist_ok=True)
    save_sample("synthetic_wheat_upload_test.jpg", create_wheat())
    save_sample("synthetic_cotton_upload_test.jpg", create_cotton())
    save_sample("synthetic_rice_upload_test.jpg", create_rice())
    workbook_path.write_bytes(create_test_workbook())
    print(f"Created {workbook_path} and sample images in {IMAGE_DIR}")


if __name__ == "__main__":
    main()