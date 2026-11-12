"""Record the wiring guide of a wiring page as the animated GIF the README shows (P791).

The page's "All at once" playback runs on the Web Animations API. The recorder pauses every
animation and moves it to each frame's time before the screenshot, so the frames are exact and
the run needs no real clock. It needs Playwright with its Chromium and Pillow, neither of which
spark installs: `pip install playwright pillow` and `playwright install chromium`, in a virtual
environment of your own.

    python3 tools/record_wiring_guide.py path/to/wiring.html docs/guide/wiring-guide.gif

The page is pixel-games' docs/wiring.html (https://github.com/xmejkal/pixel-games). The GIF
holds the mode bar, the progress bar and the picture, 10 frames a second, 960 pixels wide, and
rests 1.5 seconds on the finished picture before it loops.
"""
import io
import sys
from pathlib import Path

FPS = 10
#: The page is rendered this wide, so the figure needs no horizontal scroll, then scaled to WIDTH.
RENDER_WIDTH = 1120
WIDTH = 960
HOLD_MS = 1500
#: The id of the guide section, its replay button and its mode bar in the page.
GUIDE, REPLAY, MODE_BAR = "#guide", "#g-replay", "#guide .gbar"


def record(page_path, out_path):
    """Write the GIF and return (frame count, byte size)."""
    from PIL import Image
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": RENDER_WIDTH, "height": 1400}, device_scale_factor=1)
        page.goto(Path(page_path).resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.click(REPLAY)
        end_ms = page.evaluate(
            "() => { let end = 0; for (const a of document.getAnimations()) { a.pause();"
            " const t = a.effect.getComputedTiming(); end = Math.max(end, t.delay + t.activeDuration); } return end; }")
        section = page.locator(GUIDE)
        top = page.locator(MODE_BAR).first.bounding_box()["y"] - section.bounding_box()["y"]
        frames = []
        step_ms = 1000 / FPS
        at = 0.0
        while at <= end_ms + HOLD_MS:
            page.evaluate(
                "(t) => document.getAnimations().forEach(a => {"
                " a.currentTime = Math.min(t, a.effect.getComputedTiming().endTime - 1); })", min(at, end_ms))
            image = Image.open(io.BytesIO(section.screenshot(type="png"))).convert("RGB")
            image = image.crop((0, int(top) - 8, image.width, image.height))
            frames.append(image.resize((WIDTH, round(image.height * WIDTH / image.width)), Image.LANCZOS))
            at += step_ms
        browser.close()

    palette = frames[0].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    quantized = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    quantized[0].save(out_path, save_all=True, append_images=quantized[1:], duration=int(step_ms), loop=0,
                      optimize=True, disposal=1)
    return len(frames), Path(out_path).stat().st_size


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        print("usage: record_wiring_guide.py WIRING_HTML OUT_GIF", file=sys.stderr)
        return 2
    count, size = record(argv[0], argv[1])
    print("wrote %s: %d frames, %d KB" % (argv[1], count, size // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
