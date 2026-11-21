"""
Made-up DFRobot wiki pages for the P952 tests (#1358): a page built in code in the shape the live pages had on
2026-11-20 (headings h2 to h4, `<img>` elements, and the JSON-LD list of `DigitalDocument`s), the walk's FireBeetle 2
ESP32-C6 board record with its found files taken out, and the fake bytes of each file. A helper module, no tests in it.
No vendor's bytes: the URLs are the ones the walk's record cites, and every page and file is made up.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WALK_BOARD = ROOT / "tests" / "data" / "breadboard" / "walk-c6" / "boards" / "firebeetle2-esp32c6.json"
BOARD_ID = "firebeetle2-esp32c6"
PAGE = "https://wiki.dfrobot.com/dfr1075/"
#: The top view as the page's `src` names it (the CDN's `.webp`), and the PNG that is fetched.
TOP_VIEW_SRC = "https://dfimg.dfrobot.com/5d57611a3416442fa39bffca/wiki/f24d6c2eaa74dacadb153d6f43c12432_0x0.png.webp"
TOP_VIEW = "https://dfimg.dfrobot.com/5d57611a3416442fa39bffca/wiki/f24d6c2eaa74dacadb153d6f43c12432_0x0.png"
SECOND_PICTURE = "https://dfimg.dfrobot.com/5d57611a3416442fa39bffca/wiki/0000second0000_0x0.png.webp"
PINOUT_PICTURE = "https://dfimg.dfrobot.com/5d57611a3416442fa39bffca/wiki/1fa8b29bf6d340347ccdc39f4648b949_0x0.png.webp"
DRAWING = "https://dfimg.dfrobot.com/wiki/20576/DFR1075_firebeetle-esp32-c6-microcontroller_dimension_v1.pdf"
SCHEMATICS = "https://dfimg.dfrobot.com/wiki/20576/DFR1075_firebeetle-esp32-c6-microcontroller_schematics_v1.zip"
TOP_VIEW_BYTES = b"\x89PNG fake top view"
DRAWING_BYTES = b"%PDF fake drawing"
#: The walk record's keys of the two files P952 finds: taken out of `board()`, so a first run finds them.
FOUND_KEYS = ("firebeetle2-c6-board-overview", "firebeetle2-c6-dimension-v1-1-0")
#: The page's document list as the C6's has it: the schematics first, then the dimension drawing.
DOCUMENTS = (("Schematics", SCHEMATICS, "application/zip"), ("Dimension", DRAWING, "application/pdf"))
#: The page's sections as the C6's has them: the Board Overview with its picture (and a second one), then the pinout.
SECTIONS = (("h4", "Board Overview", (TOP_VIEW_SRC, SECOND_PICTURE)), ("h4", "Pinout", (PINOUT_PICTURE,)))


def page(sections=SECTIONS, documents=DOCUMENTS):
    """A made-up wiki page: each section a heading (its tag and text) and its images (a `src`, or (`src`, `alt`)), and
    the JSON-LD block that lists `documents` (name, url, fileFormat), or no block when `documents` is None."""
    body = []
    for tag, text, images in sections:
        body.append("<%s>%s</%s>" % (tag, text, tag))
        for image in images:
            src, alt = image if isinstance(image, tuple) else (image, text)
            body.append('<p><img src="%s" alt="%s"></p>' % (src, alt))
    listed = "" if documents is None else '<script type="application/ld+json">%s</script>' % json.dumps({"@graph": [
        {"@type": "Product", "name": "FireBeetle 2 ESP32-C6", "subjectOf": [
            {"@type": "DigitalDocument", "name": name, "url": url, "fileFormat": file_format}
            for name, url, file_format in documents]}]})
    return ("<html><head>%s</head><body><h2>FireBeetle 2 ESP32-C6</h2>%s</body></html>" % (listed, "".join(body))).encode()


def answers(**more):
    """The URLs the fake fetch answers, as the C6's page and its two files, with `more` (url -> bytes) over them."""
    return dict({PAGE: page(), TOP_VIEW: TOP_VIEW_BYTES, DRAWING: DRAWING_BYTES}, **more)


def board():
    """A fresh copy of the walk's board record with the two files P952 finds taken out of its `documents`."""
    record = json.loads(WALK_BOARD.read_text())
    for key in FOUND_KEYS:
        del record["documents"][key]
    return record


def walk_board():
    """A fresh copy of the walk's board record as it is, both found files listed."""
    return json.loads(WALK_BOARD.read_text())
