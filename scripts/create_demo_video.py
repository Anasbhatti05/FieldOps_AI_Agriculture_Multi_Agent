from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "data" / "fieldops_test_workbook.xlsx"
OUTPUT = ROOT / "docs" / "FIELDOPS_AI_Demo_Walkthrough.mp4"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
WIDTH = 1280
HEIGHT = 720
FPS = 24
SCENE_SECONDS = 4
TRANSITION_FRAMES = 10

CAPTIONS = [
    ("FIELDOPS AI", "Real app walkthrough | Urdu-first agriculture demo"),
    ("1  |  Field ki maloomat", "Fasal, stage, acres, soil moisture, aur entered weather"),
    ("2  |  Natija aur hisaab", "Demo formula: assumptions khuli aur samajhne ke liye dikhai gayi hain"),
    ("3  |  Chhay specialist checks", "Photo, pests, soil, weather, irrigation, local guidance"),
    ("4  |  Excel se test", "Workbook upload karo aur apni ya sample row chuno"),
    ("5  |  Dry wheat example", "Taqreeban 546 m3 demo estimate | irrigation advice nahi"),
    ("6  |  Barish wala case", "40 mm forecast par demo estimate zero | field dobara check"),
    ("7  |  Report aur safety", "Urdu report + JSON | human review | machine control nahi"),
]


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    filename = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(Path(r"C:\Windows\Fonts") / filename, size)


def _capture_page(page) -> Image.Image:
    page.wait_for_timeout(250)
    return Image.open(BytesIO(page.screenshot(type="png"))).convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def capture_scenes(base_url: str) -> list[Image.Image]:
    if not EDGE.exists():
        raise FileNotFoundError(f"Microsoft Edge was not found at {EDGE}")
    if not WORKBOOK.exists():
        raise FileNotFoundError(f"Demo workbook was not found at {WORKBOOK}")

    screenshots = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=str(EDGE), headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 810}, device_scale_factor=1)
        page.goto(base_url, wait_until="domcontentloaded", timeout=45_000)
        page.get_by_role("button", name="گندم کا نمونہ کھولیں").wait_for(timeout=45_000)
        screenshots.append(_capture_page(page))

        demo_values = {
            "کھیت کا رقبہ (ایکڑ)": "5",
            "گزشتہ بارش (ملی میٹر)": "1",
            "درجہ حرارت (سینٹی گریڈ)": "34",
            "مٹی کی نمی (فیصد)": "17",
            "اگلے دن کی متوقع بارش (ملی میٹر)": "0",
            "ہوا کی رفتار (کلومیٹر فی گھنٹہ)": "8",
        }
        for label, value in demo_values.items():
            page.get_by_role("spinbutton", name=label).fill(value)
        page.get_by_role("textbox", name="علاقہ یا ضلع (اختیاری)").fill("ملتان")
        stage = page.get_by_role("combobox", name="فصل کی حالت")
        stage.click(force=True)
        stage.press("ArrowDown")
        stage.press("ArrowDown")
        stage.press("Enter")
        stage.press("Enter")
        screenshots.append(_capture_page(page))

        manual_submit = page.get_by_role("button", name="کھیت کی جانچ کریں")
        expect(manual_submit).to_be_enabled(timeout=10_000)
        manual_submit.click(force=True)
        expect(page.get_by_role("heading", name="کھیت کی جانچ کا نتیجہ")).to_be_visible(timeout=20_000)
        page.get_by_role("heading", name="کھیت کی جانچ کا نتیجہ").scroll_into_view_if_needed()
        if page.get_by_text("546 m³", exact=True).count() == 0:
            raise AssertionError("The recorded wheat demo did not show the expected 546 m³ demo estimate.")
        screenshots.append(_capture_page(page))

        page.get_by_role("heading", name="کس نے کیا دیکھا؟").scroll_into_view_if_needed()
        screenshots.append(_capture_page(page))

        page.reload(wait_until="domcontentloaded", timeout=45_000)
        page.get_by_role("button", name="ایکسل فارم ڈاؤن لوڈ کریں").wait_for(timeout=45_000)
        page.locator('input[type="file"]').first.set_input_files(str(WORKBOOK))
        picker = page.get_by_role("combobox", name="اپنا کھیت یا نمونہ منتخب کریں")
        picker.wait_for(timeout=20_000)
        picker.scroll_into_view_if_needed()
        screenshots.append(_capture_page(page))

        picker.click(force=True)
        picker.press("ArrowDown")
        picker.press("Enter")
        picker.press("Enter")
        excel_submit = page.get_by_role("button", name="منتخب قطار کی جانچ کریں")
        expect(excel_submit).to_be_enabled(timeout=10_000)
        excel_submit.click(force=True)
        expect(page.get_by_text("ایکسل کے نمونے کی جانچ مکمل ہو گئی۔")).to_be_visible(timeout=20_000)
        expect(page.get_by_role("heading", name="کھیت کی جانچ کا نتیجہ")).to_be_visible(timeout=20_000)
        page.get_by_role("heading", name="کھیت کی جانچ کا نتیجہ").scroll_into_view_if_needed()
        screenshots.append(_capture_page(page))

        picker = page.get_by_role("combobox", name="اپنا کھیت یا نمونہ منتخب کریں")
        picker.click(force=True)
        picker.press("ArrowDown")
        picker.press("Enter")
        picker.press("Enter")
        excel_submit = page.get_by_role("button", name="منتخب قطار کی جانچ کریں")
        expect(excel_submit).to_be_enabled(timeout=10_000)
        excel_submit.click(force=True)
        expect(page.get_by_text("ایکسل کے نمونے کی جانچ مکمل ہو گئی۔")).to_be_visible(timeout=20_000)
        expect(page.get_by_role("heading", name="کھیت کی جانچ کا نتیجہ")).to_be_visible(timeout=20_000)
        page.get_by_role("heading", name="کھیت کی جانچ کا نتیجہ").scroll_into_view_if_needed()
        screenshots.append(_capture_page(page))

        page.get_by_text("ضروری احتیاط", exact=True).scroll_into_view_if_needed()
        screenshots.append(_capture_page(page))
        browser.close()
    return screenshots


def _caption_frame(screenshot: Image.Image, index: int, total: int) -> Image.Image:
    frame = screenshot.convert("RGBA")
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((36, HEIGHT - 132, WIDTH - 36, HEIGHT - 26), radius=12, fill=(20, 45, 35, 235))
    draw.rounded_rectangle((36, HEIGHT - 132, 46, HEIGHT - 26), radius=5, fill=(211, 168, 61, 255))
    title, subtitle = CAPTIONS[index]
    draw.text((68, HEIGHT - 119), title, font=_font(27, True), fill=(255, 255, 255, 255))
    draw.text((68, HEIGHT - 78), subtitle, font=_font(19), fill=(229, 239, 226, 255))
    progress_y = HEIGHT - 14
    draw.rounded_rectangle((40, progress_y, WIDTH - 40, progress_y + 4), radius=2, fill=(205, 215, 207, 200))
    progress_x = 40 + int((WIDTH - 80) * ((index + 1) / total))
    draw.rounded_rectangle((40, progress_y, progress_x, progress_y + 4), radius=2, fill=(211, 168, 61, 255))
    return Image.alpha_composite(frame, overlay).convert("RGB")


def render_video(screenshots: list[Image.Image], output_path: Path) -> None:
    if len(screenshots) != len(CAPTIONS):
        raise ValueError(f"Expected {len(CAPTIONS)} captured screens, got {len(screenshots)}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(),
        "-y", "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(output_path),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    rendered = [_caption_frame(image, index, len(screenshots)) for index, image in enumerate(screenshots)]
    held_frames = SCENE_SECONDS * FPS
    try:
        for index, current in enumerate(rendered):
            if index:
                previous = rendered[index - 1]
                for blend_index in range(TRANSITION_FRAMES):
                    alpha = (blend_index + 1) / (TRANSITION_FRAMES + 1)
                    process.stdin.write(Image.blend(previous, current, alpha).tobytes())
            hold_count = held_frames - (TRANSITION_FRAMES if index < len(rendered) - 1 else 0)
            for _ in range(hold_count):
                process.stdin.write(current.tobytes())
        process.stdin.close()
    except BrokenPipeError:
        error = process.stderr.read().decode("utf-8", errors="replace")
        process.wait()
        raise RuntimeError(f"FFmpeg could not encode the walkthrough: {error}") from None
    error = process.stderr.read().decode("utf-8", errors="replace")
    if process.wait() != 0:
        raise RuntimeError(f"FFmpeg could not encode the walkthrough: {error}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture and render a captioned FieldOps AI app walkthrough.")
    parser.add_argument("--url", default="http://127.0.0.1:8501", help="Running FieldOps app URL")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    screenshots = capture_scenes(args.url)
    render_video(screenshots, args.output)
    print(f"Created captioned walkthrough: {args.output}")
    print(f"Duration: approximately {len(screenshots) * SCENE_SECONDS} seconds; {WIDTH}x{HEIGHT}; {FPS} fps")


if __name__ == "__main__":
    main()